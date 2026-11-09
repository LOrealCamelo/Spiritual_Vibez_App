# Native Mobile verification

This folder is reserved for actual iOS/Android app captures, never browser images.
The **Bare React Native build checks** GitHub workflow builds Android and iOS,
launches the iOS app on an iPhone simulator and uploads the real screenshot and
launch/build logs in the `spiritual-vibez-ios-simulator` artifact. The Android
artifact is an APK, not a screenshot.

Current website previews are separately organized under `../web/desktop/` and
`../web/phone/`. A phone-width web screenshot does not demonstrate native rendering.
The application source and bundled assets for native Mobile are in `/mobile/`.
