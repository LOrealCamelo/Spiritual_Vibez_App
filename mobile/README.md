# Spiritual Vibez — Bare React Native (NO EXPO)

This is the actual **React Native CLI** mobile client with native Android and iOS projects. It uses **PNG illustration files bundled locally** in `mobile/assets/`. The web frontend and Python FastAPI backend remain separate.

## Requirements
- Node.js 20+
- For Android: Android Studio, Android SDK, Java 17 and emulator/device
- For iOS: a Mac with Xcode and CocoaPods

## Run
```bash
cd mobile
npm install
# Android emulator: backend should run at http://localhost:8000 on host
npm start
npm run android
# macOS iOS development:
cd ios && bundle install && bundle exec pod install && cd ..
npm run ios
```

Configure the `BACKEND` value near the top of `mobile/App.tsx` when running on a **physical phone** (use your computer's LAN IP or deployed HTTPS API). Android emulator uses `10.0.2.2`; iOS simulator uses `localhost`. Before production, use your real HTTPS endpoint rather than development HTTP.

The React Native CLI project was bootstrapped from official community template **0.83.0**. There is **no Expo SDK, Expo Go or EAS**. Existing app features: Home, independent Spreads, independent Tarot Academy, Cosmos, Explore (other tools), Journal. Illustrated cards load via static `require('./assets/*.png')`, without an internet connection.

**Not a release-certified app:** backend astrology calculations require validation, authentication/privacy are missing for some backend endpoints, and Android/iOS device builds need running on supported machines.
