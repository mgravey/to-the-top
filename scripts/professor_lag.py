"""Is the professor gap a bias or a delay?

Women's share among professors in post, among newly hired professors (implied by
the stock), and among doctorates shifted 10 years forward, Austria 1990-2045.
Writes figures/professor-lag.svg and data/professor-lag.json.
"""
import re, json
import os; ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'

L = open(ROOT + 'data/biz-2024-25-report.txt', encoding='utf-8').read().split('\n')
def table(title, stop=400):
    i0 = next(i for i, l in enumerate(L) if l.strip().startswith(title)); out = {}
    for l in L[i0 + 1:i0 + stop]:
        if re.match(r'\s*\d\.\d_\d', l): break
        m = re.match(r'\s*((?:19|20)\d\d)/\d\d\s+(.*)', l)
        if m: out[int(m.group(1))] = [0 if t.strip() == '-' else float(re.sub(r'[ .]', '', t).replace(',', '.')) for t in re.split(r'\s{2,}', m.group(2).strip())]
    return out

pf = table('4.1_8 Entwicklung')    # professors in post: [total, men, women], 1980-2024
dk = table('2.2_13 Entwicklung')   # doctorates: [men, women, total], 1980-2023
doc = {y: 100 * v[1] / v[2] for y, v in dk.items()}
post = {y: 100 * v[2] / v[0] for y, v in pf.items()}

LAG = 15                 # years from doctorate to appointment: best fit to the counted appointments 2006-2025 (below)
EXIT = 0.043             # yearly departures used only for the pre-2006 estimate (2024: 252 hired - 117 growth)

# counted appointments 2006-2025, all 22 public universities (data/universities.json, built by universities.py)
NAT = {r['year']: r for r in json.load(open(ROOT + 'data/universities.json'))['national']}
cnt = {y: r['appointments_women_pct'] for y, r in NAT.items()}
def mean3(y):
    ks = [k for k in (y - 1, y, y + 1) if k in NAT]
    return 100 * sum(NAT[k]['appointments_women'] for k in ks) / sum(NAT[k]['appointments_total'] for k in ks)
cnt3 = {y: mean3(y) for y in NAT}
post[2025] = 100 * NAT[2025]['professors_women'] / NAT[2025]['professors_total']   # counted, university sum

# ESTIMATE for years without counts (before 2006): new professors implied by the yearly change in professors
# in post, women = W(y+1) - W(y)(1-ew), men = M(y+1) - M(y)(1-em). The departure rates ew, em are calibrated so
# that the estimate matches the counted appointments 2006-2024 (5-year centred means); then applied before 2006.
def implied(ew, em):
    out = {}
    for y in range(1985, 2023):
        hwv = sum(pf[k + 1][2] - pf[k][2] * (1 - ew) for k in range(y - 3, y + 2))
        hmv = sum(pf[k + 1][1] - pf[k][1] * (1 - em) for k in range(y - 3, y + 2))
        out[y] = 100 * hwv / (hwv + hmv)
    return out
def mean5(y):
    ks = [k for k in range(y - 2, y + 3) if k in NAT]
    return 100 * sum(NAT[k]['appointments_women'] for k in ks) / sum(NAT[k]['appointments_total'] for k in ks)
calib = [y for y in range(2008, 2023)]
err = lambda h: sum((h[y] - mean5(y)) ** 2 for y in calib) / len(calib)
EW, EM = min(((ew / 1000, em / 1000) for ew in range(5, 80) for em in range(20, 90)), key=lambda r: err(implied(*r)))
hire = implied(EW, EM)
# same estimate as yearly counts by sex (3-year centred mean), used before 2006 by build_series.py
est_sex = {}
for y in range(1982, 2006):
    ks = range(y - 2, y + 1)   # hires during year k = change from end of k-1 to end of k
    est_sex[y] = [sum(pf[k + 1][2] - pf[k][2] * (1 - EW) for k in ks) / 3, sum(pf[k + 1][1] - pf[k][1] * (1 - EM) for k in ks) / 3]
print('calibrated departures: women %.3f, men %.3f per year; rmse vs counts %.1f pp' % (EW, EM, err(hire) ** .5))
print('equal-rate estimate rmse %.1f pp' % err(implied(0.043, 0.043)) ** .5)

# fit: ratio of counted hiring share to the doctorate share L years earlier, pooled in 3-year blocks
def ratios(L):
    out = []
    for y0 in range(2006, 2025, 3):
        ys = [y for y in range(y0, y0 + 3) if y in NAT]
        h = 100 * sum(NAT[y]['appointments_women'] for y in ys) / sum(NAT[y]['appointments_total'] for y in ys)
        out.append(h / (sum(doc[y - L] for y in ys) / len(ys)))
    return out
fits = {}
for L in range(5, 19):
    r = ratios(L); m = sum(r) / len(r); fits[L] = {'mean_ratio': m, 'sd': (sum((v - m) ** 2 for v in r) / len(r)) ** .5}
best = min(fits, key=lambda L: fits[L]['sd'])
ALPHA = fits[LAG]['mean_ratio']
print('most stable lag', best, {L: (round(f['mean_ratio'], 2), round(f['sd'], 3)) for L, f in fits.items()})
print('lag %d: women hired at %.2f x their doctorate share' % (LAG, ALPHA))

# MODEL projection from the 2025 count: number of professors and the 2021-25 hiring rate held constant;
# women hired at ALPHA x their share of doctorates LAG years earlier, then at ALPHA x the 2019-23 mean
H = sum(NAT[y]['appointments_total'] for y in range(2021, 2026)) / 5
rate = H / NAT[2025]['professors_total']
d_late = sum(doc[y] for y in range(2019, 2024)) / 5
proj = {2025: post[2025]}; s = post[2025]
for y in range(2026, 2046):
    s = s * (1 - rate) + rate * ALPHA * doc.get(y - LAG, d_late); proj[y] = s
print('projection', {y: round(proj[y], 1) for y in (2030, 2035, 2040, 2045)}, 'rate %.3f' % rate)

json.dump({'doctorates_women_pct': doc, 'professors_in_post_women_pct': post,
           'appointments_counted_women_pct': cnt, 'appointments_counted_women_pct_3y': cnt3,
           'implied_hires_women_pct_5y_ESTIMATE': hire, 'estimate_departure_rates': {'women': EW, 'men': EM}, 'implied_hires_by_sex_ESTIMATE': est_sex, 'projection_in_post_MODEL': proj,
           'lag': LAG, 'alpha': ALPHA, 'lag_fits': fits, 'hiring_rate': rate},
          open(ROOT + 'data/professor-lag.json', 'w'), indent=1)

# ---- draw   (solid = counted data, dashed = estimate or model)
W_, H_ = 820, 580; X0, X1, T, B = 58, 700, 128, 490
Y0 = 1980
x = lambda y: X0 + (y - Y0) * (X1 - X0) / (2045 - Y0)
yv = lambda v: B - v * (B - T) / 60
P = lambda pts: 'M' + ' L'.join(f'{x(a):.1f},{yv(b):.1f}' for a, b in pts)
o = [f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W_} {H_}" role="img" aria-label="Women's share among doctorates at their award year, the share they imply among new professors 15 years later, counted new professors from 2006 and professors in post, Austria 1980 to 2045, with a projection">
<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--mu)"/></marker></defs>
<style>
svg{{--fg:#1c1c1c;--mu:#6b6b6b;--bd:#dddddd;--bg:#ffffff;--c1:#6250d6;--c2:#c98500;--c3:#d55181;font-family:system-ui,-apple-system,"Segoe UI",sans-serif}}
@media (prefers-color-scheme:dark){{svg{{--fg:#ededed;--mu:#a0a0a0;--bd:#333333;--bg:#0e0e0e;--c1:#9085e9;--c2:#c98500;--c3:#d55181}}}}
.bg{{fill:var(--bg)}} text{{fill:var(--fg)}} .m{{fill:var(--mu)}}
.gl{{stroke:var(--bd);stroke-width:1}} .par{{stroke:var(--mu);stroke-width:1;stroke-dasharray:2 4}}
.l{{fill:none;stroke-width:2.5;stroke-linejoin:round;stroke-linecap:round}} .e{{stroke-dasharray:6 5;stroke-width:2}}
.c1{{stroke:var(--c1)}} .c2{{stroke:var(--c2)}} .c3{{stroke:var(--c3)}} .k{{stroke:var(--fg)}}
.d3{{fill:var(--c3);opacity:.45}} .now{{fill:var(--mu);opacity:.08}} .arr{{fill:none;stroke:var(--mu);stroke-width:1.4}}
</style>
<rect class="bg" width="{W_}" height="{H_}"/>
<text x="16" y="30" font-size="19" font-weight="600">Today's new professors are the doctorates of fifteen years ago</text>
<text x="16" y="52" font-size="14" class="m">Women's share, Austria. Violet: doctorates when awarded, and (dashed) the share they imply 15 years later.</text>
<line class="l k" x1="16" x2="40" y1="80" y2="80"/><text x="46" y="84" font-size="13">counted</text>
<line class="l k e" x1="112" x2="136" y1="80" y2="80"/><text x="142" y="84" font-size="13">estimated, expected or projected</text>
<circle class="d3" cx="362" cy="80" r="3.5"/><text x="372" y="84" font-size="13">single year, counted</text>''']
o.append(f'<rect class="now" x="{x(2025):.1f}" y="{T}" width="{x(2045) - x(2025):.1f}" height="{B - T}"/>')
o.append(f'<text class="m" x="{x(2025) + 8:.1f}" y="{T + 16}" font-size="12">projection</text>')
for v in range(0, 61, 10):
    o.append(f'<line class="{"par" if v == 50 else "gl"}" x1="{X0}" x2="{X1}" y1="{yv(v):.1f}" y2="{yv(v):.1f}"/><text class="m" x="{X0 - 8}" y="{yv(v) + 4:.1f}" font-size="12" text-anchor="end">{v} %</text>')
o.append(f'<text class="m" x="{x(1981)}" y="{yv(50) - 6:.1f}" font-size="12">parity</text>')
for y in range(1980, 2046, 10):
    o.append(f'<text class="m" x="{x(y):.1f}" y="{B + 22}" font-size="12" text-anchor="middle">{y}</text>')
o.append(f'<line class="gl" x1="{x(2006):.1f}" x2="{x(2006):.1f}" y1="{T}" y2="{B}" stroke-dasharray="3 3"/>')
o.append(f'<text class="m" x="{x(2006) - 6:.1f}" y="{T + 16}" font-size="12" text-anchor="end">no counts of new professors before 2006</text>')
# doctorates at their true year (counted) and the expectation 15 years later (model)
dtrue = sorted(doc.items()); exp = [(y + LAG, ALPHA * v) for y, v in dtrue]
o.append(f'<path class="l c1" d="{P(dtrue)}"/>')
o.append(f'<path class="l e c1" d="{P(exp)}" style="opacity:.75"/>')
# arrows showing the shift: same cohort of doctors, 15 years later
for y in (2005,):
    x1, y1, x2, y2 = x(y), yv(doc[y]) - 6, x(y + LAG), yv(ALPHA * doc[y]) - 6
    mx, my = (x1 + x2) / 2, yv(50) + 8
    o.append(f'<path class="arr" d="M{x1:.1f},{y1:.1f} Q{mx:.1f},{my:.1f} {x2:.1f},{y2:.1f}" marker-end="url(#ar)"/>')
    o.append(f'<text class="m" x="{mx:.1f}" y="{my + 12:.1f}" font-size="12" text-anchor="middle">same doctors, 15 years later</text>')
o.append(f'<path class="l e c3" d="{P([(y, hire[y]) for y in sorted(hire) if 1990 <= y < 2006] + [(2006, cnt3[2006])])}"/>')
for y, v in sorted(cnt.items()):
    o.append(f'<circle class="d3" cx="{x(y):.1f}" cy="{yv(v):.1f}" r="3"/>')
o.append(f'<path class="l c3" d="{P(sorted(cnt3.items()))}" style="stroke-width:3"/>')
o.append(f'<path class="l c2" d="{P(sorted(post.items()))}"/>')
o.append(f'<path class="l e c2" d="{P(sorted(proj.items()))}"/>')
lab = lambda xx, yy, t, s='', anchor='start': o.append(f'<text x="{xx:.1f}" y="{yy:.1f}" font-size="13" font-weight="600" text-anchor="{anchor}">{t}</text>' + (f'<text class="m" x="{xx:.1f}" y="{yy + 15:.1f}" font-size="12" text-anchor="{anchor}">{s}</text>' if s else ''))
lab(x(1981), yv(36), 'Doctorates', 'women\'s share when awarded')
lab(x(2026), yv(47.5), 'Expected new professors', f'doctorates of 15 years before × {ALPHA:.2f}')
lab(x(2045) + 8, yv(proj[2045]) + 4, f'{proj[2045]:.0f} %', 'in 2045')
lab(x(1980.8), yv(10.3), 'New professors', 'estimated')
lab(x(2027), yv(27), 'New professors', f'counted, {cnt[2025]:.0f} % in 2025')
o.append(f'<line class="gl" style="stroke:var(--mu)" x1="{x(2025) + 3:.1f}" y1="{yv(cnt3[2025]) + 4:.1f}" x2="{x(2028):.1f}" y2="{yv(27) - 15:.1f}"/>')
lab(x(1995), yv(3), 'Professors in post', f'{post[2025]:.0f} % in 2025, counted')
o.append(f'<text class="m" x="16" y="{H_ - 30}" font-size="11">Counted: Statistics Austria, Bildung in Zahlen 2024/25 (tables 2.2_13, 4.1_8); Wissensbilanzen of the 22 public universities, 2006-2025.</text>')
o.append(f'<text class="m" x="16" y="{H_ - 14}" font-size="11">Expected: women hired at {ALPHA:.2f} x their share of doctorates 15 years before, fitted on 2006-2025. Before 2006: estimate calibrated on the counts.</text>')
o.append('</svg>')
open(ROOT + 'figures/professor-lag.svg', 'w').write('\n'.join(o))
