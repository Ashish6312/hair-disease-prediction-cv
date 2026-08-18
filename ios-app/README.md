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

## Known gaps to fill in Xcode (needs a Mac, can't be done from here)

- **App icon**: no `Assets.xcassets` yet — add one (Xcode: right-click the
  `HairScalpAI` group → New File → Asset Catalog, name it `Assets.xcassets`,
  then drag in an `AppIcon` set) and set `ASSETCATALOG_COMPILER_APPICON_NAME`
  to `AppIcon` in Build Settings. The Android app's icons live at
  `android-app/app/src/main/res/mipmap-*` if you want the same artwork.
- **Bundle ID**: currently `com.hairscalp.detector` (same reverse-DNS as the
  Android `applicationId` — fine, Apple's and Google's namespaces don't
  collide). Change it in Build Settings if you want it distinct, and it must
  match whatever App ID you register in your Apple Developer account before
  you can archive for TestFlight/App Store.
- **Version**: `MARKETING_VERSION` is set to `1.2` to match the Android app's
  current `versionName`. Bump both together going forward.
