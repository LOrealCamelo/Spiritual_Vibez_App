# Clear liquid glass and platform folders

The default interface uses transparent liquid glass on the 24 illustrated panels,
spread rows, reading surfaces, action buttons and footer navigation. The artwork
itself stays unchanged and opaque where it originally was; the glass is behind
it. Live text remains sharp. The home headline is **Your journey starts here** in
both apps.

The supplied React/Tailwind component was used as a design and implementation
reference. The web app is plain JavaScript served directly by FastAPI, so its
reflective inset shadows and SVG displacement filter are adapted in
`frontend/liquid-glass.css` and `frontend/artwork.js`. A single document-level SVG
filter avoids repeated IDs. The final Gaussian blur from the supplied snippet is
omitted to honor the explicit request for clear glass rather than frosted glass.
Browsers without SVG backdrop-filter support keep transparent reflective edges.
No React-web, shadcn, Tailwind or Radix build dependency is required for the web
launcher. A `components/ui` directory is a React project convention, not a browser
requirement; adding an unused TSX file would not change this app.

The native app uses the reusable `ClearGlassSurface.tsx` component for transparent
fills and reflective highlights. It has no blur dependency. Native surfaces do
not implement the browser's SVG backdrop refraction. Both platforms retain the
pink/purple/gold artwork and readable live labels.

## Journal storage

The journal works: it saves reflections, completed readings and moods. The web
uses browser `localStorage`; the native app uses AsyncStorage on that device.
Browser reload and native screen reopen are tested. Entries do not sync across
devices, and clearing browser/site or app data removes them. The current UI does
not use the legacy server journal endpoints and has no account-backed journal.

## Web versus Mobile

- `frontend/`: the website deployed with the Python service on Render, responsive
  to both computer and phone browsers.
- `mobile/`: the separate bare React Native app for iOS and Android.
- `docs/verification/web/desktop/`: actual website captures at desktop width.
- `docs/verification/web/phone/`: actual website captures at phone width, including
  `panels-3x.png`; these are not native mobile screenshots.
- `docs/verification/mobile/`: native simulator evidence, when available. The CI
  iOS artifact contains the actual app screenshot and launch logs. Android APK
  build artifacts are not screenshots.

The old `web-mobile-*.png` filenames meant “website shown at phone width,” not a
combined app or mixed asset. Previews are now separated by platform. Image source
packs remain separately bundled under each app's own `assets/illustrations/`.
