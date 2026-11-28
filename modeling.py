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
            'floorAt:o,edgeAt:s,supports:c},jiangnanWaterShapeRules(e,jiangnanDwellingRules(n.rules??HU())),n)')
    replace('canal traffic', 'function GW(e,t={}){return HW(e,FU(e,t.rules??HU(),{buildNav:rO},t))}',
            '''function GW(e,t={}){const rules=jiangnanWaterRules(e.world,jiangnanDwellingRules(t.rules??HU()));
            return HW(e,FU(e,jiangnanIsLanternTown(e.world)?[...rules,jiangnanFestivalActivities]:rules,{buildNav:rO},t))}
            const jiangnanFestivalActivities=q({id:`L99.lantern-market`,part:`life`,tier:3,priority:723,townWide:true,
              find:({plan})=>jiangnanLanternActivities(plan),
              apply(candidate, stage){const params={...candidate.data,y:h};
                stage.actor({type:`festival-market`,variant:params.kind,at:{cell:candidate.anchor,pos:`c`},params});
              }});''')
    replace('canal moorings', '!n[p(c+a,l+o)]&&!r(c+a,l+o)||[.7,1.1,1.5].some',
            '!jiangnanIsWaterTown(e.world)&&!n[p(c+a,l+o)]&&!r(c+a,l+o)||[.7,1.1,1.5].some')
    replace('tag canal boats', 'line:hr.line,rank:e.data.rank,',
            'line:hr.line,rank:e.data.rank,canal:jiangnanIsWaterTown(n.facts.world),festival:jiangnanIsLanternTown(n.facts.world),')
    replace('canal boat proportions', 'function es(){return{length:hr.rowLength,beam:hr.rowBeam,',
            'function es(canal=false,flower=false){return{length:hr.rowLength*(flower?1.92:canal?1.4:1),beam:hr.rowBeam*(flower?2.10:canal?1.42:1),')
    replace('canal boat hull', 'actor:`rowboat`,build(e,t){let n=t.mesh(),r=Qo(e.params?.look),a=jt(n,es(),r);',
            'actor:`rowboat`,build(e,t){let n=t.mesh(),r=Qo(e.params?.look),a=jt(n,es(e.params?.canal),r);')
    replace('festival lights on boats', 'n.with({ink:`oars`},()=>{let e=a.sheer(.5)-.014;',
            'e.params?.festival&&n.at(F(0,0,a.z(.20,.16)),()=>jiangnanBoatLantern(n,z.glow)),'
            'n.with({ink:`oars`},()=>{let e=a.sheer(.5)-.014;')
    replace('festive lamps travel with the rower', 'actor:`rower`,build(e,t){let n=t.mesh(),r=Qo(e.params?.look??0),a=jt(n,es(),r);',
            'actor:`rower`,build(e,t){let n=t.mesh(),r=Qo(e.params?.look??0),festival=e.params?.festival;'
            'if(festival)r={...r,topsides:`#b38357`,rail:`#a55638`,strake:`#d5ae6d`};'
            'let a=jt(n,es(e.params?.canal,festival),r);'
            'if(festival){jiangnanFlowerBoat(n,jiangnanFestivalMaterials());'
            'n.at(F(0,0,a.z(.17,.18)),()=>jiangnanBoatLantern(n,z.glow,true));'
            'n.at(F(0,-.02,a.z(.81,.18)),()=>jiangnanBoatLantern(n,z.glow))}')
    replace('festival boat procession route', 'joined by open water (at most two in the town).`,find({facts:e}){let t=[],n=fr(e),',
            'joined by open water (at most two in the town).`,find({facts:e}){'
            'if(jiangnanIsLanternTown(e.world)){'
            'const from=S(23,0,27),landing=S(jiangnanLanternLanding.x-1,0,jiangnanLanternLanding.z);'
            'const to=e.kinds.get(landing)===`dock`?landing:S(26,0,30),a=e.structureAt.get(from),b=e.structureAt.get(to);'
            'const [ax,az,bx,bz]=[25.5,24.2,25.5,30.2];'
            'return a!==void 0&&b!==void 0&&e.kinds.get(from)===`dock`&&e.kinds.get(to)===`dock`&&'
            'Ko(Uo(e),[ax,az],[bx,bz])?[{anchor:from,structure:a,key:`festival`,data:{a,b,ax,az,bx,bz}}]:[]}'
            'let t=[],n=fr(e),')
    replace('mark the moving festival boat', 'look:A(n.seed,`L20`,`look`,r.a)%8,ax:r.ax,',
            'look:A(n.seed,`L20`,`look`,r.a)%8,festival:jiangnanIsLanternTown(n.facts.world),'
            'canal:jiangnanIsLanternTown(n.facts.world),ax:r.ax,')
    replace('hang festival lamps on the market stalls',
            '()=>uh(r,{role:a,goods:Zd(o)??qd(t.world.seed,n),front:Qd(o)??2,seed:e.seed,color:e.color}));',
            '()=>{if(jiangnanIsLanternTown(t.world)){r.rotateY(Math.PI);'
            'jiangnanFestivalStall(r,jiangnanFestivalMaterials(),Jr,w(n)===30||w(n)===35)}'
            'else uh(r,{role:a,goods:Zd(o)??qd(t.world.seed,n),front:Qd(o)??2,seed:e.seed,color:e.color})});')
    replace('register festival market meshes', '"/src/parts/actors/boats/rower.part.ts":P_,',
            '"/src/parts/actors/boats/rower.part.ts":P_,"/src/parts/actors/jiangnan/market.part.ts":jiangnanFestivalActorModule,')
    replace('festival actor model recipes', 'var $o=P({default:()=>ns,rowboatBow:()=>ts,rowboatSpec:()=>es});',
            '''const jiangnanFestivalActorModule=P({default:()=>jiangnanMarketActor});
            const jiangnanMarketActor=Y({actor:`festival-market`,build(item,ctx){
              const mesh=ctx.mesh(),p=item.params,materials=jiangnanFestivalMaterials();
              if(item.variant===`turning`)jiangnanTurningLamp(mesh,materials);
              else if(item.variant===`wash`)jiangnanFestivalWash(mesh,p.walk,z.beam);
              else if(item.variant===`riddles`)jiangnanRiddleStand(mesh,materials);
              else {
                const child=item.variant===`child`, seller=item.variant===`seller`;
                const palette=[`#b96548`,`#c89d59`,`#8e5355`,`#557e72`,`#d29d70`];
                const person={...Vi(229+p.index*109,child),top:palette[p.index%palette.length],
                  ...(seller?{jiangnan:`apron`}:{})};
                const pose=ra(child?`carry`:seller||item.variant===`guest`?`carry`:item.variant===`riddle`?`read`:`look`,.24);
                const rig=aa(person,pose);
                mesh.at(ot(child?1.16:1.22),()=>{
                  $i(Zi(person,mesh.inkOf(`festival-visitor`)),[0,1,2,3,4].map(i=>rig.subarray(i*16,(i+1)*16)),mesh);
                  if(child){mesh.translate(.111,.133,.158);jiangnanRabbitLamp(mesh,materials,Jr)}
                  if(seller||item.variant===`guest`){mesh.translate(.071,0,.149);jiangnanFestivalBowl(mesh,.197,.069,z.stone)}
                });
              }
              return {mesh:mesh.build(),animated:true};
            }});
            var $o=P({default:()=>ns,rowboatBow:()=>ts,rowboatSpec:()=>es});''')
    replace('festival bridge gallery', 'ee=e=>l(w(e),f(e))?t.terrain.height[p(w(e),f(e))]:0;for(let e of o.values())',
            'ee=e=>l(w(e),f(e))?t.terrain.height[p(w(e),f(e))]:0;'
            'const bridge=jiangnanLandmarks.bridge;'
            'if(jiangnanIsLanternTown(t.world)&&t.roles.get(e.id)?.role===`stone-bridge`&&'
            'e.cells.some(cell=>w(cell)===bridge.x&&f(cell)===bridge.z)){'
            'const xs=e.cells.map(w),left=Math.min(...xs),right=Math.max(...xs)+1;'
            'r.at(F((left+right)/2,0,bridge.z+.5),()=>'
            'jiangnanCoveredBridge(r,right-left,h,u?Oc.hump:0,fe,jiangnanFestivalMaterials()))}'
            'for(let e of o.values())')
    replace('festival gate posts', 'o=e.cells[0],s=(t.featuresByStructure.get(e.id)??[]).find(e=>e.type===`pavilion-bay`);',
            'o=e.cells[0],s=(t.featuresByStructure.get(e.id)??[]).find(e=>e.type===`pavilion-bay`);'
            'const gate=jiangnanLandmarks.gate,post=f(o);'
            'if(jiangnanIsLanternTown(t.world)&&e.color===6&&c(o)===1&&w(o)===gate.x&&gate.posts.includes(post)){'
            'r.at(F(gate.x+.5,h,post+.5),()=>jiangnanGatePost(r,Math.abs(post-gate.z)===1?1.85:1.28,jiangnanFestivalMaterials()));'
            'if(post===gate.posts[0])r.at(R(F(gate.x+.5,h,gate.z+.5),L(Math.PI/2)),()=>'
            'jiangnanGateRoof(r,jiangnanFestivalMaterials()));return{mesh:r.build(),anchors:a}}')
    replace('festival octagonal pagoda', 'a={},o=yg(e,t),{storeys:s,round:l,foot:u,belfry:d,world:f}=o,',
            'a={},first=e.cells[0],tower=jiangnanLandmarks.tower;'
            'if(jiangnanIsLanternTown(t.world)&&e.color===6&&first>>12===1&&(first&63)===tower.x&&(first>>6&63)===tower.z){'
            'const root=F(tower.x+.5,h,tower.z+.5);'
            'r.at(root,()=>jiangnanPagoda(r,jiangnanFestivalMaterials(),Math.min(4,e.cells.length)));'
            'return{mesh:r.build(),anchors:a}}'
            'let o=yg(e,t),{storeys:s,round:l,foot:u,belfry:d,world:f}=o,')
    replace('stone canal landing', 'return fl(i,e,t),Ga(i,r,e,t,n,e=>e.type===`ladder`?null:void 0),',
            'const dock=jiangnanIsWaterTown(t.world)&&e.cells.length===1?al(e,t).get(e.cells[0]):null;'
            'const bank=dock&&Mo.find(dir=>dock.side[dir]===`land`);'
            'if(dock&&bank!==void 0)jiangnanStoneLanding(i,(across,depth)=>ol(dock,bank,across,-depth),h,fe,z.stone);'
            'else fl(i,e,t);return Ga(i,r,e,t,n,e=>e.type===`ladder`?null:void 0),')
    replace('pave the canal landing ramp', 'a=eb/$y;n.setPattern(z.none).setInk(`ramp`);',
            'a=eb/$y;if(jiangnanIsWaterTown(t.plan.world)&&t.structure?.kind===`dock`&&t.structure.cells.length===1){'
            'n.setPattern(z.stone).setInk(`stone-ramp`);'
            'for(const [left,right,color] of [[-.432,-.149,`#b3b4a8`],[-.146,.147,`#bcc0b4`],[.15,.432,`#aeb3a8`]])'
            'n.setColor(color).box([left,h-.018,-.09],[right,h+.021,.44],{skip:[`bottom`]});'
            'return{mesh:n.build()}}n.setPattern(z.none).setInk(`ramp`);')

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
            'if(g===`hip`&&r.rectangular&&r.pierced.length===0&&'
            '(jiangnanIsWaterTown(n.facts.world)||![`chapel`,`greenhouse`,`manor`,`town-hall`].includes(o)))g=`gable`;'
            'if(g===`gable`&&r.rectangular&&r.pierced.length===0&&'
            '![`chapel`,`barn`,`greenhouse`].includes(o)&&'
            '(u===1&&s||u<=3&&jiangnanIsWaterTown(n.facts.world)&&o!==`warehouse`)&&'
            'k(a.seed,`fire-gable`,r.index)<.33)g=`stepped-gable`;')
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
            'const [dx,dz]=j[n],river=canal&&Ro(facts,w(e)+dx,(e>>6&63)+dz);'
            'if(!river&&i!==`chapel`&&i!==`barn`&&n!==d?.dir&&gableEnds.get(e&4095)?.has(n))return;'
            'const form=river?`river-lattice`:i!==`chapel`&&i!==`barn`&&[`bay`,`arched`,`pointed`,`shuttered`].includes(variant)?`tall`:variant;'
            'let a=t.feature({type:`window`,structure:r.id,cell:e,dir:n,variant:form}),o=form===`shopfront`?')
    replace('identify blank gable ends', 'dir:n})},p=pk(n.facts),h=new Set;',
            'dir:n})},p=pk(n.facts),h=new Set,gableEnds=new Map,facts=n.facts,canal=jiangnanIsWaterTown(facts.world);'
            'for(const region of Hf(n.facts).byStructure.get(r.id)??[]){'
            'const roof=YA(n.plan,region);if(!roof||![`gable`,`stepped-gable`].includes(roof.variant))continue;'
            'const cells=new Set(region.cells),ends=roof.params?.ridge===`x`?[1,3]:[0,2];'
            'for(const cell of cells){const dirs=ends.filter(dir=>!cells.has(M(cell,dir)));'
            'if(dirs.length)gableEnds.set(cell&4095,new Set(dirs))}}')
    replace('river lattice facade', 'l=[0,t,r]};if(a===`tall`){let e=.2+o;',
            'l=[0,t,r]};if(a===`river-lattice`){'
            'us(n,as(.76,.43,.16),0,Xb);jiangnanRiverFront(n,z.planks,z.shingles);'
            'if(e.cell>>12===1&&t.rand(`river-lantern`)<.25){'
            'n.with({color:`#5d4437`,ink:`lantern-chain`},()=>n.box([.296,.54,.146],[.304,.618,.154]));'
            'n.at(F(.3,.355,.15),()=>Yv(n,.15))}l=[0,.16,.071]'
            '}else if(a===`tall`){let e=.2+o;')
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
    replace('occasional roof vents along the canal', 'if(d===l&&l>0&&u<1&&n.rand(`any`)>=u&&(d=0),d===0)return;',
            'if(jiangnanIsWaterTown(n.facts.world))d=n.rand(`any`)<.45?1:0;'
            'else if(d===l&&l>0&&u<1&&n.rand(`any`)>=u)d=0;if(d===0)return;')
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

    for module in ('buildings', 'people', 'festival'):
        shutil.copyfile(Path(__file__).with_name(f'{module}.mjs'), assets / f'jiangnan-{module}.mjs')
    bundle.write_text('import {waterTownRules as jiangnanWaterRules,waterTownShapeRules as jiangnanWaterShapeRules,'
                      'isWaterTown as jiangnanIsWaterTown,isLanternTown as jiangnanIsLanternTown,'
                      'lanternLandmarks as jiangnanLandmarks,lanternLanding as jiangnanLanternLanding,'
                      'lanternActivities as jiangnanLanternActivities} from "./water-town.mjs";\n'
                      'import {boatLantern as jiangnanBoatLantern,festivalStall as jiangnanFestivalStall,'
                      'rabbitLantern as jiangnanRabbitLamp,flowerBoat as jiangnanFlowerBoat,'
                      'turningLamp as jiangnanTurningLamp,festivalWash as jiangnanFestivalWash,'
                      'festivalBowl as jiangnanFestivalBowl,riddleStand as jiangnanRiddleStand,'
                      'coveredBridge as jiangnanCoveredBridge,'
                      'gatePost as jiangnanGatePost,gateRoof as jiangnanGateRoof,pagoda as jiangnanPagoda} from "./jiangnan-festival.mjs";\n'
                      'const jiangnanFestivalMaterials=()=>({tiles:z.shingles,wood:z.planks,stone:z.stone,glow:z.glow});\n'
                      'import {roofLift as jiangnanRoofLift,roofNormal as jiangnanRoofNormal,'
                      'tileEnds as jiangnanTileEnds,lattice as jiangnanLattice,entryFrame as jiangnanEntry,'
                      'dwellingRules as jiangnanDwellingRules,hardGable as jiangnanHardGable,'
                      'tiledAwning as jiangnanTiledAwning,tiledStall as jiangnanTiledStall,'
                      'timberShopFront as jiangnanTimberFront,riverFront as jiangnanRiverFront,'
                      'stoneLanding as jiangnanStoneLanding,'
                      'pavilionHeight as jiangnanPavilionHeight,towerEaves as jiangnanTowerEaves,'
                      'stoveVent as jiangnanStoveVent} '
                      'from "./jiangnan-buildings.mjs";\n'
                      'import {outfit as jiangnanOutfit,residentMeshes as jiangnanResident,'
                      'reedHat as jiangnanReedHat} from "./jiangnan-people.mjs";\n' + source, encoding='utf-8')

    pointer, = assets.glob('pointer-*.js')
    source = pointer.read_text(encoding='utf-8')
    replace('register movement for the lantern market actors', '"/src/life/boats/rower.behaviour.ts":bl,',
            '"/src/life/boats/rower.behaviour.ts":bl,"/src/life/jiangnan/market.behaviour.ts":jiangnanMarketBehaviourModule,')
    replace('animate market visitors and the rotating lantern', 'function ns(e){',
            '''const jiangnanMarketBehaviourModule=ot({default:()=>jiangnanMarketBehaviour});
            const jiangnanMarketBehaviour=ns({actor:`festival-market`,
              create(item,ctx){if(item.variant===`wash`)ctx.instance.setParams(.72,0,0,-2);
                return {elapsed:0, matrix:Array(16)};
              },
              update(state,dt,signals,ctx){
                const {kind,x,y,z,walk,index}=ctx.item.params;
                state.elapsed+=dt;
                let along=x,height=y, yaw=0,lean=0;
                if(kind===`wash`)ctx.instance.setParams(.72,0,0,-2);
                if(kind===`turning`)yaw=state.elapsed*.43;
                if(kind===`child`||kind===`stroll`){
                  const phase=state.elapsed*.78+index*.28;
                  along+=walk*(.5-.5*Math.cos(phase));
                  yaw=Math.sin(phase)>0?Math.PI/2:-Math.PI/2;
                  if(z>22&&z<23&&along>22&&along<27)height+=.25*Math.sin(Math.PI*(along-22)/5);
                  height+=.016*Math.abs(Math.sin(state.elapsed*13+index));
                }
                if(kind===`watch`)yaw=-1.3;
                if(kind===`riddle`)yaw=2.8+.15*Math.sin(state.elapsed+index);
                if(kind===`riddles`)yaw=Math.PI;
                if(kind===`seller`){yaw=1.12;lean=.15*Math.sin(state.elapsed*2.1)}
                if(kind===`guest`){yaw=3.4+.15*Math.sin(state.elapsed+index);lean=.035*Math.sin(state.elapsed*2)}
                ctx.instance.setMatrix(Oi(along,height,z,yaw,lean,0,1,state.matrix));
              }});
            function ns(e){''')
    replace('bargeman clothing', 'dress:!1,hat:`straw`,hatColor:G.yellow,top:gr.roof[3]',
            'jiangnan:`reed-hat`,dress:!1,hat:`straw`,hatColor:G.yellow,top:gr.roof[3]')
    replace('sailor clothing', 'a={...i,dress:!1,top:r%2==0?G.white:gr.roof[1]',
            'a={...i,jiangnan:r%2==0?`jacket`:`apron`,dress:!1,top:r%2==0?G.white:gr.roof[1]')
    replace('preserve lanterns when a boat casts off', 'l=e.spawn({actor:c,params:{look:a}},n),',
            'l=e.spawn({actor:c,params:{look:a,canal:t.params?.canal,festival:t.params?.festival}},n),')
    replace('begin the lantern procession early', 'rowing:!1,waitLeft:6+t.rand(`first`)*20,',
            'rowing:!1,waitLeft:e.params?.festival ? .28 : 6+t.rand(`first`)*20,')
    replace('read the procession flag before resolving coordinates',
            'changed(e,t){e.ends=Tl(t.item.params??{})},update(e,t,r,i){if(i.shape',
            'changed(e,t){e.ends=Tl(t.item.params??{})},update(e,t,r,i){const festival=i.item.params?.festival;if(i.shape')
    replace('row in the lantern festival at night', 'n=r.time.isDay&&e.water?T(e.water,[e.x,e.z],e.ends[t],.15):null;',
            'n=(r.time.isDay||festival)&&e.water?T(e.water,[e.x,e.z],e.ends[t],.15):null;')
    replace('festival boat turns at each end', 'e.waitLeft=Cl+i.rand(`wait`,e.waits++)*wl)',
            'e.waitLeft=festival?2.5:Cl+i.rand(`wait`,e.waits++)*wl)')
    replace('festival boat procession pace', 'e.leg+xl*(.45+1.1*n)*t*e.slow)',
            'e.leg+(festival?xl*1.35:xl)*(.45+1.1*n)*t*e.slow)')
    replace('festival percussion schedule', 'lastNote:-1,windAt:0,peal:null,off:[]',
            'lastNote:-1,windAt:0,peal:null,marketDrums:3.2,off:[]')
    replace('a short procession of market percussion', 'if(e.windAt-=t,e.windAt<=0)',
            '''if(e.shape&&jiangnanFestivalSound(e.shape.world)&&!a.isDay&&(e.marketDrums-=t)<=0){
              e.marketDrums=19;
              const when=i.ac.currentTime;
              for(const [delay,pitch,volume] of [[0,94,.041],[.27,132,.023],[.43,101,.031],[.79,90,.036]])
                Xg(i.ac,i.master,pitch,`plank`,volume,when+delay);
              Xg(i.ac,i.master,286,`bell`,.014,when+.83);
            }
            if(e.windAt-=t,e.windAt<=0)''')
    replace('moving festival light on water', '    } else if (pat == 11) {\n      // water on a side face',
            '''    } else if (pat == 41) {
      float ripple = sin(vW.z * 9.0 + vW.x * 11.0 - uTime * 3.2) * 0.5 + 0.5;
      float light = uGlow * (0.28 + ripple * 0.72);
      if (light < 0.12) discard;
      hatchable = 0.0;
      col = mix(shade(uSea, s), base, light);
      glow = light;
    } else if (pat == 11) {
      // water on a side face''')
    replace('warm light reaches the festival stone paving', '  } else if (vParams.w < -0.5) {',
            '''  } else if (vParams.w < -1.5) {
    float a = pow(clamp(1.0 - vEdge, 0.0, 1.0), 2.35) * max(vParams.x, 0.0) * (0.12 + 0.34 * uGlow);
    oColor = vec4(toSrgb(base) * a * 1.24, a * 0.54);
  } else if (vParams.w < -0.5) {''')
    pointer.write_text('import {isLanternTown as jiangnanFestivalSound} from "./water-town.mjs";\n' + source,
                       encoding='utf-8')
