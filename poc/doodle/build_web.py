"""Build the doodle-bots viewer: poc/doodle/web_template.html with poc/results/doodle_sessions.json
embedded, written to poc/results/doodle-bots.html (or the path given)."""
from pathlib import Path
import sys
root = Path(__file__).resolve().parents[2]
tpl = (root / "poc/doodle/web_template.html").read_text()
data = (root / "poc/results/doodle_sessions.json").read_text()
out = Path(sys.argv[1]) if len(sys.argv) > 1 else root / "poc/results/doodle-bots.html"
out.write_text(tpl.replace("__DATA__", data))
print("written", out, out.stat().st_size // 1024, "KB")
