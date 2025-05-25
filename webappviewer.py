#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os,sys,logging,importlib,site

from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
from PyQt6.QtCore import QObject

default_webapp_html = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web App Viewer</title>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background-color: #f5f5f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            color: #333;
        }
    </style>
</head>
<body>
    <div>
        <h1>Web App Viewer</h1>
        <p>Place your web application module in:<pre>MODULE_PATH</pre></p>
        <p>Then place .desktop file in:<pre>APPLICATIONS_PATH</pre></p>
    </div>
</body>
</html>
""".replace("MODULE_PATH", os.path.join(site.getusersitepackages(), "webappviewer_apps")).replace("APPLICATIONS_PATH", os.path.join(os.path.expanduser("~"), ".local", "share", "applications"))

class WindowManager(QObject):
    def __init__(self):
        super().__init__()
        self.windows = []  # ウィンドウ参照を保持

    def add_window(self, window):
        self.windows.append(window)
        window.destroyed.connect(lambda: self.remove_window(window))

    def remove_window(self, window):
        if window in self.windows:
            self.windows.remove(window)

class ConsoleLogPrintableWebEnginePage(QWebEnginePage):
    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)
        self.window_manager = WindowManager()
        self.profile = profile
        self.setParent(parent)
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        print(f"JS Console [{level}]: {message} (line: {lineNumber}, source: {sourceID})")
    def createWindow(self, type):
        new_window = QMainWindow()
        new_window.resize(800, 600)
        new_browser = QWebEngineView(new_window)
        new_page = ConsoleLogPrintableWebEnginePage(self.profile, new_browser)
        new_browser.setPage(new_page)
        new_window.setCentralWidget(new_browser)
        new_window.show()
        self.window_manager.add_window(new_window)
        return new_page

class WebAppViewer(QMainWindow):
    def __init__(self, app_name, app_module):
        super().__init__()
        self.setMaximumSize(1920, 1200)
        from PyQt6.QtCore import Qt
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        profile_path = os.path.join(os.path.expanduser("~"), ".config", "webappviewer", app_name)
        storate_path = os.path.join(profile_path, "storage")
        if not os.path.exists(storate_path):
            os.makedirs(storate_path)
        cache_path = os.path.join(profile_path, "cache")
        if not os.path.exists(cache_path):
            os.makedirs(cache_path)
        self.profile = QWebEngineProfile("webappviewerProfile")
        self.profile.setPersistentStoragePath(storate_path)
        self.profile.setCachePath(os.path.join(cache_path))
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)

        # enable download
        self.profile.downloadRequested.connect(self.handle_download)

        from PyQt6.QtWebEngineCore import QWebEngineSettings
        self.browser = QWebEngineView()
        self.page = ConsoleLogPrintableWebEnginePage(self.profile, self.browser)
        self.browser.setPage(self.page)
        self.page.setBackgroundColor(Qt.GlobalColor.transparent)
        self.browser.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.browser.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        self.browser.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)
        self.setCentralWidget(self.browser)

        # setup menu
        menubar = self.menuBar()
        operation_menu = menubar.addMenu("操作")
        operation_menu.addAction("リセット", self.reset)
        operation_menu.addAction("スクリーンショット(クリップボード)", self.take_screenshot_clipboard)
        operation_menu.addAction("スクリーンショット(ファイル)", self.take_screenshot_file)
        operation_menu.addAction("閉じる", self.close)

        self.app_module = app_module
        app_module.open(self, self.browser)
        self.show()
    
    def handle_download(self, download):
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(self, "ダウンロード", f"ファイルをダウンロードしますか？\n{download.url().toString()}", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            download.accept()
            logging.info(f"ダウンロードを受け入れました: {download.url().toString()}")
        else:
            download.cancel()
            logging.info("ダウンロードがキャンセルされました。")

    def reset(self):
        self.app_module.open(self, self.browser)

    def take_screenshot_clipboard(self):
        screenshot = self.browser.grab()
        # sent it to clipboard
        from PyQt6.QtGui import QGuiApplication
        clipboard = QGuiApplication.clipboard()
        clipboard.setPixmap(screenshot)
    
    def take_screenshot_file(self):
        screenshot = self.browser.grab()
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(self, "スクリーンショットを保存", "", "PNGファイル (*.png);;JPEGファイル (*.jpg *.jpeg);;すべてのファイル (*)")
        if file_path:
            screenshot.save(file_path)
            logging.info(f"スクリーンショットを保存しました: {file_path}")
        else:
            logging.info("スクリーンショットの保存がキャンセルされました。")
    
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Webアプリケーションビューア")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--print-desktop-file", action="store_true", help="Print .desktop file")
    parser.add_argument("app_name", nargs='?', default="default", help="Application name")
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    app_module = None
    if args.app_name == "default":
        import types
        app_module = types.ModuleType("default")
        app_module.desktop = {
            "name": "Web App Viewer(default)",
            "categories": "Utility;"
        }
        app_module.open = lambda window, browser: browser.setHtml(default_webapp_html)
    else:
        app_module = importlib.import_module("webappviewer_apps." + args.app_name)

    import sys

    if args.print_desktop_file:
        executable = os.path.abspath(sys.argv[0])
        name = args.app_name
        icon = "webappviewer-" + args.app_name
        categories = "Utility;"
        if hasattr(app_module, "desktop"):
            desktop = app_module.desktop
            if "name" in desktop:
                name = desktop["name"]
            if "categories" in desktop:
                categories = desktop["categories"]

        print("# Place this file in ~/.local/share/applications/ to create a desktop entry")
        print(f"# Icon should be placed as ~/.local/share/icons/{icon}.(png|svg)")
        print(f"[Desktop Entry]\nName={name}\nType=Application\nExec={executable} {args.app_name}")
        print(f"Icon={icon}\nCategories={categories}")
        sys.exit(0)

    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("webappviewer." + args.app_name)
    app.setDesktopFileName("webappviewer-" + args.app_name)

    window = WebAppViewer(args.app_name, app_module)
    sys.exit(app.exec())
