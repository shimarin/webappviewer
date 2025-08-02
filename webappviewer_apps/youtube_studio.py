from PyQt6.QtCore import QUrl

channel_id = "YOUE_CHANNEL_ID_HERE"  # Replace with your YouTube channel ID

desktop = {
    "icon": "https://www.gstatic.com/youtube/img/creator/favicon/favicon_48_v2.png",
    "name": "YouTube Studio",
    "url": "https://studio.youtube.com/channel/" + channel_id + "/livestreaming",
    "categories": "Network;"
}

def open(window, browser):
    browser.load(QUrl(desktop["url"]))
    window.resize(1300, 800)
    window.setWindowTitle(desktop["name"])
