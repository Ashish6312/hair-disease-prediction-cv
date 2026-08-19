# HairScalpAI — iOS

WKWebView shell around the live backend (`https://hair-scalp-backend.onrender.com`),
mirroring `android-app/`: in-app navigation for backend links, external links
open in Safari, camera/photo-library upload for the scalp-image input on the
predict/camera pages, pull-to-refresh, native swipe-back, and a no-internet
retry screen.

## Requirements

Building and signing an `.ipa` requires **Xcode on a Mac** — there is no way
to cross-compile or sign an iOS app from Windows/Linux. If you don't have a
Mac, use a cloud CI service (e.g. [Codemagic](https://codemagic.io) or a
GitHub Actions `macos-latest` runner) pointed at this `ios-app/` folder; you
still need an Apple Developer Program membership ($99/yr) to sign a build for
a real device or TestFlight/App Store.

- Xcode 15+ (project uses `objectVersion 56` / Swift 5)
- iOS 15.0+ deployment target
- Apple Developer account, for device installs / TestFlight / App Store

## Open it

```
open ios-app/HairScalpAI/HairScalpAI.xcodeproj
```

Select a simulator or your device as the run destination and hit Run. First
launch on a real device: Xcode will prompt you to pick your Team under
**Signing & Capabilities** (Automatic signing is already enabled in the
project) — pick your Apple ID / team and it'll provision itself.

## What's in the project

- `HairScalpAIApp.swift` — SwiftUI app entry point.
- `ContentView.swift` — no-internet / retry screen (`NWPathMonitor`-driven),
  same signal `MainActivity#isNetworkAvailable` checks on Android.
- `WebView.swift` — the `WKWebView` wrapper: navigation policy (backend +
  file URLs load in-app, everything else opens in Safari, matching
  `MainActivity#shouldOverrideUrlLoading`), camera/photo-library upload via
  `WKUIDelegate.runOpenPanelWith`, pull-to-refresh.

No `Info.plist` file — camera/photo-library usage strings and other keys are
set via `INFOPLIST_KEY_*` build settings (Xcode 13+'s generated-Info.plist
mechanism), so there's one less hand-edited file to get wrong.

## What's filled in

- **App icon**: `Assets.xcassets/AppIcon.appiconset` has a single 1024x1024
  PNG (Xcode 14+ single-size app icon — it generates every smaller size at
  build time), redrawn to match the Android adaptive icon (teal `#14B8A6`
  background, white magnifier/crosshair mark). `ASSETCATALOG_COMPILER_APPICON_NAME`
  is set to `AppIcon` in both build configs. Swap the PNG for real artwork
  any time — it's a plain image, no Xcode needed to replace it.

## CI (`.github/workflows/ios-build.yml`)

Runs on `macos-latest` on every push/PR touching `ios-app/`:

- **No secrets set**: builds unsigned for the simulator (`CODE_SIGNING_ALLOWED=NO`)
  — just proves the project compiles, no `.ipa` comes out of this path.
- **Secrets set**: imports your distribution cert + provisioning profile,
  archives signed for device, exports a real `.ipa`, uploads it as a
  workflow artifact. Add these repo secrets (Settings → Secrets and
  variables → Actions) to unlock it:
  - `IOS_DIST_CERT_P12_BASE64` — `base64 -i Distribution.p12 | pbcopy`
  - `IOS_DIST_CERT_PASSWORD` — the `.p12` export password
  - `IOS_PROVISION_PROFILE_BASE64` — `base64 -i Profile.mobileprovision | pbcopy`
  - `IOS_EXPORT_TEAM_ID` — your 10-char Apple Developer Team ID

  All four require an active Apple Developer Program membership. The export
  method is hardcoded to `ad-hoc` (installs on devices registered in the
  provisioning profile); switch it to `app-store` in the workflow once
  you're ready to ship to TestFlight/App Store.

## Known gaps (need a Mac, can't be done from here)

- **Bundle ID**: currently `com.hairscalp.detector` (same reverse-DNS as the
  Android `applicationId` — fine, Apple's and Google's namespaces don't
  collide). Change it in Build Settings if you want it distinct, and it must
  match whatever App ID you register in your Apple Developer account before
  you can archive for TestFlight/App Store.
- **Version**: `MARKETING_VERSION` is set to `1.2` to match the Android app's
  current `versionName`. Bump both together going forward.
