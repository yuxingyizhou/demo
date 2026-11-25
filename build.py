#!/usr/bin/env python3
"""Build the Simplified Chinese static site from the pinned upstream release or a local ZIP."""
import argparse
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import tempfile
import urllib.request
import zipfile
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString, Comment

ROOT = Path(__file__).resolve().parent
REV = "af6eac24ff21cbf027d4d33fd8219237a559f5b5"
URL = f"https://codeload.github.com/yaoderek/littlecity.io/zip/{REV}"
OUT = ROOT / "dist"

def rows(name, count):
    out = [line.split("|", count-1) for line in (ROOT / name).read_text(encoding="utf-8").splitlines() if line.strip()]
    assert all(len(row) == count for row in out), name
    return out

def unpack(source):
    with zipfile.ZipFile(source) as z:
        root = z.namelist()[0].split("/")[0]
        for info in z.infolist():
            parts = Path(info.filename).parts
            if not parts or parts[0] != root or ".." in parts or info.filename.startswith("/"):
                raise ValueError("Unexpected archive path")
            path = OUT.joinpath(*parts[1:])
            if info.is_dir():
                path.mkdir(parents=True, exist_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(z.read(info))

def build(source):
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    unpack(source)
    for p in (OUT/"CNAME", OUT/"7c1f4e2a9b8d4c6e8a5f3b2d1e0c9a87.txt"):
        p.unlink(missing_ok=True)
    ui = dict(rows("ui-zh.tsv", 2))
    ui.update({
        "Residents":"居民", "Happiness":"幸福度", "of 100":"满分100",
        "Just now":"刚刚", "Today":"今天", "Yesterday":"昨天",
        "Little City trailer":"小小城镇宣传片",
        "A hand-drawn island town in Little City, with a castle, a harbour, a chapel and a lighthouse.":"小小城镇的手绘海岛，拥有城堡、港口、教堂和灯塔。",
        "You are looking at someone else's town.":"正在查看其他玩家的小镇。",
        "Square":"广场", "Blocks":"方块", "Structures":"建筑", "Features":"设施",
        "Front":"正面", "Side":"侧面", "Icons":"图标",
        "Castle":"城堡", "Farming":"农业", "Market":"集市", "River":"河流",
        "Hill":"丘陵", "Gardens":"花园", "Island":"岛屿", "Flat":"平坦",
        "A harbour town":"港口小镇", "A castle town":"城堡小镇",
        "A farming village":"农庄", "A market town":"集市小镇",
        "No town":"没有小镇", "Empty island":"空岛",
    })
    guide = {slug:(name,how) for slug,name,how in rows("guide-zh.tsv",3)}
    actual = {p.parent.name for p in (OUT/"guide").glob("*/index.html")}
    if set(guide) != actual or len(guide)!=102:
        raise ValueError(f"Guide coverage mismatch: missing {actual-set(guide)}, extra {set(guide)-actual}")
    pages = {}
    for slug,(name,how) in guide.items():
        p=OUT/"guide"/slug/"index.html"
        soup=BeautifulSoup(p.read_text(encoding="utf-8"),"html.parser")
        heading=soup.find("h1").get_text(" ",strip=True)
        en=heading.removesuffix(" in Little City")
        condition=soup.select_one("p.how").get_text(" ",strip=True).removeprefix("How to get it:").strip()
        ui[en]=name
        ui[heading]=name+"：获得方式"
        ui[en+" in Little City, drawn in ink and pencil"]=name+"（手绘）"
        ui[condition]=how
        for suffix in (": how to build it | Little City guide",": how to make it happen | Little City guide"):
            ui[en+suffix]=name+"：获得方式 | 小小城镇图鉴"
        for paragraph in soup.select("main p"):
            s=paragraph.get_text(" ",strip=True)
            if "is one of the things a town does by itself in Little City" in s:
                ui[s]=name+"是小镇会自行发生的活动。只需建造合适的场所，活动便会自动发生。"
        pages[p]=(name,how)
    # Build one shared dictionary for the DOM presentation layer. Translate HTML before serving it.
    for group in ("Houses","Towers","Stone","Bridges","Waterfront","Green","Town","Playing fields","Big days","Through the seasons","By the water","Every day","Evening and night","After mischief","The Auto block"):
        if group in ui:
            ui["More in "+group]="更多"+ui[group]
    ui["Not found | Little City"]="页面不存在 | 小小城镇"
    ui["Little City | Bringing your towns over…"]="小小城镇 | 正在迁移存档……"
    def trans(s):
        t=s.strip()
        if t in ui:
            return s.replace(t,ui[t],1)
        return s
    missing=set()
    origin=os.environ.get("SITE_URL") or os.environ.get("CF_PAGES_URL") or ""
    origin=origin.rstrip("/")
    for p in sorted(OUT.rglob("*.html")):
        soup=BeautifulSoup(p.read_text(encoding="utf-8"),"html.parser")
        soup.html["lang"]="zh-CN"
        if p in pages:
            name,how=pages[p]
            section=soup.select_one("p.how")
            section.clear()
            strong=soup.new_tag("strong")
            strong.string="获得方式："
            section.append(strong)
            section.append(" "+how)
            if soup.title:
                soup.title.string=name+"：获得方式 | 小小城镇图鉴"
        for n in list(soup.find_all(string=True)):
            if isinstance(n,Comment) or not isinstance(n,NavigableString) or n.parent is None or n.parent.name in ("script","style","pre","code","svg"):
                continue
            old=str(n)
            new=trans(old)
            if new!=old:
                n.replace_with(new)
            elif re.search(r"[A-Za-z]{3}",old) and not re.search(r"[\u3400-\u9fff]",old) and n.parent.name not in ("title",):
                missing.add(old.strip())
        for tag in soup.find_all(True):
            for attr in ("title","alt","aria-label","aria-description","placeholder"):
                if isinstance(tag.get(attr),str):
                    tag[attr]=trans(tag[attr])
        for m in soup.find_all("meta"):
            key=m.get("name") or m.get("property") or ""
            if "content" not in m:
                continue
            if key in ("description","og:description","twitter:description"):
                m["content"]=pages[p][1] if p in pages else trans(m["content"])
            elif key in ("og:title","twitter:title"):
                m["content"]=soup.title.get_text() if soup.title else trans(m["content"])
            elif key in ("og:site_name","application-name","apple-mobile-web-app-title","og:image:alt"):
                m["content"]=trans(m["content"])
            elif key in ("og:url","og:image","og:video","og:video:secure_url","twitter:image"):
                m["content"]=m["content"].replace("https://littlecity.io",origin)
        for link in soup.find_all("link",rel="canonical"):
            if origin:
                link["href"]=link["href"].replace("https://littlecity.io",origin)
            else:
                link.decompose()
        # Original structured data refers to upstream branding, URLs and English copy.
        # Do not publish misleading structured data under another domain.
        for script in soup.find_all("script",type="application/ld+json"):
            script.decompose()
        patch=soup.new_tag("script",src="/zh-cn.js")
        soup.head.append(patch)
        style=soup.new_tag("style")
        style.string=".lc-btn-label,.lc-tab,.lc-guide-words,.lc-welcome,.lc-pop{font-family:ui-rounded,system-ui,'PingFang SC','Microsoft YaHei','Noto Sans CJK SC',sans-serif;}"
        soup.head.append(style)
        # Preserve the inline load-failure path, even if the localization script cannot start.
        for script in soup.find_all("script"):
            if script.string and not script.get("src"):
                s=str(script.string)
                for en in ("This browser couldn't draw the town. Try reloading, or another browser.",):
                    s=s.replace(en,ui.get(en,en))
                script.string=s
        p.write_text(str(soup),encoding="utf-8")
    # Privacy: the original build initializes the author's PostHog and records the canvas.
    # Pinning the exact release makes a targeted, verified disable possible.
    app=next((OUT/"assets").glob("app-*.js"))
    s=app.read_text(encoding="utf-8")
    marker="function Rn(e){let t=new URLSearchParams(location.search).get(" + chr(96) + "analytics" + chr(96) + ")"
    if s.count(marker)!=1:
        raise ValueError("Analytics signature changed; review pinned source")
    s=s.replace(marker,marker.replace("{let","{return;let"),1)
    app.write_text(s,encoding="utf-8")
    manifest=OUT/"manifest.webmanifest"
    if manifest.exists():
        m=json.loads(manifest.read_text(encoding="utf-8"))
        m["name"]=m["short_name"]="小小城镇"
        m["lang"]="zh-CN"
        m["description"]=trans(m["description"])
        manifest.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding="utf-8")
    (OUT/"zh-cn.js").write_text("window.LC_ZH="+json.dumps(ui,ensure_ascii=False,separators=(",",":"))+";\n"+(ROOT/"zh-runtime.js").read_text(encoding="utf-8"),encoding="utf-8")
    (OUT/"robots.txt").write_text("User-agent: *\nDisallow: /\n",encoding="utf-8")
    (OUT/"sitemap.xml").unlink(missing_ok=True)
    (OUT/"llms.txt").write_text("# 小小城镇\n\n手绘微缩城镇建造游戏。原作者：Derek Yao。\n\n- [游戏](/)\n- [建筑图鉴](/guide/)\n- [关于](/about/)\n",encoding="utf-8")
    (OUT/"_headers").write_text("/*\n  X-Robots-Tag: noindex, nofollow\n/assets/*\n  Cache-Control: public, max-age=86400\n",encoding="utf-8")
    if shutil.which("node"):
        subprocess.run(["node","--check",str(OUT/"zh-cn.js")],check=True)
        subprocess.run(["node","--check",str(app)],check=True)
    assert len(list((OUT/"guide").glob("*/index.html")))==102
    report={"guide_entries":len(guide),"dictionary_entries":len(ui),"html_pages":len(list(OUT.rglob("*.html"))),"unmatched_static_text":sorted(x for x in missing if x)}
    (ROOT/"localization-report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    print("Static site ready:",OUT)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,help="Original gh-pages ZIP; otherwise download the pinned commit")
    args=ap.parse_args()
    if args.source:
        build(args.source)
    else:
        with tempfile.TemporaryDirectory() as tmp:
            archive=Path(tmp)/"upstream.zip"
            with urllib.request.urlopen(URL,timeout=90) as response, archive.open("wb") as f:
                shutil.copyfileobj(response,f)
            build(archive)
