from pathlib import Path
import re,sys
# Nordic ceramic: direct generator/render parameters, not an image filter.
STYLES={
'palette':dict(ink='#52635d',paper='#e7eae5',grass='#a4b99b',grassSide='#839c7d',grassHigh='#c4d3b6',dirt='#cdbba7',dirtDark='#a79585',sand='#e7d9c4',rock='#b8b5ad',path='#e3ded1',plaza='#d8d8d0',garden='#8ca986',sea='#91b6bb',seaDeep='#729aa5',seaSide='#668d9b',foam='#edf5f2',shallow='#b9d3cf',stone='#e7e3da',stoneShade='#c8c5bd',wood='#b89777',white='#f7f4ec',glass='#8bafb7',leaf='#83a68a',leafDark='#628671',bush='#95aa85',trunk='#856c58',brick='#b97760',redDark='#9a594c',red='#bd7c69',yellow='#edc77e',pink='#d8a9a4',metal='#55645f',marble='#f0eee7',magic='#afa7c6'),
'ramps':dict(wall='#ead9b3 #c4b9ce #dfb4a6 #c3d2b7 #bdcfd4 #f5f1e7 #d9c0a8 #d4d7af'.split(),stone='#e7e3da #dddcd5 #d0d1cb #e5dfd0 #c6cbc6 #f0ede5 #d9d4c7 #c5c4bd'.split(),wood='#b89777 #9e8168 #c3a68a #947b67 #ab8d75 #cfb99d #aa957f #87725c'.split(),roof='#b97860 #648593 #c49b65 #7e9c85 #7f8298'.split()),
'look':dict(inkWidth=.85,inkWidthInner=.48,inkWidthFar=.55,inkSilhouette=.52,inkSeam=.22,inkCrease=.2,inkDetailFar=.25,wobble=.08,hatch=.08,pencil=.13,paper=.1,ground=1.08,slabShadow=.24,halo=.42),
'grade':dict(dayInk='#52635d',dayChroma=.93,daySat=.9,dayCast=.62,duskInk='#60515b',duskTint='#ffe5cc',duskShade='#c6c6d4',duskSat=.83,nightTint='#637d9a',nightShade='#445f7b',nightInk='#273a4d',nightSat=.65,dawnInk='#53616e',dawnTint='#e5e3eb',dawnShade='#c2ceda'),
'house':dict(eave=.035,rake=.025,roofThick=.085,rise1=.39,rise2=.62,rise3=.82,sag=.004,sagMax=.012,lift=.018,tileTone=.025),
 'terrain':dict(wobble=.012,radiusVary=.045,rockTop='#d5d4cb',rockMoss='#b4bfa3',grassDry='#bbc4a4'),
 'season-look':dict(springGreen='#c3d6a8',autumnGrass='#cfbc89',leafYellow='#d8ba75',leafOrange='#ce956a',leafRusset='#b8785c',paperWinter='#e5e9eb',paperAutumn='#e9e3d8',paperGrey='#dce2e1')}
def literal(v):
    if isinstance(v,list): return '['+','.join(map(literal,v))+']'
    if isinstance(v,str): return '`'+v+'`'
    return str(v)
def apply(root):
    root=Path(root);seen=set()
    for p in (root/'assets').glob('*.js'):
        s=p.read_text();old=s
        for name,values in STYLES.items():
            m=re.search(r'`'+re.escape(name)+r'`,\{([^{}]+)\}',s)
            if not m: continue
            body=m.group(1)
            for k,v in values.items():
                body,n=re.subn(r'(?<!\w)'+k+r':(?:`[^`]*`|\[[^\]]*\]|-?\d*\.?\d+)',lambda _:k+':'+literal(v),body)
                if n!=1: raise ValueError(f'{name}.{k}: {n} matches')
            s=s[:m.start(1)]+body+s[m.end(1):];seen.add(name)
        if s!=old:p.write_text(s)
    if seen!=set(STYLES):raise ValueError(f'Missing style groups {set(STYLES)-seen}')
    for p in list((root/'assets').glob('*.css'))+list(root.rglob('*.html')):
        s=p.read_text();p.write_text(s.replace('#f2ede3','#e7eae5').replace('#3a2f2a','#52635d'))
    print('Applied:',', '.join(sorted(seen)))
if __name__=='__main__':apply(sys.argv[1] if len(sys.argv)>1 else 'dist')
