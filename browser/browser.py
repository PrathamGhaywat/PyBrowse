import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor


class AdBlocker(QWebEngineUrlRequestInterceptor):
    def __init__(self):
        super().__init__()

    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        if self.is_ad(url):
            info.block(True)

    def is_ad(self, url):
        #domains = open("ads.txt", "r")
        blocked_domains = [
            #domains
        ]

        for domain in blocked_domains:
            if domain in url:
                return True
        return False


class Browser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ad_blocker = AdBlocker()

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.setCentralWidget(self.tabs)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        navbar = QToolBar()
        self.addToolBar(navbar)

        back_btn = QAction("Back", self)
        back_btn.setStatusTip("Back to previous page")
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())
        navbar.addAction(back_btn)

        forward_btn = QAction("Forward", self)
        forward_btn.setStatusTip("Forward to next page")
        forward_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        navbar.addAction(forward_btn)

        reload_btn = QAction("Reload", self)
        reload_btn.setStatusTip("Reload page")
        reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        navbar.addAction(reload_btn)

        home_btn = QAction("Home", self)
        home_btn.setStatusTip("Go home")
        home_btn.triggered.connect(self.navigate_home)
        navbar.addAction(home_btn)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)

        stop_btn = QAction("Stop", self)
        stop_btn.setStatusTip("Stop loading current page")
        stop_btn.triggered.connect(lambda: self.tabs.currentWidget().stop())
        navbar.addAction(stop_btn)

        self.add_new_tab(QUrl('http://www.google.com'), 'Homepage')

        self.show()

    def add_new_tab(self, qurl=None, label="Blank"):
        if qurl is None:
            qurl = QUrl('')

        browser = QWebEngineView()
        browser.setUrl(qurl)
        browser.page().profile().setRequestInterceptor(self.ad_blocker)

        i = self.tabs.addTab(browser, label)

        self.tabs.setCurrentIndex(i)

        browser.urlChanged.connect(lambda qurl, browser=browser:
                                   self.update_urlbar(qurl, browser))

        browser.loadFinished.connect(lambda _, i=i, browser=browser:
                                     self.tabs.setTabText(i, browser.page().title()))

    def tab_open_doubleclick(self, i):
        if i == -1:
            self.add_new_tab()

    def current_tab_changed(self, i):
        qurl = self.tabs.currentWidget().url()
        self.update_urlbar(qurl, self.tabs.currentWidget())
        self.update_title(self.tabs.currentWidget())

    def close_current_tab(self, i):
        if self.tabs.count() < 2:
            return

        self.tabs.removeTab(i)

    def update_title(self, browser):
        if browser != self.tabs.currentWidget():
            return

        title = self.tabs.currentWidget().page().title()
        self.setWindowTitle("%s - Python Browser" % title)

    def navigate_home(self):
        self.tabs.currentWidget().setUrl(QUrl("http://www.google.com"))

    def navigate_to_url(self):
        q = QUrl(self.url_bar.text())
        if q.scheme() == "":
            q.setScheme("http")
        self.tabs.currentWidget().setUrl(q)

    def update_urlbar(self, q, browser=None):
        if browser != self.tabs.currentWidget():
            return

        self.url_bar.setText(q.toString())
        self.url_bar.setCursorPosition(0)


app = QApplication(sys.argv)
QApplication.setApplicationName("Python Browser")
window = Browser()
app.exec_()