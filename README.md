# Who makes it to the top?

Gender and family background on the road from school to professorship in Austria.

Live page: https://www.mgravey.com/to-the-top/

`index.html` is the page; `figures/` holds the SVG charts, built from `data/` by the scripts in `scripts/` (see `NOTES.md` for how to rebuild them and how each number is made).

Rebuild the parental-education figure with `python3 scripts/parent_education.py`. The page uses the four-level packed mosaic: parents increase from left to right and children from bottom to top. Column widths reflect verified survey-weighted population totals for 2016/17 and 2022/23; 2007 and 2011/12 use labeled estimates from a linear calendar-year trend through the observed 2016/17 and 2022/23 group proportions. Historical within-group percentages stay unchanged, and no historical headcounts are inferred. Tile heights and printed values show percentages within each parent group. A continuous 2007–2022/23 animation includes play/pause, replay, a year slider, and buttons for all four survey rounds. Between rounds, tile percentages are interpolated and explicitly labeled; playback advances one calendar year per second. Population totals and citations are in `data/parent-education-populations.json`; see `NOTES.md` for the method. The generator also retains off-page comparison SVGs.

Check the timeline interpolation with `node --test tests/parent_education_player.test.js`.

The page also includes a two-group version, `figures/parent-education-matura-animated.svg`: below Matura versus Matura or higher on both axes, with the same continuous timeline. It merges parent groups using their observed or extrapolated population proportions; see `NOTES.md` for the aggregation method.
