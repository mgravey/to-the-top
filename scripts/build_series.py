import math,csv,re,json
import os; ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/'; B=ROOT
exec(open(ROOT+'scripts/women_share.py').read().split("k=0.482")[0])   # mat{y:[m,f]}, deg{y:(m,f)} uni Austrians, doc{y:[m,f]}, prof{y:[m,w]}
mat.update({1986:[24.4,25.4],1987:[25.3,26.1],1988:[25.8,27.9],1989:[26.6,29.7]})
matT={}
L=open(B+'data/biz-2024-25-report.txt',encoding='utf-8').read().split('\n')
def table(title,stop=400):
    i0=next(i for i,l in enumerate(L) if l.strip().startswith(title)); out={}
    for l in L[i0+1:i0+stop]:
        if re.match(r'\s*\d\.\d_\d',l): break
        m=re.match(r'\s*((?:19|20)\d\d)/\d\d\s+(.*)',l)
        if m: out[int(m.group(1))]=[0 if t.strip()=='-' else float(re.sub(r'[ .]','',t).replace(',','.')) for t in re.split(r'\s{2,}',m.group(2).strip())]
    return out
rp=table('2.2_1 Reifeprüfungen'); rq=table('2.2_2 Reifeprüfungsquote'); pf=table('4.1_8 Entwicklung'); dk=table('2.2_13 Entwicklung'); tyr=table('2.2_9 Ordentliche')
# rq has multi-line rows for late years; fill from mat
tot_rate={y:v[2] for y,v in rq.items() if len(v)==3}
tot_rate.update({2019:49.9,2020:46.8,2021:42.2,2022:43.1,2023:43.4})
mat.update({2019:[42.4,57.9],2020:[39.4,54.6],2021:[35.2,49.7],2022:[36.0,50.7],2023:[36.7,50.6]})
print('rp',rp[1986],rp[2000],rp.get(2023),len(rp),'pf',pf[1980],'dk',dk[1980],dk[2023])
adj=40230/42525; FS=0.495
births={1951:102764,1952:103012,1961:131563,1962:133253,1963:134809,1964:133841,1965:129924,1966:128577,1967:127404,1968:126115,1969:121377}
coh={}
for y in range(1986,2024):
    t=sum(rp[y][:2])*adj/(tot_rate[y]/100); coh[y+1]=(t*(1-FS),t*FS)
k87=sum(coh[1987])/((births[1968]+births[1969])/2); print('births check',k87, sum(coh[1987]), sum(coh[2024]))
for Y in [1970]+list(range(1980,1987)):
    t=(births[Y-19]+births[Y-18])/2*k87; coh[Y]=(t*(1-FS),t*FS)
tot={}
for r in csv.reader(open(B+'data/2-1-9_P24.csv',encoding='utf-8-sig')):
    if r and re.match(r'(19|20)\d\d/',r[0]): tot[int(r[0][:4])]=(int(r[2]),int(r[3]))
fh={}
for r in csv.reader(open(B+'data/2-1-10_P24.csv',encoding='utf-8-sig')):
    if r and re.match(r'(19|20)\d\d/',r[0]): fh[int(r[0][:4])]=(int(r[5]),int(r[6]))
ty={}
for y,v in tyr.items():
    k=dict(DipU=v[0],Dok=v[1],BachU=0,MastU=0,DipFH=0,BachFH=0,MastFH=0,PH=0); n=len(v)
    if n==3: k['DipFH']=v[2]
    elif n==5: k.update(BachU=v[2],MastU=v[3],DipFH=v[4])
    elif n==7: k.update(BachU=v[2],MastU=v[3],DipFH=v[4],BachFH=v[5])
    elif n==8: k.update(BachU=v[2],MastU=v[3],DipFH=v[4],BachFH=v[5],MastFH=v[6])
    elif n==9: k.update(BachU=v[2],MastU=v[3],DipFH=v[4],BachFH=v[5],MastFH=v[6],PH=v[7])
    ty[y]=k
# Matura rate 1980 from counts (26749 total, 13124 women), then linear to 1987
REG={'m':([19.6,22.4,22.0,24.9,25.7,27.3,30.3],[10.0,13.6,15.3,20.8,24.8,28.6,32.8]),'h':([9.7,10.9,10.4,11.5,11.9,12.7,15.0],[3.1,4.3,5.0,7.4,8.9,10.8,13.5])}
def reg(kind,i,born):
    v=REG[kind][i]; p=(born-1940)/5; a=max(0,min(5,int(p))); return v[a]+(v[a+1]-v[a])*(p-a)
m70=((16069-5471)*adj/coh[1970][0]*100, 5471*adj/coh[1970][1]*100)
m80=((26749-13124)*adj/coh[1980][0]*100, 13124*adj/coh[1980][1]*100); print('matura 1970',m70,'1980',m80)
def M(Y,i):
    if Y>=1987: return mat[Y-1][i]
    if Y>=1980: a=(Y-1980)/7; return m80[i]*(1-a)+mat[1986][i]*a
    if Y>=1970: a=(Y-1970)/10; return m70[i]*(1-a)+m80[i]*a
    return reg('m',i,Y-19)*m70[i]/reg('m',i,1951)
act=(766/1341,595/1123); f23=[act[i]/(deg[2023][i]/tot[2023][i]) for i in (0,1)]
turn=(150/2233,102/1024); keep=(0.70,0.77); phsex=(0.23,0.77)
NAT={r['year']:r for r in json.load(open(ROOT+'data/universities.json'))['national']}
EST_SEX=json.load(open(ROOT+'data/professor-lag.json'))['implied_hires_by_sex_ESTIMATE']   # {year: [women, men]}
years=list(range(1960,2025)); S={'b':[],'g':[]}
for Y in years:
    y=Y-1; a=max(0,(Y-1990)/34); yd=max(y,1990); rows={}
    for i,k in enumerate('bg'):
        c=coh.get(Y,(1,1))[i]
        dA=dk[y][i]*deg[yd][i]/tot[yd][i]*(1+(f23[i]-1)*a) if y>=1980 else None
        first=mast=None
        if y>=1990:
            t=ty[y]; U=deg[y][i]-dA
            un=t['BachU']+t['DipU']+t['MastU']; fn=t['BachFH']+t['DipFH']+t['MastFH']; F=fh.get(y,(0,0))[i]
            phm=0.25*min(1,max(0,(y-2015)/4)); PH=t['PH']*0.94*phsex[i]
            first=(U*(t['BachU']+t['DipU'])/un+(F*(t['BachFH']+t['DipFH'])/fn if fn else 0)+PH*(1-phm))/c*100
            mast=(U*(t['MastU']+t['DipU'])/un+(F*(t['MastFH']+t['DipFH'])/fn if fn else 0)+PH*phm)/c*100
        m=M(Y,i)
        if y in NAT:   # counted new professors by sex (22 Wissensbilanzen), minus the ~48 % appointed from abroad
            w=NAT[y]['appointments_women']; prof=(NAT[y]['appointments_total']-w if i==0 else w)*0.52/c*100
        elif str(y) in EST_SEX:   # estimate: hires implied by professors in post, departure rates calibrated on the counts
            prof=EST_SEX[str(y)][1-i]*0.52/c*100
        else:
            prof=None
        rows[k]=[m/keep[i] if Y==2024 else None, m, first, mast, dA/c*100 if dA else None, prof]
    for k in 'bg': S[k].append(rows[k])
f91=[S[k][1991-1960][2] for k in 'bg']
for Y in range(1965,1991):
    for i,k in enumerate('bg'):
        v=reg('h',i,Y-25)*f91[i]/reg('h',i,1966); S[k][Y-1960][2]=v; S[k][Y-1960][3]=v
for Y in (1960,1965,1970,1980,1981,1990,1991,2024): print(Y,[[None if v is None else round(v,3) for v in S[k][Y-1960]] for k in 'gb'])
json.dump({'years':years,'S':S},open(ROOT+'data/series.json','w'))
