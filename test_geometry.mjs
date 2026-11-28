import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const assets=path.resolve(process.argv[2]||'dist','assets');
const bundle=fs.readdirSync(assets).find(x=>x.startsWith('field-basketball.scenario-')&&x.endsWith('.js'));
const saveFile=fs.readdirSync(assets).find(x=>x.startsWith('save-')&&x.endsWith('.js'));
const tmp=path.join(assets,'.jiangnan-test.mjs');
try{
fs.writeFileSync(tmp,fs.readFileSync(path.join(assets,bundle),'utf8')+'\nexport {B as MeshBuilder,tp as roofField,np as emitRoof,ns as rowboat,Yv as lantern,jiangnanMoonGate as moonGate,Qb as windowPart,Vi as resident,Hi as guard,Zi as residentParts,aa as rig,ra as pose,$i as assemble,lg as towerCap,hb as chimney,jiangnanPavilionHeight as pavilionHeight};\n');
const m=await import(pathToFileURL(tmp));const save=await import(pathToFileURL(path.join(assets,saveFile)));
const valid=(label,mesh)=>{assert(mesh.position.length>0,label);assert(mesh.position.length%9===0,label+' triangle count');assert(mesh.position.every(Number.isFinite),label+' position');assert(mesh.normal.every(Number.isFinite),label+' normal');console.log(label+': '+mesh.position.length/9+' triangles');};
const b=new m.MeshBuilder();m.moonGate(b,.24,.32);valid('moon gate',b.build());
const l=new m.MeshBuilder();assert(Math.abs(m.lantern(l,.2)-.125)<1e-9);valid('red lantern',l.build());
const ctx={seed:123,rand:()=>.5,mesh:()=>new m.MeshBuilder()};valid('rowboat canopy',m.rowboat.build({params:{look:1}},ctx).mesh);valid('lattice window',m.windowPart.build({variant:'tall'},ctx).mesh);
const canalBoat=m.rowboat.build({params:{look:1,canal:true}},ctx).mesh;
valid('canal boat canopy',canalBoat);
const riverWindow=m.windowPart.build({variant:'river-lattice',cell:save.U(12,1,12)}, {...ctx,rand:()=>.1});
valid('riverview lattice and lantern',riverWindow.mesh);
assert(riverWindow.anchors.window.every(Number.isFinite));
const tall=m.windowPart.build({variant:'tall'},ctx),square=m.windowPart.build({variant:'square'},ctx);
assert.notDeepEqual(tall.mesh.position,square.mesh.position);
assert(tall.anchors.window.every(Number.isFinite));
assert(square.anchors.window.every(Number.isFinite));
const key=save.U(12,1,12), input={cells:[key],mode:(_,d)=>d===0||d===2?'eave':'rake',base:1.6,rise:[.38,.64,.88],lift:0,sag:0,tilt:0,eave:.105,rake:.085,into:.09};const old=m.roofField(input), f=m.roofField({...input,jiangnan:true});assert(f.heightAt(key,12.5,11.9)>old.heightAt(key,12.5,11.9));assert(f.heightAt(key,12.5,12.25)<old.heightAt(key,12.5,12.25));assert.equal(f.heightAt(key,12.5,12.5),old.heightAt(key,12.5,12.5));const r=new m.MeshBuilder();m.emitRoof(r,f,{color:'#414b49',pattern:0,ink:'roof',thick:.06,fascia:'#414b49',fasciaInk:'edge'});valid('curved roof',r.build());
assert(f.heightAt(key,12,11.9)-old.heightAt(key,12,11.9)>f.heightAt(key,12.5,11.9)-old.heightAt(key,12.5,11.9));
const tower=new m.MeshBuilder();const anchors=m.towerCap(tower,.33,{roof:'#414b49',vary:.5});
valid('layered tower eaves',tower.build());assert(anchors['tower-top'].every(Number.isFinite));
const vent=m.chimney.build({variant:'plain'},ctx);
valid('low stove vent',vent.mesh);assert(vent.anchors['chimney-top'][13] < .2);
const octagon=[[0,0],[1,0],[2,1],[2,2],[1,3],[0,3],[-1,2],[-1,1]];
assert(m.pavilionHeight(1,.4,0,octagon[0],octagon)>m.pavilionHeight(1,.4,0,[.5,0],octagon)+.1);

const outfits=new Map();
for(let seed=1;seed<=40;seed++)for(const child of [false,true]){
  const look=m.resident(seed,child);
  if(!outfits.has(look.jiangnan))outfits.set(look.jiangnan,look);
  assert.deepEqual(look,m.resident(seed,child));
}
assert.deepEqual([...outfits.keys()].sort(),['apron','child-tunic','child-wrap','jacket','reed-hat','skirt']);
outfits.set('guard',m.guard(4,'#694339'));
const bodies=new Set();
for(const [style,look] of outfits){
  const parts=m.residentParts(look,311);
  bodies.add(JSON.stringify(parts.body.position));
  assert.deepEqual(Object.keys(parts).sort(),['armL','armR','body','legL','legR']);
  for(const action of ['stand','walk','sit','fish','carry']){
    const rig=m.rig(look,m.pose(action,.19));
    const mesh=m.assemble(parts,[0,1,2,3,4].map(i=>rig.subarray(i*16,i*16+16)),new m.MeshBuilder()).build();
    assert(mesh.position.length>0 && mesh.position.every(Number.isFinite),`${style} / ${action}`);
    assert(mesh.normal.every(Number.isFinite),`${style} / ${action}`);
    assert(mesh.position.every(value=>Math.abs(value)<.75),`${style} / ${action} fit`);
  }
  const triangles=Object.values(parts).reduce((total,part)=>total+part.position.length/9,0);
  assert(triangles<620,`${style}: ${triangles} triangles`);
  console.log(`${style}: ${triangles} triangles, rigged stand/walk/sit/fish/carry`);
}
assert.equal(bodies.size,outfits.size);
const reed=outfits.get('reed-hat');
assert(m.residentParts(reed,1).body.position.length>m.residentParts({...reed,hat:'none'},1).body.position.length);
const world={version:1,seed:17,nextSeq:7,blocks:new Map(Array.from({length:6},(_,i)=>[save.U(10+i,1,10),{kind:'house',color:i,rot:0,seq:i+1,style:i+1}])),floors:new Map([[save.U(10,1,11),'path']]),edges:new Map()};const encoded=save.r(world);const decoded=save.n(encoded);assert(decoded.ok);assert.deepEqual(decoded.world.blocks,world.blocks);assert.deepEqual(decoded.world.floors,world.floors);console.log('six style IDs and path round-trip: pass');
}finally{fs.rmSync(tmp,{force:true});}
