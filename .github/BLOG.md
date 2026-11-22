# Blog publishing queue

Posts wait in `_queue/` and go live automatically, one at a time, at
**07:00, 10:00, 13:00, 16:00 and 19:00 London time** (5 a day).

- `.github/workflows/publish-blog.yml` runs every hour at :17 on GitHub, so your laptop can be off.
- `.github/publish.py` checks whether a slot is due. If it is, it publishes the next `_queue/` file in name order: it builds `blog/<slug>.html`, adds the card to the top of `blog.html`, adds the URL to `sitemap.xml`, then deletes the queue file.
- A missed or delayed run is caught up on the next hour. A post is never published twice.
- If the queue is empty at 07:00, the run fails and GitHub emails you. Refill the queue.

## Check the queue
`python3 .github/publish.py --check` validates every queued file: its format, any duplicate slugs, and its links. A post may only link to posts that are live or earlier in the queue.

## Add or change posts
- Edit or delete any file in `_queue/` before it publishes. You can do this on github.com.
- Rename a file to change its position in the order (`001-…` goes first).
- To publish the next post immediately: on GitHub go to Actions → "Publish queued blog post" → Run workflow. This only publishes a post if a slot is due and not yet filled.
- File format: see any file in `_queue/`. The metadata goes in the top `<!-- -->` block, and the article body (h2/p/ul/ol) follows it.

`_queue/` and `.github/` start with `_` or `.`, so GitHub Pages does not publish them.
