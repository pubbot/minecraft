from collections import namedtuple

from construct import Struct, Container, Embed, Enum, MetaField
from construct import MetaArray, If, Switch, Const, Peek
from construct import OptionalGreedyRange, RepeatUntil
from construct import Flag, PascalString, Adapter, Padding
from construct import UBInt8, UBInt16, UBInt32, UBInt64
from construct import SBInt8, SBInt16, SBInt32, SBInt64
from construct import BFloat32, BFloat64
from construct import BitStruct, BitField
from construct import StringAdapter, LengthValueAdapter, Sequence

DUMP_ALL_PACKETS = False

# Strings.
# This one is a UCS2 string, which effectively decodes single writeChar()
# invocations. We need to import the encoding for it first, though.
from pubbot.encodings import ucs2
from codecs import register
register(ucs2)

class DoubleAdapter(LengthValueAdapter):

    def _encode(self, obj, context):
        return len(obj) / 2, obj

def AlphaString(name):
    return StringAdapter(
        DoubleAdapter(
            Sequence(name,
                UBInt16("length"),
                MetaField("data", lambda ctx: ctx["length"] * 2),
            )
        ),
        encoding="ucs2",
    )

def SecretString(name):
    return PascalString(name, length_field=UBInt16("length"), encoding=None)

# Boolean converter.
def Bool(*args, **kwargs):
    return Flag(*args, default=True, **kwargs)

# Flying, position, and orientation, reused in several places.
grounded = Struct("grounded", UBInt8("grounded"))
position = Struct("position",
    BFloat64("x"),
    BFloat64("y"),
    BFloat64("stance"),
    BFloat64("z")
)
orientation = Struct("orientation", BFloat32("rotation"), BFloat32("pitch"))

# Notchian item packing
items = Struct("items",
    SBInt16("primary"),
    If(lambda context: context["primary"] >= 0,
        Embed(Struct("item_information",
            UBInt8("count"),
            UBInt16("secondary"),
        )),
    ),
)

Metadata = namedtuple("Metadata", "type value")
metadata_types = ["byte", "short", "int", "float", "string", "slot",
    "coords"]

# Metadata adaptor.
class MetadataAdapter(Adapter):

    def _decode(self, obj, context):
        d = {}
        for m in obj.data:
            d[m.id.second] = Metadata(metadata_types[m.id.first], m.value)
        return d

    def _encode(self, obj, context):
        c = Container(data=[], terminator=None)
        for k, v in obj.iteritems():
            t, value = v
            d = Container(
                id=Container(first=metadata_types.index(t), second=k),
                value=value,
                peeked=None)
            c.data.append(d)
        c.data[-1].peeked = 127
        return c

# Metadata inner container.
metadata_switch = {
    0: UBInt8("value"),
    1: UBInt16("value"),
    2: UBInt32("value"),
    3: BFloat32("value"),
    4: AlphaString("value"),
    5: Struct("slot",
        UBInt16("primary"),
        UBInt8("count"),
        UBInt16("secondary"),
    ),
    6: Struct("coords",
        UBInt32("x"),
        UBInt32("y"),
        UBInt32("z"),
    ),
}

# Metadata subconstruct.
metadata = MetadataAdapter(
    Struct("metadata",
        RepeatUntil(lambda obj, context: obj["peeked"] == 0x7f,
            Struct("data",
                BitStruct("id",
                    BitField("first", 3),
                    BitField("second", 5),
                ),
                Switch("value", lambda context: context["id"]["first"],
                    metadata_switch),
                Peek(UBInt8("peeked")),
            ),
        ),
        Const(UBInt8("terminator"), 0x7f),
    ),
)

# Build faces, used during dig and build.
faces = {
    "noop": -1,
    "-y": 0,
    "+y": 1,
    "-z": 2,
    "+z": 3,
    "-x": 4,
    "+x": 5,
}
face = Enum(SBInt8("face"), **faces)

# World dimension.
dimensions = {
    "earth": 0,
    "sky": 1,
    "nether": 255,
}
dimension = Enum(UBInt8("dimension"), **dimensions)

# Possible effects.
# XXX these names aren't really canonized yet
effect = Enum(UBInt8("effect"),
    move_fast=1,
    move_slow=2,
    dig_fast=3,
    dig_slow=4,
    damage_boost=5,
    heal=6,
    harm=7,
    jump=8,
    confusion=9,
    regenerate=10,
    resistance=11,
    fire_resistance=12,
    water_resistance=13,
    invisibility=14,
    blindness=15,
    night_vision=16,
    hunger=17,
    weakness=18,
    poison=19,
)

slot = Struct("slot",
    SBInt16("id"),
    If(lambda context: context["id"] >= 0,
        Embed(Struct("item_information",
            UBInt8("count"),
            UBInt16("info"),
            SBInt16("size"),
            If(lambda context: context["size"] >= 0,
                MetaArray(lambda ctx: ctx.size, SBInt8("data"))
            )
        ))
    )
)

gamemode = Enum(UBInt32("mode"),
    survival=0,
    creative=1,
    adventure=2,
    )
 
# The actual packet list.
packets = {
    0: Struct("ping",
        UBInt32("pid"),
    ),
    1: Struct("login",
        UBInt32("eid"),
        AlphaString("level_type"),
        UBInt8("mode"),
        UBInt8("dimension"),
        UBInt8("difficulty"),
        UBInt8("notused"),
        UBInt8("max_players"),
    ),
    2: Struct("handshake",
        UBInt8("protocol"),
        AlphaString("username"),
        AlphaString("server_host"),
        UBInt32("server_port"),
    ),
    3: Struct("chat",
        AlphaString("message"),
    ),
    4: Struct("time",
        UBInt64("timestamp"),
    ),
    5: Struct("entity-equipment",
        UBInt32("eid"),
        UBInt16("slot"),
        slot,
    ),
    6: Struct("spawn",
        SBInt32("x"),
        SBInt32("y"),
        SBInt32("z"),
    ),
    7: Struct("use",
        UBInt32("eid"),
        UBInt32("target"),
        Enum(UBInt8("button"),
            left=0,
            right=1,
            ),
    ),
    8: Struct("update-health",
        UBInt16("hp"),
        UBInt16("fp"),
        BFloat32("saturation"),
    ),
    9: Struct("respawn",
        dimension,
        UBInt8("difficulty"),
        gamemode,
        Enum(UBInt8("gamemode"),
            survival=0,
            creative=1,
            adventure=2,
            ),
        UBInt16("height"),
        AlphaString("level_type"),
    ),
    10: grounded,
    11: Struct("position", position, grounded),
    12: Struct("orientation", orientation, grounded),
    13: Struct("location", position, orientation, grounded),
    14: Struct("digging",
        Enum(UBInt8("state"),
            started=0,
            digging=1,
            stopped=2,
            broken=3,
            dropped=4,
            shooting=5,
        ),
        SBInt32("x"),
        UBInt8("y"),
        SBInt32("z"),
        face,
    ),
    15: Struct("build",
        SBInt32("x"),
        UBInt8("y"),
        SBInt32("z"),
        face,
        slot,
        UBInt8("cursor_x"),
        UBInt8("cursor_y"),
        UBInt8("cursor_z"),
    ),
    16: Struct("equip",
        UBInt16("item"),
    ),
    17: Struct("bed",
        UBInt32("eid"),
        UBInt8("unknown"),
        SBInt32("x"),
        UBInt8("y"),
        SBInt32("z"),
    ),
    18: Struct("animate",
        UBInt32("eid"),
        Enum(UBInt8("animation"),
            noop=0,
            arm=1,
            hit=2,
            leave_bed=3,
            eat=5,
            unknown=102,
            crouch=104,
            uncrouch=105,
        ),
    ),
    19: Struct("action",
        UBInt32("eid"),
        UBInt8("action"),
    ),
    20: Struct("spawn-named-entity",
        UBInt32("eid"),
        AlphaString("username"),
        SBInt32("x"),
        SBInt32("y"),
        SBInt32("z"),
        UBInt8("yaw"),
        UBInt8("pitch"),
        SBInt16("item"),
        metadata,
    ),
    21: Struct("spawn-pickup",
        UBInt32("eid"),
        UBInt16("primary"),
        UBInt8("count"),
        UBInt16("secondary"),
        SBInt32("x"),
        SBInt32("y"),
        SBInt32("z"),
        UBInt8("yaw"),
        UBInt8("pitch"),
        UBInt8("roll"),
    ),
    22: Struct("collect",
        UBInt32("eid"),
        UBInt32("collector"),
    ),
    23: Struct("spawn-vehicle",
        UBInt32("eid"),
        UBInt8("type"),
        #Enum(UBInt8("type"),
        #    boat=1,
        #    minecart=10,
        #    storage_cart=11,
        #    powered_cart=12,
        #    tnt=50,
        #    arrow=60,
        #    snowball=61,
        #    egg=62,
        #    sand=70,
        #    gravel=71,
        #    fishing_float=90,
        #),
        SBInt32("x"),
        SBInt32("y"),
        SBInt32("z"),
        SBInt32("thrower"),
        If(lambda context: context["thrower"] > 0,
            Embed(Struct("fireball",
                UBInt16("dx"),
                UBInt16("dy"),
                UBInt16("dz"),
            )),
        ),
    ),
    24: Struct("spawn-mob",
        UBInt32("eid"),
        UBInt8("type"),
        #Enum(UBInt8("type"), **{
        #    "Creeper": 50,
        #    "Skeleton": 51,
        #    "Spider": 52,
        #    "GiantZombie": 53,
        #    "Zombie": 54,
        #    "Slime": 55,
        #    "Ghast": 56,
        #    "ZombiePig": 57,
        #    "Enderman": 58,
        #    "CaveSpider": 59,
        #    "Silverfish": 60,
        #    "Blaze": 61,
        #    "MagmaCube": 62,
        #    "EnderDragon": 63,
        #    "Pig": 90,
        #    "Sheep": 91,
        #    "Cow": 92,
        #    "Chicken": 93,
        #    "Squid": 94,
        #    "Wolf": 95,
        #    "MooShroom": 96,
        #    "Snowman": 97,
        #    "Ocelot": 98,
        #    "IronGolem": 99,
        #    "Villager": 120,
        #}),
        SBInt32("x"),
        SBInt32("y"),
        SBInt32("z"),
        SBInt8("yaw"),
        SBInt8("pitch"),
        SBInt8("head_yaw"),
        SBInt16("velocity_z"),
        SBInt16("velocity_x"),
        SBInt16("velocity_y"),
        metadata,
    ),
    25: Struct("painting",
        UBInt32("eid"),
        AlphaString("title"),
        SBInt32("x"),
        SBInt32("y"),
        SBInt32("z"),
        UBInt32("direction"),
    ),
    26: Struct("spawn-experience-orb",
        UBInt32("eid"),
        SBInt32("x"),
        SBInt32("y"),
        SBInt32("z"),
        UBInt16("quantity"),
    ),
    28: Struct("entity-velocity",
        UBInt32("eid"),
        SBInt16("dx"),
        SBInt16("dy"),
        SBInt16("dz"),
    ),
    29: Struct("entity-destroy",
        UBInt8("count"),
        MetaArray(lambda ctx: ctx.count, UBInt32("eids")),
    ),
    30: Struct("entity-create",
        UBInt32("eid"),
    ),
    31: Struct("entity-position",
        UBInt32("eid"),
        SBInt8("dx"),
        SBInt8("dy"),
        SBInt8("dz")
    ),
    32: Struct("entity-orientation",
        UBInt32("eid"),
        UBInt8("yaw"),
        UBInt8("pitch")
    ),
    33: Struct("entity-location",
        UBInt32("eid"),
        SBInt8("dx"),
        SBInt8("dy"),
        SBInt8("dz"),
        UBInt8("yaw"),
        UBInt8("pitch")
    ),
    34: Struct("teleport",
        UBInt32("eid"),
        SBInt32("x"),
        SBInt32("y"),
        SBInt32("z"),
        UBInt8("yaw"),
        UBInt8("pitch"),
    ),
    35: Struct("entity-look",
        UBInt32("eid"),
        UBInt8("yaw"),
    ),
    38: Struct("entity-status",
        UBInt32("eid"),
        Enum(UBInt8("status"),
            damaged=2,
            killed=3,
            taming=6,
            tamed=7,
            drying=8,
            eating=9,
            sheep_eating=10,
        ),
    ),
    39: Struct("entity-attach",
        UBInt32("eid"),
        UBInt32("vid"),
    ),
    40: Struct("entity-metadata",
        UBInt32("eid"),
        metadata,
    ),
    41: Struct("entity-effect",
        UBInt32("eid"),
        effect,
        UBInt8("amount"),
        UBInt16("duration"),
    ),
    42: Struct("remove-entity-effect",
        UBInt32("eid"),
        effect,
    ),
    43: Struct("set-experience",
        BFloat32("current"),
        UBInt16("level"),
        UBInt16("total"),
    ),
    51: Struct("chunk",
        SBInt32("x"),
        SBInt32("z"),
        Bool("continuous"),
        UBInt16("primary"),
        UBInt16("secondary"),
        PascalString("data", length_field=UBInt32("length"), encoding="zlib"),
    ),
    52: Struct("block-batch-change",
        SBInt32("x"),
        SBInt32("z"),
        UBInt16("record_count"),
        UBInt32("length"),
        MetaArray(lambda ctx: ctx["record_count"], BitStruct("records",
            BitField("x", 4),
            BitField("z", 4),
            BitField("y", 8),
            BitField("block_id", 12),
            BitField("meta", 4),
            )),
    ),
    53: Struct("block-change",
        SBInt32("x"),
        UBInt8("y"),
        SBInt32("z"),
        UBInt16("type"),
        UBInt8("meta"),
    ),
    # XXX This covers general tile actions, not just note blocks.
    54: Struct("block-action",
        SBInt32("x"),
        SBInt16("y"),
        SBInt32("z"),
        Enum(UBInt8("instrument"),
            harp=0,
            bass=1,
            snare=2,
            click=3,
            bass_drum=4,
        ),
        UBInt8("pitch"),
        UBInt16("blockid"),
    ),
    55: Struct("block-break-animation",
        SBInt32("eid"),
        SBInt32("x"),
        SBInt32("y"),
        SBInt32("z"),
        UBInt8("destroy_stage"),
    ),
    56: Struct("map-chunk-bulk",
        UBInt16("count"),
        PascalString("data", length_field=UBInt32("length"), encoding="zlib"),
        MetaArray(lambda context: context["count"], Struct("metadata",
            SBInt32("x"),
            SBInt32("z"),
            SBInt16("primary"),
            SBInt16("secondary"),
            ))
    ),
    60: Struct("explosion",
        BFloat64("x"),
        BFloat64("y"),
        BFloat64("z"),
        BFloat32("radius"),
        UBInt32("count"),
        MetaArray(lambda context: context["count"], Struct("records",
            SBInt8("x"),
            SBInt8("y"),
            SBInt8("z"))),
        BFloat32("unknown1"),
        BFloat32("unknown2"),
        BFloat32("unknown3"),
    ),
    61: Struct("sound_or_particle",
        Enum(UBInt32("sid"),
            click2=1000,
            click1=1001,
            bow_fire=1002,
            door_toggle=1003,
            extinguish=1004,
            record_play=1005,
            charge=1007,
            fireball=1008,
            smoke=2000,
            block_break=2001,
            splash_potion=2002,
            portal=2003,
            blaze=2004,
        ),
        SBInt32("x"),
        UBInt8("y"),
        SBInt32("z"),
        UBInt32("data"),
    ),
    62: Struct("named-sound-effect",
        AlphaString("name"),
        SBInt32("x"),
        SBInt32("y"),
        SBInt32("z"),
        BFloat32("volume"),
        UBInt8("pitch"),
    ),
    70: Struct("change-game-state",
        Enum(UBInt8("state"),
            bad_bed=0,
            start_rain=1,
            stop_rain=2,
            mode_change=3,
            run_credits=4,
        ),
        UBInt8("gamemode"),
    ),
    71: Struct("thunderbolt",
        UBInt32("eid"),
        Bool("unknown"),
        SBInt32("x"),
        SBInt32("y"),
        SBInt32("z"),
    ),
    100: Struct("open-window",
        UBInt8("wid"),
        Enum(UBInt8("type"),
            chest=0,
            workbench=1,
            furnace=2,
            dispenser=3,
            enchantment_table=4,
            ),
        AlphaString("title"),
        UBInt8("slots"),
    ),
    101: Struct("close-window",
        UBInt8("wid"),
    ),
    102: Struct("click-window",
        SBInt8("wid"),
        SBInt16("slot"),
        SBInt8("button"),
        SBInt16("action_number"),
        SBInt8("shift"),
        slot,
    ),
    103: Struct("set-slot",
        SBInt8("wid"),
        SBInt16("slot"),
        slot,
    ),
    104: Struct("set-window-items",
        SBInt8("wid"),
        SBInt16("count"),
        MetaArray(lambda context: context["count"], slot),
    ),
    105: Struct("update-window-property",
        UBInt8("wid"),
        UBInt16("property"),
        UBInt16("progress"),
    ),
    106: Struct("confirm-transaction",
        UBInt8("wid"),
        UBInt16("action_number"),
        Bool("accepted"),
    ),
    107: Struct("creative-inventory-action ",
        UBInt16("slot"),
        slot,
    ),
    108: Struct("enchant-item",
        UBInt8("wid"),
        UBInt8("enchantment"),
    ),
    130: Struct("sign",
        SBInt32("x"),
        UBInt16("y"),
        SBInt32("z"),
        AlphaString("line1"),
        AlphaString("line2"),
        AlphaString("line3"),
        AlphaString("line4"),
    ),
    131: Struct("map",
        UBInt16("primary"),
        UBInt16("secondary"),
        PascalString("data", length_field=UBInt8("length")),
    ),
    132: Struct("update-tile-entity",
        SBInt32("x"),
        SBInt16("y"),
        SBInt32("z"),
        UBInt8("action"),
        UBInt16("size"),
        If(lambda context: context["size"] >= 0,
            MetaArray(lambda ctx: ctx.size, SBInt8("data"))
        )
    ),
    200: Struct("statistics",
        UBInt32("sid"), # XXX I could be an Enum
        UBInt8("count"),
    ),
    201: Struct("players",
        AlphaString("name"),
        Bool("online"),
        UBInt16("ping"),
    ),
    202: Struct("player-abilities",
        BitStruct("flags",
            Flag("is_god"),
            Flag("is_flying"),
            Flag("can_fly"),
            Flag("is_creative"),
            Padding(4)
            ),
        UBInt8("walking_speed"),
        UBInt8("flying_speed"),
    ),
    203: Struct("tab-complete",
        AlphaString("text"),
    ),
    204: Struct("locale-view-distance",
        AlphaString("locale"),
        Enum(UBInt8("view_distance"),
            far = 0,
            normal = 1,
            short = 2,
            tiny = 3,
            ),
        UBInt8("chat_flags"),
        Enum(UBInt8("difficulty"),
            peaceful = 0,
            easy = 1,
            normal = 2,
            hard = 3,
            ),
    ),
    205: Struct("client-status",
        UBInt8("status"),
    ),
    250: Struct("plugin-message",
        AlphaString("channel"),
        PascalString("data", length_field=SBInt16("length")),
    ),
    252: Struct("encryption-key-response",
        SecretString("shared_secret"),
        SecretString("verify_token"),
    ),
    253: Struct("encryption-key-request",
        AlphaString("server_id"),
        SecretString("public_key"),
        SecretString("verify_token"),
    ),
    254: Struct("poll"),
    255: Struct("error",
        AlphaString("message"),
    ),
}

packet_stream = Struct("packet_stream",
    OptionalGreedyRange(
        Struct("full_packet",
            UBInt8("header"),
            Switch("payload", lambda context: context["header"], packets),
        ),
    ),
    OptionalGreedyRange(
        UBInt8("leftovers"),
    ),
)

def parse_packets(bytestream):
    """
    Opportunistically parse out as many packets as possible from a raw
    bytestream.

    Returns a tuple containing a list of unpacked packet containers, and any
    leftover unparseable bytes.
    """

    container = packet_stream.parse(bytestream)

    l = [(i.header, i.payload) for i in container.full_packet]
    leftovers = "".join(chr(i) for i in container.leftovers)

    if DUMP_ALL_PACKETS:
        for packet in l:
            print "Parsed packet %d" % packet[0]
            print packet[1]

    return l, leftovers

incremental_packet_stream = Struct("incremental_packet_stream",
    Struct("full_packet",
        UBInt8("header"),
        Switch("payload", lambda context: context["header"], packets),
    ),
    OptionalGreedyRange(
        UBInt8("leftovers"),
    ),
)

def parse_packets_incrementally(bytestream):
    """
    Parse out packets one-by-one, yielding a tuple of packet header and packet
    payload.

    This function returns a generator.

    This function will yield all valid packets in the bytestream up to the
    first invalid packet.

    :returns: a generator yielding tuples of headers and payloads
    """

    while bytestream:
        parsed = incremental_packet_stream.parse(bytestream)
        header = parsed.full_packet.header
        payload = parsed.full_packet.payload
        bytestream = "".join(chr(i) for i in parsed.leftovers)

        yield header, payload

packets_by_name = dict((v.name, k) for (k, v) in packets.iteritems())
packet_names = dict((k, v.name) for (k, v) in packets.iteritems())

def make_packet(packet, *args, **kwargs):
    """
    Constructs a packet bytestream from a packet header and payload.

    The payload should be passed as keyword arguments. Additional containers
    or dictionaries to be added to the payload may be passed positionally, as
    well.
    """

    if packet not in packets_by_name:
        print "Couldn't find packet name %s!" % packet
        return ""

    header = packets_by_name[packet]

    for arg in args:
        kwargs.update(dict(arg))
    container = Container(**kwargs)

    if DUMP_ALL_PACKETS:
        print "Making packet %s (%d)" % (packet, header)
        print container
    payload = packets[header].build(container)
    return chr(header) + payload

def make_error_packet(message):
    """
    Convenience method to generate an error packet bytestream.
    """

    return make_packet("error", message=message)
