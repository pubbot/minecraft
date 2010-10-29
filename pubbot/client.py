# Copyright 2010 John Carr
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Implement a twisted ClientFactory that uses our MinecraftProtocol

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

    def buildShell(self, p):
        """
        I build a telnet server for remote interaction with the API's

        FIXME: This is a horrid place for this code, move it!!!
        """
        factory = telnet.ShellFactory()
        port = reactor.listenTCP(2000, factory)
        factory.username = self.username
        factory.password = self.password

        # What stuff can they access out of the box?
        from pubbot.vector import Vector
        factory.namespace['protocol'] = p
        factory.namespace['world'] = p.world
        factory.namespace['entities'] = p.entities
        factory.namespace['bot'] = p.bot
        factory.namespace['Vector'] = Vector

        return port

    def buildProtocol(self, addr):
        p = MinecraftClientProtocol(self.username, self.password, self.session_id)
        self.shell = self.buildShell(p)
        return p

