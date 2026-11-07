#!/usr/bin/env bash
# Native iPhone simulator startup smoke check; requires macOS/Xcode.
set -euo pipefail
app_path="$1"
evidence_dir="$2"
mkdir -p "$evidence_dir"
test -d "$app_path"
xcrun simctl list devices available --json > "$evidence_dir/available-devices.json"
device_id="$(python3 - "$evidence_dir/available-devices.json" <<'PY'
import json,sys
catalog=json.load(open(sys.argv[1]))['devices']
# Use the iOS 18.5 runtime shipped with Xcode 16.4.
for runtime, devices in catalog.items():
    if runtime.endswith('iOS-18-5'):
        iphones=[device for device in devices if device.get('isAvailable') and device['name'].startswith('iPhone')]
        if iphones:
            preferred=next((device for device in iphones if device['name']=='iPhone 16'),iphones[0])
            print(preferred['udid'])
            break
else:
    raise SystemExit('No available iPhone with the expected iOS 18.5 runtime')
PY
)"
xcrun simctl boot "$device_id"
xcrun simctl bootstatus "$device_id" -b
xcrun simctl status_bar "$device_id" override --time '9:41' --batteryState charged --batteryLevel 100
xcrun simctl install "$device_id" "$app_path"
bundle_id="$(/usr/libexec/PlistBuddy -c 'Print CFBundleIdentifier' "$app_path/Info.plist")"
launch_result="$(xcrun simctl launch --terminate-running-process "$device_id" "$bundle_id")"
printf '%s\n' "$launch_result" | tee "$evidence_dir/launch.txt"
app_pid="${launch_result##* }"
for attempt in {1..20}; do
  if ! kill -0 "$app_pid" 2>/dev/null; then
    xcrun simctl spawn "$device_id" log show --last 2m --style compact > "$evidence_dir/simulator.log" 2>&1 || true
    echo 'The native iOS app exited during the startup check' >&2
    exit 1
  fi
  sleep 1
done
xcrun simctl io "$device_id" screenshot "$evidence_dir/home.png"
xcrun simctl spawn "$device_id" log show --last 2m --style compact --predicate "process == 'SpiritualVibez'" > "$evidence_dir/simulator.log" 2>&1 || true
printf 'Booted iOS 18.5, launched %s, and verified the app remained alive for 20 seconds.\n' "$bundle_id" > "$evidence_dir/result.txt"
