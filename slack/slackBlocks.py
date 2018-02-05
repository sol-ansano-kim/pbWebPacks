# Requirements webbrowserm, urllib module
#    $ pip install slackclient --user


import slackclient
from petitBloc import block
import os


class Client(object):
    def __init__(self, token):
        self.__client = slackclient.SlackClient(token)
        self.__token = token

    def token(self):
        return self.__token

    def client(self):
        return self.__client


class SlackClient(block.Block):
    def __init__(self):
        super(SlackClient, self).__init__()

    def initialize(self):
        self.addParam(str, "token")
        self.addOutput(Client, "client")

    def run(self):
        tkn = self.param("token").get()
        self.output("client").send(Client(tkn))


class SlackChannels(block.Block):
    def __init__(self):
        super(SlackChannels, self).__init__()

    def initialize(self):
        self.addInput(Client, "client")
        self.addOutput(str, "channel")

    def run(self):
        client_p = self.input("client").receive()
        if client_p.isEOP():
            return

        client = client_p.value().client()

        out = self.output("channel")
        for channel in client.api_call("channels.list").get("channels", []):
            out.send(channel.get("name", ""))


class SlackMessage(block.Block):
    def __init__(self):
        super(SlackMessage, self).__init__()

    def initialize(self):
        self.addInput(Client, "client")
        self.addInput(str, "channel")
        self.addInput(str, "message")

    def run(self):
        client = self.input("client").receive()
        if client.isEOP():
            return

        self.__client = client.value().client()

        self.__chn_eop = False
        self.__chn_dmp = None

        super(SlackMessage, self).run()

    def process(self):
        if self.__client is None:
            return False

        if not self.__chn_eop:
            chn_p = self.input("channel").receive()
            if chn_p.isEOP():
                self.__chn_eop = True
            else:
                self.__chn_dmp = chn_p.value()

        if self.__chn_dmp is None:
            return False

        msg_p = self.input("message").receive()
        if msg_p.isEOP():
            return False

        msg = msg_p.value()
        msg_p.drop()

        self.__client.api_call("chat.postMessage", text=msg, channel="#{}".format(self.__chn_dmp))

        return True


class SlackUploadFile(block.Block):
    def __init__(self):
        super(SlackUploadFile, self).__init__()

    def initialize(self):
        self.addInput(Client, "client")
        self.addInput(str, "channel")
        self.addInput(str, "filePath")

    def run(self):
        client = self.input("client").receive()
        if client.isEOP():
            return

        self.__client = client.value().client()

        self.__chn_eop = False
        self.__chn_dmp = None

        super(SlackUploadFile, self).run()

    def process(self):
        if self.__client is None:
            return False

        if not self.__chn_eop:
            chn_p = self.input("channel").receive()
            if chn_p.isEOP():
                self.__chn_eop = True
            else:
                self.__chn_dmp = chn_p.value()

        if self.__chn_dmp is None:
            return False

        file_p = self.input("filePath").receive()
        if file_p.isEOP():
            return False

        filepath = file_p.value()
        file_p.drop()

        if os.path.isfile(filepath):
            with open(filepath, "rb") as f:
                self.__client.api_call("files.upload", file=f, channels="#{}".format(self.__chn_dmp))

        return True
