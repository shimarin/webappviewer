from PyQt6.QtCore import QUrl

def open(window, browser):
    browser.load(QUrl("https://jp.tradingview.com/"))
    window.resize(1200, 900)
    window.setWindowTitle("TradingView")
