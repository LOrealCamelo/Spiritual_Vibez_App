# Spiritual Vibez — Illustrated Expo Mobile

The React Native source in this folder uses the same illustrated artwork as the approved Spiritual Vibez web app. It is in GitHub on branch `design/spiritual-vibez-illustrated-mobile`, PR #3.

## Start from the repository

```bash
git clone https://github.com/LOrealCamelo/Spiritual_Vibez_App.git
cd Spiritual_Vibez_App
git checkout design/spiritual-vibez-illustrated-mobile
cd mobile
npm install --legacy-peer-deps
npx expo start
```

Set `EXPO_PUBLIC_API_URL=http://<YOUR-COMPUTER-LAN-IP>:8000/api` for a physical phone to access your FastAPI backend. `localhost` inside a phone does not point to your computer. For a desktop/web browser, the new illustrated frontend is separately served by FastAPI on port 8000.

The artwork currently loads from the public repository's raw `frontend/assets/*.webp` URLs, requiring internet access. Importing image assets into the native bundle for offline use and confirming device compatibility remain release tasks.

## What changed

- Official brand: **Spiritual Vibez — Zodiac, Tarot & More**
- Home screen uses the actual approved illustrated portrait and image-backed tiles
- Separate tabs for Spreads, Learn Tarot, Cosmos, Explore and Journal
- Tarot draws and learning connect to the existing backend, with labeled fallback samples if it is unavailable
- A comprehensive Explore directory opens the natal, draconic, BaZi, numerology, relationship, sound, ritual, cycle and other areas
- Journal notes persist on the device via AsyncStorage, not in the backend's unauthenticated journal table
- Uses Expo SDK 51 compatible `react-native-svg` and AsyncStorage versions

## Status

- GitHub CI `npx tsc --noEmit` passed.
- Native Expo simulator, physical phone and iOS/Android release build NOT verified.
- The current Expo 51 SDK is old and should be updated before App Store release.
- The backend's astrology calculations and private-data security must be reviewed before release.
- Native frequency audio playback and fully polished artwork on deep feature screens still need implementation.