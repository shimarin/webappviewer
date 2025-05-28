from PyQt6.QtCore import QUrl

desktop = {
    "name": "Trello",
    "url": "https://trello.com",
    "categories": "Office;ProjectManagement;"
}

def open(window, browser):
    browser.load(QUrl(desktop["url"]))
    window.resize(1200, 900)
    window.setWindowTitle(desktop["name"])
