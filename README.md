# Spiritual Vibez — Zodiac, Tarot & More

This repository contains the actual web application, Python backend, and bare React Native Android/iOS source. CI evidence ZIPs contain screenshots and logs; they are **not the application download**.

## Download and run the web app on Windows

1. [Download the complete updated project ZIP](https://github.com/LOrealCamelo/Spiritual_Vibez_App/archive/refs/heads/main.zip).
2. Right-click the ZIP and choose **Extract All**. Do not run a file from inside the ZIP.
3. In the extracted project folder, double-click **START_WEB_WINDOWS.cmd**.
4. The launcher installs backend packages in a private `.venv-web` folder and opens the app in your browser. Keep its window open while testing; press Ctrl+C to stop.

Install [Python 3.11 or newer](https://www.python.org/downloads/windows/) first if the launcher reports that Python is missing. The first start needs internet to install packages. Node, Xcode, Android Studio, Flutter and Expo are not needed to test the **web app**.

The launcher starts the web UI and backend together. It chooses an available local port so an older server cannot accidentally display a previous copy of the app.

On macOS/Linux, run this from the extracted project folder:

```sh
python3 run_web.py
```

The default `main` branch contains the updated app. Updating GitHub does not
update an existing Windows folder; download and extract the current ZIP to replace
an older copy.

## Where the application code lives

| File/folder | Purpose |
| --- | --- |
| `frontend/index.html` | Small HTML entry point that loads the web JavaScript and stylesheet |
| `frontend/app.js` | Web screens, navigation, buttons and backend requests |
| `frontend/artwork.js` | New illustration definitions and live panel markup |
| `frontend/cosmic.js` | City-based birth forms, chart/report display and automatic daily sky |
| `frontend/styles.css`, `frontend/liquid-glass.css` | Responsive layout and the clear liquid-glass treatment |
| `frontend/assets/` | Web PNG artwork and locally bundled fonts |
| `backend/` | FastAPI server, data and eight API router groups |
| `mobile/App.tsx` | Native mobile screens and navigation |
| `mobile/src/components/` | Illustrated native panels and live text/progress |
| `mobile/assets/` | New illustration packs, standalone artwork and all 78 tarot PNGs |
| `mobile/android`, `mobile/ios` | Authoritative native host projects |

[All 24 interface panels](docs/UI_ARTWORK_PLACEMENT.md) have been rebuilt with 16 new illustrations and live text, borders, arrows, vibe filters and learning progress. The old blurry panel crops have been removed from Web and Mobile assets.

The mobile app has four primary tabs: Home, Spreads, Learn and Journal. Cosmos and Explore remain separate destinations. The store UI contains one link to [neurospicymystic.com](https://neurospicymystic.com/).

Birth charts now accept a selected city and local birth time, resolve historical timezones, and show a chart wheel and detailed report with Tropical/Sidereal choices. Cosmos loads automatically with date-aware Moon phases, ten planets and retrogrades. Spreads, lessons and quizzes display the actual uploaded tarot cards. See [methods, deck provenance and testing](docs/ASTROLOGY_AND_TAROT.md). The app uses 648 × 1080 PNG display copies totaling about 96 MiB; your full-resolution Drive originals remain unchanged.

## Browser hosting

[Open the live Web app](https://spiritual-vibez-app.onrender.com).

Render runs the Python service and serves `frontend/` from the same application.
Its deployment branch should be `main`; a GitHub merge triggers a new build when
automatic deploys are enabled. The native iOS/Android app is separately built from
`mobile/`. A hosted browser app does not run the native binary.

The interface uses [clear liquid glass](docs/CLEAR_GLASS.md) with the headline
**Your journey starts here**. The journal saves locally in the browser or native
device; it does not currently sync between devices. Preview folders clearly
separate Web desktop, Web phone and native Mobile evidence.

## Native app and verification

See [mobile/README.md](mobile/README.md) for Android/iOS prerequisites and commands, and [verification evidence](docs/verification/README.md) for screenshots and limits.

CI validates asset resolution, TypeScript, native component actions/API routes, both Metro bundles, Android compilation, and a native iOS Release build/launch on a cloud iPhone simulator. Another check creates a complete project ZIP, extracts it and starts the application on Windows and Linux.

Simulator screenshots and logs are evidence of a test, not installable iPhone software. Real-device testing and App Store/TestFlight distribution require separate signing setup; TestFlight/App Store distribution requires active paid Apple Developer Program membership. Astronomy calculations have numerical regression tests; astrology interpretations and production authentication/privacy are not certified by UI checks.
