from twisted.application import service
from twisted.python import usage
from twisted.application.internet import TCPClient

from pubbot.client import MinecraftClientFactory

class Options(usage.Options):
    optParameters = [
        ["username", "u", "", "The minecraft account to login as "],
        ["password", "s", "", "The password to login with"],
        ["port", "p", 25565, "The port number to connect to."],
        ["host", "h", "localhost", "The host machine to connect to."],
        ]

def makeService(options):
    s = service.MultiService()

    c = TCPClient(options["host"], int(options["port"]), MinecraftClientFactory(options["username"], options["password"]))
    c.setServiceParent(s)

    return s

