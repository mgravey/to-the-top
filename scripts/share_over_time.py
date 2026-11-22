"""Girls' and boys' share at each step, over time (x = year).

Same numbers as girls-share-all-steps-animated.svg. For each step, a girls' line and a
boys' line (they add up to 100 %). One step is shown in full at a time (data-hl on the
<svg>, default 1 = Matura; the page switches it with buttons), the others stay faint for context.
Thin horizontal lines mark the step's 2024 level, so past years can be read against today.
Writes figures/share-over-time.svg.
"""
import json
import os; ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'

d = json.load(open(ROOT + 'data/girls-share.json')); years = d['years']; G = d['girls_share_pct']
# step index in the series -> (name, first year drawn, last rough year: dashed up to and including it)
STEPS = [(1, 'Matura', 1960, 1986), (2, '1st degree', 1965, 1990), (3, 'Master', 1991, 1990),
         (4, 'Doctorate', 1981, 1980), (5, 'Professor', 1981, 2006)]
# doctorate: counted share of all doctorates; professor: counted share of new professors from frame 2007 (data 2006)
PHRASE = {'Matura': 'the Matura', '1st degree': 'a first degree', 'Master': "a master's",
          'Doctorate': 'a doctorate', 'Professor': 'a professorship'}

W, H = 820, 560; X0, X1, T, B = 70, 680, 100, 470
x = lambda y: X0 + (y - 1960) * (X1 - X0) / (2024 - 1960)
yv = lambda v: B - v * (B - T) / 100
P = lambda pts: 'M' + ' L'.join(f'{x(a):.1f},{yv(b):.1f}' for a, b in pts)

hl = ''.join(f'svg[data-hl="{c}"] .st{c}{{opacity:1}} svg[data-hl="{c}"] .st{c} .lab,svg[data-hl="{c}"] .sub{c}{{display:inline}} svg[data-hl="{c}"] .st{c} .l{{stroke-width:3}} ' for c in range(1, 6))
o = [f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" data-steps="{','.join(n for _, n, _, _ in STEPS)}" data-hl="1" role="img" aria-label="Girls' and boys' share among the people reaching each step from Matura to professorship, Austria 1960 to 2024, one step at a time">
<style>
svg{{--fg:#1c1c1c;--mu:#6b6b6b;--bd:#dddddd;--bg:#ffffff;--c1:#2f6fed;--c2:#0f9d8a;font-family:system-ui,-apple-system,"Segoe UI",sans-serif}}
@media (prefers-color-scheme:dark){{svg{{--fg:#ededed;--mu:#a0a0a0;--bd:#333333;--bg:#0e0e0e;--c1:#5b8dff;--c2:#2dd4bf}}}}
.bg{{fill:var(--bg)}} text{{fill:var(--fg)}} .m{{fill:var(--mu)}}
.gl{{stroke:var(--bd);stroke-width:1}} .par{{stroke:var(--mu);stroke-width:1.2;stroke-dasharray:2 4}}
.l{{fill:none;stroke-width:1.5;stroke-linejoin:round;stroke-linecap:round}} .r{{stroke-dasharray:5 5}}
.g{{stroke:var(--c1)}} .b{{stroke:var(--c2)}} .fg{{fill:var(--c1)}} .fb{{fill:var(--c2)}}
.today{{stroke-width:1.2;opacity:.6}} .dot{{stroke:var(--bg);stroke-width:2}}
.st{{opacity:.13;transition:opacity .25s}} .lab,.sub{{display:none}}
{hl}
</style>
<rect class="bg" width="{W}" height="{H}"/>''']
o.append('<text x="16" y="30" font-size="19" font-weight="600">The same shares over time</text>')
for c, (_, name, _, _) in enumerate(STEPS, 1):
    o.append(f'<text class="m sub sub{c}" x="16" y="52" font-size="14">Austria, 1960 to 2024. Out of every 100 people reaching {PHRASE[name]}, how many are girls and boys.</text>')
o.append('<rect class="fg" x="16" y="68" width="16" height="4" rx="2"/><text x="38" y="75" font-size="13">Girls</text>'
         '<rect class="fb" x="82" y="68" width="16" height="4" rx="2"/><text x="104" y="75" font-size="13">Boys</text>'
         '<line class="l r" x1="150" x2="174" y1="70" y2="70" style="stroke:var(--mu)"/><text x="180" y="75" font-size="13">Rough estimate</text>'
         '<line x1="290" x2="314" y1="70" y2="70" style="stroke:var(--mu);stroke-width:1.2"/><text x="320" y="75" font-size="13">Thin line: the 2024 level, for comparison</text>')
for v in range(0, 101, 10):
    o.append(f'<line class="{"par" if v == 50 else "gl"}" x1="{X0}" x2="{X1}" y1="{yv(v):.1f}" y2="{yv(v):.1f}"/>'
             f'<text class="m" x="{X0 - 8}" y="{yv(v) + 4:.1f}" font-size="12" text-anchor="end">{v} %</text>')
o.append(f'<text class="m" x="{X0 + 6}" y="{yv(50) - 7:.1f}" font-size="12">parity</text>')
for y in range(1960, 2025, 10):
    o.append(f'<text class="m" x="{x(y):.1f}" y="{B + 22}" font-size="12" text-anchor="middle">{y}</text>')
for c, (j, name, y0, rough_to) in enumerate(STEPS, 1):
    pts = {'g': [(y, G[i][j]) for i, y in enumerate(years) if y >= y0 and G[i][j] is not None]}
    pts['b'] = [(y, 100 - v) for y, v in pts['g']]
    o.append(f'<g class="st st{c}">')
    ends = []
    for k in 'gb':
        p = pts[k]; now = p[-1][1]
        rough = [q for q in p if q[0] <= rough_to + 1]; solid = [q for q in p if q[0] >= rough_to + 1]
        o.append(f'<line class="today lab {k}" x1="{x(p[0][0]):.1f}" x2="{x(2024):.1f}" y1="{yv(now):.1f}" y2="{yv(now):.1f}"/>')
        if len(rough) > 1: o.append(f'<path class="l r {k}" d="{P(rough)}"/>')
        if len(solid) > 1: o.append(f'<path class="l {k}" d="{P(solid)}"/>')
        o.append(f'<circle class="dot f{k} lab" cx="{x(2024):.1f}" cy="{yv(now):.1f}" r="4.5"/>')
        ends.append([yv(now), 'Girls' if k == 'g' else 'Boys', now])
    ends.sort()
    if ends[1][0] - ends[0][0] < 17:
        mid = (ends[0][0] + ends[1][0]) / 2; ends[0][0] = mid - 8.5; ends[1][0] = mid + 8.5
    for ly, who, v in ends:
        o.append(f'<text class="lab" x="{x(2024) + 10:.1f}" y="{ly + 4:.1f}" font-size="13"><tspan font-weight="600">{who}</tspan> {v:.0f} %</text>')
    o.append('</g>')
o.append(f'<text class="m" x="16" y="{H - 30}" font-size="11">From the rates per 100 children (girls are 49.5 % of an age group). Master\'s are counted separately from 1991. Faint lines: the other steps.</text>')
o.append(f'<text class="m" x="16" y="{H - 14}" font-size="11">Doctorate and professor (from 2007) are counted shares: all doctorates, all new professors (22 university reports). Earlier professor values: estimate.</text>')
o.append('</svg>')
open(ROOT + 'figures/share-over-time.svg', 'w').write('\n'.join(o))
