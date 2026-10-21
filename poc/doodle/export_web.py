"""Sessions for the viewer: rounds at three chaos levels, and a room session with people arriving.

  python3 -m poc.doodle.export_web   -> poc/results/doodle_sessions.json, then build_web.py embeds it.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from poc.doodle.bank import WORDS, load_bank
from poc.doodle.bots import make_bots, run_round, simulate_room, CANVAS, WEB_SEATS, FILL_TO, RESERVE

OUT = Path(__file__).resolve().parents[2] / "poc/results/doodle_sessions.json"


def round_session(word, bank, chaos, n_bots, rng):
    bots = make_bots(n_bots, chaos, rng); canvas, frame, plan = run_round(word, bank, bots, chaos, rng, duration=45.0)
    strokes = [dict(bot=s.bot, t=s.t.round(3).tolist(), xy=s.xy.round(1).tolist(), kind=s.kind, round=0) for s in canvas]
    bubbles = [dict(t=tb, who=b.name, text=tx, round=0) for b in bots for tb, tx in b.bubbles]
    events = [dict(t=0.0, type="join", who=b.name, bot=True, color=b.color) for b in bots] + [dict(t=0.0, type="word", word=word, round=0)]
    return dict(canvas=CANVAS, seats=WEB_SEATS, fill_to=FILL_TO, reserve=RESERVE, strokes=strokes, bubbles=bubbles, events=events,
                bots={b.name: dict(color=b.color, persona=b.persona, behaviour=b.behaviour, skill=round(b.skill, 2), stubborn=round(b.stubborn, 2)) for b in bots})


def main():
    rng = np.random.default_rng(7); bank = load_bank(n=400)
    sessions = {}
    for word, chaos, n in (("house", 0.1, 4), ("cat", 0.4, 4), ("bicycle", 0.4, 5), ("tree", 0.7, 4), ("sun", 0.85, 5), ("fish", 0.5, 3)):
        sessions[f"{word} · chaos {chaos}"] = round_session(word, bank, chaos, n, rng); print(word, chaos, len(sessions[f'{word} · chaos {chaos}']['strokes']), "strokes")
    sessions["room: people arrive, bots leave"] = simulate_room(bank, rng, rounds=5, round_s=40.0, arrivals=[25.0, 70.0, 95.0, 140.0, 150.0, 185.0], chaos=0.4)
    print("room events", [(round(e["t"]), e["type"], e.get("who", e.get("word"))) for e in sessions["room: people arrive, bots leave"]["events"]])
    json.dump(sessions, open(OUT, "w"), separators=(",", ":")); print("written", OUT, OUT.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
