
from pubbot import actions
from pubbot.vector import Vector

def grief(bot):
    acts =[]

    for x in range(0, 3):
        for y in range(-3, 3):
            for z in range(0, 3):
                for s in range(0, 5):
                    mine = actions.Dig(bot, bot.pos + Vector(x,y,z), s)
                    acts.append(mine)

    #pos = bot.pos + Vector(1,1,1)
    #pos = Vector(-145.71875, 72.0, -4.71875)

    #say = actions.Say(bot, "Hello, is anybody there?")
    #wait = actions.Idle(bot, 10)

    #build = actions.Build(bot, pos, 41)
    #say2 = actions.Say(bot, "I made a thing!")
    #wait2 = actions.Idle(bot, 10)

    #mine = actions.Dig(bot, pos)
    #say3 = actions.Say(bot, "My thing is gone :(")
    #wait3 = actions.Idle(bot, 10)

    #repeat = actions.Functor(bot, grief, bot)
    # return (say, wait, build, say2, wait2, mine, say3, wait3, repeat)

    return tuple(acts)

