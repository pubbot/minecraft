from twisted.application import service, internet
from twisted.internet import defer
from twisted.python import usage
from twisted.web.client import getPage

from pubbot.client import MinecraftClientFactory

class Options(usage.Options):
    optParameters = [
        ["username", "u", "", "The minecraft account to login as "],
        ["password", "s", "", "The password to login with"],
        ["port", "p", 25565, "The port number to connect to."],
        ["host", "h", "localhost", "The host machine to connect to."],
        ]

class MinecraftClientService(service.MultiService):

    def __init__(self, username, password, host="localhost", port=25565):
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        service.MultiService.__init__(self)

    def startService(self):
        self.login()
        service.MultiService.startService(self)

    def stopService(self):
        service.MultiService.stopService(self)

    @defer.inlineCallbacks
    def login(self):
        page = yield getPage("http://www.minecraft.net/game/getversion.jsp?user=%s&password=%s&version=12" % (self.username, self.password))
        try:
            version, ticket, self.username, self.session_id, dummy = page.split(":")
        except:
            raise ValueError("Need to raise a better exception, but '%s' isnt a valid handshake.." % page)
        self.factory = MinecraftClientFactory(self.username, self.password, self.session_id)
        self.client = internet.TCPClient(self.host, self.port, self.factory)
        self.client.setServiceParent(self)



def makeService(cfg):
    return MinecraftClientService(cfg["username"], cfg["password"], cfg["host"], cfg["port"])

