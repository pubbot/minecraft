from twisted.application import service
from twisted.python import usage

class Options(usage.Options):
    optParameters = [
        ]

def makeService(config):
    s = service.MultiService()

    #smtpService = makeSMTPService(smtp_port, storage)
    #smtpService.setServiceParent(s)

    return s

