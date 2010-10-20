from twisted.application.service import ServiceMaker

Sample = ServiceMaker(
    "pubbot",
    "pubbot.service",
    "pubbot minecraft client",
    "pubbot"
    )

