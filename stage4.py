from pathlib import Path
import shutil,sys

def apply(root):
    root=Path(root); assets=root/'assets'; app=next(assets.glob('app-*.js')); s=app.read_text(encoding='utf-8')
    def patch(old,new):
        nonlocal s
        assert s.count(old)==1, (old[:100],s.count(old)); s=s.replace(old,new,1)
    shutil.copyfile(Path(__file__).with_name('scene.mjs'),assets/'jiangnan-scene.mjs')
    s='import {PRESETS as jiangnanPresets,presetPlan as jiangnanPlan} from "./jiangnan-scene.mjs";\n'+s
    patch('n.style=e,m.close(),v(),n.item===`house`?i():w.select(`house`)','n.style=e,m.close(),v(),w.select(`house`)')
    patch('return b(),S(),x(),w}var Wa=', '''let modeBar=a(`div`,{class:`jn-mode`,attrs:{role:`group`,"aria-label":`建造模式`}}), detail=a(`div`,{class:`jn-detail`,attrs:{hidden:``}}), status=a(`span`,{class:`jn-status`,attrs:{role:`status`}}), mode=`auto`;
    let buttons=[`自动建造`,`精细建造`,`观察`].map((label,index)=>a(`button`,{text:label,attrs:{type:`button`,"aria-pressed":`false`},on:{click:()=>{w.closePopups();if(index===0){mode=`auto`;w.select(`auto`)}else if(index===1){mode=`detail`;if(n.idle||n.item===`auto`)w.select(`house`)}else{w.setIdle(!0)}sync()}}}));
    let style=a(`select`,{attrs:{"aria-label":`房屋样式`}},[a(`option`,{text:`随机样式`,attrs:{value:`0`}}),...Array.from({length:6},(_,i)=>a(`option`,{text:Ba(i+1),attrs:{value:String(i+1)}}))]);
    style.addEventListener(`change`,()=>{w.setStyle(Number(style.value));w.select(`house`)});
    let tools=[[`house`,`民居`,`选择房屋样式，点击或拖动建造。`],[`arch`,`石桥`,`跨水放置拱形结构，两端接岸。`],[`dock`,`乌篷船`,`在可通航水面放置码头，等待船只生成。`],[`wall`,`月洞门`,`用墙围住花园，在墙上连接道路；门洞由规则生成。`],[`path`,`灯笼街`,`连续铺设至少四格道路，街灯自动生成。`],[`garden`,`园林`,`铺设花园，配合围墙、树木与道路。`],[`pillar`,`凉亭`,`在至少四根柱子上放四块大理石，形成亭子。`]];
    detail.append(style,...tools.map(([id,label,hint])=>a(`button`,{text:label,title:hint,attrs:{type:`button`},on:{click:()=>{w.select(id);status.textContent=hint}}})),status);
    modeBar.append(...buttons);f.prepend(modeBar,detail);function sync(){let active=n.idle?2:mode===`auto`?0:1;buttons.forEach((b,i)=>b.setAttribute(`aria-pressed`,String(i===active)));detail.toggleAttribute(`hidden`,active!==1);style.value=String(n.style);if(active===1)status.textContent=tools.find(t=>t[0]===n.item)?.[2]??`选择工具后在场景中建造。`};w.onChange(()=>{if(!n.idle)mode=n.item===`auto`?`auto`:`detail`;sync()});b(),S(),x(),sync();return w}var Wa=''')
    patch('u(`grow`,`grow`,`Grow a town`,_,!0),','u(`jiangnan`,`grow`,`江南场景`,()=>{n.replaceChildren(a(`div`,{class:`lc-confirm lc-choice`,attrs:{"data-ui":`jiangnan-presets`}},[a(`p`,{text:`选择江南场景`}),p(),...jiangnanPresets.map(t=>d(`jiangnan-${t.id}`,`grow`,t.name,r=>e.jiangnanPreset(t.id,r))),f(`jiangnan-back`,h)]))},!0),u(`grow`,`grow`,`Grow a town`,_,!0),')
    patch('Ce=Da({growTown(e){','''Ce=Da({jiangnanPreset(id,signal){return Promise.resolve().then(()=>{if(signal.aborted)return;let result=jiangnanPlan(id,{terrain:ke,grow:be,resolve:Be,apply:We,can:Me});if(signal.aborted)return;ye(result.seed);me(O,{...result.plan,jiangnanName:result.name})}).catch(error=>{g.toast(`场景未能生成：`+error.message)})},growTown(e){''')
    patch('n.growing?.(`${l} ${s}`,a)','n.growing?.(o.jiangnanName??`${l} ${s}`,a)')
    patch('g.banner(`${l} ${s} is growing.`,','g.banner(o.jiangnanName?`正在生成${o.jiangnanName}……`:`${l} ${s} is growing.`,')
    patch('for(let a=0;;a++){let o=r>=n.islands||i>=n.plans','for(let a=0;a<1200;a++){let o=r>=n.islands||i>=n.plans')
    patch('exact:!1,generated:r,plans:i};yield}}var Pi=','exact:!1,generated:r,plans:i};yield}return null}var Pi=')
    patch('e&&(ye(e.seed),me(O,e.plan))','e?(ye(e.seed),me(O,e.plan)):g.toast(`未找到适宜的地形，请重试。`)')
    patch('t.tagName===`INPUT`||t.tagName===`TEXTAREA`||t.isContentEditable','t.tagName===`INPUT`||t.tagName===`TEXTAREA`||t.tagName===`SELECT`||t.isContentEditable')
    app.write_text(s,encoding='utf-8')
    bundle=next(assets.glob('field-basketball.scenario-*.js')); q=bundle.read_text(encoding='utf-8'); old='if(l&&u&&e.terrain.material[o]===te.sand)return`palm`;'; assert q.count(old)==1; bundle.write_text(q.replace(old,'if(l&&u&&e.terrain.material[o]===te.sand)return`willow`;'),encoding='utf-8')
    css=next(assets.glob('app-*.css')); css.write_text(css.read_text(encoding='utf-8')+'''\n.jn-mode,.jn-detail{display:flex;gap:4px;align-items:center;flex-wrap:wrap;padding:5px;background:#f6f2e9;border:1px solid #aab5aa;border-radius:10px;margin-bottom:4px;pointer-events:auto}.jn-detail[hidden]{display:none}.jn-mode button,.jn-detail button,.jn-detail select{font:inherit;color:#34443c;background:#faf8f0;border:1px solid #aab5aa;border-radius:6px;padding:7px 10px;cursor:pointer}.jn-mode button[aria-pressed=true]{background:#42685a;color:#fff}.jn-status{font-size:12px;flex:1 0 100%;color:#48584e}.jn-detail{max-width:min(92vw,690px)}@media(max-width:600px){.jn-detail{max-height:112px;overflow:auto}.jn-mode button,.jn-detail button,.jn-detail select{min-height:36px;padding:5px 8px}}\n''',encoding='utf-8')
if __name__=='__main__':apply(sys.argv[1] if len(sys.argv)>1 else 'dist')
