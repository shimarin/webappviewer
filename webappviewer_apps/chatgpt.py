from PyQt6.QtCore import QUrl

desktop = {
    "name": "ChatGPT",
    "url": "https://chatgpt.com/",
    "icon": "https://cdn.oaistatic.com/assets/favicon-180x180-od45eci6.webp",
    "categories": "Network;Utility;"
}

def open(window, browser):
    browser.load(QUrl(desktop["url"]))
    window.resize(1000, 800)
    window.setWindowTitle(desktop["name"])
