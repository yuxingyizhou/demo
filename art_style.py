from pathlib import Path
import re, sys, json

# 江南水乡：只修改已固定版本的美术参数与既有房屋样式；保留存档 ID。
STYLES = {
 'palette': dict(ink='#38433f',paper='#e9eae2',grass='#9db18a',grassSide='#758c72',grassHigh='#c4cdb0',dirt='#b6a692',dirtDark='#918477',sand='#d6cdb7',rock='#a9aaa1',path='#c6c9c0',plaza='#d5d6cd',garden='#87a67b',sea='#6d9b8e',seaDeep='#4d8074',seaSide='#4d746c',foam='#d9e7dc',shallow='#9ab6a3',stone='#e4e3d9',stoneShade='#b6bbb3',wood='#80664f',white='#faf7ef',glass='#68837e',leaf='#779b68',leafDark='#486c54',bush='#88a478',trunk='#75604c',brick='#ac806a',redDark='#963e35',red='#bb5041',yellow='#e6bd73',pink='#c8a8a2',metal='#424c49',marble='#e9e8df',magic='#9ba8ba'),
 'ramps': dict(wall='#f3efe4 #e5e5dc #f1eadb #e8e7dd #d8dfd7 #fcf9ef #e5d8c4 #e8e9df'.split(),stone='#e1e2d8 #ced3cd #b7bfb9 #d3d4c8 #b4bbb5 #eceae1 #c8c9bc #aab3ae'.split(),wood='#80664f #6c5544 #9c8062 #725d4e #947457 #ad9476 #88766a #5f5143'.split(),roof='#434b4b #52605f #6a6861 #4f5b54 #41494e'.split()),
 'look': dict(inkWidth=1.05,inkWidthInner=.57,inkWidthFar=.65,inkSilhouette=.72,inkSeam=.43,inkCrease=.35,inkDetailFar=.35,wobble=.28,hatch=.16,pencil=.25,paper=.30,ground=1.0,slabShadow=.18,halo=.56),
 'grade': dict(dayInk='#38433f',dayChroma=.88,daySat=.86,dayCast=.43,duskInk='#473a3c',duskTint='#f4d9bd',duskShade='#bcc7c2',duskSat=.84,nightTint='#637e90',nightShade='#465d71',nightInk='#253739',nightSat=.65,dawnInk='#465951',dawnTint='#e4e7dd',dawnShade='#c4d3cc',lamp='#f5c675',lampWarm='#ffad61'),
 'house': dict(inset=.085,eave=.105,rake=.085,eaveDrop=.02,roofThick=.065,rise1=.38,rise2=.64,rise3=.88,sag=.018,sagMax=.045,lift=.02,tileTone=.035),
 'terrain': dict(wobble=.025,radiusVary=.06,rockTop='#c5c8bc',rockMoss='#a8b79a',grassDry='#b9c2a0',beachRun=.16,bankRun=.19),
 'season-look': dict(springGreen='#bfd2a0',autumnGrass='#b8b38b',leafYellow='#d4bb78',leafOrange='#c69e6a',leafRusset='#a96f53',paperWinter='#e7eae6',paperAutumn='#ebe7dc',paperGrey='#d9e0da'),
 'monuments': dict(towerEave=.19,pyramidRise=.43,coneRise=.48,spireRise=.85,archSpring=.24,archCrown=.13,parapet=.18,parapetThick=.08,hump=.25,archRing=.075,archRingOut=.018,archTint=0),
 'floor': dict(pathMargin=.11,pathRound=.13,pathFillet=.08,pathWobble=.012,plazaBorder=.09,verge=.17),
 'tree': dict(scale=1.38,jitter=.09,lean=.10,mixRound=.72,mixCypress=.13,shadeMix=.27),
 'wall': dict(thick=.2,height=.37,coping=.075,gardenHeight=.48,creepers=.55),
 'boats': dict(rowLength=.76,rowBeam=.24,fishLength=1.14,fishBeam=.38,mast=.82),
 'stall': dict(ridgeY=.84,frontY=.66,backY=.66,valance=.055,askew=.015),
}
HOUSES = [
 ('Harbour','临水民居','粉墙灰瓦，木门临水',5,1,'square','plank'),
 ('Thatch','乡间瓦舍','浅灰粉墙，低坡瓦顶',2,2,'shuttered','plank'),
 ('Tudor','沿街民居','灰瓦宽檐，方窗木门',0,0,'square','plank'),
 ('Manor','深宅大院','白墙黛瓦，规整高窗',5,4,'tall','panel'),
 ('Farm','田园民居','灰绿瓦顶，素木窗扇',4,3,'shuttered','plank'),
 ('Villa','河畔雅居','青灰瓦顶，素色立面',7,1,'square','panel'),
]
def literal(v):
    if isinstance(v,list): return '['+','.join(map(literal,v))+']'
    if isinstance(v,str): return '`'+v+'`'
    return str(v)

def apply(root):
    root=Path(root); seen={k:0 for k in STYLES}; house_count=0
    for p in (root/'assets').glob('*.js'):
        s=p.read_text(encoding='utf-8'); old=s
        for name,values in STYLES.items():
            pattern=r'`'+re.escape(name)+r'`,\{([^{}]+)\}'
            def replace(m):
                body=m.group(1)
                for k,v in values.items():
                    body,n=re.subn(r'(?<!\w)'+k+r':(?:`[^`]*`|\[[^\]]*\]|-?\d*\.?\d+)',lambda _:k+':'+literal(v),body)
                    if n!=1: raise ValueError(f'{name}.{k}: {n} matches')
                seen[name]+=1
                return m.group(0).replace(m.group(1),body,1)
            s=re.sub(pattern,replace,s)
        # Match the exact six style records, maintaining their original order and numeric IDs.
        for en,zh,hint,wall,roof,family,door in HOUSES:
            pattern=r'\{name:`'+re.escape(en)+r'`,wall:\d+,hint:`[^`]*`,roof:\d+,(?:roofFor:\{[^{}]*\},)?cover:`[^`]*`,family:`[^`]*`,door:`[^`]*`,accent:\[[^\]]*\],accent2:`[^`]*`,trim:`[^`]*`,storeyBands:![01],timberGable:![01],plankUpper:![01],walls:(?:null|`[^`]*`),chimney:\{stack:`[^`]*`,pots:\d+\}\}'
            record='{name:'+literal(zh)+',wall:'+str(wall)+',hint:'+literal(hint)+',roof:'+str(roof)+',cover:`shingles`,family:'+literal(family)+',door:'+literal(door)+',accent:[`wood`,`metal`,`redDark`],accent2:`redDark`,trim:`wood`,storeyBands:!1,timberGable:!1,plankUpper:!1,walls:null,chimney:{stack:`plaster`,pots:1}}'
            s,n=re.subn(pattern,lambda _:record,s); house_count+=n
        if s!=old: p.write_text(s,encoding='utf-8')
    if any(v!=1 for v in seen.values()) or house_count!=6:
        raise ValueError(f'Unexpected bundle layout: {seen}, house styles={house_count}')
    for p in list((root/'assets').glob('*.css'))+list(root.rglob('*.html')):
        s=p.read_text(encoding='utf-8');p.write_text(s.replace('#f2ede3','#e9eae2').replace('#3a2f2a','#38433f'),encoding='utf-8')
    print(json.dumps({'style_groups':seen,'house_styles':house_count},ensure_ascii=False))
if __name__=='__main__':apply(sys.argv[1] if len(sys.argv)>1 else 'dist')
