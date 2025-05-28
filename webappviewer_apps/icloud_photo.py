from PyQt6.QtCore import QUrl

desktop = {
    "name": "iCloud Photos",
    "url": "https://www.icloud.com/photos/",
    "categories": "Graphics;Photography;"
}

def open(window, browser):
    browser.load(QUrl(desktop["url"]))
    window.resize(1200, 900)
    window.setWindowTitle(desktop["name"])
