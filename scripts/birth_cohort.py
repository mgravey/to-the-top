import os; ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/'
import math
from credit import with_credit
# born around: (boys matura+, boys degree, girls matura+, girls degree) — register 2022, age groups 80–84 ... 30–34
C=[(1940,19.6,10.5,10.0,3.9),(1945,22.4,12.1,13.6,5.8),(1950,22.0,12.6,15.3,8.9),(1955,24.9,13.7,20.8,12.9),(1960,25.7,13.3,24.8,13.7),(1965,27.3,13.8,28.6,14.7),(1970,30.3,16.0,32.8,17.1),(1975,32.9,18.9,38.8,22.2),(1980,36.4,20.7,45.7,26.3),(1985,37.8,21.9,48.6,29.3),(1990,39.8,22.1,51.6,31.6)]
W,H=720,470; L,R,T,Bm=64,150,104,392
AG=[10,18.5,26]
X=[L+(a-10)*(W-L-R)/16 for a in AG]
lo=3
Y=lambda v:T+(math.log(100)-math.log(v))*(Bm-T)/(math.log(100)-math.log(lo))
n=len(C); P=1.5; hold=0.8; D=n*P+3
kts=[]
for i in range(n): kts+= [i*P/D,(i*P+hold)/D]
kts.append(1)
KT=';'.join(f'{t:.4f}' for t in kts)
dup=lambda vals:';'.join(v for x in vals for v in (x,x))+';'+vals[-1]
ser={'b':[(c[1],c[2]) for c in C],'g':[(c[3],c[4]) for c in C]}
path=lambda p:f'M{X[0]:.1f},{Y(100):.1f} L{X[1]:.1f},{Y(p[0]):.1f} L{X[2]:.1f},{Y(p[1]):.1f}'
A=f'dur="{D:.2f}s" repeatCount="indefinite"'
def vis(i):
    a=0 if i==0 else ((i-1)*P+hold+ (P-hold)/2)/D
    b=(i*P+hold+(P-hold)/2)/D
    if i==0: s=f'values="visible;hidden" keyTimes="0;{b:.4f}"'
    elif i==n-1: s=f'values="hidden;visible" keyTimes="0;{a:.4f}"'
    else: s=f'values="hidden;visible;hidden" keyTimes="0;{a:.4f};{b:.4f}"'
    return f'<animate attributeName="visibility" calcMode="discrete" {A} {s}/>'
o=[f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="Per 100 girls and 100 boys in Austria: how many reach the Matura and a higher-education degree, animated by birth cohort from 1940 to 1990, log scale">
<style>
svg{{--fg:#1c1c1c;--mu:#6b6b6b;--bd:#dddddd;--bg:#ffffff;--c1:#2f6fed;--c2:#0f9d8a;font-family:system-ui,-apple-system,"Segoe UI",sans-serif}}
@media (prefers-color-scheme:dark){{svg{{--fg:#ededed;--mu:#a0a0a0;--bd:#333333;--bg:#0e0e0e;--c1:#5b8dff;--c2:#2dd4bf}}}}
.bg{{fill:var(--background,var(--bg))}} text{{fill:var(--foreground,var(--fg))}} .m{{fill:var(--muted-foreground,var(--mu))}}
.gl{{stroke:var(--border,var(--bd));stroke-width:1}}
.lg{{fill:none;stroke:var(--chart-1,var(--c1));stroke-width:3;stroke-linejoin:round}} .dg{{fill:var(--chart-1,var(--c1))}}
.lb{{fill:none;stroke:var(--chart-2,var(--c2));stroke-width:3;stroke-linejoin:round}} .db{{fill:var(--chart-2,var(--c2))}}
</style>
<rect class="bg" width="{W}" height="{H}"/>
<text x="16" y="28" font-size="17" font-weight="600">Out of 100 girls and 100 boys, how many get how far</text>
<text x="16" y="48" font-size="13" class="m">Austria, by year of birth. Logarithmic scale: equal drops mean equal shares lost.</text>
<rect class="dg" x="16" y="62" width="14" height="4" rx="2"/><text x="36" y="69" font-size="12">Girls</text>
<rect class="db" x="76" y="62" width="14" height="4" rx="2"/><text x="96" y="69" font-size="12">Boys</text>''']
for v in (5,10,20,50,100):
    o.append(f'<line class="gl" x1="{L}" x2="{X[2]+20:.0f}" y1="{Y(v):.1f}" y2="{Y(v):.1f}"/><text class="m" x="{L-8}" y="{Y(v)+4:.1f}" font-size="11" text-anchor="end">{v}</text>')
for x,a,b in zip(X,('Age 10','Matura or higher','Higher-education degree'),('','age 18–19','mid-20s or later')):
    o.append(f'<text x="{x:.1f}" y="{Bm+24}" font-size="13" font-weight="600" text-anchor="middle">{a}</text>')
    if b:o.append(f'<text class="m" x="{x:.1f}" y="{Bm+40}" font-size="11" text-anchor="middle">{b}</text>')
o.append(f'<text x="{X[0]+9:.1f}" y="{Y(100)-9:.1f}" font-size="14" font-weight="600">100</text>')
for k in ('b','g'):
    S=ser[k]
    o.append(f'<path class="l{k}" d="{path(S[-1])}"><animate attributeName="d" {A} keyTimes="{KT}" values="{dup([path(p) for p in S])}"/></path>')
    o.append(f'<circle class="d{k}" cx="{X[0]:.1f}" cy="{Y(100):.1f}" r="5"/>')
    for j in (0,1):
        o.append(f'<circle class="d{k}" cx="{X[j+1]:.1f}" cy="{Y(S[-1][j]):.1f}" r="5"><animate attributeName="cy" {A} keyTimes="{KT}" values="{dup([f"{Y(p[j]):.1f}" for p in S])}"/></circle>')
        other=ser['g' if k=='b' else 'b']
        pos=[]
        for i in range(n):
            up = S[i][j]>other[i][j] or (S[i][j]==other[i][j] and k=='g')
            pos.append(f'{X[j+1]:.1f},{Y(S[i][j])+(-12 if up else 22):.1f}')
        o.append(f'<g transform="translate({pos[-1]})"><animateTransform attributeName="transform" type="translate" {A} keyTimes="{KT}" values="{dup(pos)}"/>')
        for i in range(n):
            v=S[i][j]; t=f'{v:.0f}' if v>=10 else f'{v:.1f}'
            if j==1: t+=' girls' if k=='g' else ' boys'
            anc='start' if j==1 else 'middle'; dx=10 if j==1 else 0
            dy=0
            o.append(f'<text x="{dx}" y="{dy}" font-size="14" font-weight="600" text-anchor="{anc}" visibility="{"visible" if i==n-1 else "hidden"}">{t}{vis(i)}</text>')
        o.append('</g>')
for i,c in enumerate(C):
    o.append(f'<g visibility="{"visible" if i==n-1 else "hidden"}">{vis(i)}<text class="m" x="{W-16}" y="62" font-size="12" text-anchor="end">born around</text><text x="{W-16}" y="96" font-size="34" font-weight="700" text-anchor="end">{c[0]}</text></g>')
o.append('</svg>')
open(ROOT+'figures/'+'pipeline-log-by-birth-cohort.svg','w').write(with_credit('\n'.join(o)))
