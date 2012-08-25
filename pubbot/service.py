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

from twisted.application import service, internet
from twisted.internet import defer
from twisted.python import usage, log
from twisted.web.client import getPage
import urllib

from pubbot.client import MinecraftClientFactory
from pubbot.session import Session

class Options(usage.Options):
    optParameters = [
        ["username", "u", "", "The minecraft account to login as "],
        ["password", "s", "", "The password to login with"],
        ["port", "p", 25565, "The port number to connect to."],
        ["host", "h", "localhost", "The host machine to connect to."],
        ]

class MinecraftClientService(service.MultiService):

    LAUNCHER_VERSION = 13

    def __init__(self, username, password, host="localhost", port=25565):
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.session = None
        service.MultiService.__init__(self)

    def startService(self):
        self._really_start()
        service.MultiService.startService(self)

    def stopService(self):
        service.MultiService.stopService(self)

    @defer.inlineCallbacks
    def _really_start(self):
        self.session = Session()
        yield self.session.login(self.username, self.password)
 
        self.factory = MinecraftClientFactory(self.username, self.password, self.session)
        self.client = internet.TCPClient(self.host, self.port, self.factory)
        self.client.setServiceParent(self)



def makeService(cfg):
    return MinecraftClientService(cfg["username"], cfg["password"], cfg["host"], int(cfg["port"]))

