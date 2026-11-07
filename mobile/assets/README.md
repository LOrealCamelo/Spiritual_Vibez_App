# Spiritual Vibez — native PNG artwork

All React Native artwork is bundled from local PNG files. Android and iOS use
these same sources; there are no WebP imports, remote image requests or Expo dependencies.

`ui_cards/` contains 24 separate illustrated panels mapped by name in
`src/components/IllustratedCard.tsx`. Home, Spreads, Learn Tarot and Journal use
these panels in native touch targets. The filter chips, learning counts and
progress bars are opaque native overlays that cover sample values in the artwork.
Learning counts reflect distinct cards studied this session, not backend account progress.
Spread card counts are also native overlays over the three spread panels.

Native Home uses the standalone `home-hey-mystic-illustrated.png` greeting to
match the supplied phone reference. The skyline and transparent character layers
remain available and are composed separately in the web hero. `footer-skyline-background.png`
is a decorative background. Reset Your Energy and Grounding use the two standalone
4:3 illustrated PNGs. Images keep their original aspect ratios.

The other standalone illustrations and transparent avatars remain available on
disk. The obsolete `ARTWORK` map and all references to deleted legacy crops were
removed. No deleted crop was restored and no phone screenshot was cropped into an asset.

Run `npm run check:assets` from `mobile/` to resolve every static local PNG
require/import relative to its source, validate PNG headers, and confirm that
all 24 panels remain mapped. Static WebP image references fail this check.
