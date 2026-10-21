"""The bank for the live tool: per word, recognised doodles with at least three strokes, centred in the
256 box, with their ids, as compact JSON; then build_live.py embeds it in live_template.html.

  python3 -m poc.doodle.export_live [n per word]   -> poc/results/doodle_live_bank.json
"""
from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from poc.doodle.bank import WORDS, load_word

OUT = Path(__file__).resolve().parents[2] / "poc/results/doodle_live_bank.json"


def main(n=300):
    bank = {}
    for w in WORDS:
        rows = [(i, d) for i, d in load_word(w, 2000, with_ids=True) if len(d) >= 3][:n]
        bank[w] = [dict(id=i, s=[[[int(round(x)), int(round(y))] for x, y in st] for st in d]) for i, d in rows]
        print(w, len(bank[w]))
    json.dump(bank, open(OUT, "w"), separators=(",", ":")); print("written", OUT, OUT.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 300)
