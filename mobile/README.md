# Spiritual Vibez — Zodiac, Tarot & More

This is a **bare React Native CLI** client with real Android and iOS host projects.
It uses local PNG illustrations, without Expo. The web frontend and Python backend
remain separate. The four primary tabs are Home, Spreads, Learn Tarot and Journal. Cosmos and
Explore remain independent screens opened from the Home and Journal cards.

## Requirements and installation

Use Node 24 (CI), or Node >=20.19.4. Android needs Java 17, Android SDK 36,
Build Tools 36.0.0, NDK 27.1.12297006 and a device/emulator. iOS needs macOS,
Xcode and CocoaPods.

```sh
cd mobile
npm ci
npm start
# In another terminal:
npm run android
# On macOS, for iOS:
cd ios
bundle install
bundle exec pod install
cd ..
npm run ios
```

The lockfile pins the dependency graph. In particular, `react-native-screens`
4.25.2 supports this app's RN 0.83; later 4.26+ releases target newer RN versions
and can fail Metro code generation. `.npmrc` preserves the existing legacy peer
resolution because lucide 0.468's peer range predates React 19. No broad dependency
upgrade is part of this repair.

Change `API_BASE_URL` in `src/api/spiritualVibezClient.ts` for a physical phone
(use your computer's LAN IP or a deployed HTTPS API). Android emulator defaults
to `10.0.2.2:8000/api`; iOS simulator defaults to `localhost:8000/api`.

## Checks

```sh
npm run check:assets
npm run check:native
npm run test:assets
npm run typecheck
npm test -- --runInBand
npm run bundle:android -- --bundle-output /tmp/sv.android.bundle --assets-dest /tmp/sv-android-assets
npx react-native bundle --platform ios --dev false --entry-file index.js --max-workers 2 --bundle-output /tmp/sv.ios.bundle --assets-dest /tmp/sv-ios-assets
cd android
./gradlew :app:assembleDebug --no-daemon --max-workers=2 -PreactNativeArchitectures=arm64-v8a
```

`check:assets` scans every source file, including nested TSX components. Tests
introduce new missing references to prove that CI fails even if known assets exist.
CI separately reports assets/tests/TypeScript/Metro and the real Android Gradle build.
A successful Metro bundle alone does not certify a native build or device behavior.

## Authoritative native hosts

The CLI resolves `mobile/android` and `mobile/ios`. Their Gradle/Podfile references
point to `mobile/node_modules`. The former `android/android` and `ios/ios` trees
were byte-for-byte copies; they were removed after comparing them. The scaffold
workflow now copies directory contents, preventing nested copies, and no longer
converts obsolete web artwork into mobile assets.

See [repair verification](../docs/verification/README.md) for evidence and remaining
device checks. The expanded repair also fixes ritual search and replaces dead product URLs with
the verified creator homepage. Existing astrology accuracy is not certified.
