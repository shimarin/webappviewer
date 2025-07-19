from PyQt6.QtCore import QUrl

desktop = {
    "name": "Grok",
    "url": "https://grok.com",
    "icon": "https://grok.com/icon-192x192.png",
    "categories": "Network;Utility;"
}

def open(window, browser):
    browser.load(QUrl(desktop["url"]))
    window.resize(1000, 800)
    window.setWindowTitle(desktop["name"])
