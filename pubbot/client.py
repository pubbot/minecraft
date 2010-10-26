
from twisted.internet.protocol import ClientFactory
from twisted.manhole import telnet
from twisted.internet import reactor

from pubbot.protocol import MinecraftClientProtocol


class MinecraftClientFactory(ClientFactory):

    def __init__(self, username, password, session_id):
        self.username = username
        self.password = password
        self.session_id = session_id
        #super(MinecraftClientFactory, self).__init__()

    def buildProtocol(self, addr):
        p = MinecraftClientProtocol(self.username, self.password, self.session_id)

        factory = telnet.ShellFactory()
        port = reactor.listenTCP(2000, factory)
        factory.namespace['protocol'] = p
        factory.username = self.username
        factory.password = self.password

        self.shell = port

        return p

