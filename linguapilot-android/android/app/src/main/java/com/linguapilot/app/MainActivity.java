package com.linguapilot.app;

import android.Manifest;
import android.annotation.SuppressLint;
import android.app.DownloadManager;
import android.content.ActivityNotFoundException;
import android.content.ContentValues;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.net.ConnectivityManager;
import android.net.NetworkCapabilities;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.util.Base64;
import android.view.View;
import android.webkit.CookieManager;
import android.webkit.JavascriptInterface;
import android.webkit.PermissionRequest;
import android.webkit.URLUtil;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.ProgressBar;
import android.widget.Toast;

import androidx.activity.OnBackPressedCallback;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.ContextCompat;
import androidx.core.splashscreen.SplashScreen;

import org.json.JSONObject;

import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;

/**
 * LinguaPilot pour Android : embarque la plateforme web LinguaPilot
 * (Streamlit + HTML/JS) dans une application native, avec micro,
 * import de fichiers (CSV), téléchargement des certificats PDF,
 * écran hors-ligne et navigation par le bouton retour.
 */
public class MainActivity extends AppCompatActivity {

    private static final String JS_BRIDGE = "LinguaPilotAndroid";

    private WebView webView;
    private ProgressBar progressBar;
    private View offlineView;
    private boolean firstLoadDone = false;
    private long lastBackPress = 0;

    private ValueCallback<Uri[]> fileCallback;
    private PermissionRequest pendingWebPermission;

    private final ActivityResultLauncher<Intent> fileChooserLauncher =
            registerForActivityResult(new ActivityResultContracts.StartActivityForResult(), result -> {
                if (fileCallback == null) return;
                Uri[] uris = WebChromeClient.FileChooserParams.parseResult(result.getResultCode(), result.getData());
                fileCallback.onReceiveValue(uris);
                fileCallback = null;
            });

    private final ActivityResultLauncher<String> micPermissionLauncher =
            registerForActivityResult(new ActivityResultContracts.RequestPermission(), granted -> {
                if (pendingWebPermission == null) return;
                if (granted) {
                    pendingWebPermission.grant(new String[]{PermissionRequest.RESOURCE_AUDIO_CAPTURE});
                } else {
                    pendingWebPermission.deny();
                    toast(getString(R.string.mic_denied));
                }
                pendingWebPermission = null;
            });

    private final ActivityResultLauncher<String> storagePermissionLauncher =
            registerForActivityResult(new ActivityResultContracts.RequestPermission(), granted -> {
                if (granted) toast(getString(R.string.retry_download));
            });

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        SplashScreen splash = SplashScreen.installSplashScreen(this);
        super.onCreate(savedInstanceState);
        splash.setKeepOnScreenCondition(() -> !firstLoadDone);
        setContentView(R.layout.activity_main);

        webView = findViewById(R.id.webview);
        progressBar = findViewById(R.id.progress);
        offlineView = findViewById(R.id.offline);
        Button retry = findViewById(R.id.retry);
        retry.setOnClickListener(v -> loadApp());

        configureWebView();

        getOnBackPressedDispatcher().addCallback(this, new OnBackPressedCallback(true) {
            @Override
            public void handleOnBackPressed() {
                if (offlineView.getVisibility() != View.VISIBLE && webView.canGoBack()) {
                    webView.goBack();
                    return;
                }
                long now = System.currentTimeMillis();
                if (now - lastBackPress < 2000) {
                    finish();
                } else {
                    lastBackPress = now;
                    toast(getString(R.string.press_again));
                }
            }
        });

        if (savedInstanceState != null && webView.restoreState(savedInstanceState) != null) {
            firstLoadDone = true;
        } else {
            loadApp();
        }
    }

    @SuppressLint("SetJavaScriptEnabled")
    private void configureWebView() {
        WebSettings s = webView.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setDatabaseEnabled(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setLoadWithOverviewMode(true);
        s.setUseWideViewPort(true);
        s.setSupportZoom(false);
        s.setAllowFileAccess(false);
        s.setAllowContentAccess(true);
        s.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        s.setUserAgentString(s.getUserAgentString() + " LinguaPilotAndroid/" + BuildConfig.VERSION_NAME);

        CookieManager cookies = CookieManager.getInstance();
        cookies.setAcceptCookie(true);
        cookies.setAcceptThirdPartyCookies(webView, true);

        webView.addJavascriptInterface(new DownloadBridge(), JS_BRIDGE);
        webView.setWebViewClient(new AppWebViewClient());
        webView.setWebChromeClient(new AppChromeClient());
        webView.setDownloadListener((url, userAgent, contentDisposition, mimeType, length) ->
                handleDownload(url, userAgent, contentDisposition, mimeType));
    }

    private void loadApp() {
        if (!isOnline()) {
            showOffline();
            return;
        }
        offlineView.setVisibility(View.GONE);
        webView.setVisibility(View.VISIBLE);
        String current = webView.getUrl();
        if (current == null || current.startsWith("about:")) {
            webView.loadUrl(BuildConfig.APP_URL);
        } else {
            webView.reload();
        }
    }

    private void showOffline() {
        firstLoadDone = true;
        progressBar.setVisibility(View.GONE);
        webView.setVisibility(View.INVISIBLE);
        offlineView.setVisibility(View.VISIBLE);
    }

    private boolean isOnline() {
        ConnectivityManager cm = getSystemService(ConnectivityManager.class);
        if (cm == null) return true;
        NetworkCapabilities caps = cm.getNetworkCapabilities(cm.getActiveNetwork());
        return caps != null && caps.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET);
    }

    /** Pages qui restent dans l'application (plateforme + connexion Streamlit/GitHub/Google). */
    private boolean isInternal(Uri uri) {
        String host = uri.getHost();
        if (host == null) return false;
        String appHost = Uri.parse(BuildConfig.APP_URL).getHost();
        return host.equals(appHost)
                || host.endsWith(".streamlit.app")
                || host.endsWith("streamlit.io")
                || host.equals("github.com")
                || host.equals("accounts.google.com");
    }

    private void openExternal(Uri uri) {
        try {
            Intent intent = "intent".equals(uri.getScheme())
                    ? Intent.parseUri(uri.toString(), Intent.URI_INTENT_SCHEME)
                    : new Intent(Intent.ACTION_VIEW, uri);
            intent.addCategory(Intent.CATEGORY_BROWSABLE);
            startActivity(intent);
        } catch (ActivityNotFoundException | java.net.URISyntaxException e) {
            toast(getString(R.string.no_app));
        }
    }

    // ---------- Téléchargements (certificats PDF, exports CSV) ----------

    private void handleDownload(String url, String userAgent, String contentDisposition, String mimeType) {
        String fileName = URLUtil.guessFileName(url, contentDisposition, mimeType);
        if (url.startsWith("blob:")) {
            String js = "(function(){var x=new XMLHttpRequest();x.open('GET'," + JSONObject.quote(url) + ",true);"
                    + "x.responseType='blob';x.onload=function(){var r=new FileReader();"
                    + "r.onloadend=function(){var d=r.result;" + JS_BRIDGE + ".saveBase64(d.substring(d.indexOf(',')+1),"
                    + JSONObject.quote(mimeType == null ? "" : mimeType) + "," + JSONObject.quote(fileName) + ");};"
                    + "r.readAsDataURL(x.response);};x.send();})();";
            webView.evaluateJavascript(js, null);
            return;
        }
        if (url.startsWith("data:")) {
            int comma = url.indexOf(',');
            String meta = url.substring(5, comma);
            String mime = meta.contains(";") ? meta.substring(0, meta.indexOf(';')) : meta;
            String payload = url.substring(comma + 1);
            byte[] bytes = meta.endsWith(";base64")
                    ? Base64.decode(payload, Base64.DEFAULT)
                    : Uri.decode(payload).getBytes();
            saveBytes(bytes, mime, URLUtil.guessFileName(url, contentDisposition, mime));
            return;
        }
        if (needsLegacyStoragePermission()) return;
        try {
            DownloadManager.Request req = new DownloadManager.Request(Uri.parse(url));
            req.setMimeType(mimeType);
            String cookie = CookieManager.getInstance().getCookie(url);
            if (cookie != null) req.addRequestHeader("Cookie", cookie);
            req.addRequestHeader("User-Agent", userAgent);
            req.setTitle(fileName);
            req.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED);
            req.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, fileName);
            DownloadManager dm = getSystemService(DownloadManager.class);
            dm.enqueue(req);
            toast(getString(R.string.downloading, fileName));
        } catch (Exception e) {
            openExternal(Uri.parse(url));
        }
    }

    private boolean needsLegacyStoragePermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) return false;
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE)
                == PackageManager.PERMISSION_GRANTED) return false;
        storagePermissionLauncher.launch(Manifest.permission.WRITE_EXTERNAL_STORAGE);
        return true;
    }

    private void saveBytes(byte[] bytes, String mime, String fileName) {
        if (mime == null || mime.isEmpty()) mime = "application/octet-stream";
        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                ContentValues values = new ContentValues();
                values.put(MediaStore.Downloads.DISPLAY_NAME, fileName);
                values.put(MediaStore.Downloads.MIME_TYPE, mime);
                values.put(MediaStore.Downloads.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS + "/LinguaPilot");
                Uri uri = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values);
                if (uri == null) throw new IllegalStateException("MediaStore");
                try (OutputStream out = getContentResolver().openOutputStream(uri)) {
                    if (out == null) throw new IllegalStateException("stream");
                    out.write(bytes);
                }
            } else {
                if (needsLegacyStoragePermission()) return;
                File dir = new File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS), "LinguaPilot");
                if (!dir.exists() && !dir.mkdirs()) throw new IllegalStateException("mkdir");
                try (FileOutputStream out = new FileOutputStream(new File(dir, fileName))) {
                    out.write(bytes);
                }
            }
            toast(getString(R.string.saved, fileName));
        } catch (Exception e) {
            toast(getString(R.string.save_failed));
        }
    }

    private class DownloadBridge {
        @JavascriptInterface
        public void saveBase64(String base64, String mime, String fileName) {
            byte[] bytes = Base64.decode(base64, Base64.DEFAULT);
            runOnUiThread(() -> saveBytes(bytes, mime, fileName));
        }
    }

    // ---------- Clients WebView ----------

    private class AppWebViewClient extends WebViewClient {
        @Override
        public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
            Uri uri = request.getUrl();
            String scheme = uri.getScheme();
            if (("http".equals(scheme) || "https".equals(scheme)) && isInternal(uri)) return false;
            openExternal(uri);
            return true;
        }

        @Override
        public void onPageStarted(WebView view, String url, Bitmap favicon) {
            progressBar.setVisibility(View.VISIBLE);
        }

        @Override
        public void onPageFinished(WebView view, String url) {
            progressBar.setVisibility(View.GONE);
            firstLoadDone = true;
            CookieManager.getInstance().flush();
        }

        @Override
        public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
            if (request.isForMainFrame()) showOffline();
        }
    }

    private class AppChromeClient extends WebChromeClient {
        @Override
        public void onProgressChanged(WebView view, int newProgress) {
            progressBar.setProgress(newProgress);
            if (newProgress >= 80) firstLoadDone = true;
        }

        @Override
        public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> callback, FileChooserParams params) {
            if (fileCallback != null) fileCallback.onReceiveValue(null);
            fileCallback = callback;
            try {
                fileChooserLauncher.launch(params.createIntent());
            } catch (ActivityNotFoundException e) {
                fileCallback = null;
                toast(getString(R.string.no_app));
                return false;
            }
            return true;
        }

        @Override
        public void onPermissionRequest(PermissionRequest request) {
            boolean wantsAudio = false;
            for (String r : request.getResources()) {
                if (PermissionRequest.RESOURCE_AUDIO_CAPTURE.equals(r)) wantsAudio = true;
            }
            if (!wantsAudio) {
                request.deny();
                return;
            }
            if (ContextCompat.checkSelfPermission(MainActivity.this, Manifest.permission.RECORD_AUDIO)
                    == PackageManager.PERMISSION_GRANTED) {
                request.grant(new String[]{PermissionRequest.RESOURCE_AUDIO_CAPTURE});
            } else {
                pendingWebPermission = request;
                micPermissionLauncher.launch(Manifest.permission.RECORD_AUDIO);
            }
        }
    }

    private void toast(String msg) {
        Toast.makeText(this, msg, Toast.LENGTH_SHORT).show();
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        webView.saveState(outState);
    }

    @Override
    protected void onPause() {
        super.onPause();
        CookieManager.getInstance().flush();
    }
}
