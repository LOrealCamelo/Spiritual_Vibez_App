# Spiritual Vibez — native artwork

The 24 interface panels are rebuilt with **16 new original illustrations and live
native text, gradients, borders, arrows, filters and progress controls**. The old
screenshot-sized `ui_cards/` PNGs were removed, along with their web copies.

`illustrations/` contains four unmodified **1254 × 1254 RGBA PNG** illustration
packs. Each has four separate icons in a regular 2 × 2 layout, giving a 627 × 627
source region for each icon. `PanelIllustration` selects a region at display time;
it does not enlarge a demo crop or produce a resized source file. Icons display at
72–112 logical pixels in the native app, leaving sufficient source pixels for
high-density screens. The text and panel frame are always native elements.

`src/data/uiPanels.json` defines all 24 panels. `IllustratedCard.tsx` has the four
static Metro requires and the native rendering. Web uses byte-identical PNG packs
and matching definitions in `frontend/artwork.js`; regression checks compare both.
`illustrations/manifest.json` records dimensions, transparency and SHA-256 hashes.

Learning progress reflects distinct cards studied this session. Spread counts come
from the actual catalog, and filters use real labeled buttons. No sample counts
or labels are painted into the new artwork.

The larger supplied character, greeting, skyline and favorite-spread illustrations
remain in use. All 78 tarot card PNGs remain separate, unchanged by this panel
rebuild. These sources are bundled locally; no Expo or remote image dependency is
introduced.

Run `npm run check:assets` to validate every local PNG reference, the 24 definitions
and their static illustration mappings. See [panel placements and actions](../../docs/UI_ARTWORK_PLACEMENT.md).
