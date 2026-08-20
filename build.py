#!/usr/bin/env python3
"""
Static site generator for Pratt Ventures, LLC.

Content is a faithful reproduction of prattventures.com (wording preserved);
URLs match the legacy site so existing links and search equity carry over.
Run:  python3 build.py
"""
import json, os, pathlib, re, shutil, datetime

ROOT = pathlib.Path(__file__).parent.resolve()

# Canonical origin for canonical/OG/JSON-LD/sitemap URLs. Override while the site
# lives somewhere other than its production domain, e.g.
#   PV_ORIGIN=https://pratt-ventures.github.io/pratt-ventures python3 build.py
ORIGIN = os.environ.get("PV_ORIGIN", "https://prattventures.com").rstrip("/")

# Write a CNAME file for GitHub Pages custom domains:
#   PV_CNAME=prattventures.com python3 build.py
CNAME = os.environ.get("PV_CNAME", "").strip()

# Keep a staging deploy out of the index so it never competes with the live
# domain in search results:  PV_NOINDEX=1 python3 build.py
NOINDEX = os.environ.get("PV_NOINDEX", "").strip() not in ("", "0", "false", "no")
BRAND = "Pratt Ventures, LLC"
TAGLINE = "Driving convergence of technology and strategy to amplify results!"
PHONE = "561-693-6944"
PHONE_E164 = "+1-561-693-6944"
EMAIL = "Info@PrattVentures.com"
EMAIL_L = "info@prattventures.com"
STREET = "4125 Venetia Way"
CITY, REGION, ZIP = "Palm Beach Gardens", "FL", "33418"
HOURS = "Mon-Fri 9:00 AM to 5 PM EST"
OG_IMAGE = ORIGIN + "/assets/img/og.png"
BUILT = datetime.date.today().isoformat()

# ---------------------------------------------------------------- navigation
TEAM_LINKS = [
    ("/daniel-hoogterp/", "Dan Hoogterp"),
    ("/operating-partner-chris-rufe/", "Chris Rufe"),
    ("/technology-partner-stephen-melnick/", "Steve Melnick"),
    ("/investment-analyst-danielle-hoogterp/", "Danielle Hoogterp"),
]
NAV = [
    ("/about-us/", "About Us", None),
    ("/our-team/", "Our Team", TEAM_LINKS),
    ("/our-portfolio/", "Our Portfolio", None),
    ("/we-recommend/", "Practices & Tools", None),
    ("/contact-us/", "Contact Us", None),
    ("/login/", "Login", None),
]

def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))

# ---------------------------------------------------------------- structured data
ORG_LD = {
    "@type": "FinancialService",
    "@id": ORIGIN + "/#organization",
    "name": BRAND,
    "alternateName": "Pratt Ventures",
    "url": ORIGIN + "/",
    "logo": {"@type": "ImageObject", "url": ORIGIN + "/assets/img/logo-512.png",
              "width": 512, "height": 512},
    "image": OG_IMAGE,
    "slogan": TAGLINE,
    "description": ("Pratt Ventures, LLC accelerates business performance by driving rapid "
                    "innovation and adaptation of technology, providing advisory, opportunity "
                    "review and diligence services alongside selected investments."),
    "telephone": PHONE_E164,
    "email": EMAIL_L,
    "foundingDate": "2016-01",
    "address": {"@type": "PostalAddress", "streetAddress": STREET, "addressLocality": CITY,
                "addressRegion": REGION, "postalCode": ZIP, "addressCountry": "US"},
    "areaServed": "US",
    "openingHoursSpecification": [{
        "@type": "OpeningHoursSpecification",
        "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "opens": "09:00", "closes": "17:00"}],
    "knowsAbout": ["Venture capital", "Private equity", "Commercial real estate",
                   "Artificial intelligence", "SaaS", "Machine learning",
                   "Technology diligence", "Information security"],
}
SITE_LD = {
    "@type": "WebSite",
    "@id": ORIGIN + "/#website",
    "url": ORIGIN + "/",
    "name": BRAND,
    "publisher": {"@id": ORIGIN + "/#organization"},
    "inLanguage": "en-US",
}

def breadcrumbs_ld(trail):
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n,
             "item": ORIGIN + u} for i, (u, n) in enumerate(trail)
        ],
    }

# ---------------------------------------------------------------- shell
def head(p):
    url = ORIGIN + p["path"]
    graph = [ORG_LD, SITE_LD]
    webpage = {
        "@type": p.get("page_type", "WebPage"),
        "@id": url + "#webpage",
        "url": url,
        "name": p["title"],
        "description": p["desc"],
        "isPartOf": {"@id": ORIGIN + "/#website"},
        "about": {"@id": ORIGIN + "/#organization"},
        "inLanguage": "en-US",
        "primaryImageOfPage": p.get("og_image", OG_IMAGE),
    }
    graph.append(webpage)
    if p.get("trail"):
        graph.append(breadcrumbs_ld(p["trail"]))
    graph.extend(p.get("extra_ld", []))
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph},
                    indent=None, separators=(",", ":"))

    robots = p.get("robots", "index, follow, max-image-preview:large, "
                             "max-snippet:-1, max-video-preview:-1")
    if NOINDEX:
        robots = "noindex, nofollow"

    prev_next = ""
    return f"""<!doctype html>
<html lang="en-US">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(p['title'])}</title>
<meta name="description" content="{esc(p['desc'])}">
<link rel="canonical" href="{url}">
<meta name="robots" content="{robots}">
<meta name="author" content="{BRAND}">
<meta name="theme-color" content="#050505">
<meta name="color-scheme" content="dark">
<meta property="og:type" content="{p.get('og_type','website')}">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:locale" content="en_US">
<meta property="og:title" content="{esc(p.get('og_title', p['title']))}">
<meta property="og:description" content="{esc(p['desc'])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{p.get('og_image', OG_IMAGE)}">
<meta property="og:image:alt" content="{esc(p.get('og_alt', BRAND))}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(p.get('og_title', p['title']))}">
<meta name="twitter:description" content="{esc(p['desc'])}">
<meta name="twitter:image" content="{p.get('og_image', OG_IMAGE)}">
<meta name="twitter:site" content="@dan_hoog">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/assets/img/apple-touch-icon.png" sizes="180x180">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Inter:wght@200;300;400;500&family=Playfair+Display:ital,wght@0,400;0,500;1,400&display=swap">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@200;300;400;500&family=Playfair+Display:ital,wght@0,400;0,500;1,400&display=swap">
<link rel="stylesheet" href="/assets/css/site.css">
<link rel="sitemap" type="application/xml" href="/sitemap.xml">{prev_next}
<script type="application/ld+json">{ld}</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
"""

def header(active):
    items = []
    for href, label, sub in NAV:
        cur = ' aria-current="page"' if href == active else ""
        if sub:
            parts = []
            for h, l in sub:
                sc = ' aria-current="page"' if h == active else ""
                parts.append('<a href="%s"%s>%s</a>' % (h, sc, esc(l)))
            subs = "".join(parts)
            items.append(
                f'<div class="nav__has"><a class="nav__l" href="{href}"{cur}>{esc(label)}</a>'
                f'<div class="nav__panel">{subs}</div></div>')
        else:
            items.append(f'<a class="nav__l" href="{href}"{cur}>{esc(label)}</a>')
    nav = "".join(items)

    drawer = []
    for href, label, sub in NAV:
        drawer.append(f'<a href="{href}">{esc(label)}</a>')
        if sub:
            for h, l in sub:
                drawer.append(f'<a class="sub" href="{h}">{esc(l)}</a>')
    drawer = "".join(drawer)

    return f"""<header class="hdr">
  <div class="hdr__in">
    <a class="brand" href="/" aria-label="{BRAND} — home">
      <span class="brand__name">Pratt Ventures</span>
      <span class="brand__sub">Technology Enabled Business</span>
    </a>
    <nav class="nav" aria-label="Primary">{nav}</nav>
    <button class="burger" type="button" aria-expanded="false" aria-controls="drawer" aria-label="Open menu"><span></span></button>
  </div>
</header>
<div class="drawer" id="drawer" aria-hidden="true">
  <nav aria-label="Mobile">{drawer}</nav>
</div>
"""

def footer():
    team = "".join(f'<li><a href="{h}">{esc(l)}</a></li>' for h, l in TEAM_LINKS)
    return f"""<footer class="ftr">
  <div class="wrap">
    <div class="ftr__grid">
      <div>
        <p class="ftr__mark">Pratt&nbsp;Ventures</p>
        <p class="ftr__tag">{esc(TAGLINE)}</p>
        <p class="ftr__tag" style="margin-top:.8rem">{BRAND} is a Delaware Company</p>
      </div>
      <div>
        <h2>Firm</h2>
        <ul>
          <li><a href="/about-us/">About Us</a></li>
          <li><a href="/our-team/">Our Team</a></li>
          <li><a href="/our-portfolio/">Our Portfolio</a></li>
          <li><a href="/we-recommend/">Best Practices and Tools</a></li>
        </ul>
      </div>
      <div>
        <h2>Team</h2>
        <ul>{team}</ul>
      </div>
      <div>
        <h2>Contact</h2>
        <ul>
          <li><a href="tel:{PHONE_E164}">{PHONE}</a></li>
          <li><a href="mailto:{EMAIL_L}">{EMAIL}</a></li>
          <li><span class="muted">{STREET}<br>{CITY}, {REGION} {ZIP}</span></li>
          <li><a href="/login/">Login</a></li>
        </ul>
      </div>
    </div>
    <div class="ftr__base">
      <span>&copy; <span data-year>2026</span> {BRAND}</span>
      <span>{esc(HOURS)}</span>
    </div>
  </div>
</footer>
<script src="/assets/js/site.js" defer></script>
</body>
</html>
"""

def crumbs(trail):
    out = []
    for i, (u, n) in enumerate(trail):
        last = i == len(trail) - 1
        inner = f'<span aria-current="page">{esc(n)}</span>' if last else f'<a href="{u}">{esc(n)}</a>'
        out.append(f"<li>{inner}</li>")
    return f'<nav aria-label="Breadcrumb"><ol class="crumbs">{"".join(out)}</ol></nav>'

def band(title, lede, cta_href, cta_label):
    return f"""<section class="band">
  <div class="wrap band__in">
    <p class="eyebrow eyebrow--plain rv">Pratt Ventures, LLC</p>
    <h2 class="d2 band__ttl rv rv-d1">{title}</h2>
    <p class="lede rv rv-d2" style="max-width:52ch">{lede}</p>
    <p class="rv rv-d3"><a class="btn" href="{cta_href}">{cta_label} <span class="arw">&rarr;</span></a></p>
  </div>
</section>"""

def relativize(html, depth):
    """Rewrite root-absolute internal hrefs/srcs to be relative to this page.

    Keeps the site portable: it works at a domain root, in a GitHub Pages
    project subpath, or in any subfolder, with no rebuild. Absolute URLs
    (canonical, og:*, JSON-LD) are untouched because they start with https://.
    """
    prefix = "../" * depth

    def sub(m):
        attr, target = m.group(1), m.group(2)
        rel = prefix + target.lstrip("/")
        if not rel:
            rel = "./"
        return '%s="%s"' % (attr, rel)

    return re.sub(r'\b(href|src)="(/[^"]*)"', sub, html)


def write(path, html):
    out = ROOT / path.strip("/")
    if path == "/":
        out = ROOT / "index.html"
    elif not path.endswith(".html"):
        out = ROOT / path.strip("/") / "index.html"
    depth = len(out.relative_to(ROOT).parts) - 1
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(relativize(html, depth), encoding="utf-8")
    return out


# ================================================================= CONTENT
# All prose below is reproduced from prattventures.com.

ABOUT_P = [
    "Pratt Ventures was founded by a visionary team of entrepreneurs and executives with strong "
    "execution experience. We accelerate business performance by driving rapid innovation and "
    "adaptation of technology.",
    "Our leadership and execution experience ranges from startups to multi-billion dollar public "
    "entities. Our industry experience spans technology, media, e-commerce, telecom, fortune 50, "
    "intelligence, finance, and information security.",
    "We provide advisory, opportunity review, and diligence services in these areas. We make "
    "selected investments in firms matching our target criteria.",
]
INDUSTRIES = ["Technology", "Media", "E-commerce", "Telecom", "Fortune 50", "Intelligence",
              "Finance", "Information Security"]
SERVICES = [
    ("Advisory", "We accelerate business performance by driving rapid innovation and adaptation of technology."),
    ("Opportunity Review", "Our leadership and execution experience ranges from startups to multi-billion dollar public entities."),
    ("Diligence", "Our industry experience spans technology, media, e-commerce, telecom, fortune 50, intelligence, finance, and information security."),
    ("Selected Investments", "We make selected investments in firms matching our target criteria."),
]

PORTFOLIO = [
    {"name": "Hatcher+", "tag": "Venture Fund", "url": "https://hatcher.com/",
     "logo": "/assets/img/hatcher-plus-logo.png", "logo_kind": "logo",
     "alt": "Hatcher+ logo",
     "text": "Hatcher+ is building a new kind of venture fund. The approach uses a data driven "
             "optimal investment model to shape investments in a diverse array of early stage "
             "opportunities for superior, more predictable returns."},
    {"name": "MagicOpt", "tag": "Machine Learning", "url": "https://magicopt.com",
     "logo": "/assets/img/magicopt-logo.png", "logo_kind": "logo",
     "alt": "MagicOpt logo",
     "text": "MagicOpt provides instant prediction and hyperparameter optimization services. "
             "The prediction service extracts predictive power from tiny data, instantly. The "
             "groundbreaking adaptive tuning system beats strong approaches over 90% of the time "
             "and is 20 times more efficient than random search."},
    {"name": "Commercial Real Estate", "tag": "Real Assets", "url": None,
     "logo": "/assets/img/commercial-real-estate.png", "logo_kind": "ico",
     "alt": "Commercial real estate investments at Pratt Ventures",
     "text": "Our commercial real-estate investments leverage expertise of experienced funds for "
             "geographically distributed medical-anchored facilities."},
    {"name": "Private Equity", "tag": "Mid-Market", "url": None,
     "logo": "/assets/img/private-equity.png", "logo_kind": "ico",
     "alt": "Private equity investments at Pratt Ventures",
     "text": "Our private equity investments leverage expertise of established funds in profitable "
             "mid-market companies favoring non-cyclical industries."},
    {"name": "RocketCalm &amp; MindFusionX", "tag": "Personal Growth", "url": "https://rocketcalm.net",
     "logo": "/assets/img/rocketcalm.jpg", "logo_kind": "ico",
     "alt": "RocketCalm and MindFusionX meditation programs",
     "text": "RocketCalm and MindFusionX provide higher level meditation programs that accelerate "
             "meditation and mindfulness practices. These personal growth programs enhance well "
             "being and success using brain stimulation and leading edge learning processes."},
    {"name": "Stealth Investments", "tag": "Undisclosed", "url": None,
     "logo": None, "logo_kind": None,
     "alt": "Stealth investments at Pratt Ventures",
     "text": "E-commerce tools, a decision support tool, and engineering lifecycle tools "
             "including toteboard and mouse wiggler."},
    {"name": "Always Exploring", "tag": "Open", "url": None,
     "logo": "/assets/img/exploring.jpg", "logo_kind": "ico",
     "alt": "Pratt Ventures is always exploring new opportunities",
     "text": "We are always exploring opportunities. Stay tuned."},
]

TEAM = [
    {"slug": "/daniel-hoogterp/", "name": "Dan Hoogterp", "first": "Dan",
     "role": "CEO and Managing Director",
     "img": "/assets/img/dan-hoogterp.jpg",
     "alt": "Dan Hoogterp, CEO and Managing Director of Pratt Ventures, LLC",
     "card": "Dan Hoogterp is a founder of Pratt Ventures, LLC and serves as its CEO.",
     "title": "Dan Hoogterp, Managing Director",
     "desc": "Dan Hoogterp has served as CEO and Managing Director of Pratt Ventures, LLC since "
             "January 2016, blending deep technology expertise with keen business acumen.",
     "bio": [
        "Mr. Dan Hoogterp has served as CEO and Managing Director of Pratt Ventures, LLC since January 2016.",
        "Mr. Hoogterp is a highly versatile senior company executive who leverages deep technology "
        "expertise and keen business acumen to drive revenue, market share, competitive advantage, "
        "corporate value and operational excellence. A visionary, collaborative leader with insight "
        "for creating technology-based products and roadmaps and implementing highly successful "
        "go-to-market strategies. Blends traditional business practices with entrepreneurial mindset "
        "to strengthen company agility and market responsiveness. Proficiency with a broad range of "
        "technologies, organizations and software methodologies along with effective communication "
        "skills at all levels meets the challenges of today’s dynamic marketplaces.",
        "Prior to Pratt Ventures, LLC, Mr. Hoogterp served as SVP &amp; Chief Technology Officer of "
        "Bankrate, Inc., a personal media firm, from May 2005 through December 2015.",
        "From November 2002 until May 2005, he served as Chief Executive Officer of TQuist, LLC, a "
        "technology consulting company. From February 2001 to September 2002, Mr. Hoogterp served as "
        "Executive Vice President and Chief Technology Officer of Enamics, Inc., a company "
        "specializing in business technology management. From July 1999 to February 2001, he served "
        "as Senior Vice President and Chief Technology Officer of Sagemaker, Inc., a provider of "
        "enterprise information portals. From March 1991 to July 1999, he served as Chief Executive "
        "Officer of Retrieval Technologies, Inc.",
        "Mr. Hoogterp received a Post-Graduate Certificate in Business from Heriott-Watt "
        "University’s Edinburgh Business School in Scotland in 2004",
     ],
     "facts": [("Role", "CEO and Managing Director"), ("At Pratt Ventures", "Since January 2016"),
               ("Education", "Post-Graduate Certificate in Business, Edinburgh Business School")],
     "social": [("LinkedIn", "https://www.linkedin.com/in/danhoogterp"),
                ("X", "https://twitter.com/dan_hoog"),
                ("Facebook", "https://www.facebook.com/dan.hoogterp")],
     "job": "Chief Executive Officer"},

    {"slug": "/operating-partner-chris-rufe/", "name": "Chris Rufe", "first": "Chris",
     "role": "Technology and Operating Partner",
     "img": "/assets/img/chris-rufe.jpg",
     "alt": "Chris Rufe, Operating and Technology Partner at Pratt Ventures, LLC",
     "card": "Chris Rufe is President of MagicOpt, LLC, a Machine Learning company in our investment "
             "portfolio. He is also an operating partner for other initiatives at Pratt Ventures.",
     "title": "Chris Rufe, Operating and Technology Partner",
     "seo_title": "Chris Rufe, Operating & Tech Partner",
     "desc": "Chris Rufe is an Operating and Technology Partner at Pratt Ventures and President of "
             "MagicOpt, LLC, with a proven track record in product and software services.",
     "bio": [
        "Mr. Chris Rufe is an an Operating and Technology Partner at Pratt Ventures. He also serves "
        "as President of MagicOpt, LLC (Virginia), a portfolio company.",
        "Mr. Rufe has a proven track record of execution in product and software services. His focus "
        "is on technology that powers online and Saas offerings, principally in the information "
        "management arena for large organizations and publishers.",
     ],
     "facts": [("Role", "Operating and Technology Partner"),
               ("Also", "President, MagicOpt, LLC (Virginia)"),
               ("Focus", "Technology powering online and SaaS offerings")],
     "social": [("LinkedIn", "https://www.linkedin.com/in/chris-rufe-541b4b5/"),
                ("Facebook", "https://www.facebook.com/chris.rufe")],
     "job": "Operating and Technology Partner"},

    {"slug": "/technology-partner-stephen-melnick/", "name": "Steve Melnick", "first": "Steve",
     "role": "Technology Partner",
     "img": "/assets/img/steve-melnick.png",
     "alt": "Steve Melnick, Technology Partner at Pratt Ventures, LLC",
     "card": "Steve Melnick is a Technology Partner at Pratt Ventures, LLC and Vice President at "
             "MindFusionX.",
     "title": "Steve Melnick, Technology Partner",
     "desc": "Stephen Melnick is a Technology Partner at Pratt Ventures and Vice President of "
             "MindFusionX — a product and software visionary for web technology.",
     "bio": [
        "Mr. Stephen Melnick is a Technology Partner at Pratt Ventures. He also serves as a Vice "
        "President of MindFusionX, a portfolio company.",
        "Mr. Melnick is a product and software visionary for web technology and web service business. "
        "He provides creative software solutions to help businesses get more out of their technology "
        "infrastructure and systems. He strives for a extreme client satisfaction and has a track "
        "record of long term relationships with clients and firms.",
        "Mr. Melnick has developed a proven design and implementation methodology which has been "
        "thoroughly tested over time. Striving to be responsive to customer needs, many of his "
        "clients have been Fortune 500 companies. He is a great speaker with several years of "
        "university teaching experience in information technology. From 2005 through 2012, he served "
        "as a senior consultant to the International Atomic Energy Agency in Vienna, Austria.",
        "Mr. Melnick holds a Master of Science in Computer Science from Johns Hopkins University and "
        "a Bachelor of Arts in Mathematics at the University of Florida.",
     ],
     "facts": [("Role", "Technology Partner"), ("Also", "Vice President, MindFusionX"),
               ("Education", "M.S. Computer Science, Johns Hopkins University · B.A. Mathematics, University of Florida")],
     "social": [("LinkedIn", "https://www.linkedin.com/in/stephen-melnick-21266a34"),
                ("Facebook", "https://www.facebook.com/smmelnick")],
     "job": "Technology Partner"},

    {"slug": "/investment-analyst-danielle-hoogterp/", "name": "Danielle Hoogterp", "first": "Danielle",
     "role": "Investment Analyst",
     "img": "/assets/img/danielle-hoogterp.jpg",
     "alt": "Danielle Hoogterp, Investment Analyst at Pratt Ventures, LLC",
     "card": "Ms. Danielle Hoogterp is an Investment Analyst at Pratt Ventures, LLC.",
     "title": "Danielle Hoogterp, Investment Analyst",
     "desc": "Danielle Hoogterp is an Investment Analyst at Pratt Ventures, LLC, researching "
             "investment opportunities in real-estate, technology, AI, and SaaS.",
     "bio": [
        "Ms. Danielle Hoogterp is an Investment Analyst at Pratt Ventures, LLC.",
        "She is experienced in competitive analysis and company diligence as well as product "
        "management in the online software arena.",
        "As a part time analyst at Pratt Ventures, LLC, Danielle researches investment opportunities "
        "in real-estate, technology, AI, and SaaS. She also evaluates services to improve our "
        "operational efficiency.",
     ],
     "facts": [("Role", "Investment Analyst"),
               ("Coverage", "Real-estate, technology, AI, and SaaS"),
               ("Experience", "Competitive analysis, company diligence, product management")],
     "social": [("LinkedIn", "https://www.linkedin.com/in/danielle-hoogterp-720584254/")],
     "job": "Investment Analyst"},
]


# ================================================================= COMPONENTS
FIELD = """<div class="lume" aria-hidden="true">
    <div class="lume__sheen"></div>
    <svg class="lume__lines" viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice" focusable="false">
      <defs>
        <linearGradient id="pvSweep" x1="0" y1="1" x2="1" y2="0">
          <stop offset="0%" stop-color="#fff" stop-opacity="0"/>
          <stop offset="38%" stop-color="#fff" stop-opacity=".42"/>
          <stop offset="62%" stop-color="#fff" stop-opacity=".62"/>
          <stop offset="100%" stop-color="#fff" stop-opacity="0"/>
        </linearGradient>
      </defs>
      <path d="M-120 705 C 300 690, 520 415, 900 296 S 1400 118, 1620 44"/>
      <path d="M-120 812 C 344 796, 604 520, 984 378 S 1466 196, 1660 128"/>
      <path d="M-120 604 C 258 592, 458 338, 818 228 S 1338 58, 1560 -18"/>
      <path d="M-120 916 C 380 900, 690 640, 1064 470 S 1520 268, 1700 208"/>
    </svg>
    <div class="lume__fade"></div>
  </div>"""



def pf_rows(items, start=1):
    rows = []
    for i, it in enumerate(items, start):
        n = "%02d" % i
        end = ('<span class="pf__go">Visit <span class="arw" aria-hidden="true">&#8599;</span></span>'
               if it["url"] else '<span class="pf__go">&mdash;</span>')
        inner = f"""<span class="pf__n">{n}</span>
      <span class="pf__name-wrap">
        <span class="pf__name">{it['name']}</span>
        <span class="pf__tag">{esc(it['tag'])}</span>
      </span>
      <span class="pf__txt">{it['text']}</span>
      <span class="pf__end">{end}</span>"""
        if it["url"]:
            rows.append(f'<a class="pf__row rv" href="{it["url"]}" rel="noopener" target="_blank">{inner}</a>')
        else:
            rows.append(f'<div class="pf__row rv">{inner}</div>')
    return '<div class="pf">' + "".join(rows) + "</div>"


def team_roster(members):
    rows = []
    for i, m in enumerate(members):
        d = min(i, 5)
        rows.append(f"""<a class="roster__row rv rv-d{d}" href="{m['slug']}">
      <span class="roster__fig">
        <img src="{m['img']}" alt="{esc(m['alt'])}" width="360" height="360" loading="lazy" decoding="async">
      </span>
      <span class="roster__id">
        <span class="roster__name">{esc(m['name'])}</span>
        <span class="roster__role">{esc(m['role'])}</span>
      </span>
      <span class="roster__note">{m['card']}</span>
      <span class="roster__go">Biography <span class="arw" aria-hidden="true">&rarr;</span></span>
    </a>""")
    return '<div class="roster">' + "".join(rows) + "</div>"


# ================================================================= PAGES
def page_home():
    meta = [("Structure", "A Delaware Company"),
            ("Based", "Palm Beach Gardens, Florida"),
            ("Coverage", "Real-estate · Technology · AI · SaaS"),
            ("Services", "Advisory · Opportunity Review · Diligence")]
    dl = "".join(f"<div><dt>{esc(k)}</dt><dd>{v}</dd></div>" for k, v in meta)
    inds = "".join(f'<li class="pillar rv"><span class="pillar__n">{"%02d" % (i+1)}</span>'
                   f'<h3>{esc(x)}</h3></li>' for i, x in enumerate(INDUSTRIES))
    svc = "".join(f'<li class="pillar rv rv-d{i}"><span class="pillar__n">{"%02d" % (i+1)}</span>'
                  f'<h3>{esc(n)}</h3><p>{t}</p></li>' for i, (n, t) in enumerate(SERVICES))

    body = f"""<main id="main">
<section class="hero">
  {FIELD}
  <div class="wrap hero__in">
    <p class="eyebrow">Technology Enabled Business</p>
    <h1 class="d1 hero__ttl">
      <span style="display:block;font-size:.3em;font-style:italic;letter-spacing:.01em;color:var(--fg-dim);margin-bottom:.5em">Welcome to</span>
      <span class="leaf">Pratt Ventures,&nbsp;LLC</span>
    </h1>
    <p class="lede hero__lede">{esc(TAGLINE)}</p>
    <div class="hero__cta">
      <a class="btn btn--solid" href="/our-portfolio/">View the portfolio <span class="arw">&rarr;</span></a>
      <a class="btn" href="/about-us/">About the firm</a>
    </div>
    <dl class="hero__meta">{dl}</dl>
  </div>
  <div class="scrollcue" aria-hidden="true"><span>Scroll</span><i></i></div>
</section>

<section class="section" id="firm">
  <div class="wrap split">
    <div class="sticky">
      <p class="eyebrow rv">The Firm</p>
      <h2 class="statement rv rv-d1 mt-m">A visionary team of <em>entrepreneurs</em> and executives with strong execution experience.</h2>
    </div>
    <div class="body">
      <p class="lede rv">{ABOUT_P[0]}</p>
      <div class="mt-l rv rv-d1"><p>{ABOUT_P[1]}</p><p>{ABOUT_P[2]}</p></div>
      <p class="mt-l rv rv-d2"><a class="link" href="/about-us/">More about Pratt Ventures <span class="arw">&rarr;</span></a></p>
    </div>
  </div>
</section>

<section class="section section--tight" id="services">
  <div class="wrap">
    <p class="eyebrow rv">What We Do</p>
    <ul class="pillars mt-l">{svc}</ul>
  </div>
</section>

<section class="section" id="industries">
  <div class="wrap">
    <p class="eyebrow rv">Industry Experience</p>
    <h2 class="d3 rv rv-d1 mt-m" style="max-width:24ch">Our industry experience spans eight sectors.</h2>
    <ul class="pillars mt-l">{inds}</ul>
  </div>
</section>

<section class="section" id="portfolio">
  <div class="wrap">
    <div style="display:flex;flex-wrap:wrap;gap:1.5rem;align-items:flex-end;justify-content:space-between">
      <div>
        <p class="eyebrow rv">Portfolio</p>
        <h2 class="d2 rv rv-d1 mt-m" style="max-width:16ch">Selected investments.</h2>
      </div>
      <p class="rv rv-d2"><a class="link" href="/our-portfolio/">Full portfolio <span class="arw">&rarr;</span></a></p>
    </div>
    <div class="mt-l">{pf_rows(PORTFOLIO[:3])}</div>
  </div>
</section>

<section class="section" id="team">
  <div class="wrap">
    <div style="display:flex;flex-wrap:wrap;gap:1.5rem;align-items:flex-end;justify-content:space-between">
      <div>
        <p class="eyebrow rv">The Team</p>
        <h2 class="d2 rv rv-d1 mt-m" style="max-width:18ch">Leadership from startups to public entities.</h2>
      </div>
      <p class="rv rv-d2"><a class="link" href="/our-team/">Meet the team <span class="arw">&rarr;</span></a></p>
    </div>
    <div class="mt-l">{team_roster(TEAM)}</div>
  </div>
</section>

{band("We look forward to hearing from you.", "Advisory, opportunity review, and diligence services — and selected investments in firms matching our target criteria.", "/contact-us/", "Contact us")}
</main>"""
    return {
        "path": "/",
        "title": "Pratt Ventures, LLC | Technology Enabled Business",
        "desc": "Visionary technology entrepreneurs and executives driving innovation to accelerate "
                "business performance — advisory, diligence and selected investments.",
        "og_alt": "Pratt Ventures, LLC — technology enabled business",
        "body": body,
    }


def page_about():
    body = f"""<main id="main">
<section class="phead">
  {FIELD}
  <div class="wrap phead__in">
    {crumbs([("/", "Home"), ("/about-us/", "About Us")])}
    <p class="eyebrow mt-m">The Firm</p>
    <h1 class="d2 phead__ttl">About Pratt Ventures, LLC</h1>
    <p class="lede phead__lede">{ABOUT_P[0]}</p>
  </div>
</section>

<section class="section">
  <div class="wrap split">
    <div class="sticky">
      <p class="eyebrow rv">Mandate</p>
      <h2 class="statement rv rv-d1 mt-m">We accelerate business performance by driving rapid <em>innovation</em>.</h2>
    </div>
    <div class="body rv">
      <p class="dropcap">{ABOUT_P[1]}</p>
      <p>{ABOUT_P[2]}</p>
      <p class="muted" style="margin-top:2.4rem;font-size:.8125rem;letter-spacing:.16em;text-transform:uppercase">{BRAND} is a Delaware Company</p>
    </div>
  </div>
</section>

<section class="section section--tight">
  <div class="wrap">
    <p class="eyebrow rv">Services</p>
    <ul class="pillars mt-l">{"".join(f'<li class="pillar rv rv-d{i}"><span class="pillar__n">{"%02d" % (i+1)}</span><h3>{esc(n)}</h3><p>{t}</p></li>' for i, (n, t) in enumerate(SERVICES))}</ul>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <p class="eyebrow rv">Industry Experience</p>
    <ul class="pillars mt-l">{"".join(f'<li class="pillar rv"><span class="pillar__n">{"%02d" % (i+1)}</span><h3>{esc(x)}</h3></li>' for i, x in enumerate(INDUSTRIES))}</ul>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <p class="eyebrow rv">The Team</p>
    <h2 class="d2 rv rv-d1 mt-m" style="max-width:18ch">Founded by entrepreneurs and executives.</h2>
    <div class="mt-l">{team_roster(TEAM)}</div>
  </div>
</section>

{band("Let's talk.", "We provide advisory, opportunity review, and diligence services in these areas.", "/contact-us/", "Contact us")}
</main>"""
    return {
        "path": "/about-us/",
        "title": "About Pratt Ventures, LLC | Technology & Investment Firm",
        "desc": "Founded by entrepreneurs and executives with strong execution experience, Pratt Ventures "
                "accelerates business performance through rapid technology innovation.",
        "page_type": "AboutPage",
        "trail": [("/", "Home"), ("/about-us/", "About Us")],
        "body": body,
    }


def page_team():
    body = f"""<main id="main">
<section class="phead">
  {FIELD}
  <div class="wrap phead__in">
    {crumbs([("/", "Home"), ("/our-team/", "Our Team")])}
    <p class="eyebrow mt-m">People</p>
    <h1 class="d2 phead__ttl">The Pratt Ventures Team</h1>
    <p class="lede phead__lede">Our leadership and execution experience ranges from startups to multi-billion dollar public entities.</p>
  </div>
</section>

<section class="section">
  <div class="wrap">{team_roster(TEAM)}</div>
</section>

{band("Work with us.", "We make selected investments in firms matching our target criteria.", "/contact-us/", "Contact us")}
</main>"""
    ld = {"@type": "ItemList", "name": "The Pratt Ventures Team",
          "itemListElement": [{"@type": "ListItem", "position": i + 1,
                               "url": ORIGIN + m["slug"], "name": m["name"]}
                              for i, m in enumerate(TEAM)]}
    return {
        "path": "/our-team/",
        "title": "The Pratt Ventures Team | Leadership & Partners",
        "desc": "Meet the Pratt Ventures team — Dan Hoogterp, CEO and Managing Director; Chris Rufe and "
                "Steve Melnick, Partners; Danielle Hoogterp, Investment Analyst.",
        "trail": [("/", "Home"), ("/our-team/", "Our Team")],
        "extra_ld": [ld],
        "body": body,
    }


def page_bio(m):
    paras = "".join(f"<p>{t}</p>" for t in m["bio"])
    facts = "".join(f"<div><dt>{esc(k)}</dt><dd>{v}</dd></div>" for k, v in m["facts"])
    soc = "".join(f'<a href="{u}" rel="noopener me" target="_blank">{esc(n)}</a>' for n, u in m["social"])
    body = f"""<main id="main">
<section class="phead">
  {FIELD}
  <div class="wrap phead__in">
    {crumbs([("/", "Home"), ("/our-team/", "Our Team"), (m["slug"], m["name"])])}
    <p class="eyebrow mt-m">{esc(m['role'])}</p>
    <h1 class="d2 phead__ttl">{esc(m['title'])}</h1>
  </div>
</section>

<section class="section">
  <div class="wrap bio">
    <div class="rv">
      <figure class="bio__fig">
        <img src="{m['img']}" alt="{esc(m['alt'])}" width="900" height="1100" loading="eager" decoding="async">
      </figure>
      <dl class="bio__card">{facts}
        <div><dt>Connect</dt><dd><span class="social">{soc}</span></dd></div>
      </dl>
    </div>
    <div class="body rv rv-d1">
      {paras}
      <p class="mt-l"><a class="link" href="/our-team/">Back to the team <span class="arw">&rarr;</span></a></p>
    </div>
  </div>
</section>

{band("We look forward to hearing from you.", esc(TAGLINE), "/contact-us/", "Contact us")}
</main>"""
    person = {
        "@type": "Person",
        "@id": ORIGIN + m["slug"] + "#person",
        "name": m["name"],
        "url": ORIGIN + m["slug"],
        "image": ORIGIN + m["img"],
        "jobTitle": m["job"],
        "description": m["desc"],
        "worksFor": {"@id": ORIGIN + "/#organization"},
        "sameAs": [u for _, u in m["social"]],
    }
    return {
        "path": m["slug"],
        "title": m.get("seo_title", m["title"]) + " | Pratt Ventures, LLC",
        "desc": m["desc"],
        "page_type": "ProfilePage",
        "og_type": "profile",
        "og_image": ORIGIN + m["img"],
        "og_alt": m["alt"],
        "trail": [("/", "Home"), ("/our-team/", "Our Team"), (m["slug"], m["name"])],
        "extra_ld": [person],
        "body": body,
    }


def page_portfolio():
    body = f"""<main id="main">
<section class="phead">
  {FIELD}
  <div class="wrap phead__in">
    {crumbs([("/", "Home"), ("/our-portfolio/", "Our Portfolio")])}
    <p class="eyebrow mt-m">Investments</p>
    <h1 class="d2 phead__ttl">Pratt Ventures Portfolio</h1>
    <p class="lede phead__lede">We make selected investments in firms matching our target criteria — across venture, machine learning, real assets, private equity and personal growth.</p>
  </div>
</section>

<section class="section">
  <div class="wrap">{pf_rows(PORTFOLIO)}</div>
</section>

{band("Exploring an opportunity?", "We provide advisory, opportunity review, and diligence services in these areas.", "/contact-us/", "Contact us")}
</main>"""
    ld = {"@type": "ItemList", "name": "Pratt Ventures Portfolio",
          "itemListElement": [
              {"@type": "ListItem", "position": i + 1,
               "item": {"@type": "Organization", "name": re.sub("&amp;", "&", it["name"]),
                        "description": it["text"],
                        **({"url": it["url"]} if it["url"] else {})}}
              for i, it in enumerate(PORTFOLIO)]}
    return {
        "path": "/our-portfolio/",
        "title": "Pratt Ventures Portfolio | Investments & Holdings",
        "desc": "The Pratt Ventures portfolio: Hatcher+, MagicOpt, commercial real-estate and private "
                "equity investments, and RocketCalm and MindFusionX personal growth programs.",
        "page_type": "CollectionPage",
        "trail": [("/", "Home"), ("/our-portfolio/", "Our Portfolio")],
        "extra_ld": [ld],
        "body": body,
    }


def page_recommend():
    body = f"""<main id="main">
<section class="phead">
  {FIELD}
  <div class="wrap phead__in">
    {crumbs([("/", "Home"), ("/we-recommend/", "Best Practices and Tools")])}
    <p class="eyebrow mt-m">Recommended Practices, Tech and Data Sources</p>
    <h1 class="d2 phead__ttl">Best Practices and Tools We Like</h1>
    <p class="lede phead__lede">Here are some technologies and data sources we’ve found helpful that aren’t as widely known as they should be…</p>
  </div>
</section>

<section class="section">
  <div class="wrap wrap--narrow" style="padding-inline:0">
    <article class="rec rv">
      <p class="eyebrow eyebrow--plain">In Progress</p>
      <h2 class="d3 mt-m">We are refreshing this list.</h2>
      <p class="body mt-m">We are always exploring tools and practices worth passing on. Stay tuned.</p>
      <p class="mt-m"><a class="link" href="/contact-us/">Suggest something <span class="arw">&rarr;</span></a></p>
    </article>
  </div>
</section>

{band("Have something we should see?", esc(TAGLINE), "/contact-us/", "Contact us")}
</main>"""
    return {
        "path": "/we-recommend/",
        "title": "Best Practices and Tools We Like | Pratt Ventures",
        "desc": "Best practices, technologies and data sources Pratt Ventures has found helpful "
                "that aren’t as widely known as they should be.",
        "trail": [("/", "Home"), ("/we-recommend/", "Best Practices and Tools")],
        "body": body,
    }


def page_contact():
    body = f"""<main id="main">
<section class="phead">
  {FIELD}
  <div class="wrap phead__in">
    {crumbs([("/", "Home"), ("/contact-us/", "Contact Us")])}
    <p class="eyebrow mt-m">Get in touch</p>
    <h1 class="d2 phead__ttl">Contact Pratt Ventures, LLC</h1>
    <p class="lede phead__lede">We look forward to hearing from you.</p>
  </div>
</section>

<section class="section">
  <div class="wrap split">
    <div class="rv">
      <p class="eyebrow">Details</p>
      <dl class="cinfo mt-l">
        <div>
          <dt>Phone</dt>
          <dd><a href="tel:{PHONE_E164}">{PHONE}</a></dd>
        </div>
        <div>
          <dt>Email</dt>
          <dd><a href="mailto:{EMAIL_L}">{EMAIL}</a></dd>
        </div>
        <div>
          <dt>Business Hours</dt>
          <dd><span class="small">{esc(HOURS)}</span></dd>
        </div>
        <div>
          <dt>Mailing Address</dt>
          <dd><span class="small">{STREET}<br>{CITY}, {REGION} {ZIP}</span></dd>
        </div>
      </dl>
    </div>

    <div class="rv rv-d1">
      <p class="eyebrow">Send a message</p>
      <form class="form mt-l" action="https://formspree.io/f/YOUR_FORM_ID" method="post">
        <p class="hp" aria-hidden="true"><label>Leave this field empty<input type="text" name="_gotcha" tabindex="-1" autocomplete="off"></label></p>
        <p class="field"><input id="f-name" name="name" type="text" autocomplete="name" required placeholder="Jane Doe"><label for="f-name">Name</label></p>
        <p class="field"><input id="f-email" name="email" type="email" autocomplete="email" required placeholder="jane@company.com"><label for="f-email">Email Address</label></p>
        <p class="field"><input id="f-phone" name="phone" type="tel" autocomplete="tel" placeholder="561-555-0100"><label for="f-phone">Phone Number (optional)</label></p>
        <p class="field"><input id="f-subject" name="subject" type="text" required placeholder="How can we help?"><label for="f-subject">Subject</label></p>
        <p class="field"><textarea id="f-message" name="message" rows="6" required placeholder="Tell us a little about your company or opportunity."></textarea><label for="f-message">Message</label></p>
        <p><button class="btn btn--solid" type="submit">Submit <span class="arw">&rarr;</span></button></p>
      </form>
    </div>
  </div>
</section>
</main>"""
    ld = {"@type": "ContactPage", "@id": ORIGIN + "/contact-us/#contact",
          "url": ORIGIN + "/contact-us/",
          "mainEntity": {"@id": ORIGIN + "/#organization"}}
    return {
        "path": "/contact-us/",
        "title": "Contact Pratt Ventures, LLC | Palm Beach Gardens, FL",
        "desc": f"Contact Pratt Ventures, LLC in {CITY}, {REGION}. Phone {PHONE}, email {EMAIL}. "
                f"Business hours are {HOURS}.",
        "trail": [("/", "Home"), ("/contact-us/", "Contact Us")],
        "extra_ld": [ld],
        "body": body,
    }


def page_login():
    body = f"""<main id="main">
<section class="phead">
  {FIELD}
  <div class="wrap phead__in">
    {crumbs([("/", "Home"), ("/login/", "Login")])}
    <p class="eyebrow mt-m">Members</p>
    <h1 class="d2 phead__ttl">Login</h1>
    <p class="lede phead__lede">Access is reserved for Pratt Ventures partners and portfolio companies.</p>
    <p class="mt-l"><a class="btn" href="/contact-us/">Request access <span class="arw">&rarr;</span></a></p>
  </div>
</section>
</main>"""
    return {
        "path": "/login/",
        "title": "Login | Pratt Ventures, LLC",
        "desc": "Member login for Pratt Ventures, LLC. Access is reserved for partners and portfolio "
                "companies — contact us to request access.",
        "robots": "noindex, follow",
        "trail": [("/", "Home"), ("/login/", "Login")],
        "body": body,
    }


def page_404():
    links = "".join(f'<li><a class="link" href="{h}">{esc(l)} <span class="arw">&rarr;</span></a></li>'
                    for h, l, _ in NAV if h != "/login/")
    body = f"""<main id="main">
<section class="phead">
  {FIELD}
  <div class="wrap phead__in">
    <p class="eyebrow mt-m">Error 404</p>
    <h1 class="d2 phead__ttl">This page could not be found.</h1>
    <p class="lede phead__lede">The page you were looking for has moved or no longer exists. Try one of these instead.</p>
    <ul class="mt-l" style="display:grid;gap:.3rem;justify-items:start">{links}</ul>
  </div>
</section>
</main>"""
    return {
        "path": "/404.html",
        "title": "Page Not Found | Pratt Ventures, LLC",
        "desc": "The page you were looking for has moved or no longer exists. Browse the Pratt Ventures "
                "firm, team, portfolio and contact pages instead.",
        "robots": "noindex, follow",
        "body": body,
    }


# ================================================================= BUILD
def main():
    pages = [page_home(), page_about(), page_team()]
    pages += [page_bio(m) for m in TEAM]
    pages += [page_portfolio(), page_recommend(), page_contact(), page_login(), page_404()]

    written = []
    for p in pages:
        html = head(p) + header(p["path"]) + p["body"] + footer()
        out = write(p["path"], html)
        written.append((p, out))

    # sitemap.xml
    prio = {"/": "1.0", "/about-us/": "0.9", "/our-portfolio/": "0.9", "/our-team/": "0.8",
            "/contact-us/": "0.8", "/we-recommend/": "0.6"}
    urls = []
    for p, _ in written:
        if "noindex" in p.get("robots", ""):
            continue
        if p["path"].endswith(".html"):
            continue
        urls.append(
            "  <url>\n"
            f"    <loc>{ORIGIN}{p['path']}</loc>\n"
            f"    <lastmod>{BUILT}</lastmod>\n"
            f"    <changefreq>monthly</changefreq>\n"
            f"    <priority>{prio.get(p['path'], '0.7')}</priority>\n"
            "  </url>")
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls) + "\n</urlset>\n", encoding="utf-8")

    if NOINDEX:
        (ROOT / "robots.txt").write_text(
            "# Staging deploy - not for indexing\n"
            "User-agent: *\n"
            "Disallow: /\n", encoding="utf-8")
    else:
        (ROOT / "robots.txt").write_text(
            "User-agent: *\n"
            "Allow: /\n"
            "Disallow: /login/\n\n"
            f"Sitemap: {ORIGIN}/sitemap.xml\n", encoding="utf-8")

    (ROOT / "site.webmanifest").write_text(json.dumps({
        "name": BRAND, "short_name": "Pratt Ventures",
        "description": TAGLINE,
        "start_url": "./", "display": "standalone",
        "background_color": "#050505", "theme_color": "#050505",
        "icons": [
            {"src": "assets/img/apple-touch-icon.png", "sizes": "180x180", "type": "image/png"},
            {"src": "assets/img/logo-512.png", "sizes": "512x512", "type": "image/png"},
            {"src": "assets/img/favicon.svg", "sizes": "any", "type": "image/svg+xml"},
        ],
    }, indent=2) + "\n", encoding="utf-8")

    (ROOT / ".nojekyll").write_text("", encoding="utf-8")
    if CNAME:
        (ROOT / "CNAME").write_text(CNAME + "\n", encoding="utf-8")

    extras = "sitemap.xml + robots.txt + site.webmanifest + .nojekyll"
    if CNAME:
        extras += " + CNAME (%s)" % CNAME
    print("Built %d pages + %s" % (len(written), extras))
    print("Canonical origin: %s%s" % (ORIGIN, "  [NOINDEX]" if NOINDEX else ""))
    for p, out in written:
        print("  %-42s -> %s" % (p["path"], out.relative_to(ROOT)))


if __name__ == "__main__":
    main()
