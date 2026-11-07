const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const required = [
  'android/settings.gradle', 'android/app/build.gradle', 'android/gradlew',
  'android/gradle/wrapper/gradle-wrapper.jar',
  'android/app/src/main/AndroidManifest.xml',
  'android/app/src/main/java/com/spiritualvibez/MainActivity.kt',
  'android/app/src/main/java/com/spiritualvibez/MainApplication.kt',
  'ios/Podfile', 'ios/SpiritualVibez.xcodeproj/project.pbxproj',
  'ios/SpiritualVibez/AppDelegate.swift', 'ios/SpiritualVibez/Info.plist',
];
for (const file of required) {
  if (!fs.existsSync(path.join(root, file))) throw Error(`Missing native host: ${file}`);
}
for (const nested of ['android/android', 'ios/ios']) {
  if (fs.existsSync(path.join(root,nested))) throw Error(`Duplicate native host directory: ${nested}`);
}
const pkg = require('../package.json');
for (const name of Object.keys({...pkg.dependencies, ...pkg.devDependencies})) {
  if (/^expo(?:$|[-/])/.test(name)) throw Error(`Expo dependency in bare native app: ${name}`);
}
console.log('Authoritative bare native hosts: mobile/android and mobile/ios. No Expo dependencies.');
