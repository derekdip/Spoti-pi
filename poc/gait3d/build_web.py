"""Build the web viewer: poc/gait3d/web_template.html with poc/results/gait3d_web_data.json
(from poc/gait3d/export_web.py) embedded, written to poc/results/damaged-gait-player.html. The page
is a single file: three.js from a CDN, everything else inline."""
from pathlib import Path
import sys
root = Path(__file__).resolve().parents[2]
tpl = (root / "poc/gait3d/web_template.html").read_text()
data = (root / "poc/results/gait3d_web_data.json").read_text()
out = Path(sys.argv[1]) if len(sys.argv) > 1 else root / "poc/results/damaged-gait-player.html"
out.write_text(tpl.replace("__DATA__", data))
print("written", out, out.stat().st_size // 1024, "KB")
