from PyQt6.QtCore import QUrl

desktop = {
    "name": "X Pro",
    "url": "https://pro.x.com",
    "icon": "https://abs.twimg.com/gryphon-client/client-web/icon-svg.ea5ff4aa.svg",
    "categories": "Network;Utility;"
}

def open(window, browser):
    browser.load(QUrl(desktop["url"]))
    window.resize(1400, 800)
    window.setWindowTitle(desktop["name"])
