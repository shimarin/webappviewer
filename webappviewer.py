#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os,sys,logging,importlib,site,re
from io import BytesIO

import requests
from bs4 import BeautifulSoup
from PIL import Image

from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QLineEdit, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage, QWebEngineNewWindowRequest
from PyQt6.QtCore import Qt, QObject
from PyQt6.QtGui import QDesktopServices

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
        <p><a href="https://www.google.com" target="_blank">Google</a>
    </div>
</body>
</html>
""".replace("MODULE_PATH", os.path.join(site.getusersitepackages(), "webappviewer_apps")).replace("APPLICATIONS_PATH", os.path.join(os.path.expanduser("~"), ".local", "share", "applications"))

def convert_to_png(image_binary):
    """
    Convert image binary data to PNG format.
    """
    try:
        img = Image.open(BytesIO(image_binary))
        img = img.convert("RGBA")  # Ensure it's in RGBA format
        output = BytesIO()
        img.save(output, format='PNG')
        return output.getvalue()
    except Exception as e:
        logging.error(f"Failed to convert image to PNG: {e}")
        return None

def save_icon_file(url, save_as):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    icons = []
    # <link rel="icon"> や <link rel="apple-touch-icon"> を取得
    for link in soup.find_all('link', rel=['icon', 'apple-touch-icon', 'shortcut icon']):
        href = link.get('href')
        sizes = link.get('sizes')
        logging.debug(f"Found icon link: {href}, sizes: {sizes}")
        
        if not href:
            continue
            
        # 絶対URLに変換
        if not href.startswith('https://'):
            href = requests.compat.urljoin(url, href)
            
        # サイズ情報を取得（例: 192x192）
        size_value = 0
        if sizes:
            match = re.match(r'(\d+)x(\d+)', sizes)
            if match:
                size_value = int(match.group(1)) * int(match.group(2))
                
        icons.append((href, size_value))
    
    if not icons:
        logging.error("No icons found on the page")
        return False
        
    # 解像度が最大のアイコンを選択（サイズ情報がない場合は面積0として扱う）
    icon_url = max(icons, key=lambda x: x[1])[0]

    # アイコンをダウンロード
    icon_response = requests.get(icon_url)
    img = convert_to_png(icon_response.content)
    if img is None:
        logging.error(f"Failed to convert icon from {icon_url} to PNG.")
        return False
    #else
    os.makedirs(os.path.dirname(save_as), exist_ok=True)
    with open(save_as, 'wb') as f:
        f.write(img)
    
    return True

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
        #self.pending_url = None
        self.newWindowRequested.connect(self.handle_new_window)
    
    def handle_new_window(self, request):
        logging.info(f"New window requested for URL: {request.requestedUrl()} in {request.destination()}")
        if request.destination() != QWebEngineNewWindowRequest.DestinationType.InNewDialog:
            QDesktopServices.openUrl(request.requestedUrl())

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        print(f"JS Console [{level}]: {message} (line: {lineNumber}, source: {sourceID})")

    def createWindow(self, type):
        if type != QWebEnginePage.WebWindowType.WebDialog:
            return super().createWindow(type)
        #else
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

        central_widget = QWidget()
        self.vbox = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # VBox content 1 : browser
        # VBox content 2 : content search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("コンテンツを検索...")
        self.search_bar.returnPressed.connect(lambda: self.browser.findText(self.search_bar.text()))
        self.vbox.addWidget(self.browser)
        self.vbox.addWidget(self.search_bar)
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.vbox.setSpacing(0)
        self.search_bar.setVisible(False)  # 初期状態では非表示

        # setup menu
        menubar = self.menuBar()
        operation_menu = menubar.addMenu("操作")
        operation_menu.addAction("リセット", self.reset)
        operation_menu.addAction("スクリーンショット(クリップボード)", self.take_screenshot_clipboard)
        operation_menu.addAction("スクリーンショット(ファイル)", self.take_screenshot_file)
        operation_menu.addAction("閉じる", self.close)
        menubar.setVisible(False)  # 初期状態では非表示

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
    
    # Ctrl+Fで検索バーを表示/非表示
    # Ctrl+Lでメニューバーを表示/非表示
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_F and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.search_bar.setVisible(not self.search_bar.isVisible())
            if self.search_bar.isVisible():
                self.search_bar.setFocus()
            else:
                self.browser.findText("")
        elif event.key() == Qt.Key.Key_L and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.menuBar().setVisible(not self.menuBar().isVisible())

def enable(app_name, app_module):
    executable = os.path.abspath(sys.argv[0])
    name = app_name
    icon_url = None
    page_url = None
    icon = "webappviewer-" + app_name
    categories = "Utility;"
    
    if hasattr(app_module, "desktop"):
        desktop = app_module.desktop
        if "name" in desktop:
            name = desktop["name"]
        if "url" in desktop:
            page_url = desktop["url"]
        if "icon" in desktop:
            icon_url = desktop["icon"]
        if "categories" in desktop:
            categories = desktop["categories"]

    with open(os.path.join(os.path.expanduser("~"), ".local", "share", "applications", f"webappviewer-{app_name}.desktop"), "w") as f:
        f.write(f"[Desktop Entry]\nName={name}\nType=Application\n")
        f.write(f"Exec=python -m webappviewer {app_name}\n")
        f.write(f"Icon={icon}\nCategories={categories}\n")
    
    icon_path = os.path.join(os.path.expanduser("~"), ".local", "share", "icons", icon + ".png")
    if icon_url is not None:
        req = requests.get(icon_url)
        if req.status_code == 200:
            with open(icon_path, "wb") as icon_file:
                icon_file.write(convert_to_png(req.content))
            logging.info(f"Icon saved to {icon_path}")
        else:
            logging.error(f"Failed to download icon from {icon_url}, status code: {req.status_code}")
    elif page_url:
        if save_icon_file(page_url, icon_path):
            logging.info(f"Icon saved to {icon_path}")
        else:
            logging.error("Failed to save icon.")
    logging.info(f"Desktop entry created at ~/.local/share/applications/webappviewer-{app_name}.desktop")   

def disable(app_name):
    done = False
    desktop_file = os.path.join(os.path.expanduser("~"), ".local", "share", "applications", f"webappviewer-{app_name}.desktop")
    icon_path = os.path.join(os.path.expanduser("~"), ".local", "share", "icons", "webappviewer-" + app_name + ".png")
    if os.path.exists(desktop_file):
        os.remove(desktop_file)
        done = True
        logging.info(f"Desktop entry removed: {desktop_file}")
    else:
        logging.warning(f"Desktop entry not found: {desktop_file}")
    if os.path.exists(icon_path):
        os.remove(icon_path)
        logging.info(f"Icon removed: {icon_path}")
    else:
        logging.warning(f"Icon not found: {icon_path}")
    return done

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Webアプリケーションビューア")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--enable", action="store_true", help="Install .desktop file and icon")
    parser.add_argument("--disable", action="store_true", help="Uninstall .desktop file and icon")
    parser.add_argument("app_name", nargs='?', default="default", help="Application name")
    args = parser.parse_args()
    if args.enable and args.disable:
        logging.error("Cannot specify both --enable and --disable options.")
        sys.exit(1)
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

    if args.enable:
        try:
            enable(args.app_name, app_module)
        except Exception as e:
            logging.error(f"Failed to enable: {e}")
            sys.exit(1)
        logging.info(f"Web Application '{args.app_name}' has been enabled.")
        sys.exit(0)
    elif args.disable:
        if disable(args.app_name):
            logging.info(f"Web Application '{args.app_name}' has been disabled.")
        sys.exit(0)

    # else
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("webappviewer." + args.app_name)
    app.setDesktopFileName("webappviewer-" + args.app_name)

    window = WebAppViewer(args.app_name, app_module)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()