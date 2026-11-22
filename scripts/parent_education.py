"""Own education by parents' education, Austria, Adult Education Survey 2007 to 2022/23.

A rectangular mosaic with one column per parental-education group, sized by
verified survey-weighted population totals where available (2016/17, 2022/23).
Earlier group proportions are extrapolated linearly in calendar time from the
two observed rounds, without assigning historical population counts.
Children's education is stacked from lowest to highest, bottom to top; tile
heights show conditional percentages. The animation covers four survey rounds
for people aged 25 to 44.
Also builds population-weighted two-group views, split at Matura and at a
university degree, with the same player.
Builds aligned heatmap and proportional-area alternatives, using the
same categories, survey times, and published percentages. A grouped four-tile
treemap merges the lower two and upper two categories with equal parent weights.
Writes figures/parent-education-*.svg and data/parent-education.json.
"""
import json
from html import escape
import os; ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'

OWN = ['Compulsory school', 'Apprenticeship or VET school', 'Matura (AHS/BHS)', 'University or college degree']
PAR = OWN.copy()
# columns = parents' highest education, values = own highest education (column per cent), age 25 to 44.
# 2007 and 2011/12: top category "university, Fachhochschule, hochschulverwandte Ausbildung"; parents' education
# at age 14 (2007) or 16 (2011/12). 2016/17 values in brackets in the source (fewer than 20 cases): 6.0 and 3.6.
FRAMES = [
    dict(title='Survey 2007', sub='aged 25 to 44, born 1963 to 1982', src='AES 2007 report, Grafik 4',
         m=[[30.1, 56.6, 7.4, 5.9], [8.2, 63.1, 17.9, 10.8], [4.3, 24.5, 41.4, 29.8], [5.1, 13.6, 29.5, 51.8]]),
    dict(title='Survey 2011/12', sub='aged 25 to 44, born 1967 to 1987', src='AES 2011/12 report, Grafik 4',
         m=[[27.3, 55.1, 11.0, 6.6], [10.1, 60.8, 16.5, 12.6], [4.6, 22.4, 32.1, 41.0], [5.1, 13.7, 25.4, 55.8]]),
    dict(title='Survey 2016/17', sub='aged 25 to 44, born 1972 to 1992', src='Bildung in Zahlen 2018/19, table 5.1_9a',
         m=[[32.6, 46.1, 14.4, 6.9], [7.5, 59.3, 17.3, 15.9], [6.0, 18.6, 41.9, 33.6], [3.6, 15.6, 23.5, 57.3]]),
    dict(title='Survey 2022/23', sub='aged 25 to 44, born 1978 to 1997', src='Bildung in Zahlen 2024/25, table 5.1_9a',
         m=[[36.2, 42.3, 12.1, 9.4], [8.9, 54.1, 18.7, 18.3], [5.9, 20.8, 30.8, 42.5], [5.8, 11.7, 21.2, 61.3]]),
]
# same table for ages 45 to 64 (not animated; kept for reference). 2016/17: (3.9) and x (suppressed) in the source.
OLDER = {
    '2007': [[34.2, 54.5, 6.5, 4.8], [13.1, 67.4, 10.6, 8.9], [5.6, 27.8, 40.1, 26.5], [3.3, 16.3, 18.6, 61.8]],
    '2011/12': [[29.2, 57.4, 8.7, 4.7], [10.8, 65.0, 14.1, 10.1], [2.8, 30.4, 32.5, 34.3], [1.6, 17.2, 21.8, 59.4]],
    '2016/17': [[28.7, 57.7, 8.1, 5.6], [10.4, 65.7, 12.8, 11.1], [3.9, 26.9, 35.6, 33.6], [None, 10.9, 27.9, 57.6]],
    '2022/23': [[29.3, 54.5, 9.2, 7.0], [8.1, 60.4, 17.1, 14.4], [6.6, 21.8, 28.1, 43.5], [2.9, 16.6, 22.4, 58.1]],
}
POPULATIONS = json.load(open(ROOT + 'data/parent-education-populations.json'))
WIDTH_MODEL = POPULATIONS['width_estimation']


def width_weights(round_name):
    """Preserve observations; estimate missing shares on a calendar-year line."""
    observed = POPULATIONS['rounds'][round_name]
    if observed:
        return observed['counts']
    first, last = WIDTH_MODEL['anchor_rounds']
    years = WIDTH_MODEL['survey_years']
    fraction = (years[round_name] - years[first]) / (years[last] - years[first])
    start, end = [POPULATIONS['rounds'][r]['counts'] for r in (first, last)]
    shares = [a / sum(start) + fraction * (b / sum(end) - a / sum(start))
              for a, b in zip(start, end)]
    if len(shares) != len(PAR) or min(shares) <= 0 or abs(sum(shares) - 1) > 1e-9:
        raise ValueError(f'Invalid extrapolated group proportions for {round_name}')
    return shares


for frame in FRAMES:
    round_name = frame['title'].replace('Survey ', '')
    population = POPULATIONS['rounds'][round_name]
    frame['parent_population'] = population['counts'] if population else None
    frame['parent_population_source'] = population
    frame['parent_width_weights'] = width_weights(round_name)
    frame['parent_width_source_rounds'] = [round_name] if population else WIDTH_MODEL['anchor_rounds']
    frame['parent_width_is_assumed'] = population is None
    frame['parent_width_method'] = 'observed' if population else 'linear_extrapolation_of_group_shares'
    frame['survey_year'] = WIDTH_MODEL['survey_years'][round_name]

MATURA_LEVELS = ['Below Matura', 'Matura or higher']
MATURA_BANDS = [(0, 1), (2, 3)]
DEGREE_LEVELS = ['No degree', 'University or|college degree']
DEGREE_BANDS = [(0, 1, 2), (3,)]


def threshold_frame(frame, bands):
    """Merge joint shares, then condition on the merged parent group."""
    weights = frame['parent_width_weights']
    grouped_weights = [sum(weights[p] for p in parents) for parents in bands]
    matrix = []
    for group, parents in enumerate(bands):
        matrix.append([100 * sum(weights[p] * sum(frame['m'][p][c] for c in children)
                                 / sum(frame['m'][p]) for p in parents) / grouped_weights[group]
                       for children in bands])
    counts = frame['parent_population']
    return dict(frame, m=matrix, parent_width_weights=grouped_weights,
                parent_population=[sum(counts[p] for p in parents) for parents in bands] if counts else None)


MATURA_FRAMES = [threshold_frame(frame, MATURA_BANDS) for frame in FRAMES]
DEGREE_FRAMES = [threshold_frame(frame, DEGREE_BANDS) for frame in FRAMES]
json.dump({'own_levels': OWN, 'parent_levels': PAR, 'frames_age_25_44': FRAMES, 'age_45_64': OLDER,
           'matura_levels': MATURA_LEVELS, 'frames_matura_threshold': MATURA_FRAMES,
           'degree_levels': [l.replace('|', ' ') for l in DEGREE_LEVELS], 'frames_degree_threshold': DEGREE_FRAMES},
          open(ROOT + 'data/parent-education.json', 'w'), indent=1)

W, H = 940, 760
BX, BW, T, BH = 260, 660, 140, 440
CW = BW / len(PAR)
n = len(FRAMES)
hold, move = 2.6, 0.9
D = n * (hold + move)
# Hold each survey, then interpolate to the next (last returns to first).
kt, idx = [], []
for i in range(n):
    kt += [i * (hold + move) / D, (i * (hold + move) + hold) / D]
    idx += [i, i]
kt.append(1)
idx.append(0)
KT = ';'.join(f'{t:.4f}' for t in kt)
A = f'dur="{D:.2f}s" repeatCount="indefinite" keyTimes="{KT}" calcMode="spline" keySplines="{";".join(["0.4 0 0.2 1"] * (len(kt) - 1))}"'


def seg(frame, parent, child):
    """Top and height, normalized only to remove source rounding error."""
    values = FRAMES[frame]['m'][parent]
    total = sum(values)
    height = BH * values[child] / total
    top = T + BH * (1 - sum(values[:child + 1]) / total)
    return top, height


def column(frame, parent):
    """Size columns by observed counts or estimated calendar-year shares."""
    counts = FRAMES[frame]['parent_width_weights']
    total = sum(counts)
    return BX + BW * sum(counts[:parent]) / total, BW * counts[parent] / total


def animate(attribute, values):
    return f'<animate attributeName="{attribute}" {A} values="{";".join(f"{v:.3f}" for v in values)}"/>'


def opacity(frame):
    return animate('opacity', [int(i == frame) for i in idx])


def lines(text, x, center, anchor='end', css='m', size=14):
    """Center a wrapped category label vertically at its tick."""
    parts = text.split('|')
    y = center - (len(parts) - 1) * 8
    spans = ''.join(f'<tspan x="{x}" dy="{0 if i == 0 else 16}">{part}</tspan>' for i, part in enumerate(parts))
    return f'<text class="{css}" x="{x}" y="{y:.3f}" dominant-baseline="middle" text-anchor="{anchor}" font-size="{size}">{spans}</text>'


TIMES = ','.join(f'{i * (hold + move):.2f}' for i in range(n))
LABELS = ','.join(F['title'].replace('Survey ', '') for F in FRAMES)
TIMELINE = escape(json.dumps({'frames': FRAMES, 'parent_levels': PAR, 'own_levels': OWN,
                             'plot': {'x': BX, 'y': T, 'width': BW, 'height': BH}}), quote=False)
o = [f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" data-times="{TIMES}" data-labels="{LABELS}" data-continuous="parent-education" role="img" aria-labelledby="chart-title chart-description">
<title id="chart-title">How far children get, by how far their parents got</title>
<desc id="chart-description">Austria, ages 25 to 44, surveys 2007 to 2022/23. Parents' education increases left to right; children's education increases bottom to top. Column widths use observed parent-group proportions for 2016/17 and 2022/23. Widths for 2007 and 2011/12 are extrapolated linearly in calendar time from those two observations; their tile areas are approximate. Historical conditional percentages are unchanged. Above the columns, earlier surveys show estimated group shares and later surveys show observed weighted population totals.</desc>
<metadata id="timeline-data">{TIMELINE}</metadata>
<style>
svg{{--fg:#1c1c1c;--mu:#6b6b6b;--bd:#dddddd;--bg:#ffffff;--s1:#86b6ef;--s2:#3987e5;--s3:#1c5cab;--s4:#0d366b;font-family:system-ui,-apple-system,"Segoe UI",sans-serif}}
@media (prefers-color-scheme:dark){{svg{{--fg:#ededed;--mu:#a0a0a0;--bd:#333333;--bg:#0e0e0e;--s1:#184f95;--s2:#2a78d6;--s3:#6da7ec;--s4:#cde2fb}}}}
.bg{{fill:var(--bg)}} text{{fill:var(--fg)}} .m{{fill:var(--mu)}}
.s0{{fill:var(--s1)}} .s1{{fill:var(--s2)}} .s2{{fill:var(--s3)}} .s3{{fill:var(--s4)}}
.tile{{stroke:var(--bg);stroke-width:3}}
.v0{{fill:#0b0b0b}} .v1,.v2,.v3{{fill:#ffffff}}
@media (prefers-color-scheme:dark){{.v0,.v1{{fill:#ffffff}} .v2,.v3{{fill:#0b0b0b}}}}
.tick{{stroke:var(--mu);stroke-width:1}}
</style>
<rect class="bg" width="{W}" height="{H}"/>
<text x="16" y="30" font-size="21" font-weight="600">How far children get, by how far their parents got</text>
<text x="16" y="54" font-size="15" class="m">Austria. Numbers = percentages within each parent group; widths = observed or assumed group sizes.</text>
<text x="16" y="115" font-size="15" font-weight="600">Children's highest education</text>''']
# The left labels follow the first column's segment centers. Categories have
# the same order in every column; boundaries vary to encode the percentages.
Y_LABELS = ['Compulsory school', 'Apprenticeship|or VET school', 'Matura (AHS/BHS)', 'University or|college degree']
X_LABELS = ['Compulsory|school', 'Apprenticeship|or VET school', 'Matura|AHS / BHS', 'University|or college|degree']
for child, label in enumerate(Y_LABELS):
    centers = [sum((seg(i, 0, child)[0], seg(i, 0, child)[1] / 2)) for i in idx]
    o.append(f'<g data-child-label="{child}" transform="translate(0 {centers[0]:.3f})"><animateTransform attributeName="transform" type="translate" {A} values="{";".join(f"0 {c:.3f}" for c in centers)}"/>')
    o.append(lines(label, BX - 24, 0))
    o.append(f'<line class="tick" x1="{BX - 15}" x2="{BX - 5}" y1="0" y2="0"/></g>')

for frame, F in enumerate(FRAMES):
    scale_note = ('Estimated widths: calendar-year trend from 2016/17 to 2022/23; numbers above = estimated group shares.'
                  if F['parent_width_is_assumed'] else
                  'Widths = weighted population; numbers above columns = people represented.')
    o.append(f'<g data-survey-frame="{frame}" opacity="{int(frame == 0)}">{opacity(frame)}'
             f'<text data-time-title="" x="{BX + BW}" y="92" font-size="24" font-weight="700" text-anchor="end">{F["title"]}</text>'
             f'<text data-time-sub="" class="m" x="{BX + BW}" y="115" font-size="14" text-anchor="end">{F["sub"]}</text>'
             f'<text data-width-note="" class="m" x="16" y="683" font-size="12">{scale_note}</text></g>')

for parent, name in enumerate(PAR):
    columns = [column(i, parent) for i in idx]
    x, width = columns[0]
    centers_x = [a + b / 2 for a, b in columns]
    o.append(f'<g data-parent-label="{parent}" transform="translate({centers_x[0]:.3f} 0)"><animateTransform attributeName="transform" type="translate" {A} values="{";".join(f"{c:.3f} 0" for c in centers_x)}"/>')
    o.append(lines(X_LABELS[parent], 0, T + BH + 35, 'middle', size=13))
    o.append('</g>')
    for frame, F in enumerate(FRAMES):
        weights = F['parent_width_weights']
        group_label = (f'{100 * weights[parent] / sum(weights):.1f}%'
                       if F['parent_width_is_assumed'] else
                       f'{F["parent_population"][parent]:,}')
        o.append(f'<text data-parent-total="{parent}" data-total-frame="{frame}" class="m" x="{centers_x[0]:.3f}" y="132" text-anchor="middle" font-size="12" opacity="{int(frame == 0)}">'
                 + animate('x', centers_x) + opacity(frame) + f'{group_label}</text>')
    for child in range(len(OWN)):
        positions = [seg(i, parent, child) for i in idx]
        top, height = positions[0]
        tooltip = f"Parents: {name}. Children: {OWN[child]}. " + '; '.join(f"{F['title']}: {F['m'][parent][child]:.1f} per 100" for F in FRAMES)
        o.append(f'<rect class="tile s{child}" data-parent="{parent}" data-child="{child}" x="{x:.3f}" y="{top:.3f}" width="{width:.3f}" height="{height:.3f}"><title>{tooltip}</title>'
                 + animate('x', [a for a, b in columns])
                 + animate('width', [b for a, b in columns])
                 + animate('y', [a for a, b in positions])
                 + animate('height', [b for a, b in positions]) + '</rect>')
        # Keep numeric labels in the center of their moving tile. Frame values
        # cross-fade rather than interpolating published survey percentages.
        for frame in range(n):
            centers = [a + b / 2 for a, b in positions]
            o.append(f'<text data-value-parent="{parent}" data-value-child="{child}" data-value-frame="{frame}" class="v{child}" x="{centers_x[0]:.3f}" y="{centers[0]:.3f}" dominant-baseline="middle" font-size="15" font-weight="600" text-anchor="middle" opacity="{int(frame == 0)}">'
                     + animate('x', centers_x) + animate('y', centers) + opacity(frame)
                     + f'{FRAMES[frame]["m"][parent][child]:.1f}</text>')

o.append(f'<text x="{BX + BW / 2}" y="665" text-anchor="middle" font-size="15" font-weight="600">Parents&apos; highest education</text>')
o.append('<text class="m" x="16" y="701" font-size="12">Tile numbers = percentages within each parent group. Widths are normalized over the four reported parent groups.</text>')
o.append('<text class="m" x="16" y="726" font-size="11">Statistics Austria, Adult Education Survey 2007, 2011/12, 2016/17, 2022/23; Bildung in Zahlen 2018/19 and 2024/25, table 5.1_9a.</text>')
o.append('<text class="m" x="16" y="745" font-size="11">Parents&apos; education is the higher of mother and father. Degree includes colleges; 2007 and 2011/12 group it slightly differently.</text>')
o.append('</svg>')
open(ROOT + 'figures/parent-education-animated.svg', 'w').write('\n'.join(o))


def aligned_chart(mode):
    """Aligned category cells; encode percentage by color or rectangle area."""
    area = mode == 'area'
    explanation = (
        'Aligned rows and columns. Rectangle area = percentage of its cell; empty space completes the 100% reference.'
        if area else
        'Aligned rows and columns. Color intensity = percentage, using the same 0 to 100 scale in every survey.'
    )
    description = (
        'Aligned proportional-area matrix: each cell is a 100 percent reference; '
        'the centered rectangle occupies the published percentage of that area.'
        if area else
        'Aligned heatmap: each equal-size tile shows the published percentage '
        'as a number and color intensity on a fixed 0 to 100 percent scale.'
    )
    # Reuse the mosaic's header and palette while describing each encoding.
    header = o[0].replace('data-continuous="parent-education"', '')
    header = header.replace('Austria. Numbers = percentages within each parent group; widths = observed or assumed group sizes.',
                            'Austria. Percentages within each parent group; fixed cells align education categories.')
    start = header.index('<desc ')
    end = header.index('</desc>', start) + len('</desc>')
    header = header[:start] + (
        f'<desc id="chart-description">Austria, ages 25 to 44, surveys 2007 to 2022/23. '
        f'{description} Parents increase left to right; children increase bottom to top. '
        'Both axes use the same four education categories. Percentages are within each parent group.</desc>'
    ) + header[end:]
    extra_style = '''<style>
    .cell{fill:none;stroke:var(--bd);stroke-width:1}
    .heat{fill:var(--s3)}
    .value{fill:var(--fg)}
    </style>'''
    chart = [header, extra_style]
    ch = BH / len(OWN)
    for child, label in enumerate(Y_LABELS):
        center = T + (3 - child) * ch + ch / 2
        chart.append(lines(label, BX - 24, center))
        chart.append(f'<line class="tick" x1="{BX - 15}" x2="{BX - 5}" y1="{center}" y2="{center}"/>')
    for frame, F in enumerate(FRAMES):
        chart.append(f'<g opacity="{int(frame == 0)}">{opacity(frame)}'
                     f'<text x="{BX + BW}" y="92" font-size="24" font-weight="700" text-anchor="end">{F["title"]}</text>'
                     f'<text class="m" x="{BX + BW}" y="115" font-size="14" text-anchor="end">{F["sub"]}</text></g>')
    for parent, name in enumerate(PAR):
        x = BX + parent * CW
        chart.append(lines(X_LABELS[parent], x + CW / 2, T + BH + 35, 'middle', size=14))
        for child in range(len(OWN)):
            y = T + (3 - child) * ch
            cx, cy = x + CW / 2, y + ch / 2
            values = [FRAMES[i]['m'][parent][child] for i in idx]
            tooltip = f'Parents: {name}. Children: {OWN[child]}. ' + '; '.join(
                f"{F['title']}: {F['m'][parent][child]:.1f} per 100" for F in FRAMES)
            inset = 6 if area else 2
            chart.append(f'<rect class="cell" x="{x + inset}" y="{y + inset}" width="{CW - 2 * inset}" height="{ch - 2 * inset}"/>')
            if area:
                # Scale both dimensions by sqrt(p), so area (not length) is p.
                widths = [(CW - 12) * (v / 100) ** 0.5 for v in values]
                heights = [(ch - 12) * (v / 100) ** 0.5 for v in values]
                xs = [cx - w / 2 for w in widths]
                ys = [cy - h / 2 for h in heights]
                chart.append(f'<rect class="s2" data-parent="{parent}" data-child="{child}" x="{xs[0]:.3f}" y="{ys[0]:.3f}" width="{widths[0]:.3f}" height="{heights[0]:.3f}"><title>{tooltip}</title>'
                             + animate('x', xs) + animate('y', ys)
                             + animate('width', widths) + animate('height', heights) + '</rect>')
            else:
                chart.append(f'<rect class="heat" data-parent="{parent}" data-child="{child}" x="{x + 2}" y="{y + 2}" width="{CW - 4}" height="{ch - 4}" fill-opacity="{values[0] / 100:.3f}"><title>{tooltip}</title>'
                             + animate('fill-opacity', [v / 100 for v in values]) + '</rect>')
            for frame, F in enumerate(FRAMES):
                chart.append(f'<text class="{"v2" if area else "value"}" x="{cx}" y="{cy}" dominant-baseline="middle" text-anchor="middle" font-size="14" font-weight="600" opacity="{int(frame == 0)}">'
                             + opacity(frame) + f'{F["m"][parent][child]:.1f}</text>')
    chart.append(f'<text x="{BX + BW / 2}" y="665" text-anchor="middle" font-size="15" font-weight="600">Parents&apos; highest education</text>')
    if not area:
        # Compact fixed legend, including endpoints absent from the data.
        chart.append('<text class="m" x="16" y="640" font-size="11">Share (%)</text>')
        for i, value in enumerate([0, 25, 50, 75, 100]):
            x = 16 + i * 42
            chart.append(f'<rect class="cell" x="{x}" y="649" width="24" height="16"/>'
                         f'<rect class="heat" x="{x}" y="649" width="24" height="16" fill-opacity="{value / 100}"/>'
                         f'<text class="m" x="{x + 12}" y="682" text-anchor="middle" font-size="11">{value}</text>')
    chart.append(f'<text class="m" x="16" y="699" font-size="13">{explanation}</text>')
    chart.extend(o[-3:])  # Source, category caveat, closing SVG tag.
    filename = f'figures/parent-education-{mode}-animated.svg'
    open(ROOT + filename, 'w').write('\n'.join(chart))


aligned_chart('heatmap')
aligned_chart('area')


def threshold_chart(levels, bands, grouped, slug, title, description, footnote):
    """The selected mosaic and continuous player, merged into two groups on both axes."""
    plain = [l.replace('|', ' ') for l in levels]
    metadata = escape(json.dumps({'frames': FRAMES, 'parent_levels': plain,
                                 'own_levels': plain, 'bands': bands,
                                 'plot': {'x': BX, 'y': T, 'width': BW, 'height': BH}}), quote=False)
    header = o[0].replace(TIMELINE, metadata).replace(
        'How far children get, by how far their parents got', title)
    start, end = header.index('<desc '), header.index('</desc>') + len('</desc>')
    header = header[:start] + (
        f'<desc id="chart-description">Population-weighted mosaic with two groups on both axes: {description} '
        'Parents increase left to right; children bottom to top. '
        'The original parent categories in each band are merged using their population proportions. '
        'The 2007 and 2011/12 proportions are extrapolated; 2016/17 and 2022/23 use observed totals. '
        'Between surveys, source percentages are interpolated before merging.</desc>'
    ) + header[end:]
    chart = [header]

    def position(frame, parent, child):
        values = grouped[frame]['m'][parent]
        return T + BH * (1 - sum(values[:child + 1]) / sum(values)), BH * values[child] / sum(values)

    def group_column(frame, parent):
        weights = grouped[frame]['parent_width_weights']
        return BX + BW * sum(weights[:parent]) / sum(weights), BW * weights[parent] / sum(weights)

    for child, label in enumerate(levels):
        centers = [position(i, 0, child)[0] + position(i, 0, child)[1] / 2 for i in idx]
        chart.append(f'<g data-child-label="{child}" transform="translate(0 {centers[0]:.3f})"><animateTransform attributeName="transform" type="translate" {A} values="{";".join(f"0 {c:.3f}" for c in centers)}"/>')
        chart.append(lines(label, BX - 24, 0))
        chart.append(f'<line class="tick" x1="{BX - 15}" x2="{BX - 5}" y1="0" y2="0"/></g>')
    for frame, F in enumerate(grouped):
        note = ('Estimated widths and merged shares use extrapolated parent-group proportions.'
                if F['parent_width_is_assumed'] else
                'Population-weighted merged survey shares; numbers above columns = people represented.')
        chart.append(f'<g data-survey-frame="{frame}" opacity="{int(frame == 0)}">{opacity(frame)}'
                     f'<text data-time-title="" x="{BX + BW}" y="92" font-size="24" font-weight="700" text-anchor="end">{F["title"]}</text>'
                     f'<text data-time-sub="" class="m" x="{BX + BW}" y="115" font-size="14" text-anchor="end">{F["sub"]}</text>'
                     f'<text data-width-note="" class="m" x="16" y="683" font-size="12">{note}</text></g>')
    for parent, label in enumerate(levels):
        columns = [group_column(i, parent) for i in idx]
        centers_x = [x + width / 2 for x, width in columns]
        chart.append(f'<g data-parent-label="{parent}" transform="translate({centers_x[0]:.3f} 0)"><animateTransform attributeName="transform" type="translate" {A} values="{";".join(f"{c:.3f} 0" for c in centers_x)}"/>')
        chart.append(lines(label, 0, T + BH + 35, 'middle', size=15))
        chart.append('</g>')
        for frame, F in enumerate(grouped):
            weights = F['parent_width_weights']
            total_label = (f'{100 * weights[parent] / sum(weights):.1f}%'
                           if F['parent_width_is_assumed'] else f'{F["parent_population"][parent]:,}')
            chart.append(f'<text data-parent-total="{parent}" data-total-frame="{frame}" class="m" x="{centers_x[0]:.3f}" y="132" text-anchor="middle" font-size="12" opacity="{int(frame == 0)}">'
                         + animate('x', centers_x) + opacity(frame) + total_label + '</text>')
        for child in range(2):
            color = 1 if child == 0 else 3
            positions = [position(i, parent, child) for i in idx]
            chart.append(f'<rect class="tile s{color}" data-parent="{parent}" data-child="{child}" x="{columns[0][0]:.3f}" width="{columns[0][1]:.3f}" y="{positions[0][0]:.3f}" height="{positions[0][1]:.3f}"><title>{plain[parent]}: children {plain[child]}</title>'
                         + animate('x', [x for x, width in columns]) + animate('width', [width for x, width in columns])
                         + animate('y', [y for y, height in positions]) + animate('height', [height for y, height in positions]) + '</rect>')
            for frame in range(n):
                centers_y = [y + height / 2 for y, height in positions]
                chart.append(f'<text data-value-parent="{parent}" data-value-child="{child}" data-value-frame="{frame}" class="v{color}" x="{centers_x[0]:.3f}" y="{centers_y[0]:.3f}" dominant-baseline="middle" text-anchor="middle" font-size="22" font-weight="600" opacity="{int(frame == 0)}">'
                             + animate('x', centers_x) + animate('y', centers_y) + opacity(frame)
                             + f'{grouped[frame]["m"][parent][child]:.1f}</text>')
    chart.append(f'<text x="{BX + BW / 2}" y="665" text-anchor="middle" font-size="15" font-weight="600">Parents&apos; highest education</text>')
    chart.append(f'<text class="m" x="16" y="701" font-size="12">{footnote}</text>')
    chart.extend(o[-3:])
    open(ROOT + f'figures/parent-education-{slug}-animated.svg', 'w').write('\n'.join(chart))


threshold_chart(MATURA_LEVELS, MATURA_BANDS, MATURA_FRAMES, 'matura', "Reaching Matura, by parents' education",
                'below Matura (compulsory school or apprenticeship/VET), and Matura or higher '
                '(Matura or a university/college degree).',
                'Below Matura = compulsory school or VET. Matura or higher = Matura or a university/college degree.')
threshold_chart(DEGREE_LEVELS, DEGREE_BANDS, DEGREE_FRAMES, 'degree', "Reaching a degree, by parents' education",
                'no degree (compulsory school, apprenticeship/VET, or Matura), and a university or college degree.',
                'No degree = compulsory school, VET or Matura. Degree = university, Fachhochschule or college degree.')


def grouped_chart():
    """Four-tile treemap of two education bands, with equal parent weights."""
    grouped = []
    for F in FRAMES:
        matrix = []
        for parents in [(0, 1), (2, 3)]:
            matrix.append([sum(F['m'][p][c] for p in parents for c in children) / 2
                           for children in [(0, 1), (2, 3)]])
        grouped.append(matrix)
    header = o[0].replace('data-continuous="parent-education"', '').replace('How far children get, by how far their parents got',
                          'Grouped education: lower and upper levels')
    header = header.replace('Austria. Numbers = percentages within each parent group; widths = observed or assumed group sizes.',
                            'Austria. Illustrative merged percentages, with equal weights for original parent groups.')
    start = header.index('<desc ')
    end = header.index('</desc>', start) + len('</desc>')
    header = header[:start] + (
        '<desc id="chart-description">Four-tile grouped treemap. '
        'Lower education combines compulsory school and apprenticeship or VET; '
        'upper education combines Matura and university or college degree. '
        'Parents increase left to right and children bottom to top. '
        'Each of the four original parent categories receives equal weight. '
        'These merged percentages are illustrative, not population-weighted estimates.</desc>'
    ) + header[end:]
    chart = [header]
    labels = ['Compulsory school|or apprenticeship / VET', 'Matura or degree']

    def position(frame, parent, child):
        values = grouped[frame][parent]
        total = sum(values)
        return T + BH * (1 - sum(values[:child + 1]) / total), BH * values[child] / total

    for child, label in enumerate(labels):
        centers = [position(i, 0, child)[0] + position(i, 0, child)[1] / 2 for i in idx]
        chart.append(f'<g transform="translate(0 {centers[0]:.3f})"><animateTransform attributeName="transform" type="translate" {A} values="{";".join(f"0 {c:.3f}" for c in centers)}"/>')
        chart.append(lines(label, BX - 24, 0))
        chart.append(f'<line class="tick" x1="{BX - 15}" x2="{BX - 5}" y1="0" y2="0"/></g>')
    for frame, F in enumerate(FRAMES):
        chart.append(f'<g opacity="{int(frame == 0)}">{opacity(frame)}'
                     f'<text x="{BX + BW}" y="92" font-size="24" font-weight="700" text-anchor="end">{F["title"]}</text>'
                     f'<text class="m" x="{BX + BW}" y="115" font-size="14" text-anchor="end">{F["sub"]}</text></g>')
    for parent in range(2):
        x, width = BX + parent * BW / 2, BW / 2
        chart.append(lines(labels[parent], x + width / 2, T + BH + 35, 'middle', size=14))
        for child in range(2):
            color = 1 if child == 0 else 3
            positions = [position(i, parent, child) for i in idx]
            top, height = positions[0]
            chart.append(f'<rect class="tile s{color}" data-parent="{parent}" data-child="{child}" x="{x}" y="{top:.3f}" width="{width}" height="{height:.3f}">'
                         + animate('y', [a for a, b in positions])
                         + animate('height', [b for a, b in positions]) + '</rect>')
            for frame in range(n):
                chart.append(f'<text class="v{color}" x="{x + width / 2}" y="{top + height / 2:.3f}" dominant-baseline="middle" text-anchor="middle" font-size="22" font-weight="600" opacity="{int(frame == 0)}">'
                             + animate('y', [a + b / 2 for a, b in positions]) + opacity(frame)
                             + f'{grouped[frame][parent][child]:.1f}</text>')
    chart.append(f'<text x="{BX + BW / 2}" y="665" text-anchor="middle" font-size="15" font-weight="600">Parents&apos; highest education</text>')
    chart.append('<text class="m" x="16" y="686" font-size="12">Each column combines two parent levels. Children: compulsory + VET at the bottom; Matura + degree at the top.</text>')
    chart.append('<text class="m" x="16" y="704" font-size="12">Equal weight for the four original parent groups; illustrative merged shares, not population-weighted estimates.</text>')
    chart.extend(o[-3:])
    open(ROOT + 'figures/parent-education-grouped-animated.svg', 'w').write('\n'.join(chart))


grouped_chart()
for F in FRAMES:
    print(F['title'], 'degree by parents:', [c[3] for c in F['m']], 'ratio %.1f gap %.1f pts' % (F['m'][3][3] / F['m'][0][3], F['m'][3][3] - F['m'][0][3]))
