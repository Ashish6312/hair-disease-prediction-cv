import SwiftUI
import WebKit
import PhotosUI
import UniformTypeIdentifiers

/// Mirrors android-app/app/src/main/java/com/hairscalp/detector/MainActivity.java:
/// a thin WKWebView shell around the live backend, with in-app navigation for
/// backend/file URLs, external links opened in Safari, camera/photo upload
/// support for the scalp-image <input type="file"> on predict/camera pages,
/// and native pull-to-refresh + swipe-back gestures.
struct WebView: UIViewRepresentable {
    let url: URL
    @Binding var isLoading: Bool
    @Binding var loadFailed: Bool
    @Binding var reloadToken: Int

    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }

    func makeUIView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()
        config.allowsInlineMediaPlayback = true

        let webView = WKWebView(frame: .zero, configuration: config)
        webView.navigationDelegate = context.coordinator
        webView.uiDelegate = context.coordinator
        webView.allowsBackForwardNavigationGestures = true

        let refresh = UIRefreshControl()
        refresh.addTarget(context.coordinator, action: #selector(Coordinator.handlePullToRefresh), for: .valueChanged)
        webView.scrollView.refreshControl = refresh
        context.coordinator.refreshControl = refresh

        context.coordinator.webView = webView
        webView.load(URLRequest(url: url))
        return webView
    }

    func updateUIView(_ webView: WKWebView, context: Context) {
        if context.coordinator.lastReloadToken != reloadToken {
            context.coordinator.lastReloadToken = reloadToken
            loadFailed = false
            webView.load(URLRequest(url: url))
        }
    }

    final class Coordinator: NSObject, WKNavigationDelegate, WKUIDelegate {
        let parent: WebView
        weak var webView: WKWebView?
        weak var refreshControl: UIRefreshControl?
        var lastReloadToken = 0

        // Completion handler for a pending <input type="file"> request, resolved
        // once the user picks/captures an image (or cancels).
        private var pendingUploadCompletion: (([URL]?) -> Void)?

        init(_ parent: WebView) {
            self.parent = parent
        }

        @objc func handlePullToRefresh() {
            webView?.reload()
        }

        // MARK: - Navigation

        func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
            guard let url = navigationAction.request.url else {
                decisionHandler(.allow)
                return
            }
            // Same pattern as MainActivity#shouldOverrideUrlLoading: keep backend
            // and local navigation inside the app, send everything else to Safari.
            if url.host?.contains("onrender.com") == true || url.isFileURL {
                decisionHandler(.allow)
                return
            }
            if navigationAction.targetFrame == nil || navigationAction.navigationType == .linkActivated {
                if url.scheme == "http" || url.scheme == "https" {
                    // External link (docs, third-party auth, etc.) — open outside the app.
                    UIApplication.shared.open(url)
                    decisionHandler(.cancel)
                    return
                }
            }
            decisionHandler(.allow)
        }

        func webView(_ webView: WKWebView, didStartProvisionalNavigation navigation: WKNavigation!) {
            parent.isLoading = true
        }

        func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
            parent.isLoading = false
            parent.loadFailed = false
            refreshControl?.endRefreshing()
        }

        func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
            failed()
        }

        func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
            failed()
        }

        private func failed() {
            parent.isLoading = false
            parent.loadFailed = true
            refreshControl?.endRefreshing()
        }

        // MARK: - File upload (camera capture / photo picker for scalp images)

        func webView(_ webView: WKWebView, runOpenPanelWith parameters: WKOpenPanelParameters, initiatedByFrame frame: WKFrameInfo, completionHandler: @escaping ([URL]?) -> Void) {
            pendingUploadCompletion = completionHandler

            guard let presenter = topViewController() else {
                completionHandler(nil)
                pendingUploadCompletion = nil
                return
            }

            let sheet = UIAlertController(title: "Upload Scalp Image", message: nil, preferredStyle: .actionSheet)

            sheet.addAction(UIAlertAction(title: "Take Photo", style: .default) { [weak self] _ in
                self?.presentCamera(from: presenter)
            })
            sheet.addAction(UIAlertAction(title: "Choose from Library", style: .default) { [weak self] _ in
                self?.presentPhotoPicker(from: presenter)
            })
            sheet.addAction(UIAlertAction(title: "Cancel", style: .cancel) { [weak self] _ in
                self?.resolveUpload(nil)
            })

            if let popover = sheet.popoverPresentationController {
                popover.sourceView = webView
                popover.sourceRect = CGRect(x: webView.bounds.midX, y: webView.bounds.midY, width: 0, height: 0)
            }
            presenter.present(sheet, animated: true)
        }

        private func presentCamera(from presenter: UIViewController) {
            guard UIImagePickerController.isSourceTypeAvailable(.camera) else {
                resolveUpload(nil)
                return
            }
            let picker = UIImagePickerController()
            picker.sourceType = .camera
            picker.delegate = self
            presenter.present(picker, animated: true)
        }

        private func presentPhotoPicker(from presenter: UIViewController) {
            var config = PHPickerConfiguration()
            config.filter = .images
            config.selectionLimit = 1
            let picker = PHPickerViewController(configuration: config)
            picker.delegate = self
            presenter.present(picker, animated: true)
        }

        fileprivate func resolveUpload(_ urls: [URL]?) {
            pendingUploadCompletion?(urls)
            pendingUploadCompletion = nil
        }

        private func topViewController() -> UIViewController? {
            guard let scene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
                  var top = scene.keyWindow?.rootViewController else { return nil }
            while let presented = top.presentedViewController {
                top = presented
            }
            return top
        }
    }
}

// MARK: - UIImagePickerControllerDelegate (camera capture)

extension WebView.Coordinator: UIImagePickerControllerDelegate, UINavigationControllerDelegate {
    func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey: Any]) {
        picker.dismiss(animated: true)
        guard let image = info[.originalImage] as? UIImage,
              let data = image.jpegData(compressionQuality: 0.9) else {
            resolveUpload(nil)
            return
        }
        let tmpURL = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString)
            .appendingPathExtension("jpg")
        do {
            try data.write(to: tmpURL)
            resolveUpload([tmpURL])
        } catch {
            resolveUpload(nil)
        }
    }

    func imagePickerControllerDidCancel(_ picker: UIImagePickerController) {
        picker.dismiss(animated: true)
        resolveUpload(nil)
    }
}

// MARK: - PHPickerViewControllerDelegate (photo library upload)

extension WebView.Coordinator: PHPickerViewControllerDelegate {
    func picker(_ picker: PHPickerViewController, didFinishPicking results: [PHPickerResult]) {
        picker.dismiss(animated: true)
        guard let provider = results.first?.itemProvider,
              provider.hasItemConformingToTypeIdentifier(UTType.image.identifier) else {
            resolveUpload(nil)
            return
        }
        provider.loadFileRepresentation(forTypeIdentifier: UTType.image.identifier) { [weak self] url, _ in
            guard let self, let url else {
                self?.resolveUpload(nil)
                return
            }
            // The URL WebKit hands back is only valid inside this callback's
            // sandbox, so copy it somewhere the upload can actually read from.
            let tmpURL = FileManager.default.temporaryDirectory
                .appendingPathComponent(UUID().uuidString)
                .appendingPathExtension(url.pathExtension.isEmpty ? "jpg" : url.pathExtension)
            do {
                try? FileManager.default.removeItem(at: tmpURL)
                try FileManager.default.copyItem(at: url, to: tmpURL)
                DispatchQueue.main.async { self.resolveUpload([tmpURL]) }
            } catch {
                DispatchQueue.main.async { self.resolveUpload(nil) }
            }
        }
    }
}
