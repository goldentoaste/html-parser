from urllib.request import *
from typing import *
from html.parser import HTMLParser
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot


# https://stackoverflow.com/questions/16627227/http-error-403-in-python-3-web-scraping
stuffRequest = Request("https://nhentai.net/", headers={"User-Agent": "Mozilla/5.0"})


stuff = urlopen(stuffRequest).read()


# https://stackoverflow.com/questions/3276040/how-can-i-use-the-python-htmlparser-library-to-extract-data-from-a-specific-div
class LinksParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.inGallery = 0
        self.postTitles = []
        self.inNewPosts = 0
        self.postImages = []
        self.imageAdded = False

    def handle_starttag(self, tag, attributes):
        if tag != "div":
            return
        if self.inGallery:
            self.inGallery += 1
        if self.inNewPosts:
            self.inNewPosts += 1

        if self.inGallery and self.inNewPosts:
            return
        for name, value in attributes:
            if name == "class":
                if value == "gallery" and not self.inGallery:
                    self.inGallery = 1
                    self.imageAdded = False
                    break
                elif value == "container index-container" and not self.inNewPosts:
                    self.inNewPosts = 1

    def handle_endtag(self, tag):
        if tag == "div":
            if self.inGallery:
                self.inGallery -= 1
            elif self.inNewPosts:
                self.inNewPosts -= 1

    def handle_data(self, data):
        if self.inGallery and self.inNewPosts:
            self.postTitles.append(data)

    def handle_startendtag(
        self, tag: str, attrs: List[Tuple[str, Optional[str]]]
    ) -> None:
        if self.inGallery and not self.imageAdded:
            if self.inNewPosts:
                for name, value in attrs:
                    if name == "data-src":
                        self.postImages.append(value)
                self.imageAdded = True


class Browser(QDialog):
    def __init__(self) -> None:
        super().__init__()

        # init ui

        self.setWindowTitle("New posts from nhentai owo")
        self.setGeometry(100, 100, 400, 400)

        # https://stackoverflow.com/questions/16627227/http-error-403-in-python-3-web-scraping
        pageRequest = Request(
            "https://nhentai.net/", headers={"User-Agent": "Mozilla/5.0"}
        )
        result = urlopen(stuffRequest).read()

        parser = LinksParser()
        parser.feed(str(result))

        self.titles = parser.postTitles
        self.images = parser.postImages

    def imageFromLinks(links):
        return


parser = LinksParser()

parser.feed(str(stuff))
for line in parser.postTitles:
    print(line)

for line in parser.postImages:
    print(line)

print(f"len of titles {len(parser.postTitles)}, len of images {len(parser.postImages)}")
