import os; ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/'
from credit import with_credit
mat={1990:[27.1,30.6],1991:[27.5,31.7],1992:[27.5,32.9],1993:[28.3,34.4],1994:[30.1,37.5],1995:[31.0,38.0],1996:[32.0,40.0],1997:[32.2,41.9],1998:[32.2,42.7],1999:[31.2,42.1],2000:[30.9,41.6],2001:[29.6,40.4],2002:[29.8,41.7],2003:[30.8,43.4],2004:[31.2,43.4],2005:[31.7,45.1],2006:[32.5,46.0],2007:[33.1,45.9],2008:[33.2,46.3],2009:[33.4,46.8],2010:[33.7,47.1],2011:[34.4,48.7],2012:[35.5,49.7],2013:[36.4,51.0],2014:[36.0,49.6],2015:[33.1,47.4],2016:[35.7,50.7],2017:[36.2,51.1],2018:[37.3,51.6],2019:[42.4,57.9],2020:[39.4,54.6],2021:[35.2,49.7],2022:[36.0,50.7],2023:[36.7,50.6]}
deg="2023,10748,13243 2022,11005,13063 2021,10885,12919 2020,12000,14724 2019,12080,14503 2018,11645,13974 2017,11972,14144 2016,11504,14288 2015,12090,14733 2014,11675,14400 2013,11500,14686 2012,12235,16943 2011,11874,15442 2010,11261,13888 2009,10304,12674 2008,10128,12796 2007,8953,11396 2006,8468,10482 2005,8738,10206 2004,8278,9998 2003,8661,9236 2002,8027,8690 2001,7347,7656 2000,7564,7703 1999,7115,6639 1998,7244,6799 1997,7619,6529 1996,8003,6416 1995,7262,5643 1994,7035,5420 1993,6934,5205 1992,6477,4845 1991,6300,4650 1990,6158,4484"
deg={int(a):(int(b),int(c)) for a,b,c in (x.split(',') for x in deg.split())}
doc={1990:[875,316],1991:[884,342],1992:[1018,345],1993:[1109,445],1994:[1144,465],1995:[1197,536],1996:[1395,720],1997:[1271,630],1998:[1277,666],1999:[1142,648],2000:[1304,775],2001:[1335,800],2002:[1311,908],2003:[1475,994],2004:[1277,980],2005:[1270,900],2006:[1217,890],2007:[1270,937],2008:[1291,993],2009:[1432,1065],2010:[1377,981],2011:[1403,1009],2012:[1265,981],2013:[1293,929],2014:[1247,960],2015:[1305,955],2016:[1442,1198],2017:[1563,1229],2018:[1285,939],2019:[1287,901],2020:[1270,851],2021:[1214,929],2022:[1219,922],2023:[1341,1123]}
prof={1990:[1840,98],1991:[1866,97],1992:[1898,109],1993:[1940,109],1994:[1936,124],1995:[1908,134],1996:[1883,140],1997:[1855,139],1998:[1847,154],1999:[1791,175],2000:[1869,221],2001:[1856,221],2002:[1842,241],2003:[1818,265],2004:[1952,322],2005:[1887,336],2006:[1854,345],2007:[1861,349],2008:[1823,368],2009:[1791,412],2010:[1794,438],2011:[1833,476],2012:[1829,504],2013:[1834,522],2014:[1876,544],2015:[1909,558],2016:[1903,591],2017:[1924,623],2018:[1959,651],2019:[1991,699],2020:[2069,802],2021:[2140,848],2022:[2135,889],2023:[2183,957]}
k=0.482
years=list(range(1990,2024))
def sh(y):
    m,f=mat[y]; a=100*k*f/(k*f+(1-k)*m)
    return [a,100*deg[y][1]/sum(deg[y]),100*doc[y][1]/sum(doc[y]),100*prof[y][1]/sum(prof[y])]
V={y:sh(y) for y in years}
W,H=720,450; T,Bm=96,372; X=[120,280,440,600]
Y=lambda v:T+(70-v)*(Bm-T)/70
path=lambda v:'M'+' L'.join(f'{x},{Y(a):.1f}' for x,a in zip(X,v))
n=len(years); step=0.45; hold=3.5; D=n*step+hold
kt=[i*step/D for i in range(n)]
ktl=';'.join(f'{t:.4f}' for t in kt)+';1'
o=[]
o.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="Women's share at four stages of the academic ladder in Austria, animated from 1990 to 2023">
<style>
svg{{--fg:#1c1c1c;--mu:#6b6b6b;--bd:#dddddd;--bg:#ffffff;--ln:#2f6fed;font-family:system-ui,-apple-system,"Segoe UI",sans-serif}}
@media (prefers-color-scheme:dark){{svg{{--fg:#ededed;--mu:#a0a0a0;--bd:#333333;--bg:#0e0e0e;--ln:#5b8dff}}}}
.bg{{fill:var(--background,var(--bg))}} text{{fill:var(--foreground,var(--fg))}} .m{{fill:var(--muted-foreground,var(--mu))}}
.g{{stroke:var(--border,var(--bd));stroke-width:1}} .p{{stroke:var(--muted-foreground,var(--mu));stroke-width:1;stroke-dasharray:2 4}}
.l{{fill:none;stroke:var(--chart-1,var(--ln));stroke-width:3;stroke-linejoin:round}} .d{{fill:var(--chart-1,var(--ln))}}
.r{{fill:none;stroke:var(--muted-foreground,var(--mu));stroke-width:1.5;stroke-dasharray:5 5}}
</style>
<rect class="bg" width="{W}" height="{H}"/>
<text x="16" y="28" font-size="17" font-weight="600">Women's share at each step of the academic ladder</text>
<text x="16" y="48" font-size="13" class="m">Austria, 1990 to 2023. Above the dotted line, women are the majority.</text>''')
for v in range(0,71,10):
    o.append(f'<line class="{"p" if v==50 else "g"}" x1="60" x2="{W-40}" y1="{Y(v):.1f}" y2="{Y(v):.1f}"/><text class="m" x="52" y="{Y(v)+4:.1f}" font-size="11" text-anchor="end">{v} %</text>')
o.append(f'<text class="m" x="{W-40}" y="{Y(50)-6:.1f}" font-size="11" text-anchor="end">parity</text>')
names=[('Matura','school-leaving exam'),('University degree','all levels'),('Doctorate',''),('Professors','in post that year')]
for x,(a,b) in zip(X,names):
    o.append(f'<text x="{x}" y="{Bm+24}" font-size="13" font-weight="600" text-anchor="middle">{a}</text>')
    if b:o.append(f'<text class="m" x="{x}" y="{Bm+40}" font-size="11" text-anchor="middle">{b}</text>')
v0=V[1990]
o.append(f'<path class="r" d="{path(v0)}"/><text class="m" x="{X[3]+10}" y="{Y(v0[3])+4:.1f}" font-size="11">1990</text>')
vals=';'.join(path(V[y]) for y in years)+';'+path(V[years[-1]])
o.append(f'<path class="l" d="{path(V[years[-1]])}"><animate attributeName="d" dur="{D:.2f}s" repeatCount="indefinite" keyTimes="{ktl}" values="{vals}"/></path>')
for j,x in enumerate(X):
    cy=';'.join(f'{Y(V[y][j]):.1f}' for y in years)+f';{Y(V[years[-1]][j]):.1f}'
    o.append(f'<circle class="d" cx="{x}" cy="{Y(V[years[-1]][j]):.1f}" r="5"><animate attributeName="cy" dur="{D:.2f}s" repeatCount="indefinite" keyTimes="{ktl}" values="{cy}"/></circle>')
for i,y in enumerate(years):
    last=i==n-1
    if i==0: an=f'values="visible;hidden" keyTimes="0;{kt[1]:.4f}"'
    elif last: an=f'values="hidden;visible" keyTimes="0;{kt[i]:.4f}"'
    else: an=f'values="hidden;visible;hidden" keyTimes="0;{kt[i]:.4f};{kt[i+1]:.4f}"'
    o.append(f'<g visibility="{"visible" if last else "hidden"}"><animate attributeName="visibility" calcMode="discrete" dur="{D:.2f}s" repeatCount="indefinite" {an}/>')
    o.append(f'<text x="{W-40}" y="80" font-size="34" font-weight="700" text-anchor="end">{y}</text>')
    for j,x in enumerate(X):
        o.append(f'<text x="{x}" y="{Y(V[y][j])-13:.1f}" font-size="14" font-weight="600" text-anchor="middle">{V[y][j]:.0f} %</text>')
    o.append('</g>')
o.append('</svg>')
open(ROOT+'figures/'+'women-share-evolution.svg','w').write(with_credit('\n'.join(o)))
for y in (1990,2000,2010,2023): print(y,[round(a,1) for a in V[y]])
