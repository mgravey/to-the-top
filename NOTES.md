# Who makes it to the top?

Working notes carried over from the exploratory session (21 Nov 2026). Page title: **Who makes it to the top?** — subtitle *Gender and family background on the road from school to professorship in Austria*.

## Planned page structure

0. **In short** — abstract paragraph and one chart under the lede: gender gap (signed: girls / boys behind) against the parents'-education gap for Matura and degree, measured as the dissimilarity index (`figures/bias-comparison.svg`, `scripts/bias_comparison.py`, `data/bias-comparison.json`).
1. **The path** — per 100 children, age 10 to professor; log scale by default, button to switch to linear (`figures/pipeline-log-all-steps-animated.svg`, `figures/pipeline-linear-all-steps-animated.svg`).
2. **By gender** — girls' and boys' share among those reaching each step, 1960–2024; button to switch between the animated step view and an over-time view, one line per step (`figures/girls-share-all-steps-animated.svg`, `figures/share-over-time.svg`; share = 0.495·g / (0.495·g + 0.505·b) from the per-100 rates for school and university steps; doctorate = counted share of all doctorates (2.2_13), professor = counted share of new professors from the 22 Wissensbilanzen, 2006–2025, estimate before). The girls-per-100-boys version (`gender-ratio-all-steps-animated.svg`, linear) is still built but not on the page.
3. **Bias or delay?** — women among doctorates (shifted +15 y), new professors (counted 2006–2025 from the 22 Wissensbilanzen; estimated before 2006, dashed), professors in post, projection to 2045 (dashed) (`figures/professor-lag.svg`, `scripts/professor_lag.py`, data from `scripts/universities.py`).
4. **Will it overshoot?** — text only; projection levels off at ~41 % because doctorates are flat at 40–46 % women since 2004.
5. **By parents' education** — rectangular mosaic, AES 2007, 2011/12, 2016/17, 2022/23, ages 25–44, animated (`figures/parent-education-animated.svg`, `scripts/parent_education.py`). Nothing for doctorate or professor, and no pay by parental education.
6. **Closing question** — is gender still the right bias to fight?

The page is `index.html`, deployed to GitHub Pages by `.github/workflows/pages.yml` (tests, then `index.html`, `figures/`, the player script, `llms.txt`, `llms-full.txt`, `sitemap.xml`), at https://mgravey.com/to-the-top/ (`www.` redirects to the apex, so canonical and sitemap use the apex).

Search and LLMs: the head carries description, canonical, Open Graph / Twitter tags with `figures/social-card.png` (1200 × 630) and Article JSON-LD. `llms.txt` is hand-written (key findings, sources, data files); `llms-full.txt` is generated from the page by `scripts/llms_full.py`, also in the workflow. When the findings change, update `llms.txt`, the JSON-LD description and the social card by hand. The main site still has to list `https://mgravey.com/to-the-top/sitemap.xml` in its sitemap index and the page in its root `llms.txt`.

Interactive charts are loaded with `<object>` so the page script can drive them: animated SVGs carry `data-times`/`data-labels` (frame start times in seconds), play once when scrolled into view, stop on the last frame, and get Pause/Replay plus a year slider (or round buttons when ≤ 6 frames). Animated charts in the same figure (log and linear) share one player and clock, so switching views keeps the year; hidden views are kept loaded (visibility: hidden) so they can be driven. The over-time chart carries `data-steps` and a default `data-hl="1"`; it draws girls' and boys' lines for one step at a time (others faint) with thin lines at the 2024 level, and the page's step buttons change `data-hl`. This needs http(s): opened from `file://`, the charts just loop as plain SVGs. Test locally with `python3 -m http.server`.

## Findings (Nov 2026)

- **Counted appointments (22 universities, 2006–2025, `data/universities/*.json` → `data/universities.json`)**: research agents transcribed each university's Wissensbilanz (II.1.3 / 1.A.3 / 1.A.2 appointments; II.1.1 / 1.A.1 professor headcount at 31 Dec). Professor sums match table 4.1_8 within 0.1 pp every year 2006–2024; 2024 appointments = 102/252 = BMFWF figure. Adjustments: Uni Wien 2006–11 and Akbild 2006 totals rescaled (fixed-term/visiting counted), JKU 2012 filled, JKU 2010 women derived. 2005 not usable (15 Oct census, no appointment indicator).
- Women among new professors: 27.6 % (2006–10), 30.1 % (2011–15), 39.1 % (2016–20), 39.9 % (2021–25); 44.7 % in 2025. Against doctorates 15 years earlier: ratio 0.98 / 0.86 / 0.96 / 0.94. Most stable lag 15–16 years (sd of ratio 0.04); with a 10-year lag the ratio jumps from ~0.77 to ~0.93 in 2016.
- Pre-2006 new professors: estimate from the change in professors in post with departure rates calibrated on the counted 2006–2024 years (women 7.9 %/yr, men 7.1 %/yr; rmse 2.2 pp vs 4.8 pp with one equal 4.3 % rate). Shown dashed, joined to the first counted point (2006).
- Projection (model, lag 15, ratio 0.94, 2021–25 hiring rate 7.3 %/yr): 34.9 % (2030), 36.4 % (2035), 38.4 % (2045).

- Degree → doctorate by nationality, 2023/24 (table 2.2.5, master's + diploma, all institutions): Austrians 55.5 % women among graduates → 43.7 % among doctorates (odds ratio 0.62); foreign students 57.2 % → 47.9 % (0.69). The drop is not caused by foreign students; it is larger among Austrians.
- Degree → doctorate: women's share of graduates ~55 % and of doctorates 40–46 % since 2004; odds ratio (doctorate odds / graduate odds) 0.55–0.68, ~0.6 on average (0.50 in 1990). Parity among doctorates at r≈0.6–0.68 would need 60–62 % women among graduates (~150–165 per 100 men).
- Degree by parental education, ages 25–44: compulsory 5.9 → 9.4, degree 51.8 → 61.3 (2007 → 2022/23). Ratio 8.8 → 6.5, gap in points 45.9 → 51.9.

## Regenerating the figures

```
python3 scripts/universities.py      # data/universities/*.json -> data/universities.json
python3 scripts/professor_lag.py     # needs universities.json; writes professor-lag.json used below
python3 scripts/build_series.py      # data/ -> data/series.json
python3 scripts/draw_animations.py   # -> the all-steps animations (log, linear, ratio, girls' share)
python3 scripts/women_share.py       # -> women-share-evolution.svg
python3 scripts/birth_cohort.py      # -> pipeline-log-by-birth-cohort.svg
python3 scripts/share_over_time.py    # -> share-over-time.svg (needs data/girls-share.json from draw_animations.py)
python3 scripts/parent_education.py  # -> parent-education-animated.svg, data/parent-education.json
python3 scripts/bias_comparison.py   # needs series.json and parent-education.json -> bias-comparison.svg
python3 scripts/social_card.py       # needs Chrome; bias-comparison.svg -> social-card.png
python3 scripts/llms_full.py         # index.html -> llms-full.txt
```

`build_series.py` reads the hard-coded series at the top of `women_share.py` (Matura rates, university degrees, doctorates, professors).

## Sources

- Statistics Austria, *Bildung in Zahlen* 2024/25: report text (`data/biz-2024-25-report.txt`, accessible tables 2.2_1, 2.2_2, 2.2_9, 2.2_13, 4.1_8) and tables 1.1.5, 2.1.9, 2.1.10, 2.2.5.
- *Bildung in Zahlen* 2023/24: tables 3.8 and 3.12 (education register 2022, by age group and sex).
- Adult Education Survey parental-education matrices (4×4, ages 25–44 and 45–64): AES 2007 report (Grafik 4, p. 24), AES 2011/12 report (Grafik 4, p. 24; same in BiZ 2012/13 and 2013/14, where the older group is labelled 45–59), BiZ 2018/19 tables 5.1_9a/b (AES 2016/17; the AES 2016/17 report prints one cell as (5,9) instead of (6,0)), BiZ 2024/25 tables 5.1_9a/b (AES 2022/23). 2007 and 2011/12 define the top category as university/FH/hochschulverwandt and measure parents at age 14/16. Also found, not used: EU-SILC 2011 matrix in BiZ 2011/12, p. 93; AES 2007 3×3 version in BiZ 2008/09.
- Foreign students: 2023/24 degrees at public universities, 11,969 of 35,960 to foreign students (table 2.1.9). Doctorates 2023/24: 2,464 in total (BiZ 2024/25, Grafik 2.2_13); 1,361 to Austrians (766 men, 595 women): table 2.2.5 (`data/2-2-5_P24.csv`), which also splits master's and diploma degrees by nationality.
- BMFWF, Statistisches Taschenbuch 2025: 252 professors appointed in 2024, 102 women; about 48 % of 2020–22 appointees came from abroad.
- The full source archive (PDFs, all 1,331 extracted tables) is not in this repo.

## How each step is built (per 100 of one age group, by sex)

| Step | Basis | Reliability |
|---|---|---|
| Matura, 1987+ | Official rate by sex | Solid |
| Matura, 1970–1986 | Interpolated between 1970 and 1980 (exam counts ÷ age-group size) and 1987 | Fair |
| Matura, 1960–1969 | Register birth cohorts (born = year − 19), scaled to the 1970 value | Rough |
| 1st degree, Master, 1991+ | Degrees by type (totals) split by sex with the overall share of women among Austrian graduates; public universities, FH, PH | Fair |
| 1st degree, Master, 1965–1990 | Register birth cohorts (born = year − 25, universities only), scaled to 1991 | Rough; likely overstates women |
| Matura track at 14 | Matura rate ÷ share staying to the end (77 % girls, 70 % boys); shown for 2024 only | Weak |
| Doctorate, 1981+ | Counted by sex, reduced to Austrian graduates (Austrian share interpolated before recent years) | Counted, one correction |
| Professor, 2006+ | Counted new professors by sex (22 Wissensbilanzen) × 0.52 (not from abroad) | Solid (counted, one correction) |
| Professor, 1983–2005 | Hires by sex implied by professors in post, departure rates calibrated on 2006–2024 counts (professor_lag.py), × 0.52 | Estimate |

## Assumptions not taken from the documents

- **Birth counts** 1951–52 and 1961–69 (used for age-group sizes before 1987) were entered from memory. They match the document-based 1987 figure within 1 %, but need a proper source.
- **Professor at age 43**: no Austrian figure found; taken from the German average age at first appointment.
- **Share of Austrians among doctorates**: published only for recent years; interpolated back to about 90 % in 1990 and held constant before.
- **Professor turnover** is assumed constant at its 2024 level in every year.
- **Girls' share of an age group** is fixed at 49.5 %.

## Open points

- Parental-education version of the path beyond the first degree: no published source.
- Doctorates by field and sex, to test how much of the master's → doctorate drop is field choice.
- Charts are fixed-size SVGs; text is small on phones.
- Pay gap among graduates by parental education: not in any document read so far. Candidate microdata: Austrian Micro Data Center, graduate career monitoring, EU-SILC modules, GGP via AUSSDA — none of these checked yet.
- Postdoc and researcher steps: only headcounts of current staff exist (46 % women), no per-100 figure.

## Parental-education mosaic

`python3 scripts/parent_education.py` builds the rectangular tiling in `figures/parent-education-animated.svg` and refreshes `data/parent-education.json`.

Both dimensions use the same four category names. Parents increase from left to right; children's attainment increases from bottom to top in each column. For 2016/17 and 2022/23, column widths are proportional to the survey-weighted parent-group population totals published above the bars in the official figures. Width is normalized over the four reported parent groups. Within a column, rectangle height is proportional to the share reaching that level; every column totals 100. Thus a tile's area is its joint share of the population represented by the four groups. Tile labels continue to show conditional percentages within the parent group, not percentages of the whole chart. The 2007 and 2011/12 widths are estimated by extending the linear calendar-year trend between the observed 2016/17 and 2022/23 group proportions. These years are explicitly labeled as assumptions; their conditional percentages remain the published historical values, and no historical headcounts are inferred. Segment heights are normalized for the occasional 100.1 total caused by source rounding, while labels retain the published values to one decimal place.

The left category labels follow the centers of the first column's rectangles. Boundaries vary across columns; this is a packed mosaic rather than a matrix with aligned rows. Colors identify children's categories. The SVG keeps the existing survey animation and `data-times` / `data-labels` contract, so the page's replay and year buttons continue to work.

## Aligned parental-education alternatives

The same generator also writes `figures/parent-education-heatmap-animated.svg` and `figures/parent-education-area-animated.svg`. These comparison prototypes are retained as SVGs. The page uses the selected four-level packed mosaic and two population-weighted two-group views, split at Matura and at a university degree (`figures/parent-education-matura-animated.svg`, `figures/parent-education-degree-animated.svg`), shown as one switchable figure ("All four levels" / "Split at Matura" / "Split at degree") with a single shared player, so switching keeps the year. The layout comparison prototypes remain off the page.

Both aligned versions use a fixed 4×4 grid, with exactly the same category order as the mosaic. The heatmap encodes the published percentage as fill opacity over the background, using a fixed 0–100 scale across all cells and years; a legend shows that scale. The area version centers a rectangle in each outlined reference cell, scaling both dimensions by `sqrt(percentage / 100)`. Its area therefore equals the published percentage of the outlined reference area, with the remaining space left empty. Numeric labels show the published value to one decimal place in both versions. The area scale uses 100%, not the largest value in a survey, as its reference.

## Grouped 2×2 treemap

`figures/parent-education-grouped-animated.svg` merges compulsory school + apprenticeship/VET into one lower band and Matura + degree into one upper band on both dimensions. Each original parent category is weighted equally: a grouped cell is the sum of its four original percentages divided by two. This assumes a 50/50 mix of the two original categories within each parent band. The source matrices contain no parent-group population sizes, so these are illustrative merged shares rather than population-weighted estimates. This assumption is displayed on the figure and in its accessible description. Column widths are equal; children's bands are packed bottom to top within each parent column. As in the four-level mosaic, horizontal boundaries may differ between the two columns.

## Population-scaled mosaic columns

Population totals are stored with provenance in `data/parent-education-populations.json` and copied into the generated `data/parent-education.json` survey frames. They are weighted estimates of people represented by the survey, not unweighted respondent/sample counts. Figures are transcribed in category order (compulsory, VET, Matura, degree):

| Survey | Compulsory | VET | Matura | Degree | Source |
|---|---:|---:|---:|---:|---|
| 2016/17 | 409,900 | 1,241,600 | 294,100 | 361,200 | [Bildung in Zahlen 2018/19](https://www.statistik.at/fileadmin/publications/Bildung_in_Zahlen_2018_19_-_Schluesselindikatoren_und_Analysen.pdf), p. 103, figure 5.1.9 |
| 2022/23 | 395,800 | 1,184,300 | 379,000 | 443,300 | [Bildung in Zahlen 2024/25](https://www.statistik.at/fileadmin/publications/BiZ-2024-25.pdf), p. 99, figure 5.1.9 |

The 2007 and 2011/12 source graphics show conditional percentages without matching group totals. Counts found in a later republication of the 2011/12 results accompany revised percentages, so they are not mixed with this chart's original matrix. The two earlier rounds use an explicitly labeled linear extrapolation of the observed group shares. Between frames, column positions, widths, labels, and tile heights animate together. Every frame still fills the plot; verified historical population totals remain null in the data. Separate `parent_width_weights`, `parent_width_source_rounds`, and `parent_width_is_assumed` fields describe the width approximation.

The earlier note that population sizes were unavailable applied to the conditional tables, which omit them; totals were subsequently verified in the 2016/17 and 2022/23 source graphics. Off-page comparison prototypes retain their documented fixed-grid or equal-weight encodings.

## Earlier-survey width estimates over time

The width model in `data/parent-education-populations.json` normalizes each observed count vector to group shares, then fits a straight line in calendar time through the 2016/17 and 2022/23 shares. Survey coordinates are 2007.0, 2011.5, 2016.5, and 2022.5; two-year rounds use their midpoint. For each category, `share(t) = share(2016.5) + (t - 2016.5) / 6 × (share(2022.5) - share(2016.5))`. Thus 2007 and 2011/12 are extrapolations, rather than interpolations between observed years. Their estimated group shares change gradually with the survey year. This replaces the earlier constant-composition approximation.

Observed 2016/17 and 2022/23 widths remain exact. All four shares sum to one at every modeled date; the generator rejects nonpositive or invalid estimated proportions instead of clipping them. Source population totals stay null for earlier years: no historical headcounts are inferred. The chart prints estimated group shares above these columns and labels their trend-based origin below the plot. Each survey's published conditional percentages still determine tile heights and numeric labels. Column positions, widths, and label centers move together using the existing smooth animation transitions; narrower labels wrap to avoid overlap.

## Continuous time animation

The selected mosaic embeds its source survey frames as SVG metadata. `scripts/parent_education_player.js` drives continuous calendar time when loaded on the page, replacing the SVG's four-round SMIL fallback. Playback runs from 2007.0 to 2022.5 at one calendar year per second, with play/pause/replay, a continuous slider, and buttons to seek exact survey rounds. It plays once on entering view, unless reduced motion is requested; users can replay manually.

Between rounds, each published conditional percentage is interpolated linearly using actual survey-year gaps. Geometry normalizes the resulting columns for source rounding. Parent-group shares follow the existing time trend. Tile rectangles, values, category-label centers, and group shares update together on each animation frame. Intermediate dates are labeled as interpolated; exact survey dates restore their published title and values. Raw population totals appear only at the verified 2016/17 and 2022/23 anchors, with group proportions elsewhere. The year slider pauses playback when dragged, and survey buttons seek exact source dates. The published data matrices are unchanged.

## Two-group Matura figure

The page's second parental-education mosaic, `figures/parent-education-matura-animated.svg`, uses **Below Matura** (compulsory school + apprenticeship/VET) and **Matura or higher** (Matura + university/college degree) for both parents and children. Matura itself belongs to the upper group, so the bands include every category exactly once.

Grouping preserves joint population shares: normalize each original conditional row for source rounding, multiply it by the original parent-group share, sum the relevant 2×2 blocks, then divide by the merged parent share to obtain its conditional percentages. This is population weighting, not a simple average of two parent categories. For 2007 and 2011/12, the group weights are extrapolated, so the merged percentages as well as the widths are estimates. Observed parent counts are summed for the two later surveys. The data JSON includes the derived matrices under `frames_matura_threshold`.

During playback, the player first interpolates the original four-level data at the selected year and then groups those joint shares. This keeps the two-group figure consistent with the four-level figure throughout the animation, including between survey dates. The original four-level matrices are unchanged. Both figures have their own play/pause, slider, replay, and exact-round controls.
