
class Plugin(object):

    def __init__(self, parent, config):
        self.parent = parent
        self.config = config

    def on_join(self, source, user, channel):
        pass

    def on_leave(self, source, user, channel):
        pass

    def on_rename(self, source, oldnick, newnick):
        pass

    def on_commit(self, source, usr, project, rev, msg):
        pass

    def on_private(self, source, msg):
        """ Message a user privately """
        pass

    def on_direct(self, source, msg):
        """ Process a message that is public but aimed at a specific user """
        pass

    def on_message(self, source, user, msg):
        """ Process a message that is public (in a channel) """
        pass

    def on_shutdown(self):
        """ Pubbot is about to go offline, do we want to do anything about it? """
        pass

    @classmethod
    def configured(self, config):
        """ Can this plugin load?  """
        return True

