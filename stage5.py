"""Apply V5 to the pinned V4 build. Reusable on fresh V4 only."""
from pathlib import Path
import shutil, sys

def apply(root):
    root=Path(root); assets=root/'assets'; app=next(assets.glob('app-*.js')); s=app.read_text(encoding='utf-8')
    def patch(old,new):
        nonlocal s
        if s.count(old)!=1: raise ValueError((old[:120],s.count(old)))
        s=s.replace(old,new,1)
    shutil.copyfile(Path(__file__).with_name('districts.mjs'),assets/'jiangnan-districts.mjs')
    patch('import {PRESETS as jiangnanPresets,presetPlan as jiangnanPlan,nativeSceneAPI as jiangnanEngine} from "./jiangnan-scene.mjs";', '''import {PRESETS as jiangnanPresets,presetPlan as jiangnanBase,nativeSceneAPI as jiangnanEngine} from "./jiangnan-scene.mjs";
import {addDistrict as jiangnanDistrict,pavilionPlan as jiangnanPavilion} from "./jiangnan-districts.mjs";
const jiangnanPlan=(id,api)=>jiangnanDistrict(jiangnanBase(id,api),id,api);''')
    # Explicitly distinguish native tools from automatic components; macro state belongs to tray.
    patch('setIdle(e){n.idle!==e&&(n.idle=e,S(),i())},select(e){let t=hr(e)', 'setIdle(e){n.idle!==e&&(n.idle=e,n.stamp=null,S(),i())},selectStamp(){w.select(`pillar`);n.stamp=`pavilion`;i()},select(e){n.stamp=null;let t=hr(e)')
    patch('[`dock`,`乌篷船`,`在可通航水面放置码头，等待船只生成。`]', '[`dock`,`码头`,`在可通航水面放置码头，等待船只生成。`]')
    patch('[`wall`,`月洞门`,`用墙围住花园，在墙上连接道路；门洞由规则生成。`]', '[`wall`,`院墙`,`用墙围住花园，在墙上连接道路；月洞门由规则生成。`]')
    patch('[`path`,`灯笼街`,`连续铺设至少四格道路，街灯自动生成。`]', '[`path`,`街道`,`连续铺设至少四格道路，街灯自动生成。`]')
    patch('[`pillar`,`凉亭`,`在至少四根柱子上放四块大理石，形成亭子。`]', '[`pillar`,`柱子`,`单独放置柱子，供自由组合。`]')
    patch('})),status);\n    modeBar.append', '})),a(`button`,{text:`一键凉亭`,attrs:{type:`button`,"data-jn-stamp":`pavilion`,"aria-pressed":`false`},on:{click:()=>w.selectStamp()}}),status);\n    modeBar.append')
    patch('style.value=String(n.style);if(active===1)status.textContent=', 'style.value=String(n.style);detail.querySelector(`[data-jn-stamp]`).setAttribute(`aria-pressed`,String(n.stamp===`pavilion`&&!n.idle));if(active===1)status.textContent=n.stamp===`pavilion`?`选择 2×2 格空旷平地；点击建造完整凉亭，撤销可恢复。`:')
    # Reuse existing full-edit ghost preview, not a fake overlay.
    patch('if(!e)return ot(null,``);if(U(m.state.item)){', 'if(!e)return ot(null,``);if(m.state.stamp===`pavilion`){let key=`${F}|pavilion|${e.pick.target}`;return key===$e?void 0:at(()=>Vi(jiangnanPavilion(c.world,c.terrain,e.pick.target,jiangnanEngine),c),key)}if(U(m.state.item)){')
    patch('R=()=>m.state.idle||ga(m.state.item)===null?', 'R=()=>m.state.idle||m.state.stamp||ga(m.state.item)===null?')
    patch('let r=A(e,t);if(!r)return;let i=R();', 'let r=A(e,t);if(!r)return;if(m.state.stamp===`pavilion`){let p=jiangnanPavilion(c.world,c.terrain,r.pick.target,jiangnanEngine);if(!p.edits.length){j(p.refusal,e,t);return}c.editAll(p.edits);return}let i=R();')
    patch('runStart(e,t){if(Lt||D.active||Ut||m.state.idle||!dr(m.state.item))', 'runStart(e,t){if(Lt||D.active||Ut||m.state.idle||m.state.stamp||!dr(m.state.item))')
    # If already in detail mode, clicking it cancels the macro instead of leaving it armed.
    patch('if(n.idle||n.item===`auto`)w.select(`house`)', 'if(n.idle||n.item===`auto`||n.stamp)w.select(`house`)')
    # Restrict stepped gables to a single-cell cross-section. Wider ends were producing repeated caps.
    bundle=next(assets.glob('field-basketball.scenario-*.js')); q=bundle.read_text(encoding='utf-8')
    fixes=[
      ('}if(g===`gable`&&o!==`chapel`&&o!==`barn`&&o!==`greenhouse`&&r.rectangular&&r.pierced.length===0)g=`stepped-gable`;','}if(g===`stepped-gable`&&u!==1)g=`gable`;if(g===`gable`&&u===1&&o!==`chapel`&&o!==`barn`&&o!==`greenhouse`&&r.rectangular&&r.pierced.length===0)g=`stepped-gable`;'),
      ('let t=r+Cp,i=(d-u)/5,s=[];for(let e=0;e<5;e++)','let t=r+Cp,i=(d-u)/3,s=[];for(let e=0;e<3;e++)'),
      ('for(let e=0;e<5;e++){let n=u+e*i,a=n+i,c=s[e]','for(let e=0;e<3;e++){let n=u+e*i,a=n+i,c=s[e]'),
      ('d=e+1<5?Math.min(c,s[e+1]):0','d=e+1<3?Math.min(c,s[e+1]):0'),
      ('o.box([n-.012,c,-t-.012],[a+.012,c+.03,-r+.012]','o.box([n,c,-t-.014],[a,c+.045,-r+.014]'),
      ('thick:ge.roofThick,fascia:s.trim,fasciaInk:','thick:ge.roofThick,fascia:s.cover===`glass`?s.trim:s.roofColor,fasciaInk:'),
      ('color:i,pattern:z.marble,ink:`col-shaft`','color:`#774638`,pattern:z.planks,ink:`col-shaft`'),
      ('u(-.075,.075,t.architrave,d,`architrave`,n.stone),u(-.09,.11,d,t.eave,`cornice`,n.shade)','u(-.075,.075,t.architrave,d,`architrave`,`#774638`),u(-.09,.11,d,t.eave,`cornice`,`#594b42`)')]
    for old,new in fixes:
        if old.startswith('for(let e=0;e<5;e++){let n=u+e*i,a=n+i,c=s[e]'):
            if q.count(old)!=2: raise ValueError(('gable-loop',q.count(old)))
            q=q.replace(old,new)
        else:
            if q.count(old)!=1: raise ValueError(('geometry',old[:70],q.count(old)))
            q=q.replace(old,new,1)
    bundle.write_text(q,encoding='utf-8')
    app.write_text(s,encoding='utf-8')
    css=next(assets.glob('app-*.css')); css.write_text(css.read_text(encoding='utf-8')+'\n.jn-detail button[aria-pressed=true]{background:#42685a;color:#fff}.jn-detail button:focus-visible,.jn-mode button:focus-visible,.jn-detail select:focus-visible{outline:2px solid #42685a;outline-offset:2px}\n',encoding='utf-8')
if __name__=='__main__':apply(sys.argv[1] if len(sys.argv)>1 else 'dist')
