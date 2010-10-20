
from twisted.internet.protocol import ClientFactory

from pubbot.protocol import MinecraftClientProtocol

class MinecraftClientFactory(ClientFactory):

    def __init__(self, username, password):
        self.username = username
        self.password = password
        #super(MinecraftClientFactory, self).__init__()

    def buildProtocol(self, addr):
        return MinecraftClientProtocol(self.username, self.password)

