from os import link
from urllib import request
from urllib.request import *
from typing import *
from html.parser import HTMLParser
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap

from PIL import Image
from PIL.ImageQt import ImageQt
from io import BytesIO

# https://stackoverflow.com/questions/16627227/http-error-403-in-python-3-web-scraping


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
        self.setGeometry(100, 100, 1200, 800)

        # https://stackoverflow.com/questions/16627227/http-error-403-in-python-3-web-scraping
        pageRequest = Request(
            "https://nhentai.net/", headers={"User-Agent": "Mozilla/5.0"}
        )
        result = urlopen(pageRequest).read()

        parser = LinksParser()
        parser.feed(str(result, "utf8"))

        self.titles = parser.postTitles
        self.images = imageFromLinks(parser.postImages)

        box = QGroupBox()

        layout = QGridLayout()

        for i in range(len(self.titles)):
            layout.addWidget(TitledImage(self.images[i], self.titles[i]), i // 5, i % 5)

        box.setLayout(layout)

        windowLayout = QVBoxLayout()
        # windowLayout.addWidget(box)

        scroll = QScrollArea()
        scroll.setWidget(box)
        scroll.setWidgetResizable(True)
        windowLayout.addWidget(scroll)
        self.setLayout(windowLayout)
        self.show()


class TitledImage(QWidget):
    def __init__(self, imageData, title):
        super().__init__()
        layout = QVBoxLayout()

        imageLabel = QLabel()
        imageLabel.setPixmap(QPixmap.fromImage(imageData).scaledToWidth(200))
        layout.addWidget(imageLabel)
        textLabel = QLabel(title)
        textLabel.setMaximumWidth(200)
        textLabel.setWordWrap(True)
        layout.addWidget(textLabel)
        self.setLayout(layout)


def imageFromLinks(links):
    return [
        ImageQt(
            Image.open(
                BytesIO(
                    request.urlopen(
                        Request(l, headers={"User-Agent": "Mozilla/5.0"})
                    ).read()
                )
            )
        )
        for l in links
    ]


# parser = LinksParser()

# parser.feed(str(stuff))
# for line in parser.postTitles:
#     print(line)

# for line in imageFromLinks(parser.postImages):
#     print(line)

# print(f"len of titles {len(parser.postTitles)}, len of images {len(parser.postImages)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Browser()
    sys.exit(app.exec_())
