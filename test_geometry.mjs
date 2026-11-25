import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const assets=path.resolve(process.argv[2]||'dist','assets');
const bundle=fs.readdirSync(assets).find(x=>x.startsWith('field-basketball.scenario-')&&x.endsWith('.js'));
const saveFile=fs.readdirSync(assets).find(x=>x.startsWith('save-')&&x.endsWith('.js'));
const tmp=path.join(assets,'.jiangnan-test.mjs');
try{
fs.writeFileSync(tmp,fs.readFileSync(path.join(assets,bundle),'utf8')+'\nexport {B as MeshBuilder,tp as roofField,np as emitRoof,ns as rowboat,Yv as lantern,jiangnanMoonGate as moonGate,Qb as windowPart};\n');
const m=await import(pathToFileURL(tmp));const save=await import(pathToFileURL(path.join(assets,saveFile)));
const valid=(label,mesh)=>{assert(mesh.position.length>0,label);assert(mesh.position.length%9===0,label+' triangle count');assert(mesh.position.every(Number.isFinite),label+' position');assert(mesh.normal.every(Number.isFinite),label+' normal');console.log(label+': '+mesh.position.length/9+' triangles');};
const b=new m.MeshBuilder();m.moonGate(b,.24,.32);valid('moon gate',b.build());
const l=new m.MeshBuilder();assert(Math.abs(m.lantern(l,.2)-.125)<1e-9);valid('red lantern',l.build());
const ctx={seed:123,rand:()=>.5,mesh:()=>new m.MeshBuilder()};valid('rowboat canopy',m.rowboat.build({params:{look:1}},ctx).mesh);valid('lattice window',m.windowPart.build({variant:'tall'},ctx).mesh);
const key=save.U(12,1,12), input={cells:[key],mode:(_,d)=>d===0||d===2?'eave':'rake',base:1.6,rise:[.38,.64,.88],lift:0,sag:0,tilt:0,eave:.105,rake:.085,into:.09};const old=m.roofField(input), f=m.roofField({...input,jiangnan:true});assert(f.heightAt(key,12.5,11.9)>old.heightAt(key,12.5,11.9));assert(f.heightAt(key,12.5,12.25)<old.heightAt(key,12.5,12.25));assert.equal(f.heightAt(key,12.5,12.5),old.heightAt(key,12.5,12.5));const r=new m.MeshBuilder();m.emitRoof(r,f,{color:'#414b49',pattern:0,ink:'roof',thick:.06,fascia:'#414b49',fasciaInk:'edge'});valid('curved roof',r.build());
const world={version:1,seed:17,nextSeq:7,blocks:new Map(Array.from({length:6},(_,i)=>[save.U(10+i,1,10),{kind:'house',color:i,rot:0,seq:i+1,style:i+1}])),floors:new Map([[save.U(10,1,11),'path']]),edges:new Map()};const encoded=save.r(world);const decoded=save.n(encoded);assert(decoded.ok);assert.deepEqual(decoded.world.blocks,world.blocks);assert.deepEqual(decoded.world.floors,world.floors);console.log('six style IDs and path round-trip: pass');
}finally{fs.rmSync(tmp,{force:true});}
