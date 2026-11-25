// V5: three distinct native-edit districts. No new save types or fake placement APIs.
const layouts={
 canal:{name:'沿街集市',x:23,z:12,h:1,entry:'N',rows:['spps','gqqg','hqqh','pppp']},
 village:{name:'田园菜圃',x:30,z:32,h:1,entry:'N',rows:['ggpgg','ggpgg','ggpgg','ggpgg','hhphh']},
 garden:{name:'围合园林',x:11,z:14,h:1,entry:'E',rows:['ggggg','gttgg','gttpp','ggpgg','ggpgg']}
};
const key=(x,y,z)=>x+64*z+4096*y;
const dirs=[[0,-1],[1,0],[0,1],[-1,0]];
function edge(x,y,z,d){const k=key(x,y,z);return d===1?k*2:d===2?k*2+1:d===3?(k-1)*2:(k-64)*2+1;}
export function addDistrict(result,id,api){
 const spec=layouts[id];if(!spec)throw Error('未知街区');
 const {x,z,h,rows}=spec,w=rows[0].length,d=rows.length,t=result.terrain;let world=result.world,added=[];
 const occupied=new Set([...world.blocks.keys()].map(k=>k&4095));
 for(let j=0;j<d;j++)for(let i=0;i<w;i++){
  const cell=key(x+i,h,z+j),floor=world.floors.get(cell);
  if(t.height[x+i+(z+j)*48]!==h||occupied.has(cell&4095)||floor&&floor!=='garden')throw Error('街区占地冲突');
 }
 function edit(e){const c=api.can(world,t,e);if(!c.ok)throw Error('街区指令拒绝: '+JSON.stringify(e)+' '+c.reason);world=api.apply(world,t,e);added.push(e);}
 for(let j=0;j<d;j++)for(let i=0;i<w;i++){
  const cell=key(x+i,h,z+j),kind=rows[j][i],floor=world.floors.get(cell),want=kind==='p'?'path':kind==='q'?'plaza':kind==='g'?'garden':null;
  if(floor&&floor!==want)edit({type:'eraseFloor',cell});
  if(want&&floor!==want)edit({type:'placeFloor',cell,floor:want});
  if(kind==='s')edit({type:'placeBlock',cell,kind:'stall',color:0});
  if(kind==='h')edit({type:'placeBlock',cell,kind:'house',color:id==='canal'?(i===0?0:5):(i<2?2:7),style:id==='canal'?3:5});
  if(kind==='t'){edit({type:'placeBlock',cell,kind:'pillar',color:2});edit({type:'placeBlock',cell:cell+4096,kind:'pillar',color:2});}
 }
 for(let j=0;j<d;j++)for(let i=0;i<w;i++)if(rows[j][i]==='t')edit({type:'placeBlock',cell:key(x+i,h+2,z+j),kind:'marble',color:0});
 if(id==='garden')for(let j=0;j<d;j++)for(let i=0;i<w;i++)for(let k=0;k<4;k++){
  const [dx,dz]=dirs[k];if(i+dx>=0&&i+dx<w&&j+dz>=0&&j+dz<d)continue;
  if(rows[j][i]==='p')continue;const e=edge(x+i,h,z+j,k);if(!world.edges.has(e))edit({type:'placeEdge',edge:e,kind:'wall'});
 }
 const shape=api.resolve(world,t),roles={};for(const {role} of shape.roles.values())roles[role]=(roles[role]??0)+1;
 if(id==='garden'&&(roles.bandstand??0)<=(result.audit.roles.bandstand??0))throw Error('园林亭子没有形成');
 if(['chapel','steeple','lighthouse','windmill','keep'].some(k=>roles[k]))throw Error('街区引入了西式地标');
 return {...result,world,plan:{...result.plan,edits:[...result.plan.edits,...added]},audit:{...result.audit,roles,blocks:world.blocks.size,floors:world.floors.size,edges:world.edges.size,district:{name:spec.name,x,z,w,d,added:added.length,layout:rows}}};
}

// Place a complete 2x2 pavilion as a single preflighted native edit batch.
export function pavilionPlan(world,terrain,target,api){
 const fail=refusal=>({edits:[],world,at:target,refusal});
 if(!Number.isInteger(target)||target<0)return fail('请选择空旷平地');
 const x=target&63,z=(target>>6)&63,h=target>>12;
 if(x>=47||z>=47||h<1||h>28)return fail('需要至少 2×2 格平地');
 const cells=[target,target+1,target+64,target+65],columns=new Set(cells.map(c=>c&4095));
 if(cells.some(c=>terrain.height[(c&63)+((c>>6)&63)*48]!==h)||[...world.blocks.keys()].some(c=>columns.has(c&4095))||[...world.floors.keys()].some(c=>columns.has(c&4095)))return fail('凉亭需要 2×2 格无遮挡的同高空地');
 if([...world.edges.keys()].some(e=>{const c=e>>1;return columns.has(c&4095)||columns.has((c+(e&1?64:1))&4095)}))return fail('凉亭位置与围墙或栅栏冲突');
 const edits=[...cells.map(cell=>({type:'placeBlock',cell,kind:'pillar',color:2})),...cells.map(cell=>({type:'placeBlock',cell:cell+4096,kind:'pillar',color:2})),...cells.map(cell=>({type:'placeBlock',cell:cell+8192,kind:'marble',color:0}))];
 let next=world;for(const e of edits){const check=api.can(next,terrain,e);if(!check.ok)return fail('凉亭无法放置：'+check.reason);next=api.apply(next,terrain,e)}
 const shape=api.resolve(next,terrain),owner=shape.structureAt.get(target+8192);if(shape.roles.get(owner)?.role!=='bandstand')return fail('此处不能形成完整凉亭');
 return {edits,world:next,at:target,refusal:null};
}
export function navAudit(nav){
 const counts=new Map();for(const part of nav.part)counts.set(part,(counts.get(part)??0)+1);
 const [mainPart,main]=[...counts].sort((a,b)=>b[1]-a[1]||a[0]-b[0])[0]??[-1,0];
 const onMain=d=>d.node>=0&&nav.part[d.node]===mainPart;
 return {mainPart,main,navTotal:nav.nodes.length,doors:nav.doors.length,connectedDoors:nav.doors.filter(d=>d.node>=0).length,mainDoors:nav.doors.filter(onMain).length,mainEntrances:nav.doors.filter(d=>d.main).length,mainEntrancesReachable:nav.doors.filter(d=>d.main&&onMain(d)).length};
}
