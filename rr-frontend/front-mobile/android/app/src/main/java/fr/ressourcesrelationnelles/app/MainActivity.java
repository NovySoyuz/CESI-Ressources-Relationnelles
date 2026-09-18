package fr.ressourcesrelationnelles.app;

import android.graphics.Rect;
import android.os.Bundle;
import android.webkit.JavascriptInterface;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {

    private int statusBarHeightDp = 0;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Lire la hauteur de la status bar après layout
        getWindow().getDecorView().post(() -> {
            Rect rect = new Rect();
            getWindow().getDecorView().getWindowVisibleDisplayFrame(rect);
            float density = getResources().getDisplayMetrics().density;
            statusBarHeightDp = Math.round(rect.top / density);
        });

        // Exposer la valeur à Angular via window.AndroidBridge
        getBridge().getWebView().addJavascriptInterface(new Object() {
            @JavascriptInterface
            public int getStatusBarHeight() {
                return statusBarHeightDp;
            }
        }, "AndroidBridge");
    }
}
