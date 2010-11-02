from twisted.application import service, internet
from twisted.internet import reactor, defer, protocol
import time, sys, os, re
import random
import plugins

import sys
sys.path.append("thirdparty")

__TALK_AS_ME__ = ['tepic','fuzzpedal','tomds','jc2k','mitchell']

def sibpath(path):
    root, _ = os.path.split(__file__)
    return os.path.join(root, path)

class Pubbot(object):

    plugins_dir = sibpath("plugins")

    def __init__(self):
        self.endpoints = {}

        # Load configuration
        self.config = {}
        self.load_config("default.cfg")
        self.load_config("pubbot.cfg")

        # Load plugins
        self.register_plugins()

    def load_config(self, file):
        if not os.path.exists(file):
            return
        _globals = {}
        execfile(file, _globals)
        self.config.update(_globals['config'])

    @defer.inlineCallbacks
    def on_join(self, source, user, channel):
        for pluginname, plugin in self.plugins.items():
            retval = yield defer.maybeDeferred(plugin.on_join, source, user, channel)
            if retval:
                return

    @defer.inlineCallbacks
    def on_leave(self, source, user, channel):
        """ channel may be the channel or '*' if the user quits. """
        for pluginname, plugin in self.plugins.items():
            retval = yield defer.maybeDeferred(plugin.on_leave, source, user, channel)
            if retval:
                return

    @defer.inlineCallbacks
    def on_rename(self, source, oldnick, newnick):
        for pluginname, plugin in self.plugins.items():
            retval = yield defer.maybeDeferred(plugin.on_rename, source, oldnick, newnick)
            if retval:
                return

    @defer.inlineCallbacks
    def on_commit(self, source, usr, project, rev, msg):
        for pluginname, plugin in self.plugins.items():
            retval = yield defer.maybeDeferred(plugin.on_commit, source, usr, project, rev, msg)
            if retval:
                return

    @defer.inlineCallbacks
    def on_private(self, source, msg):
        for pluginname, plugin in self.plugins.items():
            retval = yield defer.maybeDeferred(plugin.on_private, source, msg)
            if retval:
                return

    @defer.inlineCallbacks
    def on_direct(self, source, msg):
        for pluginname, plugin in self.plugins.items():
            retval = yield defer.maybeDeferred(plugin.on_direct, source, msg)
            if retval:
                return

    @defer.inlineCallbacks
    def on_message(self, source, user, msg):
        #if channel == "pubbot" and not msg.lower().startswith('meetingpint') and not msg.lower().startswith('test: '):
        #    source.msg(self.config['irc']['user'], '%s: %s' % (user, msg))
        #    if user.lower() in __TALK_AS_ME__:
        #        source.msg(self.config['irc']['channel'], msg)
        #        return

        # if channel.find("isotoma") == -1:
        #     return

        #if channel == "pubbot" and msg.lower().startswith('test: '):
        #     msg=msg[6:]
        #     channel = user

        for pluginname, plugin in self.plugins.items():
            retval = yield defer.maybeDeferred(plugin.on_message, source, user, msg)
            if retval:
                return

    @defer.inlineCallbacks
    def on_shutdown(self):
        # Notify all the plugins that we are about to shutdown, hopefully giving them time to
        #  say goodbye etc
        for pluginname, plugin in self.plugins.items():
            yield defer.maybeDeferred(plugin.on_shutdown)

    def register_endpoint(self, alias, endpoint):
        """ Register a place where a pubbot instance can talk """
        self.endpoints[alias] = endpoint

    def get_endpoint(self, alias):
        """ Return a place where pubbot can talk """
        return self.endpoints[alias]

    def register_plugins(self):
        self.plugins = {}
        self.import_modules()
        for plugin in plugins.Plugin.__subclasses__():
            self.register_plugin(plugin)

    def register_plugin(self, plugin):
        cfg = self.config.get(plugin.name, {})
        if not plugin.configured(cfg):
            return
        self.plugins[plugin.name]  = plugin(self, cfg)

    def import_modules(self):
        for root, dirs, files in os.walk(self.plugins_dir):
            for dir in dirs:
                if dir[:1] != ".":
                    self.import_module(dir)
            for file in sorted(files):
                if file.endswith(".py"):
                    self.import_module(file[:-3])
            break

    def import_module(self, module):
        if module in self.config:
            if "enabled" in self.config[module]:
                if self.config[module]["enabled"] != True:
                    print "%s is disabled, not importing" % module
                    return

        print "import_module(%s)" % module
        if sys.modules.has_key(module):
            reload(sys.modules[module])
        else:
            __import__('pubbot.plugins', {}, {}, [module])

