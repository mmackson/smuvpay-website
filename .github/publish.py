#!/usr/bin/env python3
"""Publish the next queued blog post when a London posting slot is due.

Queue: _queue/*.html, published in filename order, one post per run.
Run hourly (GitHub Actions). `--check` validates the whole queue without publishing.
"""
import datetime as dt, html, json, re, sys
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
BLOG, QUEUE = ROOT / "blog", ROOT / "_queue"
SLOTS = (7, 10, 13, 16, 19)  # London local hours; a missed slot is caught up on the next run
FIELDS = ("slug", "title", "h1", "desc", "cat", "mins", "summary", "lede")
AUTHOR = "SMUVPAY Daily Articles Review"


def parse(path):
    m = re.match(r"<!--\n(.*?)\n-->\n(.*)", path.read_text(), re.S)
    if not m:
        sys.exit(f"{path.name}: missing <!-- metadata --> header")
    meta = dict(line.split(": ", 1) for line in m.group(1).splitlines() if line.strip())
    missing = [f for f in FIELDS if not meta.get(f)]
    if missing:
        sys.exit(f"{path.name}: missing {missing}")
    if not re.fullmatch(r"[a-z0-9-]+", meta["slug"]):
        sys.exit(f"{path.name}: bad slug {meta['slug']!r}")
    return meta, m.group(2).strip("\n")


def check(queue):
    live = {p.name for p in BLOG.glob("*.html")}
    anchors = set(re.findall(r'id="([^"]+)"', (ROOT / "index.html").read_text()))
    for path in queue:
        meta, body = parse(path)
        if f"{meta['slug']}.html" in live:
            sys.exit(f"{path.name}: slug {meta['slug']} already exists")
        for href in re.findall(r'href="([^"]+)', body):
            target, _, anchor = href.partition("#")
            if href.startswith(("http", "mailto:")):
                continue
            if target.startswith("../"):
                ok = (ROOT / target[3:]).exists() and (not anchor or target != "../index.html" or anchor in anchors)
            else:  # must be live or earlier in the queue by the time this post publishes
                ok = target in live
            if not ok:
                sys.exit(f"{path.name}: broken link {href}")
        live.add(f"{meta['slug']}.html")
    print(f"queue ok: {len(queue)} posts")


def render(meta, body, now):
    header = next(l for l in (ROOT / "blog.html").read_text().splitlines() if '<header class="site-header"' in l)
    header = re.sub(r'href="(?!https?:|mailto:)', 'href="../', header)
    ref = (BLOG / "payment-orchestrator.html").read_text()
    footer = ref[ref.index("  <footer"):ref.index("</footer>") + len("</footer>")]
    slug, date, date_h = meta["slug"], now.date().isoformat(), f"{now.day} {now:%b %Y}"
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": meta["title"], "description": meta["desc"],
          "datePublished": date, "mainEntityOfPage": f"https://smuvpay.com/blog/{slug}.html",
          "author": {"@type": "Organization", "name": AUTHOR, "url": "https://smuvpay.com/blog.html"},
          "publisher": {"@type": "Organization", "name": "SMUVPAY", "url": "https://smuvpay.com/"}}
    cta = ('<p><strong>Working through this for your business?</strong> <a href="../enquiry.html">Send us an enquiry</a> '
           'or email <a href="mailto:support@smuvpay.com">support@smuvpay.com</a> and we will map it to your volumes, markets and risk profile.</p>')
    page = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#0b2029">
  <meta name="description" content="{html.escape(meta["desc"])}">
  <title>{html.escape(meta["title"], quote=False)} | SMUVPAY</title>
  <link rel="canonical" href="https://smuvpay.com/blog/{slug}.html">
  <link rel="icon" href="../favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="../styles.css">
  <script src="../script.js" defer></script>
  <script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body class="subpage">
  <a class="skip-link" href="#main">Skip to content</a>
{header}

  <main id="main">
    <section class="guide-hero"><div class="wrap"><a class="back-link" href="../blog.html">← All insights</a><p class="eyebrow light">{meta["cat"]}</p><h1>{meta["h1"]}</h1><div class="guide-meta"><span>By {AUTHOR}</span><span>{date_h}</span><span>{meta["mins"]} min read</span><span>{meta["cat"]}</span></div></div></section>

    <article class="post"><div class="wrap post-body">
      <p class="post-lede">{meta["lede"]}</p>
{body}

      {cta}
    </div></article>
  </main>

{footer}
</body>
</html>
'''
    card = f'''        <article class="blog-card">
          <span class="blog-date">{date_h} · {meta["cat"]}</span>
          <h2><a href="blog/{slug}.html">{html.escape(meta["title"], quote=False)}</a></h2>
          <p>{meta["summary"]}</p>
          <a class="text-link" href="blog/{slug}.html">Read more <span aria-hidden="true">↗</span></a>
        </article>
'''
    return page, card


def main():
    queue = sorted(QUEUE.glob("*.html"))
    check(queue)
    if "--check" in sys.argv:
        return
    now = dt.datetime.now(ZoneInfo("Europe/London"))
    today = now.date().isoformat()
    due = sum(h <= now.hour for h in SLOTS)
    done = sum(bool(re.search(rf'"datePublished":\s*"{today}"', p.read_text())) for p in BLOG.glob("*.html"))
    if not queue and done < due and now.hour == SLOTS[0]:
        sys.exit("queue is empty: add posts to _queue/")  # failed run = one GitHub email per day
    if done >= due or not queue:
        print(f"nothing to publish: {done}/{due} slots filled today, {len(queue)} queued")
        return
    meta, body = parse(queue[0])
    page, card = render(meta, body, now)
    (BLOG / f"{meta['slug']}.html").write_text(page)

    index = ROOT / "blog.html"
    anchor = '      <div class="blog-grid">\n'
    text = index.read_text()
    assert text.count(anchor) == 1, "blog.html grid anchor not found"
    index.write_text(text.replace(anchor, anchor + card))

    sitemap = ROOT / "sitemap.xml"
    text, n = re.subn(r"(<loc>https://smuvpay.com/blog.html</loc><lastmod>)[^<]*(</lastmod></url>\n)",
                      rf"\g<1>{today}\g<2>  <url><loc>https://smuvpay.com/blog/{meta['slug']}.html</loc><lastmod>{today}</lastmod></url>\n",
                      sitemap.read_text())
    assert n == 1, "sitemap blog.html entry not found"
    sitemap.write_text(text)

    queue[0].unlink()
    print(f"published {meta['slug']} ({done + 1}/{len(SLOTS)} today, {len(queue) - 1} left in queue)")


if __name__ == "__main__":
    main()
