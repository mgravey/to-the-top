"""How unequal is access to Matura and a degree: gender (1960-2024) against parents' education (AES 2007-2022/23).

One measure for both: the dissimilarity index, i.e. the share of everyone reaching a step who would have to be
swapped with someone from another group so that every group holds exactly its share of the population
(0 = proportional). Gender uses the per-100 rates by sex (girls = 49.5 % of an age group); parents' education
uses the four parent groups, their population weights and the share of each reaching the step, ages 25 to 44.
Gender is drawn signed (above zero girls behind, below zero boys behind) so the flip is visible.
Needs data/series.json and data/parent-education.json (python3 scripts/parent_education.py).
Writes data/bias-comparison.json and figures/bias-comparison.svg.
"""
import json
from html import escape
import os; ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
from credit import with_credit

GIRLS = 0.495
STEPS = [('matura', 'Matura', 1, [2, 3]), ('degree', 'Degree', 2, [3])]  # series index, own levels counted
series = json.load(open(ROOT + 'data/series.json'))
parents = json.load(open(ROOT + 'data/parent-education.json'))['frames_age_25_44']
odds = lambda p: p / (100 - p)

out = {}
for key, _, s, own in STEPS:
    gender = []
    for year, g, b in zip(series['years'], series['S']['g'], series['S']['b']):
        if g[s] is None:
            continue
        share = GIRLS * g[s] / (GIRLS * g[s] + (1 - GIRLS) * b[s])
        gender.append(dict(year=year, signed=round(100 * (GIRLS - share), 2),
                           odds_ratio=round(max(odds(g[s]) / odds(b[s]), odds(b[s]) / odds(g[s])), 2)))
    fam = []
    for f in parents:
        w = f['parent_width_weights']; total = sum(w)
        reach = [w[p] / total * sum(f['m'][p][c] for c in own) / sum(f['m'][p]) for p in range(4)]
        d = 50 * sum(abs(r / sum(reach) - w[p] / total) for p, r in enumerate(reach))
        fam.append(dict(year=f['survey_year'], label=f['title'].replace('Survey ', ''), D=round(d, 2),
                        estimated_group_sizes=f['parent_width_is_assumed']))
    out[key] = dict(gender=gender, parents=fam)
json.dump(out, open(ROOT + 'data/bias-comparison.json', 'w'), indent=1)

W, H = 820, 560
X0, X1, T, B = 56, 640, 120, 500
LO, HI = -12, 37
x = lambda y: X0 + (y - 1960) * (X1 - X0) / (2025 - 1960)
yv = lambda v: T + (HI - v) * (B - T) / (HI - LO)
path = lambda pts: 'M' + ' L'.join(f'{x(a):.1f},{yv(b):.1f}' for a, b in pts)
DASH = {'matura': '', 'degree': ' stroke-dasharray="7 5"'}

o = [f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-labelledby="bias-title bias-desc">
<title id="bias-title">Unequal access by gender and by parents' education, Austria</title>
<desc id="bias-desc">Share of people reaching Matura or a degree who would have to be swapped for every group to hold its population share. Gender 1960 to 2024: girls behind until about 1982 (Matura) and 2002 (degree), boys behind since, about 8 percent for both in 2024. Parents' education, adults 25 to 44, surveys 2007 to 2022/23: 21 percent for Matura (the size of the gender gap in 1961) and 29 percent for a degree (larger than any gender gap since 1965).</desc>
<style>
svg{{--fg:#1c1c1c;--mu:#6b6b6b;--bd:#dddddd;--bg:#ffffff;--g:#2f6fed;--b:#0f9d8a;--p:#e2622f;font-family:system-ui,-apple-system,"Segoe UI",sans-serif}}
@media (prefers-color-scheme:dark){{svg{{--fg:#ededed;--mu:#a0a0a0;--bd:#333333;--bg:#0e0e0e;--g:#5b8dff;--b:#199e70;--p:#d95926}}}}
.bg{{fill:var(--bg)}} text{{fill:var(--fg)}} .m{{fill:var(--mu)}}
.gl{{stroke:var(--bd);stroke-width:1}} .zero{{stroke:var(--mu);stroke-width:1}}
.l{{fill:none;stroke-width:2.2;stroke-linejoin:round}} .g{{stroke:var(--g)}} .b{{stroke:var(--b)}} .p{{stroke:var(--p)}}
.ref{{stroke:var(--p);stroke-width:1.2;stroke-dasharray:1.5 3.5}}
.dot{{stroke:var(--bg);stroke-width:2}} .hit{{fill:transparent}} .hit:hover{{fill:var(--mu);fill-opacity:.12}}
</style>
<rect class="bg" width="{W}" height="{H}"/>
<text x="16" y="30" font-size="19" font-weight="600">Family background is today's big gap; the gender gap has flipped</text>
<text class="m" x="16" y="52" font-size="13">Share of people reaching each step who would have to be swapped for every group to hold its population share (0 = fair)</text>''']
# legend
lx, ly = 16, 80
for label, cls, dash, dot in [("Gender, girls behind", 'g', '', False), ('Gender, boys behind', 'b', '', False),
                              ("Parents' education (adults 25-44)", 'p', '', True)]:
    o.append(f'<line class="l {cls}" x1="{lx}" x2="{lx + 24}" y1="{ly}" y2="{ly}"/>' +
             (f'<circle cx="{lx + 12}" cy="{ly}" r="4" fill="var(--p)"/>' if dot else '') +
             f'<text x="{lx + 30}" y="{ly + 4}" font-size="13">{label}</text>')
    lx += 30 + 8 * len(label) + 22
lx = 16; ly = 102
for label, dash in [('Matura or higher', ''), ('University or college degree', ' stroke-dasharray="7 5"')]:
    o.append(f'<line x1="{lx}" x2="{lx + 24}" y1="{ly}" y2="{ly}" stroke="var(--fg)" stroke-width="2.2"{dash}/>'
             f'<text x="{lx + 30}" y="{ly + 4}" font-size="13">{label}</text>')
    lx += 30 + 7.6 * len(label) + 22
# axes
for v in (-10, 10, 20, 30):
    o.append(f'<line class="gl" x1="{X0}" x2="{x(2025)}" y1="{yv(v):.1f}" y2="{yv(v):.1f}"/>'
             f'<text class="m" x="{X0 - 8}" y="{yv(v) + 4:.1f}" font-size="12" text-anchor="end">{abs(v)}%</text>')
o.append(f'<line class="zero" x1="{X0}" x2="{x(2025)}" y1="{yv(0):.1f}" y2="{yv(0):.1f}"/>'
         f'<text class="m" x="{X0 - 8}" y="{yv(0) + 4:.1f}" font-size="12" text-anchor="end">0</text>')
for yr in range(1960, 2021, 10):
    o.append(f'<text class="m" x="{x(yr):.1f}" y="{B + 22}" font-size="12" text-anchor="middle">{yr}</text>')
o.append(f'<text x="{X0 + 6}" y="{yv(0) - 8:.1f}" font-size="12">▲ girls behind</text>'
         f'<text x="{X0 + 6}" y="{yv(0) + 18:.1f}" font-size="12">▼ boys behind</text>')

hover = {}
right = []
for key, name, _, _ in STEPS:
    g, fam = out[key]['gender'], out[key]['parents']
    now = fam[-1]
    o.append(f'<line class="ref" x1="{X0}" x2="{x(now["year"]):.1f}" y1="{yv(now["D"]):.1f}" y2="{yv(now["D"]):.1f}"/>')
    k = next(i for i, d in enumerate(g) if d['signed'] < 0)
    a, b = g[k - 1], g[k]
    flip = a['year'] + a['signed'] / (a['signed'] - b['signed'])
    up = [(d['year'], d['signed']) for d in g[:k]] + [(flip, 0)]
    down = [(flip, 0)] + [(d['year'], d['signed']) for d in g[k:]]
    o.append(f'<path class="l g" d="{path(up)}"{DASH[key]}/><path class="l b" d="{path(down)}"{DASH[key]}/>')
    o.append(f'<circle class="dot" cx="{x(flip):.1f}" cy="{yv(0):.1f}" r="4.5" fill="var(--fg)"/>'
             f'<text x="{x(flip) + 8:.1f}" y="{yv(0) - 8:.1f}" font-size="12.5" font-weight="600">{name} flips ~{round(flip)}</text>')
    o.append(f'<path class="l p" d="{path([(d["year"], d["D"]) for d in fam])}"{DASH[key]}/>')
    for d in fam:
        fill = 'var(--bg)' if d['estimated_group_sizes'] else 'var(--p)'
        o.append(f'<circle cx="{x(d["year"]):.1f}" cy="{yv(d["D"]):.1f}" r="5" fill="{fill}" stroke="var(--p)" stroke-width="2.2"/>')
    same = [d for d in g if d['signed'] >= now['D']]
    if same:
        y0 = same[-1]['year']
        o.append(f'<circle class="dot" cx="{x(y0):.1f}" cy="{yv(now["D"]):.1f}" r="4.5" fill="var(--g)"/>')
        note = f'= gender gap of {y0}'
    else:
        note = f'> any gender gap since {g[0]["year"]}'
    right.append((yv(now['D']), f"Parents · {name} {now['D']:.0f}%", note))
    for d in g:
        hover.setdefault(d['year'], []).append(f"{name}, gender: {abs(d['signed']):.1f}% ({'girls' if d['signed'] > 0 else 'boys'} behind, odds ratio {d['odds_ratio']:.2f})")
    for d in fam:
        hover.setdefault(round(d['year']), []).append(
            f"{name}, parents' education ({d['label']}): {d['D']:.1f}%" + (' (estimated group sizes)' if d['estimated_group_sizes'] else ''))
last = [out[k]['gender'][-1]['signed'] for k, *_ in STEPS]
right.append((yv(sum(last) / len(last)), f'Gender · both ≈ {abs(sum(last) / len(last)):.0f}%', 'boys behind, 2024'))
for yy, a, b in right:
    o.append(f'<text x="{x(2025) + 10:.1f}" y="{yy + 4:.1f}" font-size="13" font-weight="600">{a}</text>'
             f'<text class="m" x="{x(2025) + 10:.1f}" y="{yy + 20:.1f}" font-size="12">{b}</text>')
# one hover strip per year, with a native tooltip
step = (X1 - X0) / (2025 - 1960)
for year in sorted(hover):
    o.append(f'<rect class="hit" x="{x(year) - step / 2:.1f}" y="{T}" width="{step:.1f}" height="{B - T}"><title>{year}\n' +
             escape('\n'.join(hover[year])) + '</title></rect>')
o.append(f'<text class="m" x="16" y="{H - 22}" font-size="11">Gender: Statistics Austria, per-100 rates by sex (1960s values rough). Parents: Adult Education Survey 2007 to 2022/23, Bildung in Zahlen.</text>'
         f'<text class="m" x="16" y="{H - 7}" font-size="11">Hollow dots: estimated parent-group sizes. Dotted lines: today\'s parental level carried back in time.</text>')
o.append('</svg>')
open(ROOT + 'figures/bias-comparison.svg', 'w').write(with_credit('\n'.join(o)))
