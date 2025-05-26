from PyQt6.QtCore import QUrl

desktop = {
    "name": "ChatGPT",
    "url": "https://chatgpt.com/",
    "categories": "Network;Utility;"
}

def open(window, browser):
    browser.load(QUrl(desktop["url"]))
    window.resize(1000, 800)
    window.setWindowTitle(desktop["name"])
