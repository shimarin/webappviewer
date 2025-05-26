from PyQt6.QtCore import QUrl

desktop = {
    "name": "Apple Music",
    "url": "https://music.apple.com/jp/",
    "categories": "Audio;Player;"
}

def open(window, browser):
    browser.load(QUrl(desktop["url"]))
    window.resize(1000, 600)
    window.setWindowTitle(desktop["name"])
