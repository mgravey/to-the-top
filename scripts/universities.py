"""National series of professorial appointments and professors in post by sex, 2006-2025.

Reads data/universities/*.json (counts transcribed from each public university's Wissensbilanz)
and writes data/universities.json. Every national value is tagged:
  counted   - sum of published university counts
  adjusted  - counted, but one university's total was rescaled (see ADJUST) or one value filled
2005 is not used: the reports of that year have no appointments indicator and count staff on 15 October.
"""
import json, glob
import os; ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'

YEARS = [str(y) for y in range(2006, 2026)]
# Universität Wien 2006-2011 and Akademie 2006 counted every short fixed-term (mostly visiting) and repeat
# appointment, which inflates their totals. Keep their women's share, rescale the total to later years' mean.
ADJUST = {'Universität Wien': ([str(y) for y in range(2006, 2012)], [str(y) for y in range(2012, 2017)]),
          'Akademie der bildenden Künste Wien': (['2006'], [str(y) for y in range(2007, 2012)])}

U = {}
for f in sorted(glob.glob(ROOT + 'data/universities/*.json')):
    u = json.load(open(f)); U[u['university']] = u
assert len(U) == 22, len(U)

notes = {y: [] for y in YEARS}
A = {}
for n, u in U.items():
    a = {y: list(v) for y, v in u['appointments'].items() if y in YEARS}
    if n in ADJUST:
        yrs, ref = ADJUST[n]
        m = sum(a[r][1] for r in ref) / len(ref)
        for y in yrs:
            w, t = a[y]; a[y] = [w / t * m, m]; notes[y].append(f'{n}: total rescaled from {t} to {m:.0f}, share kept')
    for y in u.get('derived', {}).get('appointments', []):
        notes[y].append(f'{n}: women derived from a multi-year total')
    for y in YEARS:
        if y not in a:  # fill from the university's own neighbouring years
            nb = [k for k in a if abs(int(k) - int(y)) <= 3]
            t = sum(a[k][1] for k in nb) / len(nb); s = sum(a[k][0] for k in nb) / sum(a[k][1] for k in nb)
            a[y] = [s * t, t]; notes[y].append(f'{n}: missing, filled from neighbouring years ({s * t:.1f} of {t:.1f})')
    A[n] = a

national = []
for y in YEARS:
    aw = sum(A[n][y][0] for n in U); at = sum(A[n][y][1] for n in U)
    p = [U[n]['professors'][y] for n in U if y in U[n]['professors']]
    national.append({'year': int(y), 'appointments_women': round(aw, 2), 'appointments_total': round(at, 2),
                     'appointments_women_pct': round(100 * aw / at, 2),
                     'professors_women': sum(v[0] for v in p), 'professors_total': sum(v[1] for v in p),
                     'universities_with_professor_count': len(p),
                     'quality': 'adjusted' if notes[y] else 'counted', 'notes': notes[y]})

json.dump({'source': 'Wissensbilanzen of the 22 Austrian public universities, 2006-2025; see data/universities/',
           'national': national}, open(ROOT + 'data/universities.json', 'w'), indent=1, ensure_ascii=False)
for r in national:
    print(r['year'], f"{r['appointments_women']:.1f}/{r['appointments_total']:.1f} = {r['appointments_women_pct']:.1f}%",
          f"profs {r['professors_women']}/{r['professors_total']} ({r['universities_with_professor_count']})", r['quality'])
