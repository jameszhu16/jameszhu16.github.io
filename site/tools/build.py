#!/usr/bin/env python3
"""Generate the bilingual site: Chinese at site/, English at site/en/.

Both trees share css/style.css, js/main.js and assets/, so only the copy differs.
The nav, footer and page shell are generated here rather than hand-maintained in
twelve files — that is what keeps the two languages from drifting apart.

Run from site/:  python3 tools/build.py
"""
import hashlib
import pathlib

SITE = pathlib.Path(__file__).resolve().parent.parent
BASE_URL = "https://jamesjz.com"


def rev(relpath):
    """?v=<content hash> so a changed stylesheet or script is never served from
    a stale cache. GitHub Pages sends max-age=600 on everything, so without
    this a visitor keeps yesterday's CSS for ten minutes after a deploy."""
    data = (SITE / relpath).read_bytes()
    return f"{relpath}?v={hashlib.sha1(data).hexdigest()[:8]}"
PAGES = ["index", "about", "skills", "work", "experience", "milo", "contact"]

# Company marks for the experience page. Keyed by the organisation name up to
# the " · " separator, which is the one part of the org line that is identical
# in both languages. A job renders its mark only when the file is actually
# present in assets/logos/, so the page stays correct for however many have
# been supplied — no broken images, no placeholders.
LOGO_STEM = {
    "CAA China": "caa",
    "East Goes Global": "east-goes-global",
    "Wasserman Media Group": "wasserman",
    "Los Angeles Sparks (WNBA)": "la-sparks",
    "Sports, Sponsorships and Events Consulting": "ssec",
    "ONE Championship": "one-championship",
    "SIDELINE": "sideline",
}


def logo_img(org, up, cls="job__logo"):
    """An <img> for the company mark, or "" if that file has not been added."""
    name = org.split(" · ")[0]
    stem = next((v for k, v in LOGO_STEM.items() if name.startswith(k)), None)
    if not stem:
        return ""
    for ext in ("svg", "png", "webp", "jpg"):
        if (SITE / "assets" / "logos" / f"{stem}.{ext}").exists():
            return (f'<img class="{cls}" src="{up}assets/logos/{stem}.{ext}"'
                    f' alt="{name}" loading="lazy">\n          ')
    return ""


# Cloudflare Web Analytics. Empty token emits nothing, so the site keeps its
# zero-external-request property until one is supplied — same contract as
# logo_img(): no asset, no markup, never a broken reference.
CF_BEACON_TOKEN = "7a365c5d4c774a3fa937ffdee6c04279"


def analytics():
    """The Cloudflare beacon, or "" when no token is configured.

    Deferred and last in the body: if the script is blocked — an ad blocker,
    a network that cannot reach Cloudflare — the page has already rendered and
    nothing on it depends on the beacon.
    """
    if not CF_BEACON_TOKEN:
        return ""
    return ('\n<script defer src="https://static.cloudflareinsights.com/beacon.min.js"'
            f' data-cf-beacon=\'{{"token": "{CF_BEACON_TOKEN}"}}\'></script>')


NAV = {
    "zh": {"index": "首页", "about": "关于", "skills": "技能",
           "work": "案例", "experience": "经历", "milo": "Milo", "contact": "联系"},
    "en": {"index": "Home", "about": "About", "skills": "Skills",
           "work": "Work", "experience": "Experience", "milo": "Milo", "contact": "Contact"},
}
LANG_LABEL = {"zh": "EN", "en": "中文"}
LANG_ARIA = {"zh": "Switch to English", "en": "切换到中文"}
NEXT_LABEL = {"zh": "下一页", "en": "Next"}


# The scroll fade-in hides content until JavaScript reveals it, so the hiding
# itself has to be conditional on JavaScript being there. This marks the page
# while it is still parsing (before anything paints, so no flash), and takes the
# mark back off if js/main.js never announces itself — a blocked or failed
# script fetch then costs the animation, not the text.
JS_FLAG = """<script>
(function (h) {
  h.classList.add("js");
  setTimeout(function () { if (!window.__reveal) h.classList.remove("js"); }, 2500);
})(document.documentElement);
</script>"""


def head(lang, page, title, desc):
    up = "../" if lang == "en" else ""
    zh = f"{BASE_URL}/{'' if page == 'index' else page + '.html'}"
    en = f"{BASE_URL}/en/{'' if page == 'index' else page + '.html'}"
    here = zh if lang == "zh" else en
    return f"""<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
{JS_FLAG}
<meta name="description" content="{desc}">
<link rel="canonical" href="{here}">
<link rel="alternate" hreflang="zh-CN" href="{zh}">
<link rel="alternate" hreflang="en" href="{en}">
<link rel="alternate" hreflang="x-default" href="{en}">

<!-- Link previews. Without these a shared URL renders as a bare grey link on
     LinkedIn, WeChat and iMessage — the first impression this site makes is
     usually the card, not the page. -->
<meta property="og:type" content="website">
<meta property="og:site_name" content="James Zhu · 朱晋辰">
<meta property="og:locale" content="{'zh_CN' if lang == 'zh' else 'en_US'}">
<meta property="og:locale:alternate" content="{'en_US' if lang == 'zh' else 'zh_CN'}">
<meta property="og:url" content="{here}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{BASE_URL}/assets/share.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="James Zhu 朱晋辰 — {'体育营销与品牌赞助' if lang == 'zh' else 'Sports Marketing & Partnerships'}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{BASE_URL}/assets/share.jpg">

<link rel="icon" href="{up}favicon.ico" sizes="32x32">
<link rel="icon" href="{up}assets/icon-32.png" type="image/png">
<link rel="apple-touch-icon" href="{up}assets/apple-touch-icon.png">
<link rel="preload" href="{up}assets/fonts/jost-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{up}{rev('css/style.css')}">"""


def nav(lang, page):
    labels = NAV[lang]
    other = f"en/{page}.html" if lang == "zh" else f"../{page}.html"
    links = "\n".join(
        '      <a href="%s.html"%s>%s</a>' % (p, ' class="is-active"' if p == page else "", labels[p])
        for p in PAGES
    )
    return f"""<div class="topbar">
  <div class="topbar__inner">
    <nav>
{links}
    </nav>
    <a class="topbar__lang" href="{other}" hreflang="{'en' if lang == 'zh' else 'zh-CN'}" aria-label="{LANG_ARIA[lang]}">{LANG_LABEL[lang]}</a>
  </div>
</div>"""


def shell(lang, page, title, desc, body, extra_script=None):
    """extra_script takes one script name or several; the home page needs two."""
    up = "../" if lang == "en" else ""
    names = [extra_script] if isinstance(extra_script, str) else (extra_script or [])
    extra = "".join(
        f'\n<script src="{up}{rev("js/" + name)}"></script>' for name in names
    )
    return f"""<!DOCTYPE html>
<html lang="{'zh-CN' if lang == 'zh' else 'en'}">
<head>
{head(lang, page, title, desc)}
</head>
<body>

{nav(lang, page)}

<main>

{body}

</main>

<footer class="footer">
  <p>&copy; <span id="year"></span> James Zhu · 朱晋辰</p>
</footer>

<script src="{up}{rev('js/main.js')}"></script>{extra}{analytics()}
</body>
</html>
"""


def page_head(title, sub):
    return f"""  <section class="page-head reveal">
    <h1>{title}</h1>
    <p>{sub}</p>
  </section>"""


def next_link(lang, target, label):
    return f"""    <div class="next reveal">
      <a href="{target}.html">{NEXT_LABEL[lang]} — {label} <i>→</i></a>
    </div>"""


MARQUEE_LABEL = {"zh": "工作过", "en": "Worked at"}

# The order the marks scroll past in. These are all employers (see the jobs
# list), which is why the label says "worked at" and not "clients" — the home
# page already carries a "worked with" line, and that one is the athletes.
MARQUEE_ORGS = ["CAA China", "East Goes Global", "Wasserman Media Group",
                "Los Angeles Sparks (WNBA)",
                "Sports, Sponsorships and Events Consulting", "ONE Championship"]


def marquee(label, items, reverse=False):
    """One plain row that wraps; js/marquee.js clones it into a rolling loop.

    Emitting a single wrapping row means scripts off, a failed script fetch and
    reduce motion all land on something finished and readable rather than on a
    fallback — a non-wrapping row would be clipped by the viewport and the tail
    of the list would be unreachable on a phone.
    """
    body = "\n".join(f"            {item}" for item in items if item)
    if not body:
        return ""
    rev = ' data-marquee="reverse"' if reverse else " data-marquee"
    return f"""  <div class="wrap">
    <div class="marquee reveal"{rev}>
      <em>{label}</em>
      <div class="marquee__viewport">
        <div class="marquee__track">
          <div class="marquee__group">
{body}
          </div>
        </div>
      </div>
    </div>
  </div>"""


def logo_marquee(lang, up):
    return marquee(
        MARQUEE_LABEL[lang],
        [logo_img(org, up, "marquee__logo").strip() for org in MARQUEE_ORGS],
    )


def roster_marquee(lang, names):
    """The athletes. The separating middot is drawn by CSS rather than written
    into the text: a screen reader should not read it out, and a wrapped row
    should not end a line on a lone dot."""
    return marquee(
        C[lang]["index"]["roster_label"],
        [f'<span class="marquee__name">{n}</span>' for n in names],
        reverse=True,
    )


def stats_strip(items):
    cells = "\n".join(
        f'      <div class="stat"><b>{v}</b><span>{k}</span></div>' for v, k in items
    )
    return f"""<div class="strip reveal">
  <div class="strip__inner">
{cells}
  </div>
</div>"""


# ---------------------------------------------------------------------------
C = {
    "zh": {
        "index": {
            "title": "James Zhu · 朱晋辰 — 体育经纪人",
            "desc": "朱晋辰 (James Zhu) 的个人主页 —— 体育营销、赞助策略与运动员数字增长",
            "role": "体育营销 &amp; 品牌赞助<br>帮助运动员、品牌、联赛建立连接",
            "meta": "CAA CHINA — 北京",
            "links": [("work", "看案例"), ("experience", "看经历"), ("contact", "联系我")],
            "stats": [("200K+", "账号矩阵涨粉"), ("500+", "内容产出"),
                      ("30%", "互动率增长")],
            "roster_label": "合作过",
            "pet_say": "汪!|带我出去|摸摸|饿了",
        },
        "about": {
            "title": "关于 · James Zhu", "desc": "关于朱晋辰 (James Zhu) —— 背景与专业方向",
            "h1": "关于我", "sub": "我是谁,在做什么,以及为什么做这些。",
            "text": """我是朱晋辰(James),现在 CAA China 做体育营销与品牌赞助,常驻北京。
        我毕业于南加州大学应用传播研究(Applied Communication Research)硕士,本科就读于纽约大学体育管理专业、经济学辅修。
        过去几年我一直游走在体育、市场营销与跨文化传播的交叉点上——从为布克、布伦森、约什·哈特等 NBA
        球星策划社媒增长与品牌代言方案,到参与湖人队、牛仔队等职业球队的赞助招标项目。
        我擅长把分散的数据和市场洞察,转化成能落地执行的营销策略,也享受在中美两种语境里做桥梁的过程。""",
            "facts": [("现职", "CAA China · 体育营销与赞助"), ("硕士", "USC 应用传播研究"),
                      ("本科", "NYU 体育管理 · 经济学辅修"),
                      ("方向", "体育营销 · 赞助策略 · 数字增长"), ("所在地", "北京 · Beijing")],
            "next": ("skills", "技能"),
        },
        "skills": {
            "title": "技能 · James Zhu", "desc": "朱晋辰 (James Zhu) 的核心能力、平台工具与语言",
            "h1": "技能", "sub": "从策略到执行,从中文互联网到英文互联网。",
            "groups": [("核心能力", ["体育营销策略", "赞助激活", "商务拓展", "数据分析与洞察", "跨文化沟通"]),
                       ("平台 &amp; 工具", ["小红书", "抖音 / TikTok", "微博 / 微信视频号",
                                        "Instagram / Twitter", "Excel &amp; 数据报表"]),
                       ("语言", ["中文(母语)", "英文(流利 · 双语办公)"])],
            "next": ("work", "精选案例"),
        },
        "work": {
            "title": "精选案例 · James Zhu", "desc": "朱晋辰 (James Zhu) 的代表性项目与成果",
            "h1": "精选案例", "sub": "几个能代表我工作方式和成果的项目。",
            "cases": [
                ("NBA 球星社媒增长矩阵", "East Goes Global",
                 "负责布伦森、布克、约什·哈特等球员的账号矩阵运营,统筹内容策略与发布节奏,并牵头布克 × 耐克品牌代言合作项目。",
                 [("200K+", "矩阵涨粉"), ("4 个月", "周期")]),
                ("顶级球队赞助资产招标", "Wasserman（现 The Team）",
                 "参与洛杉矶湖人队与 NFL 牛仔队的赞助商招标项目,梳理球衣广告位、训练场馆冠名、场边曝光等赞助资产,推动招标方案落地。",
                 [("12 个月", "周期")]),
                ("“Feature Friday” 内容专栏", "SIDELINE",
                 "从 0 到 1 策划社媒原创系列,帮助大学生运动员获得更广泛曝光,成为账号增长最快的内容线。",
                 [("2.5万+", "账号涨粉")]),
            ],
            "next": ("experience", "经历"),
        },
        "experience": {
            "title": "经历 · James Zhu", "desc": "朱晋辰 (James Zhu) 的工作与实习经历、荣誉认证",
            "h1": "经历", "sub": "从纽约到上海,从洛杉矶到北京。",
            "jobs": [
                ("2026.08 — 至今", "体育营销与赞助销售助理", "CAA China · 北京",
                 "参与头部品牌体育营销及商业合作策略制定,覆盖 NBA 等核心体育资源,策划品牌赞助激活方案,开展市场与竞品研究。"),
                ("2025.09 — 2026.02", "NBA 项目经理", "East Goes Global · 洛杉矶",
                 "负责布克、布伦森、约什·哈特等 NBA 球星账号矩阵的营销与数字增长策略,推动账号矩阵累计涨粉 200K+,并主导品牌代言合作项目。"),
                ("2025.01 — 2026.05", "战略与商务拓展实习生", "Wasserman Media Group（现 The Team） · 洛杉矶",
                 "为湖人队、牛仔队等顶级职业球队推动赞助商招标项目,支持球员市场活动的中国区落地,涵盖 Shai Gilgeous-Alexander、Klay Thompson 等球星。"),
                ("2025.05 — 2025.09", "社区关系与青少年篮球实习生", "Los Angeles Sparks (WNBA) · 洛杉矶",
                 "参与执行 WNBA 赛季球队活动(季票欢迎、青少年篮球营、慈善活动等),主场比赛日运营支持,现场观赛人流量提升约 25%。"),
                ("2024.01 — 2024.05", "赞助销售与市场实习生",
                 "Sports, Sponsorships and Events Consulting · 新泽西州普林斯顿",
                 "面向全美 20+ 州的青少年足球组织开展赞助拓展,促成区域汽车品牌与青少年足球联盟的三年赞助协议。"),
                ("2023.05 — 2023.08", "社交媒体与市场实习生", "ONE Championship · 上海",
                 "运营 TikTok、微信、微博账号,推动粉丝增长 30K+;支持李小龙纪念日活动策划及周边产品上市,吸引 2K+ 现场观众。"),
                ("2022.09 — 2022.12", "内容营销实习生", "SIDELINE · 纽约",
                 "管理 Twitter &amp; Instagram 账号,7 个月内涨粉 25K+;策划社媒专栏「Feature Friday」,帮助大学生运动员获得更广泛曝光。"),
            ],
            "honors_title": "荣誉 &amp; 认证",
            "honors": ["体育经纪人资格 · 中华人民共和国国家体育总局认可 (2021)",
                       "纽约大学优秀学生名单 (2022)",
                       "高中校队队长 &amp; 赛季最佳队友奖 (2020)"],
            "next": ("milo", "Milo"),
        },
        "milo": {
            "title": "Milo · James Zhu", "desc": "James Zhu 的狗 Milo —— 首席陪伴官",
            "h1": "Milo",
            "sub": "网站看到这里,该介绍一下真正的老板了。",
            "intro": """Milo,金毛贵宾,家里的首席陪伴官。
        主要职责包括:全天候监督我在家办公、在我打字时把下巴压在键盘上、
        以及在任何人进门后的三十秒内完成热情迎接。
        它不懂什么叫赞助权益,但它确实是我见过最会经营个人形象的一位。""",
            "captions": [("等饭的姿态", "只要厨房有动静,它就出现在这个位置。"),
                         ("出门警报", "车一开后备箱,它比谁都先上车。"),
                         ("后座常客", "上车之后就是这个表情,不管去哪。"),
                         ("上班监工", "居家办公期间的固定视角。"),
                         ("凑得太近", "它认为所有对话都应该在这个距离进行。")],
            "next": ("contact", "联系我"),
        },
        "contact": {
            "title": "联系 · James Zhu", "desc": "联系朱晋辰 (James Zhu)",
            "h1": "联系我", "sub": "有想聊的项目、合作机会,或者只是想打个招呼?欢迎联系。",
        },
    },
    "en": {
        "index": {
            "title": "James Zhu — Sports Agent",
            "desc": "Personal site of Jinchen (James) Zhu — sports marketing, sponsorship strategy and athlete digital growth",
            "role": "Sports Marketing &amp; Partnerships<br>Connecting athletes, brands and leagues",
            "meta": "CAA CHINA — BEIJING",
            "links": [("work", "See the work"), ("experience", "Experience"), ("contact", "Get in touch")],
            "stats": [("200K+", "Follower growth"), ("500+", "Posts published"),
                      ("30%", "Engagement lift")],
            "roster_label": "Worked with",
            "pet_say": "Woof!|Walk?|Pet me|Snack time",
        },
        "about": {
            "title": "About · James Zhu", "desc": "About Jinchen (James) Zhu — background and focus",
            "h1": "About me", "sub": "Who I am, what I do, and why I do it.",
            "text": """I'm Jinchen Zhu — most people call me James. I work on sports marketing and brand
        partnerships at CAA China, based in Beijing. I hold a master's in Applied Communication Research
        from the University of Southern California, and a bachelor's in Sports Management with an
        economics minor from New York University.
        For the past few years I've worked at the intersection of sports, marketing and cross-cultural
        communication — from building social growth and endorsement strategies for NBA athletes like
        Devin Booker, Jalen Brunson and Josh Hart, to sponsorship sales for properties including the
        Los Angeles Lakers and Dallas Cowboys.
        What I'm good at is turning scattered data and market insight into marketing plans people can
        actually execute — and I genuinely enjoy being the bridge between the US and Chinese markets.""",
            "facts": [("Now", "CAA China · Sports Marketing"), ("Master's", "USC · Applied Communication Research"),
                      ("Bachelor's", "NYU · Sports Management, Econ minor"),
                      ("Focus", "Marketing · Sponsorship · Growth"), ("Based in", "Beijing, China")],
            "next": ("skills", "Skills"),
        },
        "skills": {
            "title": "Skills · James Zhu", "desc": "Core skills, platforms and languages — Jinchen (James) Zhu",
            "h1": "Skills", "sub": "From strategy to execution, across the Chinese and English internets.",
            "groups": [("Core skills", ["Sports marketing strategy", "Sponsorship activation",
                                        "Business development", "Data analysis &amp; insight",
                                        "Cross-cultural communication"]),
                       ("Platforms &amp; tools", ["Xiaohongshu", "Douyin / TikTok", "Weibo / WeChat Channels",
                                               "Instagram / Twitter", "Excel &amp; reporting"]),
                       ("Languages", ["Mandarin (native)", "English (fluent · bilingual workplace)"])],
            "next": ("work", "Selected work"),
        },
        "work": {
            "title": "Selected Work · James Zhu", "desc": "Selected projects and results — Jinchen (James) Zhu",
            "h1": "Selected work", "sub": "A few projects that show how I work and what came of it.",
            "cases": [
                ("NBA athlete social growth", "East Goes Global",
                 "Ran the account network for Jalen Brunson, Devin Booker and Josh Hart — owning content strategy and publishing cadence, and leading the Booker × Nike endorsement collaboration.",
                 [("200K+", "Follower growth"), ("4 months", "Span")]),
                ("Sponsorship sales for major franchises", "Wasserman (now The Team)",
                 "Supported sponsorship sales for the Los Angeles Lakers and Dallas Cowboys — mapping inventory across jersey patches, courtside branding and digital exposure, and preparing partnership materials.",
                 [("12 months", "Span")]),
                ("“Feature Friday” content series", "SIDELINE",
                 "Built an original social series from scratch to give college athletes wider exposure; it became the fastest-growing content line on the account.",
                 [("25K+", "New followers")]),
            ],
            "next": ("experience", "Experience"),
        },
        "experience": {
            "title": "Experience · James Zhu",
            "desc": "Work and internship experience, honors and certifications — Jinchen (James) Zhu",
            "h1": "Experience", "sub": "New York to Shanghai, Los Angeles to Beijing.",
            "jobs": [
                ("Aug 2026 — Present", "Sports Marketing &amp; Partnership Sales Associate", "CAA China · Beijing",
                 "Support sports marketing and partnership strategy for leading brands across the NBA and other major properties; develop sponsorship activations integrating athletes, events, content and fan engagement; turn market research into actionable client recommendations."),
                ("Sep 2025 — Feb 2026", "NBA Project Manager", "East Goes Global · Los Angeles",
                 "Owned marketing and digital growth strategy for NBA athletes including Devin Booker, Jalen Brunson and Josh Hart, contributing to 200K+ total follower growth, and led brand endorsement collaborations."),
                ("Jan 2025 — May 2026", "Strategy &amp; Business Development Intern", "Wasserman Media Group (now The Team) · Los Angeles",
                 "Drove sponsorship sales efforts for properties including the Los Angeles Lakers and Dallas Cowboys, and led China-market activation for NBA athletes such as Shai Gilgeous-Alexander and Klay Thompson, driving 100K+ follower growth."),
                ("May 2025 — Sep 2025", "Community Relations &amp; Youth Basketball Intern",
                 "Los Angeles Sparks (WNBA) · Los Angeles",
                 "Executed game-day operations and playoff preparation, plus community events from season ticket holder welcomes to youth camps and charity galas. Attendance up roughly 25% year over year."),
                ("Jan 2024 — May 2024", "Sponsorship Sales &amp; Marketing Intern",
                 "Sports, Sponsorships and Events Consulting · Princeton, NJ",
                 "Ran sponsorship outreach across youth soccer organizations in 20+ US states, and sourced a three-year sponsorship agreement between a regional automotive brand and a youth soccer league."),
                ("May 2023 — Aug 2023", "Social Media &amp; Marketing Intern", "ONE Championship · Shanghai",
                 "Managed TikTok, WeChat and Weibo accounts, generating 30K+ total follower growth; supported the Bruce Lee Memorial Day event and merchandise launch, which drew 2K+ on-site attendees."),
                ("Sep 2022 — Dec 2022", "Content Marketing Intern", "SIDELINE · New York",
                 "Managed Twitter and Instagram accounts, driving 25K+ new followers in seven months, and created the “Feature Friday” series giving college athletes wider exposure."),
            ],
            "honors_title": "Honors &amp; certifications",
            "honors": ["Licensed sports agent · recognized by the General Administration of Sport of China (2021)",
                       "NYU Annual Honor Student list (2022)",
                       "High school team captain &amp; Teammate of the Year (2020)"],
            "next": ("milo", "Milo"),
        },
        "milo": {
            "title": "Milo · James Zhu", "desc": "Milo, James Zhu's goldendoodle and chief company officer",
            "h1": "Milo",
            "sub": "You made it this far — time to meet the actual boss.",
            "intro": """Milo is a goldendoodle and the household's chief company officer.
        His duties include supervising every work-from-home day, resting his chin on the keyboard
        mid-sentence, and greeting anyone who walks through the door within thirty seconds.
        He has no idea what sponsorship inventory is, but he is the best personal brand I have
        ever worked with.""",
            "captions": [("Waiting for dinner", "Any noise from the kitchen and he is already in position."),
                         ("Car alarm", "Open the boot and he is in before anyone else."),
                         ("Back seat regular", "This is the face once he is in, wherever we are going."),
                         ("Supervising", "The standard work-from-home viewing angle."),
                         ("Too close", "He believes every conversation should happen at this range.")],
            "next": ("contact", "Contact"),
        },
        "contact": {
            "title": "Contact · James Zhu", "desc": "Get in touch with Jinchen (James) Zhu",
            "h1": "Get in touch",
            "sub": "Working on something interesting, hiring, or just want to say hello? I'd love to hear from you.",
        },
    },
}

ROSTER = ["德文·布克 / Devin Booker", "杰伦·布伦森 / Jalen Brunson", "约什·哈特 / Josh Hart",
          "谢伊·吉尔杰斯-亚历山大 / Shai Gilgeous-Alexander",
          "克莱·汤普森 / Klay Thompson",
          "贾维尔·麦基 / JaVale McGee", "小贾伦·杰克逊 / Jaren Jackson Jr.",
          "杨瀚森 / Yang Hansen", "纽约尼克斯 / New York Knicks"]
ROSTER_EN = ["Devin Booker", "Jalen Brunson", "Josh Hart", "Shai Gilgeous-Alexander",
             "Klay Thompson", "JaVale McGee", "Jaren Jackson Jr.", "Yang Hansen",
             "New York Knicks"]

# The desk pet, drawn rather than cut out of a photo: at ~72px a photo crop is
# just a smudge, and a flat cartoon keeps its legs, ear and tail readable enough
# to animate. Faces right; js/pet.js mirrors it with scaleX to walk the other way.
PET_SVG = """<svg viewBox="0 0 128 96" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">
          <g fill="#C9B18E">
            <rect class="pet-leg-b" x="35" y="58" width="11" height="28" rx="5.5"/>
            <rect class="pet-leg-b" x="72" y="58" width="11" height="28" rx="5.5"/>
          </g>
          <g class="pet-tail" fill="#EFE0C6">
            <circle cx="13" cy="23" r="7.5"/><circle cx="18" cy="31" r="8"/>
            <circle cx="24" cy="39" r="8.5"/><circle cx="31" cy="46" r="9"/>
          </g>
          <g fill="#EFE0C6">
            <circle cx="36" cy="47" r="15"/><circle cx="50" cy="40" r="15"/>
            <circle cx="64" cy="42" r="15"/><circle cx="76" cy="49" r="14"/>
            <ellipse cx="55" cy="57" rx="30" ry="15"/>
          </g>
          <g fill="#EFE0C6">
            <rect class="pet-leg-a" x="42" y="59" width="12" height="28" rx="6"/>
            <rect class="pet-leg-a" x="64" y="59" width="12" height="28" rx="6"/>
          </g>
          <circle cx="95" cy="35" r="17" fill="#EFE0C6"/>
          <circle cx="86" cy="22" r="9" fill="#EFE0C6"/>
          <circle cx="101" cy="20" r="9" fill="#EFE0C6"/>
          <circle cx="110" cy="29" r="8" fill="#EFE0C6"/>
          <ellipse cx="111" cy="45" rx="13" ry="10" fill="#F7EEDD"/>
          <ellipse cx="120" cy="42" rx="5.5" ry="4.5" fill="#2B2723"/>
          <path d="M111 50 q4 4.5 8 1.5" stroke="#2B2723" stroke-width="1.8" fill="none" stroke-linecap="round"/>
          <circle cx="101" cy="33" r="3.2" fill="#2B2723"/>
          <circle cx="102.4" cy="31.7" r="1.1" fill="#fff"/>
          <path class="pet-ear" d="M88 23 q-11 6 -11 22 q0 12 9 13 q9 1 10 -10 q1 -8 -3 -12 q5 -6 -5 -13 z" fill="#C9AE85"/>
        </svg>"""


def build_index(lang):
    c = C[lang]["index"]
    up = "../" if lang == "en" else ""
    links = "\n".join(f'          <a href="{t}.html">{label} <i>→</i></a>'
                      for t, label in c["links"])
    names = ROSTER if lang == "zh" else ROSTER_EN
    say = c["pet_say"]
    body = f"""  <div class="wrap">
    <div class="hero">
      <div class="hero__text">
        <h1 class="reveal">JAMES<span>ZHU</span></h1>
        <p class="hero__cn reveal">朱 晋 辰</p>
        <p class="hero__role reveal">{c['role']}</p>
        <p class="hero__meta reveal">{c['meta']}</p>
        <div class="hero__links reveal">
{links}
        </div>
      </div>
      <div class="hero__photo reveal">
        <img src="{up}assets/james-portrait.png" alt="James Zhu 朱晋辰" width="1180" height="1197">
      </div>

      <div class="pet" id="miloPet" data-say="{say}" title="Milo" role="img" aria-label="Milo">
        <span class="pet__say" aria-hidden="true"></span>
        <span class="pet__sprite">{PET_SVG}</span>
      </div>
    </div>
  </div>

{stats_strip(c['stats'])}

{roster_marquee(lang, names)}

{logo_marquee(lang, up)}"""
    return shell(lang, "index", c["title"], c["desc"], body,
                 extra_script=("pet.js", "stats.js", "marquee.js"))


def build_about(lang):
    c = C[lang]["about"]
    facts = "\n".join(f"          <li><span>{k}</span><strong>{v}</strong></li>"
                      for k, v in c["facts"])
    body = f"""{page_head(c['h1'], c['sub'])}

  <section class="section">
    <div class="about">
      <p class="about__text reveal">{c['text']}</p>
      <ul class="about__facts reveal">
{facts}
      </ul>
    </div>

{next_link(lang, *c['next'])}
  </section>"""
    return shell(lang, "about", c["title"], c["desc"], body)


def build_skills(lang):
    c = C[lang]["skills"]
    groups = "\n".join(
        '      <div class="group reveal">\n        <h2>%s</h2>\n        <div class="tags">\n%s\n        </div>\n      </div>'
        % (name, "\n".join(f'          <span class="tag">{t}</span>' for t in tags))
        for name, tags in c["groups"]
    )
    body = f"""{page_head(c['h1'], c['sub'])}

  <section class="section">
    <div class="groups">
{groups}
    </div>

{next_link(lang, *c['next'])}
  </section>"""
    return shell(lang, "skills", c["title"], c["desc"], body)


def build_work(lang):
    c = C[lang]["work"]
    cases = "\n".join(
        """      <article class="case reveal">
        <div>
          <h2>%s</h2>
          <div class="case__who">%s</div>
        </div>
        <div>
          <p>%s</p>
          <div class="case__num">
%s
          </div>
        </div>
      </article>""" % (
            title, who, text,
            "\n".join(f"            <div><b>{v}</b><span>{k}</span></div>" for v, k in nums),
        )
        for title, who, text, nums in c["cases"]
    )
    body = f"""{page_head(c['h1'], c['sub'])}

  <section class="section">
    <div class="cases">
{cases}
    </div>

{next_link(lang, *c['next'])}
  </section>"""
    return shell(lang, "work", c["title"], c["desc"], body)


def build_experience(lang):
    c = C[lang]["experience"]
    up = "../" if lang == "en" else ""
    jobs = "\n".join(
        """      <article class="job reveal">
        <div class="job__side">
          %s<time>%s</time>
        </div>
        <div>
          <h2>%s</h2>
          <div class="job__org">%s</div>
          <p>%s</p>
        </div>
      </article>""" % (logo_img(org, up), date, role, org, desc)
        for date, role, org, desc in c["jobs"]
    )
    honors = "\n".join(f"        <li>{h}</li>" for h in c["honors"])
    body = f"""{page_head(c['h1'], c['sub'])}

  <section class="section">
    <div class="timeline">
{jobs}
    </div>

    <div class="honors reveal">
      <h2>{c['honors_title']}</h2>
      <ul>
{honors}
      </ul>
    </div>

{next_link(lang, *c['next'])}
  </section>"""
    return shell(lang, "experience", c["title"], c["desc"], body)


# The resume is not published. It carries a phone number and a home market's
# worth of personal detail, and a file on a public URL is a file anyone can
# take. Asking for it by email keeps James in the loop on who has a copy.
RESUME_NOTE = {
    "zh": "需要简历的话,发邮件给我就好。",
    "en": "Happy to send my resume — just email me.",
}


def build_contact(lang):
    c = C[lang]["contact"]
    body = f"""{page_head(c['h1'], c['sub'])}

  <section class="section">
    <div class="contact reveal">
      <a class="contact__email" href="mailto:jinchenzhu2000@outlook.com">jinchenzhu2000@outlook.com</a>
      <div class="contact__links">
        <a href="https://www.linkedin.com/in/jinchen-zhu-a9015a223" target="_blank" rel="noopener">LinkedIn</a>
      </div>

      <p class="contact__note">{RESUME_NOTE[lang]}</p>
    </div>
  </section>"""
    return shell(lang, "contact", c["title"], c["desc"], body)


def build_milo(lang):
    c = C[lang]["milo"]
    up = "../" if lang == "en" else ""
    shots_html = []
    n = len(c["captions"])
    # first shot is the 2x2 feature; if the remaining count would strand an
    # empty cell in the 4-column grid, the last one widens to close it
    widen_last = (n - 1) % 2 == 1
    for i, (title, caption) in enumerate(c["captions"], 1):
        cls = "shot reveal"
        if i == 1:
            cls += " shot--feature"
        elif i == n and widen_last:
            cls += " shot--wide"
        shots_html.append(
            """      <figure class="%s">
        <img src="%sassets/dog-%d.jpg" alt="Milo — %s" loading="lazy" width="600" height="800">
        <figcaption><b>%s</b>%s</figcaption>
      </figure>""" % (cls, up, i, title, title, caption))
    shots = "\n".join(shots_html)
    body = f"""{page_head(c['h1'], c['sub'])}

  <section class="section">
    <p class="milo__intro reveal">{c['intro']}</p>

    <div class="shots">
{shots}
    </div>

{next_link(lang, *c['next'])}
  </section>"""
    return shell(lang, "milo", c["title"], c["desc"], body)


BUILDERS = {"index": build_index, "about": build_about, "skills": build_skills,
            "work": build_work, "experience": build_experience, "milo": build_milo,
            "contact": build_contact}


NOT_FOUND = {
    "zh": ("404 · James Zhu", "页面不存在", "找不到这个页面",
           "链接可能过期了,或者地址打错了。", "回首页"),
    "en": ("404 · James Zhu", "Page not found", "This page does not exist",
           "The link may be out of date, or the address mistyped.", "Back to home"),
}


def build_404():
    """One page for both languages, served by Pages for any unknown path.

    Every path is absolute: a 404 can be reached at any depth (/a/b/c), and a
    relative stylesheet would resolve against that phantom directory and 404
    in turn, leaving an unstyled error page.
    """
    title, kicker, h1, sub, back = NOT_FOUND["zh"]
    _, kicker_en, h1_en, sub_en, back_en = NOT_FOUND["en"]
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="robots" content="noindex">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="stylesheet" href="/{rev('css/style.css')}">
</head>
<body>

<main>
  <section class="page-head">
    <p class="notfound__code">404</p>
    <h1>{h1}</h1>
    <p>{sub}</p>
    <p class="notfound__en">{h1_en}. {sub_en}</p>
    <p class="notfound__back"><a href="/">{back} <i>→</i></a> &nbsp;
       <a href="/en/">{back_en} <i>→</i></a></p>
  </section>
</main>

<footer class="footer">
  <p>&copy; <span id="year"></span> James Zhu · 朱晋辰</p>
</footer>

<script src="/{rev('js/main.js')}"></script>{analytics()}
</body>
</html>
"""


def build_sitemap():
    urls = []
    for lang in ("zh", "en"):
        prefix = BASE_URL if lang == "zh" else f"{BASE_URL}/en"
        for page in PAGES:
            urls.append(f"{prefix}/" if page == "index" else f"{prefix}/{page}.html")
    body = "\n".join(f"  <url><loc>{u}</loc></url>" for u in urls)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{body}\n</urlset>\n")


def main():
    (SITE / "en").mkdir(exist_ok=True)
    for lang in ("zh", "en"):
        out = SITE if lang == "zh" else SITE / "en"
        for page in PAGES:
            (out / f"{page}.html").write_text(BUILDERS[page](lang), encoding="utf-8")
            print("wrote", (out / f"{page}.html").relative_to(SITE))

    # generated here rather than hand-written so they cannot fall out of step
    # with PAGES when a page is added or renamed
    (SITE / "404.html").write_text(build_404(), encoding="utf-8")
    (SITE / "sitemap.xml").write_text(build_sitemap(), encoding="utf-8")
    (SITE / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {BASE_URL}/sitemap.xml\n", encoding="utf-8")
    for extra in ("404.html", "sitemap.xml", "robots.txt"):
        print("wrote", extra)


if __name__ == "__main__":
    main()
