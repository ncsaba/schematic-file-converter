
from construct import *
from flrecords import *

# The values in this map are records defined in flrecords.py
type_map = {
    0x10 : DRAWING,
    0x11 : SETTINGS,
    0x12 : GRID,
    0x13 : LAYER,
    0x14 : SCHEMATIC,
    0x15 : LIBRARY,

    0x17 : DEVICE_SETS,
    0x18 : SYMBOLS,
    0x19 : PACKAGES,
    0x1A : SHEET,

    0x1D : SYMBOL,
    0x1E : PACKAGE,
    0x1F : NET,
    0x20 : SEGMENT,
    0x21 : POLYGON,
    0x22 : WIRE,

    0x25 : CIRCLE,
    0x26 : RECTANGLE,
    0x27 : JUNCTION,
    0x28 : HOLE,

    0x2A : PAD,
    0x2B : SMD,
    0x2C : PIN,
    0x2D : GATE,

    0x30 : INSTANCE,
    0x31 : TEXT,

    0x33 : LABEL,
    0x34 : NAME_ATTR,
    0x35 : VALUE_ATTR,
    0x36 : DEVICE,
    0x37 : DEVICE_SET,
    0x38 : PART,

    0x3A : BUS,

    0x3C : CONNECTS,
    0x3D : PIN_REF,

    0x3F : PART_ATTR,

    0x41 : ATTRIBUTE,
    0x42 : ATTRIBUTE_DEF,
    0x43 : FRAME,
}

strings_map = {
    0x13 : ['name'], # LAYER
    0x14 : ['xrefinfo'], # SCHEMATIC
    0x15 : ['name'], # LIBRARY
    0x17 : ['library'], # DEVICE_SETS
    0x18 : ['library'], # SYMBOLS
    0x19 : ['library'], # PACKAGES
    0x1D : ['name'], # SYMBOL
    0x1E : ['name','description'], # PACKAGE
    0x1F : ['name'], # NET
    0x2A : ['name'], # PAD
    0x2B : ['name'], # SMD
    0x2C : ['name'], # PIN
    0x2D : ['name'], # GATE
    0x31 : ['text'], # TEXT
    0x36 : ['name','techstr'], # DEVICE
    0x37 : ['name','description','prefix',], # DEVICE_SET
    0x38 : ['value','name'], # PART
    0x3A : ['name'], # BUS
    0x41 : ['name'], # ATTRIBUTE
    0x42 : ['attribute_def'], # ATTRIBUTE_DEF
}

def FixedLengthRecord(name, debug=False):
    return Struct(name,
        ULInt8("type_id"),
        Value("type", lambda ctx: type_map.get(ctx.type_id, UNKNOWN).name),
        ULInt8("flags"),
        Peek(HexLineAdapter(Field("data", 0x16))),
        Embed(Switch("record_data",
            # key function:
            lambda ctx: ctx.type_id,
            # cases map (replace with {0x10 : DRAWING} for debugging a dump):
#            {0x10 : DRAWING},
            type_map,
            # default value:
            UNKNOWN 
        ))
    ) if debug else Struct(name,
        ULInt8("type_id"),
        Value("type", lambda ctx: type_map.get(ctx.type_id, UNKNOWN).name),
        ULInt8("flags"),
        Embed(Switch("record_data",
            # key function:
            lambda ctx: ctx.type_id,
            # cases map (replace with {0x10 : DRAWING} for debugging a dump):
#            {0x10 : DRAWING},
            type_map,
            # default value:
            UNKNOWN
        ))
    )

