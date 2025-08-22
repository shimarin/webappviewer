from PyQt6.QtCore import QUrl
desktop = {
    "icon": "https://www.youtube.com/s/desktop/45ea6c88/img/logos/favicon_144x144.png",
    "name": "YouTube",
    "url": "https://youtube.com",
    "categories": "Video;" # https://specifications.freedesktop.org/menu-spec/latest/category-registry.html
}

def open(window, browser):
    browser.load(QUrl(desktop["url"]))
    window.resize(1300, 800)
    window.setWindowTitle(desktop["name"])
