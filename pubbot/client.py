
from twisted.internet.protocol import ClientFactory

from pubbot.protocol import MinecraftClientProtocol

class MinecraftClientFactory(ClientFactory):

    def __init__(self, username, password, session_id):
        self.username = username
        self.password = password
        self.session_id = session_id
        #super(MinecraftClientFactory, self).__init__()

    def buildProtocol(self, addr):
        return MinecraftClientProtocol(self.username, self.password, self.session_id)

