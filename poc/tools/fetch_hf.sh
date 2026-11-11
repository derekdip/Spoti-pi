#!/bin/sh
# fetch_hf.sh REPO DIR FILE...   (public Hugging Face model files)
set -e; R=$1; D=$2; shift 2; mkdir -p "$D"
for f in "$@"; do [ -s "$D/$f" ] || curl -fsSL --retry 4 -o "$D/$f" "https://huggingface.co/$R/resolve/main/$f"; done
