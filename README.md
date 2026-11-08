# Spiritual Vibez — Zodiac, Tarot & More

This repository contains the actual web application, Python backend, and bare React Native Android/iOS source. CI evidence ZIPs contain screenshots and logs; they are **not the application download**.

## Download and run the web app on Windows

1. [Download the complete updated project ZIP](https://github.com/LOrealCamelo/Spiritual_Vibez_App/archive/refs/heads/fix/mobile-assets-metro-ci.zip).
2. Right-click the ZIP and choose **Extract All**. Do not run a file from inside the ZIP.
3. In the extracted project folder, double-click **START_WEB_WINDOWS.cmd**.
4. The launcher installs backend packages in a private `.venv-web` folder and opens the app in your browser. Keep its window open while testing; press Ctrl+C to stop.

Install [Python 3.11 or newer](https://www.python.org/downloads/windows/) first if the launcher reports that Python is missing. The first start needs internet to install packages. Node, Xcode, Android Studio, Flutter and Expo are not needed to test the **web app**.

The launcher starts the web UI and backend together. It chooses an available local port so an older server cannot accidentally display a previous copy of the app.

On macOS/Linux, run this from the extracted project folder:

```sh
python3 run_web.py
```

The updated work is on `fix/mobile-assets-metro-ci` in [PR #7](https://github.com/LOrealCamelo/Spiritual_Vibez_App/pull/7). Until it is merged, the `main` branch and any ZIP you previously downloaded from `main` retain their older files. Updating GitHub does not automatically update an existing Windows folder.

## Where the application code lives

| File/folder | Purpose |
| --- | --- |
| `frontend/index.html` | Small HTML entry point that loads the web JavaScript and stylesheet |
| `frontend/app.js` | Web screens, navigation, buttons and backend requests |
| `frontend/cosmic.js` | City-based birth forms, chart/report display and automatic daily sky |
| `frontend/styles.css` | Web layout, colors, fonts, backgrounds and responsive styles |
| `frontend/assets/` | Web PNG artwork and locally bundled fonts |
| `backend/` | FastAPI server, data and eight API router groups |
| `mobile/App.tsx` | Native mobile screens and navigation |
| `mobile/src/components/` | Illustrated native card components and live overlays |
| `mobile/assets/` | The 24 clean UI panels, standalone artwork and all 78 tarot PNGs |
| `mobile/android`, `mobile/ios` | Authoritative native host projects |

The mobile app has four primary tabs: Home, Spreads, Learn and Journal. Cosmos and Explore remain separate destinations. The store UI contains one link to [neurospicymystic.com](https://neurospicymystic.com/).

Birth charts now accept a selected city and local birth time, resolve historical timezones, and show a chart wheel and detailed report with Tropical/Sidereal choices. Cosmos loads automatically with date-aware Moon phases, ten planets and retrogrades. Spreads, lessons and quizzes display the actual uploaded tarot cards. See [methods, deck provenance and testing](docs/ASTROLOGY_AND_TAROT.md). The complete source now includes about 232 MiB of original tarot PNGs.

## Browser hosting

[Open Render deployment setup for the updated branch](https://render.com/deploy?repo=https://github.com/LOrealCamelo/Spiritual_Vibez_App/tree/fix/mobile-assets-metro-ci).

The existing `render.yaml` starts the web UI and backend together. This link opens deployment setup in your own Render account; it does not indicate that a public service has already been created. A hosted browser app does not run the native iOS binary.

## Native app and verification

See [mobile/README.md](mobile/README.md) for Android/iOS prerequisites and commands, and [verification evidence](docs/verification/README.md) for screenshots and limits.

CI validates asset resolution, TypeScript, native component actions/API routes, both Metro bundles, Android compilation, and a native iOS Release build/launch on a cloud iPhone simulator. Another check creates a complete project ZIP, extracts it and starts the application on Windows and Linux.

Simulator screenshots and logs are evidence of a test, not installable iPhone software. Real-device testing and App Store/TestFlight distribution require separate signing setup; TestFlight/App Store distribution requires active paid Apple Developer Program membership. Astronomy calculations have numerical regression tests; astrology interpretations and production authentication/privacy are not certified by UI checks.
