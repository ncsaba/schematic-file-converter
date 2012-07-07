
from upconvert.core.annotation import Annotation
from upconvert.core.component_instance import ComponentInstance, SymbolAttribute
from upconvert.core.design import Design
from upconvert.core.net import Net, NetPoint, ConnectedComponent
from upconvert.core.components import Component, Symbol, Body, Pin
from upconvert.core.shape import Point, Line, Label, Arc
from construct import *


EAGLE_CONVERTER = Struct("schematics",
    FixedLengthRecord("drawing"),
    MetaArray(
        lambda ctx: ctx.drawing.record_count - 1,
        FixedLengthRecord("flrecords"),
    ),
    OptionalGreedyRange(VariableLengthRecord("vlrecords")),
)


def parse(eagle_obj):
    design = Design()
    