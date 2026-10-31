"""Build the live doodle-bots tool: poc/doodle/live_template.html with poc/results/doodle_live_bank.json
embedded, written to poc/results/doodle-bots-live.html (or the path given). The simulation runs in
the browser; the page is self-contained."""
from pathlib import Path
import sys
root = Path(__file__).resolve().parents[2]
tpl = (root / "poc/doodle/live_template.html").read_text()
data = (root / "poc/results/doodle_live_bank.json").read_text()
sim = (root / "poc/doodle/sim.js").read_text()
out = Path(sys.argv[1]) if len(sys.argv) > 1 else root / "poc/results/doodle-bots-live.html"
out.write_text(tpl.replace("__SIM__", sim).replace("__BANK__", data))
print("written", out, out.stat().st_size // 1024, "KB")
