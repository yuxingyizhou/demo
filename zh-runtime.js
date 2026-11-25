/* Simplified Chinese presentation layer; game identifiers and user input are untouched. */
(() => {
  'use strict';
  const dict = new Map(Object.entries(window.LC_ZH || {}));
  const lower = new Map([...dict].map(([a,b])=>[a.toLowerCase(),b]));
  const find = s => dict.get(s) ?? lower.get(s.toLowerCase());
  const translate = original => {
    if (!original) return original;
    const s = original.trim();
    if (!s || /[\u3400-\u9fff]/.test(s) && !/[A-Za-z]{3}/.test(s)) return original;
    let out = find(s), m;
    if (out === undefined) {
      if ((m = s.match(/^(.*?) \(([^()]*)\)$/)) && find(m[1])) out = find(m[1]) + '（' + (find(m[2]) || m[2]) + '）';
      else if ((m=s.match(/^(\d+) of (\d+)$/))) out=m[1]+'/'+m[2];
      else if ((m=s.match(/^of (\d+)$/))) out='满分 '+m[1];
      else if ((m=s.match(/^Colour (\d+)$/))) out='颜色 '+m[1];
      else if ((m=s.match(/^Speed ×(.+)$/))) out='速度 ×'+m[1];
      else if ((m=s.match(/^(Time of day|Season|Weather): holding (.+)$/i))) out=find(m[1])+'：固定为'+(find(m[2])||m[2]);
      else if ((m=s.match(/^(Music|Sounds) volume$/))) out=find(m[1])+'音量';
      else if ((m=s.match(/^(House style|House): (.+)$/))) out=find(m[1])+'：'+(find(m[2])||m[2]);
      else if ((m=s.match(/^(.+?)\. Hover for styles$/))) out=(find(m[1])||m[1])+'。悬停选择风格';
      else if ((m=s.match(/^(.+?): scroll over the island, or press − and \+$/))) out=(find(m[1])||m[1])+'：滚动鼠标滚轮，或按 − 与 +';
      else if ((m=s.match(/^(Length|Brush) (\d+)$/))) out=find(m[1])+' '+m[2];
      else if ((m=s.match(/^Delete (.+)\?$/))) out='删除 '+m[1]+'？';
      else if ((m=s.match(/^Open (.+)$/))) out='打开 '+m[1];
      else if ((m=s.match(/^(A|An) (.+) is growing\.$/i))) out='正在生成'+(find(m[2])||m[2])+'……';
      else if ((m=s.match(/^(\d+) (minute|hour|day)s? ago$/))) out=m[1]+({minute:'分钟',hour:'小时',day:'天'}[m[2]])+'前';
      else if ((m=s.match(/^Town (\d+)$/))) out='小镇 '+m[1];
      else if ((m=s.match(/^(.+) \(from the old address\)$/))) out=m[1]+'（从原地址迁移）';
      else if ((m=s.match(/^(.+): (.+)$/)) && find(m[1]) && find(m[2])) out=find(m[1])+'：'+find(m[2]);
      else if ((m=s.match(/^More in (.+)$/)) && find(m[1])) out='更多'+find(m[1]);
      else if ((m=s.match(/^(.+) in Little City(?:, drawn in ink and pencil)?$/)) && find(m[1])) out='小小城镇中的'+find(m[1]);
      else if ((m=s.match(/^(.+) is one of the things a town does by itself in Little City,/)) && find(m[1])) out=find(m[1])+'是小镇会自行发生的活动。只需建造合适的场所，活动便会自动发生。';
      else if ((m=s.match(/^Tap − and \+ to make (.+) (longer|shorter|wider|narrower)$/))) out='点击 − 与 + 调整'+(find(m[1])||'范围');
      else if ((m=s.match(/^Scroll to make (.+) (longer|shorter|wider|narrower)$/))) out='滚动鼠标滚轮调整'+(find(m[1])||'范围');
    }
    return out === undefined ? original : original.replace(s,()=>out);
  };
  const attrs=['title','aria-label','aria-description','aria-valuetext','placeholder','alt'];
  const excluded='script,style,svg,canvas,input,textarea,pre,code,[contenteditable],.lc-town-name';
  function textNode(n) {
    const p=n.parentElement;
    if (!p || p.closest(excluded)) return;
    const old=n.nodeValue, next=translate(old);
    if (old!==next) n.nodeValue=next;
  }
  function element(e) {
    if (e.closest('script,style,svg,pre,code,[contenteditable]')) return;
    for (const attr of attrs) {
      const old=e.getAttribute(attr);
      if (old===null) continue;
      const next=translate(old);
      if (old!==next) e.setAttribute(attr,next);
    }
  }
  function scan(n) {
    if(n.nodeType===Node.TEXT_NODE){textNode(n);return;}
    if(n.nodeType!==Node.ELEMENT_NODE)return;
    element(n);
    if(n.matches(excluded))return;
    for(const el of n.querySelectorAll(attrs.map(x=>'['+x+']').join(','))) element(el);
    const walker=document.createTreeWalker(n,NodeFilter.SHOW_TEXT);
    while(walker.nextNode())textNode(walker.currentNode);
  }
  document.documentElement.lang='zh-CN';
  function start() {
    scan(document.body);
    new MutationObserver(records=>{
      for(const r of records){
        if(r.type==='characterData')textNode(r.target);
        else if(r.type==='attributes')element(r.target);
        else for(const n of r.addedNodes)scan(n);
      }
    }).observe(document.body,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:attrs});
  }
  if(document.body)start();else document.addEventListener('DOMContentLoaded',start,{once:true});
})();