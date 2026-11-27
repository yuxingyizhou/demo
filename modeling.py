"""Connect original Jiangnan meshes to the pinned renderer's mesh and rig entry points."""
from pathlib import Path
import shutil


def apply(root):
    assets = Path(root) / 'assets'
    bundle, = assets.glob('field-basketball.scenario-*.js')
    source = bundle.read_text(encoding='utf-8')

    def replace(label, before, after):
        nonlocal source
        count = source.count(before)
        if count != 1:
            raise ValueError(f'{label}: expected one mesh anchor, found {count}')
        source = source.replace(before, after, 1)

    replace('dwelling features', 'floorAt:o,edgeAt:s,supports:c},n.rules??HU(),n)',
            'floorAt:o,edgeAt:s,supports:c},jiangnanDwellingRules(n.rules??HU()),n)')
    replace('canal traffic', 'function GW(e,t={}){return HW(e,FU(e,t.rules??HU(),{buildNav:rO},t))}',
            'function GW(e,t={}){return HW(e,FU(e,jiangnanWaterRules(e.world,'
            'jiangnanDwellingRules(t.rules??HU())),{buildNav:rO},t))}')
    replace('canal moorings', '!n[p(c+a,l+o)]&&!r(c+a,l+o)||[.7,1.1,1.5].some',
            '!jiangnanIsWaterTown(e.world)&&!n[p(c+a,l+o)]&&!r(c+a,l+o)||[.7,1.1,1.5].some')

    replace('resident style', 's=n(`hat`),c=s<.14?`straw`:s<.24?`cap`:s<.3?`bobble`:`none`;return{skin:Bi(wr.skin,n(`skin`))',
            'outfit=jiangnanOutfit(n(`clothing`),t);return{jiangnan:outfit,skin:Bi(wr.skin,n(`skin`))')
    replace('resident hat state', 'hairStyle:o,hat:c,hatColor:Bi(wr.hats',
            'hairStyle:o,hat:outfit===`reed-hat`?`straw`:`none`,hatColor:Bi(wr.hats')
    replace('resident hair tones', 'hair:[`#4a3a34`,`#6b4a34`,`#2f2b33`,`#b98a52`,`#d8b46a`,`#9c5a3c`,`#e4dfd6`,`#c96a4a`]',
            'hair:[`#332e29`,`#4f3a30`,`#2d2929`,`#5f5042`,`#4a413a`,`#685044`,`#a6a19a`,`#43332d`]')
    replace('guard style', 'return{...Vi(e,!1),top:t,bottom:i.metal,',
            'return{...Vi(e,!1),jiangnan:`guard`,top:t,bottom:i.metal,')
    replace('animated resident mesh', 'function Zi(e,t){let n=Wi(e),r=e=>',
            'function Zi(e,t){let n=Wi(e);if(e.jiangnan)return jiangnanResident(()=>new B({ink:t}),'
            '{profile:Yr,ball:Jr,scale:ot},e,n);let r=e=>')
    replace('rower hat',
            'n.with({color:l(wr.hats,`hat`),ink:`rower-hat`},()=>{Ya(n,0,s+.165,f+.004,.05,.008,.05,10,3),Ya(n,0,s+.178,f+.004,.028,.02,.028,8,4)})',
            'n.at(F(0,0,f+.004),()=>jiangnanReedHat(n,Yr,s+.161,.063))')

    replace('roof section', 'i<0?Math.min(.065,-i*.55):-.24*v*d*o*(1-o)',
            'jiangnanRoofLift(i,d,v,o,c,e.hardGable)')
    replace('roof silhouette',
            'if(g===`stepped-gable`&&u!==1)g=`gable`;if(g===`gable`&&u===1&&o!==`chapel`&&o!==`barn`&&o!==`greenhouse`&&r.rectangular&&r.pierced.length===0)g=`stepped-gable`;',
            'if(g===`stepped-gable`)g=`gable`;'
            'if(g===`hip`&&r.rectangular&&r.pierced.length===0&&!['
            '`chapel`,`greenhouse`,`manor`,`town-hall`].includes(o))g=`gable`;'
            'if(g===`gable`&&r.rectangular&&r.pierced.length===0&&'
            '![`chapel`,`barn`,`greenhouse`].includes(o)&&'
            '(u===1&&s||u===2&&jiangnanIsWaterTown(n.facts.world)&&[`inn`,`shop`].includes(o))&&'
            'k(a.seed,`fire-gable`,r.index)<.4)g=`stepped-gable`;')
    replace('hard-gable roof profile', 'p=tp({cells:m,mode:u,jiangnan:s.cover!==`glass`&&v!==`lean-to`,base:g-ge.eaveDrop,pitch:v===`lean-to`?ge.leanRise:void 0,',
            'hardGable=v===`gable`&&c!==`chapel`&&s.cover!==`glass`,p=tp({cells:m,mode:u,hardGable,'
            'jiangnan:s.cover!==`glass`&&v!==`lean-to`,base:g-ge.eaveDrop,'
            'pitch:v===`lean-to`?ge.leanRise:hardGable ? .46 : void 0,')
    replace('straight roof ridges', 'sag:Math.min(ge.sagMax,ge.sag*f),tilt:s.lean*.025,',
            'sag:hardGable?0:Math.min(ge.sagMax,ge.sag*f),tilt:hardGable?0:s.lean*.025,')
    replace('close tile ends to gable', 'eave:ge.eave,rake:ge.rake,into:ge.inset+.005',
            'eave:ge.eave,rake:hardGable?0:ge.rake,into:ge.inset+.005')
    replace('render plaster hard gable', 'o.at(R(s,F(0,i-c(n.cell)*h,0)),()=>{if(!a){let e=[u,0,d];',
            'const hardGable=t.input.hardGable&&t.mode(n.cell,n.dir)===`rake`&&r>0;'
            'o.at(R(s,F(0,i-c(n.cell)*h,0)),()=>{if(hardGable)'
            'return jiangnanHardGable(o,f,u,d,r,l.color,z.plaster,z.shingles);'
            'if(!a){let e=[u,0,d];')
    replace('roof normals', 'e.tri(y,b,x,S===void 0?{normals:[_,_,_]}:{normals:[_,_,_],colors:[S,S,S]})',
            'let N=t.input.jiangnan?jiangnanRoofNormal(y,b,x,_):_;'
            'e.tri(y,b,x,S===void 0?{normals:[N,N,N]}:{normals:[N,N,N],colors:[S,S,S]})')
    replace('tile ends', 'c(i,v(r,p),v(.5,p)),c(i,v(.5,p),v(1-a,p)),s(i,v(u,0)',
            'c(i,v(r,p),v(.5,p)),c(i,v(.5,p),v(1-a,p)),'
            't.input.jiangnan&&d===`eave`&&jiangnanTileEnds(e,(along,overhang,offset)=>{'
            'let [x,z]=v(along,p+overhang);return [x,t.heightAt(i,x,z)+offset,z]},r,1-a,n.fascia),'
            's(i,v(u,0)')
    replace('tall lattice',
            'n.with({color:`#705745`,ink:`lattice`},()=>{for(let j of [1/3,2/3]){fs(n,e+(t-e)*j,r,e+(t-e)*j,i,.015,c);fs(n,e,r+(i-r)*j,t,r+(i-r)*j,.015,c)}})',
            'jiangnanLattice(n,fs,e,t,r,i,c,`grid`)')
    replace('square lattice', 'd(as(.33,.37,e),.042,(e,t,r,i)=>{fs(n,0,r,0,i,.022,c),fs(n,e,(r+i)/2,t,(r+i)/2,.022,c)})',
            'd(as(.33,.37,e),.042,(e,t,r,i)=>jiangnanTimberFront(n,fs,0,r,t-e,i-r,c))')
    replace('window forms', 'f=(e,n,i)=>{let a=t.feature({type:`window`,structure:r.id,cell:e,dir:n,variant:i}),o=i===`shopfront`?',
            'f=(e,n,variant)=>{if(i!==`chapel`&&variant===`round`)return;'
            'if(i!==`chapel`&&i!==`barn`&&n!==d?.dir&&gableEnds.get(e&4095)?.has(n))return;'
            'const form=i!==`chapel`&&i!==`barn`&&[`bay`,`arched`,`pointed`,`shuttered`].includes(variant)?`tall`:variant;'
            'let a=t.feature({type:`window`,structure:r.id,cell:e,dir:n,variant:form}),o=form===`shopfront`?')
    replace('identify blank gable ends', 'dir:n})},p=pk(n.facts),h=new Set;',
            'dir:n})},p=pk(n.facts),h=new Set,gableEnds=new Map;'
            'for(const region of Hf(n.facts).byStructure.get(r.id)??[]){'
            'const roof=YA(n.plan,region);if(!roof||![`gable`,`stepped-gable`].includes(roof.variant))continue;'
            'const cells=new Set(region.cells),ends=roof.params?.ridge===`x`?[1,3]:[0,2];'
            'for(const cell of cells){const dirs=ends.filter(dir=>!cells.has(M(cell,dir)));'
            'if(dirs.length)gableEnds.set(cell&4095,new Set(dirs))}}')
    replace('shop lattice', 'fs(n,.13,.16,.13,.47,.022,.052),n.with({color:r.accent,ink:`board`}',
            'jiangnanTimberFront(n,fs,.13,.16,.46,.31,.056),n.with({color:r.accent,ink:`board`}')
    replace('full shop window panels', 'd(as(.74,.39,e+.13),.04,(e,t,r,i)=>{fs(n,e+(t-e)/3,r,e+(t-e)/3,i,.022,c),fs(n,e+(t-e)*2/3,r,e+(t-e)*2/3,i,.022,c)})',
            'd(as(.74,.39,e+.13),.04,(e,t,r,i)=>jiangnanTimberFront(n,fs,0,r,t-e,i-r,c))')
    awning = source.index('prop:`awning`,build(e,t){')
    awning_end = source.index('}),fb=P({default:()=>pb})', awning)
    replace('tiled shop awning', source[awning:awning_end],
            'prop:`awning`,build(e,t){let n=t.mesh();jiangnanTiledAwning(n,z.shingles);return{mesh:n.build()}}')
    stall = source.index('function Hm(e,t){')
    stall_end = source.index('function Um(e,t){', stall)
    replace('tiled market stall', source[stall:stall_end],
            'function Hm(e){e.rigid(()=>jiangnanTiledStall(e.b,Ud.halfWidth,'
            '[Ud.backY,Ud.backZ],[Ud.ridgeY,Ud.ridgeZ],[Ud.frontY,Ud.frontZ],z.shingles))}')
    replace('entry frame', 'if(n.setColor(r.trim).setInk(`frame`),a===`double`)',
            'const role=t.structure&&t.plan.roles.get(t.structure.id)?.role;'
            'if(a===`shop`||a===`double`&&s&&[`town-hall`,`manor`,`inn`,`schoolhouse`].includes(role))'
            'jiangnanEntry(n,r.roofColor,a,z.shingles);'
            'if(n.setColor(r.trim).setInk(`frame`),a===`double`)')
    replace('stove vent', 'a=e.variant??`plain`,o=.32;if(a===`pipe`)',
            'a=e.variant??`plain`,o=.32;'
            'if(a===`plain`){jiangnanStoveVent(n,z.shingles);return {mesh:n.build(),anchors:{"chimney-top":F(0,.14,0)}}}'
            'if(a===`pipe`)')
    replace('short roof vents along the canal', 'c=!s&&o>=1&&o<=2&&n.rand(`flue`,e)<.6&&v++===0,',
            'c=!s&&!jiangnanIsWaterTown(n.facts.world)&&o>=1&&o<=2&&n.rand(`flue`,e)<.6&&v++===0,')
    replace('omit canal maypole', 'for(let e of m)if(o.put({type:`maypole`',
            'if(!jiangnanIsWaterTown(e.world))for(let e of m)if(o.put({type:`maypole`')

    replace('pavilion field', 'let s=.045,c=e=>r+e*t.pitch+.06*Math.exp(-Math.max(0,e)*5),l=i??1/0;',
            'let s=.045,outline=sm(t.outline,n),corners=t.round||t.hubs.length===1?outline:[],'
            'c=(h,p)=>jiangnanPavilionHeight(r,t.pitch,h,p,corners),l=i??1/0;')
    replace('pavilion roof points', 'i<=l+1e-9&&t.push([n[0],c(i),n[1]]),',
            'i<=l+1e-9&&t.push([n[0],c(i,n),n[1]]),')
    replace('octagonal roof segments', 'for(let e=0;e<n.length;e++)i.push({p:[r,n[e],n[(e+1)%n.length]],h:[1+t,0,0]});return i',
            'for(let e=0;e<n.length;e++){let a=n[e],b=n[(e+1)%n.length],m=[(a[0]+b[0])/2,(a[1]+b[1])/2];'
            'i.push({p:[r,a,m],h:[1+t,0,0]},{p:[r,m,b],h:[1+t,0,0]})}return i')
    replace('pavilion roof clipping', 't.push([n[0]+(a[0]-n[0])*e,c(l),n[1]+(a[1]-n[1])*e])',
            'let p=[n[0]+(a[0]-n[0])*e,n[1]+(a[1]-n[1])*e];t.push([p[0],c(l,p),p[1]])')
    replace('pavilion fascia', 'let i=sm(t.outline,n);for(let t=0;t<i.length;t++){let n=i[t],a=i[(t+1)%i.length];e.quad([a[0],r-s,a[1]],[n[0],r-s,n[1]],[n[0],c(0),n[1]],[a[0],c(0),a[1]])}',
            'for(let t=0;t<outline.length;t++){let n=outline[t],a=outline[(t+1)%outline.length];'
            'let m=[(n[0]+a[0])/2,(n[1]+a[1])/2];'
            'for(let [first,last] of [[n,m],[m,a]])'
            'e.quad([last[0],r-s,last[1]],[first[0],r-s,first[1]],'
            '[first[0],c(0,first),first[1]],[last[0],c(0,last),last[1]])}')
    replace('pavilion ridge points', '_=c(s),v=c(o),y=u*t.pitch*.9+.004',
            '_=c(s,n),v=c(o,i),y=u*t.pitch*.9+.004')
    replace('tower cap',
            'return e.with({color:n.roof,pattern:z.shingles,ink:`roof`},()=>e.lathe([[t+i-.01,0],[a,-.015],[a,.03],[a*.74,o*.2],[a*.46,o*.5],[a*.2,o*.8],[0,o]],{segments:18})),og(sg(e,o-.01))',
            'return jiangnanTowerEaves(e,a/1.38,o,n.roof,z.shingles),og(sg(e,o-.01))')

    for module in ('buildings', 'people'):
        shutil.copyfile(Path(__file__).with_name(f'{module}.mjs'), assets / f'jiangnan-{module}.mjs')
    bundle.write_text('import {waterTownRules as jiangnanWaterRules,isWaterTown as jiangnanIsWaterTown} from "./water-town.mjs";\n'
                      'import {roofLift as jiangnanRoofLift,roofNormal as jiangnanRoofNormal,'
                      'tileEnds as jiangnanTileEnds,lattice as jiangnanLattice,entryFrame as jiangnanEntry,'
                      'dwellingRules as jiangnanDwellingRules,hardGable as jiangnanHardGable,'
                      'tiledAwning as jiangnanTiledAwning,tiledStall as jiangnanTiledStall,'
                      'timberShopFront as jiangnanTimberFront,'
                      'pavilionHeight as jiangnanPavilionHeight,towerEaves as jiangnanTowerEaves,'
                      'stoveVent as jiangnanStoveVent} '
                      'from "./jiangnan-buildings.mjs";\n'
                      'import {outfit as jiangnanOutfit,residentMeshes as jiangnanResident,'
                      'reedHat as jiangnanReedHat} from "./jiangnan-people.mjs";\n' + source, encoding='utf-8')

    pointer, = assets.glob('pointer-*.js')
    source = pointer.read_text(encoding='utf-8')
    replace('bargeman clothing', 'dress:!1,hat:`straw`,hatColor:G.yellow,top:gr.roof[3]',
            'jiangnan:`reed-hat`,dress:!1,hat:`straw`,hatColor:G.yellow,top:gr.roof[3]')
    replace('sailor clothing', 'a={...i,dress:!1,top:r%2==0?G.white:gr.roof[1]',
            'a={...i,jiangnan:r%2==0?`jacket`:`apron`,dress:!1,top:r%2==0?G.white:gr.roof[1]')
    pointer.write_text(source, encoding='utf-8')
