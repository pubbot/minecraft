import pubbot.plugins as plugins
import random

class AyeupPlugin(plugins.Plugin):

    name = "ayeup"

    def on_join(self, source, user, channel):
        if "powe" in user.lower():
            return
        source.msg(random.choice([
                "hi %s",
                "lo %s",
                "lo. how you doing, %s?",
                "%s, we all love you",
                "Help me, Obi Wan %s, you're my only hope",
                "Wave %s, wave",
                "Give us a smile %s",
                "%s! We've missed you!",
                "%s is in the room. I have a bad feeling about this.",
                "ewwo %s",
                "yo, %s",
                "Greetings %s"
            ]) % user)
