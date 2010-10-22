
from pubbot import actions

def grief(bot):
    say = actions.Say(bot, "Hello, is anybody there?")
    wait = actions.Idle(bot, 600)
    repeat = actions.Functor(bot, grief, bot)
    return (say, wait, repeat)

