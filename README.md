# Poster Lab

Layered HTML recreations of Pinterest-style travel posters. Every photo, cut-out and word is its own layer you can select, swap, restyle and move — upload your own photos (on macOS, Apple Vision can cut the subject out for you) to remix a poster into your own.

- Posters live in `posters/<id>.json` (layers + shared photo sources — see `posters/README.md`); their images are in `assets/`, the originals they recreate in `refs/`.
- Your edits are saved per poster on this machine only (`.fused/data/remix/`), so the shipped posters stay untouched.
- `store.py` handles saving, photo uploads and subject cut-outs; no extra Python packages needed.
