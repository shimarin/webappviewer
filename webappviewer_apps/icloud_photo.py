from PyQt6.QtCore import QUrl

desktop = {
    "name": "iCloud Photos",
    "url": "https://www.icloud.com/photos/",
    "icon": "https://www.icloud.com/system/icloud.com/2518Project43/7e9d65d32973291b9c02698411402cbc.png",
    "categories": "Graphics;Photography;"
}

def open(window, browser):
    browser.load(QUrl(desktop["url"]))
    window.resize(1200, 900)
    window.setWindowTitle(desktop["name"])
