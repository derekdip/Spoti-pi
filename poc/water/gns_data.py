"""Minimal reader for the DeepMind "Learning to Simulate" TFRecord datasets, no TensorFlow.

Each record is a tf.train.SequenceExample with
  context      : 'key' (int64), 'particle_type' (bytes: int64 array)
  feature_lists: 'position' (one bytes entry per step: float32 array (n_particles, dim))

Also extracts a free-surface height profile from the 2-D particle clouds.
"""
from __future__ import annotations

import struct
from pathlib import Path

import numpy as np


def _varint(buf: bytes, i: int) -> tuple[int, int]:
    shift, val = 0, 0
    while True:
        b = buf[i]
        i += 1
        val |= (b & 0x7F) << shift
        if not b & 0x80:
            return val, i
        shift += 7


def _fields(buf: bytes):
    """Yield (field_number, value) for a protobuf message; length-delimited values as bytes."""
    i, n = 0, len(buf)
    while i < n:
        tag, i = _varint(buf, i)
        fn, wt = tag >> 3, tag & 7
        if wt == 0:
            v, i = _varint(buf, i)
        elif wt == 1:
            v, i = buf[i:i + 8], i + 8
        elif wt == 2:
            ln, i = _varint(buf, i)
            v, i = buf[i:i + ln], i + ln
        elif wt == 5:
            v, i = buf[i:i + 4], i + 4
        else:
            raise ValueError(f"unsupported wire type {wt}")
        yield fn, v


def _feature_bytes(feature: bytes) -> list[bytes]:
    """Feature{bytes_list=1{value=1 repeated}} -> list of bytes values."""
    out = []
    for fn, v in _fields(feature):
        if fn == 1:  # bytes_list
            out += [val for f2, val in _fields(v) if f2 == 1]
    return out


def _feature_int64(feature: bytes) -> list[int]:
    out = []
    for fn, v in _fields(feature):
        if fn == 3:  # int64_list
            for f2, val in _fields(v):
                if f2 == 1:
                    if isinstance(val, bytes):  # packed
                        i = 0
                        while i < len(val):
                            x, i = _varint(val, i)
                            out.append(x)
                    else:
                        out.append(val)
    return out


def _map_entries(msg: bytes):
    """Features / FeatureLists map: repeated entry{key=1 string, value=2 message}."""
    for fn, entry in _fields(msg):
        if fn != 1:
            continue
        key, val = None, None
        for f2, v in _fields(entry):
            if f2 == 1:
                key = v.decode()
            elif f2 == 2:
                val = v
        yield key, val


def read_tfrecords(path: str | Path, dim: int = 2, max_records: int | None = None):
    """Yield (particle_type (N,), positions (T, N, dim)) per trajectory."""
    data = Path(path).read_bytes()
    i, count = 0, 0
    while i < len(data):
        (length,) = struct.unpack_from("<Q", data, i)
        i += 8 + 4  # length + masked crc
        rec = data[i:i + length]
        i += length + 4
        context, feature_lists = b"", b""
        for fn, v in _fields(rec):
            if fn == 1:
                context = v
            elif fn == 2:
                feature_lists = v
        ptype = None
        for key, feat in _map_entries(context):
            if key == "particle_type":
                ptype = np.frombuffer(b"".join(_feature_bytes(feat)), dtype=np.int64)
        positions = None
        for key, flist in _map_entries(feature_lists):
            if key == "position":
                steps = [v for fn, v in _fields(flist) if fn == 1]  # FeatureList.feature repeated
                frames = [np.frombuffer(b"".join(_feature_bytes(s)), dtype=np.float32).reshape(-1, dim) for s in steps]
                positions = np.stack(frames)
        yield ptype, positions
        count += 1
        if max_records and count >= max_records:
            return


def surface_profile(positions: np.ndarray, bounds, bins: int = 64, top_fraction: float = 0.004) -> tuple[np.ndarray, np.ndarray]:
    """Free-surface height per x-bin and frame for a 2-D particle cloud.

    Height is the mean of the top few particles in each column (robust to single fliers).
    Empty columns are NaN. Returns (x_centres (bins,), h (T, bins)).
    """
    (x0, x1), (y0, _) = bounds
    edges = np.linspace(x0, x1, bins + 1)
    xc = 0.5 * (edges[:-1] + edges[1:])
    T, N, _ = positions.shape
    h = np.full((T, bins), np.nan)
    k = max(1, int(round(top_fraction * N)))  # top few particles of a column define the surface
    for t in range(T):
        col = np.clip(np.searchsorted(edges, positions[t, :, 0]) - 1, 0, bins - 1)
        ys = positions[t, :, 1] - y0
        order = np.argsort(-ys)
        col_o, ys_o = col[order], ys[order]
        for b in range(bins):
            m = col_o == b
            if m.any():
                h[t, b] = ys_o[m][:k].mean()
    return xc, h
