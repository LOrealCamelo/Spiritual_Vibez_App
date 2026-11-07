# Spiritual Vibez repair verification

Checked November 7, 2026. See the PR's checks for hosted CI results.

| Check | Local result |
| --- | --- |
| Every static local PNG reference | Pass: source syntax is parsed across all mobile JS/TS/JSX/TSX files, including unused requires and nested components. All 24 clean UI panels are present and mapped. |
| Asset-validator regressions | Missing nested requires, filename case, empty PNGs, WebP imports, absent panel mappings and CLI failure status are tested. |
| Frontend image URLs | All rendered image URLs and CSS image URLs resolve to real uploaded PNGs. No WebP references remain in app.js, styles.css or index.html. |
| TypeScript | `npm run typecheck` passes, including screen tests. |
| React Native interactions | Tests cover Home navigation, distinct study counts, single quiz attempts, spread filters/reveals, journal persistence and real Learn/Spreads tab navigation. |
| Metro Android | Production bundle and asset export pass. |
| Metro iOS | Production bundle and asset export pass. |
| Native CLI discovery | Correctly resolves mobile/android and mobile/ios. |
| Native Android build | Not verified locally: Android SDK/emulator is not installed; Gradle's initial download also failed in this cloud environment. A separate CI job runs arm64 assembleDebug and retains the debug APK for seven days. |
| Native iOS build / simulator | Unavailable in this Linux environment. Metro iOS validation does not replace Xcode compilation. |
| Physical devices | Still need checks for layout, safe areas, touch targets, keyboard behavior, offline behavior and backend connectivity on Android and iOS. |

## Artwork audit

All retained PNGs decode successfully. The three transparent character PNGs have
real alpha channels with both fully transparent and fully opaque pixels:

| Layer | Dimensions | Fully transparent pixels |
| --- | --- | --- |
| hero-mystic-cutout / cartoon_me_transparent3 | 1122 × 1402 | 528,963 |
| avatar-sunglasses / cartoon_me_transparent2 | 1254 × 1254 | 491,815 |
| avatar-tarot-headphones / cartoon_me_transparent1 | 1254 × 1254 | 610,615 |

The mobile and frontend copies of these corresponding character layers match.
Card panels preserve intrinsic aspect ratios; standalone spread art remains 4:3.
Native learning counters/bars and spread counts cover the sample values painted
into the retained artwork. No deleted image was restored from the old crop commit.
Unused legacy files are preserved on disk without retaining unused require aliases.

## Web browser evidence

Chromium loaded all 15 rendered Home images as PNGs. Desktop (1440px) and phone
(390px) layouts have no horizontal overflow. These screenshots are of the web
frontend, not a native simulator. Browser actions also passed for all six page destinations, a spread-card reveal and
local journal persistence, with no JavaScript errors or WebP network requests.
API requests use the existing offline fallback
when the backend is absent.

- [Desktop web Home](web-desktop.png)
- [Phone-width web Home](web-mobile.png)

## Native host cleanup

`diff -qr` found no content differences between the outer host trees and their
nested copies. The CLI points at the outer trees, and their dependency paths are
relative to mobile/node_modules. Only the identical nested copies were removed.
The scaffold workflow now copies directory contents and no longer regenerates
obsolete mobile images from the former web assets.

## CI versions

Validated official action metadata before updating: checkout v7, setup-node v7,
setup-java v6, setup-python v7 and upload-artifact v7 run on Node 24. Workflows
use ubuntu-24.04; the mobile workflow selects Node 24 and installs the committed
lockfile. No Python backend source or behavior changed.
