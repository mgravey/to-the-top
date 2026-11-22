import math,json
import os; ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/'; B=ROOT+'figures/'
from credit import with_credit
d=json.load(open(ROOT+'data/series.json')); years=d['years']; S=d['S']; n=len(years)
# which frames have counted data at the top steps (frame Y uses data of year Y-1)
NAT={r['year']:r['appointments_women_pct'] for r in json.load(open(ROOT+'data/universities.json'))['national']}
PROF_COUNTED=lambda i: years[i]-1 in NAT
COUNTED_EST=lambda j,i: j==0 or (j==5 and not PROF_COUNTED(i))   # Matura track (2024 only) and professor before 2006 stay estimates
COUNTED_SOLID=lambda i: 6 if PROF_COUNTED(i) else 5
AG=[10,14,18.5,24.5,27.4,32.1,43]; EST=[True,False,False,False,True,True]
names=('Age 10','Matura track','Matura','1st degree','Master','Doctorate','Professor'); subs=('','age 14','age 18½','age 24½','age 27','age 32','about 43, assumed')
W,H=820,610; L,R,T,Bm=58,112,112,520
X=[L+(a-10)*(W-L-R)/33 for a in AG]
step=0.38; D=n*step+4
kt=[i*step/D for i in range(n)]+[1]; KT=';'.join(f'{t:.4f}' for t in kt)
ext=lambda v:';'.join(v)+';'+v[-1]
A=f'dur="{D:.2f}s" repeatCount="indefinite"'
def vis(i):
    a=kt[i]; b=kt[i+1]
    if i==0: s=f'values="visible;hidden" keyTimes="0;{b:.4f}"'
    elif i==n-1: s=f'values="hidden;visible" keyTimes="0;{a:.4f}"'
    else: s=f'values="hidden;visible;hidden" keyTimes="0;{a:.4f};{b:.4f}"'
    return f'<animate attributeName="visibility" calcMode="discrete" {A} {s}/>'
def since(f):
    return '' if f==0 else f'<animate attributeName="visibility" calcMode="discrete" {A} values="hidden;visible" keyTimes="0;{kt[f]:.4f}"/>'
def fill(row,start=100.0):
    # (x,value) per point; missing inner points log-interpolated along age, missing trailing points collapsed on the last known one
    v=[start]+list(row); out=[]
    last=max(k for k in range(7) if v[k] is not None)
    for j,x in enumerate(v):
        if x is not None: out.append((X[j],x))
        elif j>last: out.append((X[last],v[last]))
        else:
            a=max(k for k in range(j) if v[k] is not None); b=min(k for k in range(j+1,7) if v[k] is not None)
            t=(AG[j]-AG[a])/(AG[b]-AG[a]); out.append((X[j],math.exp(math.log(v[a])*(1-t)+math.log(v[b])*t)))
    return out
STYLE='''<style>
svg{--fg:#1c1c1c;--mu:#6b6b6b;--bd:#dddddd;--bg:#ffffff;--c1:#2f6fed;--c2:#0f9d8a;font-family:system-ui,-apple-system,"Segoe UI",sans-serif}
@media (prefers-color-scheme:dark){svg{--fg:#ededed;--mu:#a0a0a0;--bd:#333333;--bg:#0e0e0e;--c1:#5b8dff;--c2:#2dd4bf}}
.bg{fill:var(--background,var(--bg))} text{fill:var(--foreground,var(--fg))} .m{fill:var(--muted-foreground,var(--mu))}
.gl{stroke:var(--border,var(--bd));stroke-width:1} .ax{stroke:var(--muted-foreground,var(--mu));stroke-width:1.5;fill:none}
.lg,.lb,.eg,.eb{fill:none;stroke-width:3;stroke-linejoin:round} .lg,.eg{stroke:var(--chart-1,var(--c1))} .lb,.eb{stroke:var(--chart-2,var(--c2))}
.eg,.eb{stroke-width:2.5;stroke-dasharray:6 5}
.dg{fill:var(--chart-1,var(--c1))} .db{fill:var(--chart-2,var(--c2))}
.hg{fill:var(--background,var(--bg));stroke:var(--chart-1,var(--c1));stroke-width:2.5} .hb{fill:var(--background,var(--bg));stroke:var(--chart-2,var(--c2));stroke-width:2.5}
.ghg,.ghb{fill:none;stroke-width:2;stroke-linejoin:round;opacity:.28} .ghg{stroke:var(--chart-1,var(--c1))} .ghb{stroke:var(--chart-2,var(--c2))}
</style>'''
def chart(fname,title,sub,aria,series,lo,hi,ticks,fmt,legend,parity=None,suffix=None,log=True,start=100.0,tickfmt=str,solid_upto=lambda i:4,est=lambda j,i:EST[j]):
    # solid_upto(i): last point (0=age 10 ... 6=professor) drawn solid in frame i; est(j,i): step j is an estimate in frame i
    Yv=(lambda v:T+(math.log(hi)-math.log(v))*(Bm-T)/(math.log(hi)-math.log(lo))) if log else (lambda v:T+(hi-v)*(Bm-T)/(hi-lo))
    times=','.join(f'{i*step:.2f}' for i in range(n)); labels=','.join(str(y) for y in years)
    o=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="{aria}" data-times="{times}" data-labels="{labels}">',STYLE,f'<rect class="bg" width="{W}" height="{H}"/>',
       f'<text x="16" y="30" font-size="19" font-weight="600">{title}</text>',f'<text x="16" y="52" font-size="14" class="m">{sub}</text>',legend]
    for v in ticks:
        o.append(f'<line class="{"ax" if v==parity else "gl"}" x1="{L}" x2="{X[-1]:.0f}" y1="{Yv(v):.1f}" y2="{Yv(v):.1f}"{" stroke-dasharray=\"2 4\"" if v==parity else ""}/><text class="m" x="{L-8}" y="{Yv(v)+4:.1f}" font-size="12" text-anchor="end">{tickfmt(v)}</text>')
    if parity: o.append(f'<text class="m" x="{X[-1]:.0f}" y="{Yv(parity)-7:.1f}" font-size="12" text-anchor="end">parity</text>')
    for x,a,b in zip(X,names,subs):
        o.append(f'<line class="gl" x1="{x:.1f}" x2="{x:.1f}" y1="{Bm}" y2="{Bm+6}"/><text x="{x:.1f}" y="{Bm+24}" font-size="12.5" font-weight="600" text-anchor="middle">{a}</text>')
        if b:o.append(f'<text class="m" x="{x:.1f}" y="{Bm+40}" font-size="11.5" text-anchor="middle">{b}</text>')
    st=start if isinstance(start,dict) else {k:start for k in series}
    if not isinstance(start,dict): o.append(f'<text x="{X[0]+9:.1f}" y="{Yv(start)-9:.1f}" font-size="14" font-weight="600">{start:g}</text>')
    keys=list(series)
    full={k:[fill(r,st[k]) for r in series[k]] for k in keys}
    for k in keys:  # faint copy of the latest year, kept as a reference while the past plays
        o.append(f'<path class="gh{k}" d="M'+' L'.join(f'{a:.1f},{Yv(b):.1f}' for a,b in full[k][-1])+'"/>')
    for k in keys:
        s=series[k]; F=full[k]; ok=keys[1] if (len(keys)>1 and k==keys[0]) else keys[0]
        # always 7 points per path (unused ones collapsed on the break point) so frames interpolate smoothly
        def seg(p,kb,solid):
            q=[p[min(j,kb)] if solid else p[max(j,kb)] for j in range(7)]
            return 'M'+' L'.join(f'{a:.1f},{Yv(b):.1f}' for a,b in q)
        for cls,solid in ((f'l{k}',True),(f'e{k}',False)):
            o.append(f'<path class="{cls}" d="{seg(F[-1],solid_upto(n-1),solid)}"><animate attributeName="d" {A} keyTimes="{KT}" values="{ext([seg(p,solid_upto(i),solid) for i,p in enumerate(F)])}"/></path>')
        o.append(f'<circle class="d{k}" cx="{X[0]:.1f}" cy="{Yv(st[k]):.1f}" r="5"/>')
        for j in range(6):
            f=next(i for i in range(n) if s[i][j] is not None)
            cl=[f'h{k}' if est(j,i) else f'd{k}' for i in range(n)]
            anim='' if len(set(cl))==1 else f'<animate attributeName="class" calcMode="discrete" {A} keyTimes="{KT}" values="{ext(cl)}"/>'
            o.append(f'<circle class="{cl[-1]}" cx="{X[j+1]:.1f}" cy="{Yv(F[-1][j+1][1]):.1f}" r="5">{since(f)}{anim}<animate attributeName="cy" {A} keyTimes="{KT}" values="{ext([f"{Yv(p[j+1][1]):.1f}" for p in F])}"/></circle>')
            pos=[]
            for i in range(n):
                v=F[i][j+1][1]; w=full[ok][i][j+1][1]
                up=True if len(keys)==1 else (v>w or (v==w and k=='g'))
                if j==5: pos.append(f'{X[6]+11:.1f},{Yv(v)+(((-4 if up else 13) if not log else (0 if up else 10)) if len(keys)>1 else 5):.1f}')
                elif not log and v<5 and len(keys)>1: pos.append(f'{X[j+1]:.1f},{Yv(v)+(-28 if up else -12):.1f}')
                else: pos.append(f'{X[j+1]:.1f},{Yv(v)+(-12 if up else 24):.1f}')
            o.append(f'<g transform="translate({pos[-1]})"><animateTransform attributeName="transform" type="translate" {A} keyTimes="{KT}" values="{ext(pos)}"/>')
            for i in range(f,n):
                t=fmt(s[i][j])+((suffix[k] if suffix else '') if j==5 else '')
                o.append(f'<text font-size="14" font-weight="600" text-anchor="{"start" if j==5 else "middle"}" visibility="{"visible" if i==n-1 else "hidden"}">{t}{vis(i)}</text>')
            o.append('</g>')
    for i,Y in enumerate(years):
        o.append(f'<g visibility="{"visible" if i==n-1 else "hidden"}">{vis(i)}<text x="{W-16}" y="88" font-size="38" font-weight="700" text-anchor="end">{Y}</text></g>')
    o.append('</svg>'); open(B+fname,'w').write(with_credit('\n'.join(o)))
f1=lambda v: f'{v:.0f}' if v>=10 else f'{v:.1f}' if v>=1 else f'{v:.2f}' if v>=0.1 else f'{v:.3f}'
leg1='<rect class="dg" x="16" y="68" width="16" height="4" rx="2"/><text x="38" y="75" font-size="13">Girls</text><rect class="db" x="82" y="68" width="16" height="4" rx="2"/><text x="104" y="75" font-size="13">Boys</text><circle class="ax" cx="158" cy="70" r="4.5"/><line class="ax" x1="170" x2="192" y1="70" y2="70" stroke-dasharray="5 4"/><text x="198" y="75" font-size="13">Rough estimate</text><line class="ghb" x1="312" x2="334" y1="73" y2="73"/><line class="ghg" x1="312" x2="334" y1="68" y2="68"/><text x="340" y="75" font-size="13">Faint: 2024, for reference</text>'
chart('pipeline-log-all-steps-animated.svg','From age 10 to a professorship, per 100 children','Austria, 1960 to 2024. Logarithmic scale. Doctorates and professors: counted, Austrian graduates only.',
      'Per 100 girls and 100 boys in Austria: how many reach each step from age 10 to a professorship, animated from 1960 to 2024, log scale',
      {'b':S['b'],'g':S['g']},0.004,100,(0.01,0.1,1,10,100),f1,leg1,suffix={'g':' girls','b':' boys'},solid_upto=COUNTED_SOLID,est=COUNTED_EST)
chart('pipeline-linear-all-steps-animated.svg','From age 10 to a professorship, per 100 children','Austria, 1960 to 2024. Linear scale. Doctorates and professors: counted, Austrian graduates only.',
      'Per 100 girls and 100 boys in Austria: how many reach each step from age 10 to a professorship, animated from 1960 to 2024, linear scale',
      {'b':S['b'],'g':S['g']},0,100,(0,20,40,60,80,100),f1,leg1,suffix={'g':' girls','b':' boys'},log=False,solid_upto=COUNTED_SOLID,est=COUNTED_EST)
ratio=[[None if g is None else 100*g/b for g,b in zip(rg,rb)] for rg,rb in zip(S['g'],S['b'])]
leg2='<rect class="dg" x="16" y="68" width="16" height="4" rx="2"/><text x="38" y="75" font-size="13">Girls per 100 boys</text><circle class="ax" cx="178" cy="70" r="4.5"/><line class="ax" x1="190" x2="212" y1="70" y2="70" stroke-dasharray="5 4"/><text x="218" y="75" font-size="13">Rough estimate</text><line class="ghg" x1="332" x2="354" y1="70" y2="70"/><text x="360" y="75" font-size="13">Faint: 2024, for reference</text>'
chart('gender-ratio-all-steps-animated.svg','Girls per 100 boys reaching each step','Austria, 1960 to 2024. Below the dotted line, fewer girls than boys get that far.',
      'Girls per 100 boys reaching each step from age 10 to a professorship in Austria, animated from 1960 to 2024',
      {'g':ratio},0,160,(0,25,50,75,100,125,150),lambda v:f'{v:.0f}',leg2,parity=100,log=False,solid_upto=COUNTED_SOLID,est=COUNTED_EST)
print('max ratio',max(v for r in ratio for v in r if v is not None))
FS=0.495  # girls' share of an age group
share=[[None if g is None else 100*FS*g/(FS*g+(1-FS)*b) for g,b in zip(rg,rb)] for rg,rb in zip(S['g'],S['b'])]
# shares can be counted directly where the per-100 rates need assumptions:
# doctorate = women among all doctorates awarded (Statistics Austria 2.2_13, 1980-2023);
# professor = women among all new professors (Wissensbilanzen of the 22 universities, 2006-2025).
# Frame Y uses data of year Y-1, like every other step.
DOC=json.load(open(ROOT+'data/professor-lag.json'))['doctorates_women_pct']
for i,Y in enumerate(years):
    if str(Y-1) in DOC and share[i][4] is not None: share[i][4]=DOC[str(Y-1)]
    if Y-1 in NAT: share[i][5]=NAT[Y-1]
bshare=[[None if v is None else 100-v for v in r] for r in share]
chart('girls-share-all-steps-animated.svg','Out of every 100 people reaching each step, how many are girls and boys','Austria, 1960 to 2024. The two lines always add up to 100; they cross at parity.',
      'Girls\' and boys\' share among the people reaching each step from age 10 to a professorship in Austria, animated from 1960 to 2024',
      {'b':bshare,'g':share},0,100,(0,10,20,30,40,50,60,70,80,90,100),lambda v:f'{v:.0f} %',leg1,parity=50,log=False,start={'g':100*FS,'b':100-100*FS},tickfmt=lambda v:f'{v} %',
      solid_upto=COUNTED_SOLID, est=COUNTED_EST)
json.dump({'years':years,'girls_share_pct':share},open(ROOT+'data/girls-share.json','w'))
for Y in (1960,1970,1981,1991,2000,2010,2024): print(Y,[None if v is None else round(v) for v in ratio[Y-1960]],[None if v is None else round(v,1) for v in share[Y-1960]])
