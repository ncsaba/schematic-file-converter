__author__="csaba"
__date__ ="$May 7, 2012 7:29:42 PM$"

from construct import *
from eagle_adapters import *

UNKNOWN = Struct("UNKNOWN",
    MetaField("record",
        lambda ctx: ctx.length,
    )
)

NET_CLASS = Struct("NET_CLASS",
    CString("name"),
    ULInt32("number"),
    Const(ULInt32("start"), 0x87654321),
    EagleFloat(SLInt32("width")),
    EagleFloat(SLInt32("drill")),
    RepeatUntil(
        lambda obj, ctx: obj == -198522.9329, # this is the value for 0x89abcdef
        EagleFloat(SLInt32("clearances")),
    ),
)

STRINGS = Struct("STRINGS",
    OptionalGreedyRange(CString("text")),
)

NC_STRINGS = Struct("NC_STRINGS",
    MetaField("record",
        lambda ctx: ctx.length,
    )
)

END = Struct("END")

type_map = {
    0x19991213 : STRINGS,
    0x20000425 : NET_CLASS,
    0x20061012 : NC_STRINGS,
    0x99999999 : END,
}

def VariableLengthRecord(name, type=None):
    def validate(obj, ctx):
        if type == None or type == obj.type:
            return None
        return 'Type mismatch, expected: {0}, but got: {1}'.format(
            type, obj.type
        )
    return MetaValidator(
        Struct(name,
            ULInt32("type_id"),
            Value("type", lambda ctx: type_map.get(ctx.type_id, UNKNOWN).name),
            ULInt32("length"),
            Embed(TunnelAdapter(
                MetaField("record_data", lambda ctx: ctx.length),
                Switch(None,
                    lambda ctx: ctx.type_id,
                    type_map,
                    UNKNOWN
                ),
            )),
            If(
                lambda ctx: ctx.length > 0,
                ULInt32("checksum"),
            ),
        ),
        validate
    )

