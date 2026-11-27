[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/leonsis6/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/leonsis6/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

# Thursday 26 November 2026: 50 stories, 10 regions, 21 fields — Gulf on fire, Macy's parade grounded, 18 years since 26/11

Entry for the make.fun **news-image-20261126** competition ($100, top 50 paid
places; deadline 2026-11-28T00:00:00Z).

## What it is

A code-rendered 1024×1024 newspaper front page summing up Thursday
26 November 2026's world news in one picture — 50 verified stories in the
winner's template: a UTC timeline, a numbers strip, 3 illustrated leads
(Gulf on fire, Macy's 100th parade grounded, 18 years since 26/11), 12 more
illustrated stories, a world map with numbered pins 1–15, numbered briefs
16–50, a DATE CHECK of what was deliberately left out, and a source footer.

Every number, claim and headline comes from live wire reporting (Reuters, AP,
AFP, Xinhua, ONS, PTI, FIDE, BBC, CBS, dpa, ESA, CSIS) named per story in
`STORIES.md`. Nothing is invented: unverified claims were dropped, not
filled in.

## Files

- `STORIES.md` — the authoritative spec: all 50 stories with sources and
  CONFIRMED / REPORTED / CLAIM / ONGOING tags, the UTC timeline, the numbers
  strip, the DATE CHECK, and the dropped-claims list.
- `render.py` — Python + PIL only. Draws the front page from the spec and
  writes `entry.png` (1024×1024). Re-renders deterministically.
- `entry.png` — the rendered front page (1024×1024, ~172 KB).
- `main.ts` — Node 22, standard library only. Validates `entry.png` (PNG
  signature, IHDR 1024×1024, every chunk CRC, trailing IEND) and copies it
  to `$MAKEFUN_OUTPUT_DIR` (default `/output`). Refuses a truncated file.
- `prompt.txt` — the research request and the build go-ahead for this entry.

## Run

```sh
python3 render.py            # regenerate entry.png
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts   # copy to out/entry.png
```
