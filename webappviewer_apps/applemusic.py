from PyQt6.QtCore import QUrl

desktop = {
    "name": "Apple Music",
    "categories": "Audio;Player;"
}

def open(window, browser):
    browser.load(QUrl("https://music.apple.com/jp/"))
    window.resize(1000, 600)
    window.setWindowTitle("Apple Music")
