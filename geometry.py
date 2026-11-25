"""Jiangnan v3 mesh patch for pinned af6eac24 release. Fail closed on changed anchors."""
from pathlib import Path
import sys, json

def apply(root):
    root=Path(root)
    p=next((root/'assets').glob('field-basketball.scenario-*.js'))
    s=p.read_text(encoding='utf-8')
    counts={}
    def patch(name,old,new):
        nonlocal s
        n=s.count(old)
        if n!=1: raise ValueError(f'{name}: expected 1, found {n}')
        s=s.replace(old,new,1)
        counts[name]=n
    patch('stepped_gables','}if(g===`gable`||g===`stepped-gable`){let e=o===`chapel`','}if(g===`gable`&&o!==`chapel`&&o!==`barn`&&o!==`greenhouse`&&r.rectangular&&r.pierced.length===0)g=`stepped-gable`;if(g===`gable`||g===`stepped-gable`){let e=o===`chapel`')
    patch('dark_coping','color:e.persona.trim,ink:`coping${n.cell*4+n.dir}`','color:`#414b49`,ink:`coping${n.cell*4+n.dir}`')
    patch('stepped_wall_height','f((t+n)/2))+.085','f((t+n)/2))+.135')
    patch('roof_opt_in','p=tp({cells:m,mode:u,base:g-ge.eaveDrop,','p=tp({cells:m,mode:u,jiangnan:s.cover!==`glass`&&v!==`lean-to`,base:g-ge.eaveDrop,')
    patch('roof_curve','return e.base+v*i-l};return{input:e,pitch:v,span:d,','return e.base+v*i-l+(e.jiangnan?(i<0?Math.min(.065,-i*.55):-.24*v*d*o*(1-o)):0)};return{input:e,pitch:v,span:d,')
    patch('wupeng_canopy','n.with({ink:`oars`},()=>{let e=a.sheer(.5)-.014;','n.with({color:`#353c39`,pattern:z.planks,ink:`wupeng-canopy`},()=>{let points=(u,k)=>{let y=a.sheer(u),w=Math.max(.025,a.inner(u,y-.015)-.007),q=Math.PI*k/8;return [Math.cos(q)*w,y+.012+Math.sin(q)*.14,a.z(u,y)]};for(let j=0;j<8;j++)n.quad(points(.28,j),points(.28,j+1),points(.72,j+1),points(.72,j));for(let u of [.28,.5,.72])n.with({color:`#665747`,ink:`canopy-rib`},()=>{let pts=[];for(let j=0;j<=8;j++)pts.push(points(u,j));K(n,pts,.009,{seg:3})})}),n.with({ink:`oars`},()=>{let e=a.sheer(.5)-.014;')
    patch('moon_gate_helper','var n_=za({kind:`wall`,build(e,t,n){','function jiangnanMoonGate(b,thick,r){let center=.13,outer=r+.095,angle=Math.asin(center/r),N=16;let point=(rad,q,depth)=>[Math.cos(q)*rad,Math.max(0,center+Math.sin(q)*rad),depth];for(let k=0;k<N;k++){let q=-angle+(Math.PI+2*angle)*k/N,v=-angle+(Math.PI+2*angle)*(k+1)/N,f=thick/2,g=-f;let a=point(r,q,f),c=point(r,v,f),d=point(outer,v,f),e=point(outer,q,f),A=point(r,q,g),C=point(r,v,g),D=point(outer,v,g),E=point(outer,q,g);b.quad(e,d,c,a);b.quad(A,C,D,E);b.quad(a,c,C,A);b.quad(E,D,d,e)}}var n_=za({kind:`wall`,build(e,t,n){')
    patch('moon_gate_usage','}else{let e=hl.archHalf;a.with({color:u,pattern:z.stone,ink:`gate`},()=>t_(a,e+.12,m+.108,e,hl.archSpring,`round`,!0)),','}else if(s===`garden-wall`){a.with({color:`#e9e7dc`,pattern:z.plaster,ink:`moon-gate`},()=>jiangnanMoonGate(a,m+.055,.32));}else{let e=hl.archHalf;a.with({color:u,pattern:z.stone,ink:`gate`},()=>t_(a,e+.12,m+.108,e,hl.archSpring,`round`,!0)),')
    patch('lattice_window','if(a===`tall`){let e=.2+o;d(as(.27,.46,e),.04,(e,t,r,i)=>fs(n,e,r+(i-r)*.52,t,r+(i-r)*.52,.022,c)),','if(a===`tall`){let e=.2+o;d(as(.27,.46,e),.04,(e,t,r,i)=>{n.with({color:`#705745`,ink:`lattice`},()=>{for(let j of [1/3,2/3]){fs(n,e+(t-e)*j,r,e+(t-e)*j,i,.015,c);fs(n,e,r+(i-r)*j,t,r+(i-r)*j,.015,c)}})}),')
    a=s.index('function Yv(e,t,n=`lantern`,r=i.metal){');b=s.index('function Xv(e,t,n=0,r=.012)',a)
    patch('red_lantern',s[a:b],'function Yv(e,t,n=`lantern`,r=i.metal){let a=t*.48;e.with({color:`#9c4034`,pattern:z.glow,ink:`${n}-glass`},()=>e.lathe([[a*.65,t*.15],[a*.94,t*.29],[a*1.12,t*.58],[a*1.04,t*.93],[a*.72,t*1.20]],{segments:12}));e.with({color:`#664e35`,pattern:z.none,ink:`${n}-cap`},()=>{e.lathe([[a*.72,t*.08],[a*.72,t*.17]],{segments:12,capBottom:!0});e.lathe([[a*.80,t*1.19],[a*.80,t*1.29],[a*.38,t*1.38]],{segments:12,capTop:!0});e.lathe([[t*.06,0],[t*.06,t*.09]],{segments:6})});return t*.625}')
    patch('pavilion_roof','function ym(e,t,n,r,i,a,o){let s=.045,c=e=>r+e*t.pitch,l=i??1/0;','function ym(e,t,n,r,i,a,o){let s=.045,c=e=>r+e*t.pitch+.06*Math.exp(-Math.max(0,e)*5),l=i??1/0;')
    patch('pavilion_fascia','e.quad([a[0],r-s,a[1]],[n[0],r-s,n[1]],[n[0],r,n[1]],[a[0],r,a[1]])','e.quad([a[0],r-s,a[1]],[n[0],r-s,n[1]],[n[0],c(0),n[1]],[a[0],c(0),a[1]])')
    a=s.index('var Nb=Y({prop:`hanging-sign`');b=s.index('Pb=P({default:()=>Fb})',a)
    old=s[a:b]
    new=old.replace('color:i.wood,ink:`board`','color:`#813e32`,ink:`board`').replace('color:i.white,ink:`board`','color:`#493c31`,ink:`board`').replace('u=r===`cafe`?i.redDark:c','u=`#e5bd77`')
    if old==new:raise ValueError('hanging plaque anchor changed')
    patch('lacquered_plaque',old,new)
    patch('wardrobe','tops:[`#e56b58`,`#6d8ccf`,`#ffd96e`,`#7cbf9b`,`#f4a3bf`,`#fdfaf3`,`#c6b2ff`,`#eaa65c`,`#9a92b8`,`#88c26b`]','tops:[`#a15d4d`,`#627d80`,`#c1a16c`,`#7b9276`,`#b08e87`,`#e8e2d2`,`#8e9398`,`#9e7b57`,`#716b79`,`#8d9b77`]')
    p.write_text(s,encoding='utf-8')
    app=next((root/'assets').glob('app-*.js'))
    s=app.read_text(encoding='utf-8')
    patch('drag_house_style','kind:r.kind,color:z.color,from:null}', 'kind:r.kind,color:z.color,from:null,...r.style===void 0?{}:{style:r.style}}')
    patch('welcome_hint','Here is a town to start you off. Build on it, change it, or begin with an empty island.','在小镇上继续建造，或从空岛开始。选中房屋后，电脑悬停或手机长按可选样式；再次点击已选工具可进入观察模式。')
    patch('grow_hint','a(`p`,{text:`What kind of town?`}),t===`new`?p():null','a(`p`,{text:`选择小镇类型`}),a(`small`,{text:`推荐河畔小镇：临水民居、石桥、码头与灯笼。`}),t===`new`?p():null')
    patch('terrain_hint','a(`p`,{text:`What kind of island?`}),p()','a(`p`,{text:`选择地形`}),a(`small`,{text:`推荐河谷地形，便于建造河道与两岸街巷。`}),p()')
    patch('style_hint','. Hover for styles`','。悬停 / 长按选房屋样式`')
    patch('undo_label','title:`Undo (⌘Z)`','title:/Mac|iPhone|iPad/.test(navigator.platform??``)?`撤销 (⌘Z)`:`撤销 (Ctrl+Z)`')
    patch('redo_label','title:`Redo (⇧⌘Z)`','title:/Mac|iPhone|iPad/.test(navigator.platform??``)?`重做 (⇧⌘Z)`:`重做 (Ctrl+Y / Ctrl+Shift+Z)`')
    app.write_text(s,encoding='utf-8')
    print(json.dumps(counts,ensure_ascii=False))
    return counts

if __name__=='__main__':apply(sys.argv[1] if len(sys.argv)>1 else 'dist')
