import SwiftUI
import Network

/// Mirrors MainActivity's no-internet fallback view + retry button.
struct ContentView: View {
    private let appURL = URL(string: "https://hair-scalp-backend.onrender.com")!

    @State private var isLoading = true
    @State private var loadFailed = false
    @State private var reloadToken = 0
    @StateObject private var reachability = Reachability()

    var body: some View {
        ZStack {
            if reachability.isConnected {
                WebView(url: appURL, isLoading: $isLoading, loadFailed: $loadFailed, reloadToken: $reloadToken)
                    .ignoresSafeArea(edges: .bottom)

                if isLoading {
                    ProgressView()
                        .progressViewStyle(.circular)
                }
            }

            if !reachability.isConnected || loadFailed {
                NoInternetView {
                    reloadToken += 1
                }
            }
        }
    }
}

private struct NoInternetView: View {
    let onRetry: () -> Void

    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "wifi.slash")
                .font(.system(size: 48))
                .foregroundColor(.secondary)
            Text("No Internet Connection")
                .font(.headline)
            Text("Please check your network and try again.")
                .font(.subheadline)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 32)
            Button("Retry", action: onRetry)
                .buttonStyle(.borderedProminent)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color(.systemBackground))
    }
}

/// Minimal NWPathMonitor wrapper — same signal MainActivity#isNetworkAvailable
/// checks via ConnectivityManager before deciding whether to load the WebView
/// or show the retry screen.
final class Reachability: ObservableObject {
    @Published var isConnected = true

    private let monitor = NWPathMonitor()
    private let queue = DispatchQueue(label: "com.hairscalp.detector.reachability")

    init() {
        monitor.pathUpdateHandler = { [weak self] path in
            DispatchQueue.main.async {
                self?.isConnected = path.status == .satisfied
            }
        }
        monitor.start(queue: queue)
    }

    deinit {
        monitor.cancel()
    }
}
