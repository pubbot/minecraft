import hashlib
import urllib

from twisted.application import service, internet
from twisted.internet import defer
from twisted.python import usage, log
from twisted.web.client import getPage


class Session(object):

    LAUNCHER_VERSION = 13

    def __init__(self):
        self.username = None
        self.uid = None
        self.session_id = None

    @defer.inlineCallbacks
    def login(self, username, password):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            }

        postdata = urllib.urlencode(dict(
            user = username,
            password = password,
            version = str(self.LAUNCHER_VERSION),
            ))

        page = yield getPage("https://login.minecraft.net", method='POST', postdata=postdata, headers=headers)
        try:
            version, ticket, self.username, self.session_id, self.uid = page.split(":")
        except:
            raise ValueError("Need to raise a better exception, but '%s' isnt a valid handshake.." % page)

        log.msg("Case corrected username is '%s'" % self.username)
        log.msg("UID is '%s'" % self.uid)
        log.msg("Session id is '%s'" % self.session_id)

    @defer.inlineCallbacks
    def join_server(self, server_id, shared_secret, public_key):
        server_hash = self._hash(server_id + shared_secret + public_key)

        log.msg("Calculuated session server hash is %s" % server_hash)

        # Name verification call...
        confirmation = yield getPage("http://session.minecraft.net/game/joinserver.jsp?user=%s&sessionId=%s&serverId=%s" % (self.username, self.session_id, server_hash), timeout=60)
        if confirmation != "OK":
            raise ValueError("Minecraft.net says: %s", confirmation)

    def _to_signed(self, value, wordlength=20*8):
        mask = long("1" * wordlength, 2)
        if value > (mask >> 1):
            return True, -((~value + 1) & mask)
        else:
            return False, value

    def _hash(self, data):
        m = hashlib.sha1()
        m.update(data)

        negative, signed = self._to_signed(long(m.hexdigest(), 16))
        hexdigest = hex(signed).lstrip("-").lstrip("0x").rstrip("L")
        if negative:
            hexdigest = "-" + hexdigest
        return hexdigest


if __name__ == "__main__":
    s = Session()
    assert s._hash("Notch") == "4ed1f46bbe04bc756bcb17c0c7ce3e4632f06a48"
    assert s._hash("simon") == "88e16a1019277b15d58faf0541e11910eb756f6"
    assert s._hash("jeb_") == "-7c9d5b0044c130109a5d7b5fb5c317c02b4e28c1"


