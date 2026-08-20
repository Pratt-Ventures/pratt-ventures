# Pratt Ventures, LLC — Website

A static, SEO-optimised rebuild of [prattventures.com](https://prattventures.com), redesigned as a
dark, monochrome, editorial site. Copy is reproduced from the live site; the design is new.

## Design

| | |
|---|---|
| Headlines | **Playfair Display** (serif) |
| Body & subtitles | **Inter** (sans-serif) |
| Palette | Pure monochrome — `#050505` ground, `#f4f3f1` type, hairline rules at 10–34% white |
| Mode | Dark only (`color-scheme: dark`) |

No stock photography. The hero and page headers use a generated "light field" — layered radial
lights, a fine hairline grid, a slowly drifting sheen, and four sweeping SVG hairlines that draw in
on load. Photography is limited to the team portraits, all rendered greyscale.

## Structure

Legacy URLs are preserved exactly, so existing inbound links and search equity carry over.

```
/                                        Home
/about-us/                               About Pratt Ventures, LLC
/our-team/                               The Pratt Ventures Team
/daniel-hoogterp/                        Dan Hoogterp, Managing Director
/operating-partner-chris-rufe/           Chris Rufe, Operating and Technology Partner
/technology-partner-stephen-melnick/     Steve Melnick, Technology Partner
/investment-analyst-danielle-hoogterp/   Danielle Hoogterp, Investment Analyst
/our-portfolio/                          Pratt Ventures Portfolio
/we-recommend/                           We Recommend
/contact-us/                             Contact Pratt Ventures, LLC
/login/                                  Login (noindex)
/404.html                                Not found
```

## Build

Pages are generated from a single source of truth so the head, nav, footer and schema stay
consistent. Edit `build.py`, then:

```bash
python3 build.py
```

That regenerates every `index.html`, plus `sitemap.xml`, `robots.txt` and `site.webmanifest`.
Python 3.9+, no dependencies.

Preview locally:

```bash
python3 -m http.server 8899
```

## SEO

- Unique `<title>` (≤62 chars) and meta description (110–165 chars) per page
- Canonical URL, `robots`, Open Graph and Twitter card tags on every page
- JSON-LD `@graph` per page: `FinancialService` + `WebSite` + `WebPage`, plus `BreadcrumbList`,
  `Person` (bios), `ItemList` (team, portfolio) and `ContactPage` where relevant
- One `<h1>` per page, semantic heading order, visible breadcrumbs
- Descriptive `alt` text on every image; `loading`/`decoding` hints; `fetchpriority` on the LCP element
- `sitemap.xml` (excludes `/login/`), `robots.txt`, `site.webmanifest`
- Skip link, `:focus-visible` styles, `aria-current`, `prefers-reduced-motion` support
- Font preconnect + preload, `display=swap`

## Before going live

1. **Contact form** — `contact-us/index.html` posts to a Formspree placeholder. Replace
   `YOUR_FORM_ID` in `build.py` (`page_contact`) with a real endpoint, or point `action` at your own
   handler. A honeypot field (`_gotcha`) is already in place.
2. **Login** — `/login/` is a styled placeholder pointing at Contact. Wire it to the real portal.
3. **Twitter handle** — `twitter:site` is set to `@dan_hoog`; swap for a firm account if one exists.

## Notes on content

Wording is taken from the live site. Three small additions were made for structure, all easy to
change in `build.py`:

- Section labels (*The Firm*, *What We Do*, *Industry Experience*) and portfolio category tags
  (*Venture Fund*, *Machine Learning*, *Real Assets*, *Mid-Market*, *Personal Growth*, *Open*)
- The heading **Always Exploring** for the untitled "We are always exploring opportunities" item
- The home page composes its sections from About, Portfolio and Team copy — the original home page
  carried only the welcome line and tagline

Dead social links from the old site (Google+, Skype) were dropped. LinkedIn, X and Facebook remain.

## Assets

`assets/img/archive/` holds legacy logos and stock icons from the old portfolio page. They are not
referenced by the site — the portfolio is typographic — but are kept in case they are wanted later.
