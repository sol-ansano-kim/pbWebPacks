# Requirements webbrowserm, urllib module


import webbrowser
import urllib
from petitBloc import block


class WebOpen(block.Block):
    def __init__(self):
        super(WebOpen, self).__init__()

    def initialize(self):
        self.addInput(str, "url")

    def process(self):
        url_p = self.input("url").receive()
        if url_p.isEOP():
            return False

        url = url_p.value()
        url_p.drop()

        self.debug("open : {}".format(url))
        webbrowser.open_new_tab(url)


class WebDownload(block.Block):
    def __init__(self):
        super(WebDownload, self).__init__()

    def initialize(self):
        self.addInput(str, "url")
        self.addInput(str, "filePath")
        self.addOutput(str, "file")

    def process(self):
        url_p = self.input("url").receive()
        if url_p.isEOP():
            return False

        url = url_p.value()
        url_p.drop()

        file_p = self.input("filePath").receive()
        if file_p.isEOP():
            return False

        filepath = file_p.value()
        file_p.drop()
        self.debug("dowload : {} >> {}".format(url, filepath))
        urllib.urlretrieve(url, filepath)

        self.output("file").send(filepath)

        return True
