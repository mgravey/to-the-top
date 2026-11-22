"""Link-preview image (Open Graph / Twitter card), 1200 x 630, from the summary chart.

Renders a small HTML page (title + figures/bias-comparison.svg) with headless Chrome.
Writes figures/social-card.png. Needs Google Chrome (or set CHROME=/path/to/chrome).
"""
import os
import subprocess
import tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
CHROME = os.environ.get('CHROME', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')

page = f'''<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;width:1200px;height:630px;background:#ffffff;color:#1c1c1c;overflow:hidden;
  font-family:system-ui,-apple-system,"Segoe UI",sans-serif}}
.wrap{{display:grid;grid-template-columns:400px 1fr;height:630px}}
.text{{padding:56px 24px 48px 56px;display:flex;flex-direction:column;justify-content:space-between}}
.k{{font-size:17px;letter-spacing:.08em;text-transform:uppercase;color:#5f5f5f}}
h1{{font-size:56px;line-height:1.02;margin:18px 0 18px;letter-spacing:-.02em}}
p{{font-size:23px;line-height:1.35;margin:0;color:#3a3a3a}}
.by{{font-size:18px;color:#5f5f5f}}
.chart{{display:flex;align-items:center;padding-right:24px}}
img{{width:100%}}
</style></head><body><div class="wrap">
<div class="text"><div><div class="k">Austria · 1960–2024</div><h1>Who makes it to the top?</h1>
<p>The gender gap in education has flipped. The gap by parents' education is about three times larger.</p></div>
<div class="by">mgravey.com/to-the-top</div></div>
<div class="chart"><img src="file://{ROOT}figures/bias-comparison.svg"></div>
</div></body></html>'''

with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False) as f:
    f.write(page)
subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--allow-file-access-from-files',
                '--blink-settings=preferredColorScheme=1', '--window-size=1200,630', '--virtual-time-budget=2000',
                f'--screenshot={ROOT}figures/social-card.png', f'file://{f.name}'],
               check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
os.unlink(f.name)
print('figures/social-card.png')
