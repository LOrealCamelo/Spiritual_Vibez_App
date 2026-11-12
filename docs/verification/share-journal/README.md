# Readable result sharing and consistent journal actions

Web, phone browsers and the native app use matching home artwork: the deck above the tagline, the larger ball below its left side, two identical purple/yellow suns on the right, and crystal-ball pink Bright Sunshine Caps lettering. The tuning fork, approved main logo, tattooed guide and room art remain in place. New ornament PNGs have alpha transparency and identical web/native bytes.

Every illustrated feature, spread, study card and reading panel has Share and Add to journal controls. Journals remain local to the current device. Writes report success only after persistence. Native journal changes notify an already mounted Journal screen.

Sharing opens a preview containing a branded result PNG, readable full reading text, and a canonical “Get your own here” link. Natal charts include the real chart wheel; individual Tarot cards include their card image. Long chart images summarize placements while the accompanying text retains the complete result. Birth details are never encoded in invitation URLs. Membership and Stripe behavior are outside this change.

Supported phone browsers send the PNG file and caption through the system share sheet. Other browsers offer Download image and Copy text and link. Receiving apps control how they display attachments and captions. Native Android/iOS use react-native-share and react-native-view-shot; installed native apps require a new build to include these libraries.

Validation:

- 28 backend endpoint checks and 103 pytest checks pass.
- 14 frontend asset/formatter checks, 6 native asset validator checks, 37 native screen/action checks, and TypeScript pass.
- Production Metro bundles resolve on Android and iOS.
- Connected Chrome flow exercises all tool routes, chart calculations, spreads, study, journal, Moon calendar, result PNG attachments, captions, clean invite links, download/copy fallback, cancellation, and failed storage writes.
- Home layout checked at 17 widths from 320 to 3730 pixels, including desktop navigation, full logo aspect ratio, pale phone welcome and no horizontal overflow.

Screenshots and a sample downloadable chart image are included here. Physical-device share targets still need a final installed-app check after native builds finish.
