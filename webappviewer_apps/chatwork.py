from PyQt6.QtCore import QUrl

desktop = {
    "name": "Chatwork",
    "url": "https://www.chatwork.com",
    "categories": "Network;InstantMessaging;"
}

def open(window, browser):
    browser.load(QUrl(desktop["url"]))
    window.resize(1000, 600)
    window.setWindowTitle(desktop["name"])
