// Explicit, bounded presets on the original engine. Dependencies injected for headless tests.
import {waterTown,waterTownSeed} from './water-town.mjs';
export const PRESETS=[{id:'canal',name:'枕水古镇',seed:waterTownSeed},{id:'village',name:'田园水村',seed:8},{id:'garden',name:'园林水镇',seed:163}];
export function presetPlan(id,api){
 const spec=PRESETS.find(x=>x.id===id);if(!spec)throw new Error('未知场景模板');
 if(id==='canal')return waterTown(spec,api);
 const seed=spec.seed,t=api.terrain(seed,2),base=api.grow(t,seed,{character:'river'});
 if(base.fellBack||base.refused||base.unjoined.length)throw new Error('基础场景规划未通过检查');
 const empty=()=>({version:1,seed,terrainGen:2,nextSeq:1,blocks:new Map(),floors:new Map(),edges:new Map()});
 let original=empty();for(const e of base.edits)original=api.apply(original,t,e);
 const shape=api.resolve(original,t),remove=new Set();
 for(const [cell,kind] of shape.kinds)if(['tower','windmill','lighthouse'].includes(kind))remove.add(cell);
 const rejected=[],edits=[];let world=empty();
 for(const source of base.edits){
  if(source.type==='placeBlock'&&remove.has(source.cell))continue;
  const e=source.type==='placeBlock'&&source.kind==='house'?{...source,style:[3,2,1,6,5,4,3,6][Number(source.color)%8]??1}:source;
  const check=api.can(world,t,e);if(!check.ok){rejected.push({edit:e,reason:check.reason});continue;}
  world=api.apply(world,t,e);edits.push(e);
 }
 const final=api.resolve(world,t),roles={};for(const {role} of final.roles.values())roles[role]=(roles[role]??0)+1;
 if(!roles['stone-bridge']||!roles.boathouse||!roles.shop||roles.chapel||roles.steeple||roles.lighthouse||roles.windmill||roles.keep)throw new Error('水乡模板关键构件不符合要求');
 return {seed, name:spec.name, plan:{...base,edits},audit:{removed:remove.size,skipped:rejected,roles,blocks:world.blocks.size,floors:world.floors.size,edges:world.edges.size},world,terrain:t};
}
