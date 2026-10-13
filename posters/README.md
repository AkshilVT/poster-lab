# Poster format

One JSON file per poster, listed in `index.json` (`file` set = shown as recreated).
Coordinates are poster pixels — the size of the reference pin — so the
Overlay / Split / Difference views line up 1:1 with the original.

```jsonc
{
  "id": "tokyo", "title": "Tokyo — Asakusa", "ref": "refs/tokyo.jpg",
  "width": 735, "height": 919, "background": "#e4dad0",
  "sources": {                     // swappable photos, shared by layers
    "landmark": {
      "label": "Landmark",
      "src": "assets/tokyo/pagoda.png",   // the photo
      "cut": "assets/tokyo/pagoda.png",   // its subject cut-out (same pixel size)
      "frame": {"x": 0, "y": 0, "w": 735, "h": 919},  // where it lands (default: whole poster)
      "fit": "cover", "zoom": 1, "fx": 0.5, "fy": 0.5  // fit, zoom, pan (0..1)
    }
  },
  "layers": [                      // bottom -> top
    {"id": "band", "type": "shape", "x": 0, "y": 438, "w": 735, "h": 481, "fill": "#d82c2c"},
    {"id": "city", "type": "text", "text": "TOKYO", "font": "Anton", "size": 310.5,
     "leading": 1, "tracking": 0, "color": "#d82c2c", "x": 14, "y": 152},
    {"id": "landmark", "type": "image", "source": "landmark", "cut": true}
  ]
}
```

## Layer types

| type | draws | own keys |
|---|---|---|
| `shape` | a box | `fill` (any CSS background, or `"@source"` = that photo seen through the box), `radius` |
| `image` | a source photo (moves with the layer) | `source`, `cut` (use the cut-out) |
| `text` | live text | `text` (`\n` = new line), `font` (family in `fonts/fonts.json`), `weight`, `italic`, `size`, `leading` (×size), `tracking` (em), `align`, `case`, `color` or `fill: "@source"` (photo inside the letters), `stroke`, `shadow`, `opsz`, `stretch`, `art` |
| `svg` | inline SVG markup in the box | `svg` (use `currentColor`; colour comes from `style.color`) |

Every layer: `id`, `name`, `x`, `y`, `w`, `h`, `rotate` (deg), `scale`, `opacity`,
`blend` (mix-blend-mode), `filter` (CSS filter), `poly` ([[x,y],…] clip polygon in
poster pixels), `clip` (raw CSS clip-path), `mask` (CSS mask-image), `hidden`, `locked`,
`style` (raw CSS, camelCase or kebab-case — the escape hatch).

`art` on a text layer — `{"src", "text", "w", "h", "dx", "dy"}` — is the original
lettering traced from the pin as an alpha mask. It is shown (in the layer's
`color`, or its `fill` photo) while `text` equals `art.text`; once the words change,
the live font takes over.

Text boxes are positioned by the top-left of the line box (`leading` × `size` tall).
Photo-filled text and boxes are windows: moving them slides the window, the photo stays put.
