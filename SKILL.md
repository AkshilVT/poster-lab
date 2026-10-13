---
name: poster-lab
description: Layered HTML recreations of Pinterest posters — every photo, cut-out and word is its own swappable layer.
approve: [store.py]
---
# Poster Lab

Each poster is `posters/<id>.json` (layers + shared photo sources, see `posters/README.md`);
the page saves a user's edits per poster in `.fused/data/remix/<id>.json`.

## store.py
Saved remixes, uploaded photos and Apple Vision subject cut-outs. `load` reads; `save` and `upload` write under .fused/data; `cutout` writes .fused/cache.
- Args: `op` (str, one of "load" | "save" | "upload" | "cutout", default "load"), `poster` (str, poster id — load/save), `data` (str — save: the remix as JSON text; upload: a `data:image/...;base64,` URL), `path` (str, app-relative image path — cutout)
- Returns: load → the remix object (`{}` when none); save → `{"ok": true}`; upload / cutout → `{"path": str}` (app-relative)
- Example: `{"action":"py","app":"poster-lab","file":"store.py","args":{"op":"load","poster":"tokyo"}}`
