__author__="csaba"
__date__ ="$May 7, 2012 7:29:42 PM$"

from construct import *
from struct import unpack
import re
import math

class EagleFloat(Adapter):
    """
    Divides by a fixed factor (mostly 10000, but can be other too).
    """
    def __init__(self, original, factor=10000):
        Adapter.__init__(self, original)
        self.factor = factor
    def _encode(self, obj, context):
        return int(round(obj * self.factor))
    def _decode(self, obj, context):
        return obj * 1.0 / self.factor

def EagleText(name, length):
    return Select(name,
        Struct(None,
            Padding(1, pattern = "\x7f", strict=True),
            ULInt32("address"),
            Padding(length - 5, pattern = "\x00", strict=True),
        ),
        String("text", length, padchar="\x00"),
    )

class MetaValidator(Adapter):
    """
    Validates a condition on the encoded/decoded object.

    Parameters:
    * subcon - the subcon to validate
    * get_errors - a function which should return the error messages
                   in case the object is invalid, or None if it is valid
    """
    __slots__ = ["_get_errors"]
    def __init__(self, subcon, get_errors):
        Adapter.__init__(self, subcon)
        self._get_errors = get_errors
    def _decode(self, obj, context):
        errors = self._get_errors(obj, context)
        if errors:
            raise ValidationError(str(errors), obj)
        return obj
    def _encode(self, obj, context):
        return self._decode(obj, context)

def parse_techs(tech_str):
    techs = []
    attr_names = []
    attr_values = []
    attr_const = []
    if 0 < len(tech_str):
        if b'\x04' == tech_str[0]:
            for tech in tech_str.split(b'\x04')[1:]:
                techs.append(tech)
        elif b'\x01' == tech_str[0]:
            attr_parts = tech_str.split(b'\x04')
            attr_names = attr_parts[0].split(b'\x01')[1:]
            for attr_part in attr_parts[1:]:
                part_values = re.split('([\x02\x03])', attr_part)
                techs.append(part_values[0])
                crt_values = part_values[2::2]
                attr_values.append(crt_values)
                crt_const = [ord(x) - 2 for x in part_values[1::2]]
                attr_const.append(crt_const)
                for i in range(len(crt_values),len(attr_names)):
                    crt_values.append('Missing value !!!')
                    crt_const.append(0)
        else:
            for x in re.findall('[\x00-\x7F]*[\x80-\xFF]', tech_str):
                index = len(x) - 1
                fixed_char = ord(x[index]) & 0x7F
                fixed_x = x[:index] + chr(fixed_char) if fixed_char else x[:index]
                techs.append(fixed_x)
    if len(techs) == 0:
        techs.append('')
    return (techs, attr_names, attr_values, attr_const)

class WireCurve(Adapter):
    """
    Calculates the curve in a wire record.
    """
    LOW_SIGN = 1 << 23
    LOW_CORRECTION = 1 << 24
    LOW_MASK = LOW_CORRECTION - 1
    HIGH_MASK = 0xFFL

    def __init__(self, original):
        Adapter.__init__(self, original)

    def _encode(self, obj, context):
        # TODO: implement
        return obj

    def _decode(self, obj, ctx):
        (c0, obj.x1) = self.split_wire_number(obj.x1)
        (c1, obj.y1) = self.split_wire_number(obj.y1)
        (c2, obj.x2) = self.split_wire_number(obj.x2)
        obj.y2 = self.split_wire_number(obj.y2)[1]
        if not (obj.common or obj.complex):
            # no curve
            obj.curve = 0
        elif not obj.common:
            # special common curves
            obj.curve = (1 if obj.curvesign else -1) * (180 if obj.curve90 else 90)
        else:
            # arbitrary curve values
            cut_bytes = chr(c0) + chr(c1) + chr(c2) + chr(255 if c2 > 127 else 0)
            cut = unpack('<i', cut_bytes)[0] / 10000.0
            obj.curve = self.calculate_curve(
                obj.x1, obj.y1, obj.x2, obj.y2, cut, obj.curvesign
            )
        return obj

    def split_wire_number(self, num):
        low_num = num & self.LOW_MASK
        if low_num & self.LOW_SIGN:
            low_num -= self.LOW_CORRECTION
        low_num = low_num * 1.0 / 10000
        high_num = (num >> 24) & self.HIGH_MASK
        return (int(high_num), low_num)

    def calculate_curve(self, x1, y1, x2, y2, cut, sign):
        dx = x2 - x1
        dy = y2 - y1
        d = math.sqrt(dx**2 + dy**2)
        u = dx/d
        v = dy/d
        if abs(dx) >= abs(dy):
            # the cut's coordinate is on the y axis
            h = (-(y1+y2)/2 + cut)/u
        else:
            # the cut's coordinate is on the x axis
            h = ((x1+x2)/2 - cut)/v
        Th = 2 * math.atan(d/h/2.0) if h != 0 else 0
        curve = 180 * Th / math.pi
        if sign > 0 and curve < 0:
            curve += 360
        elif sign == 0 and curve > 0:
            curve -= 360
        return curve

class SizeAdapter(Adapter):
    """
    Encodes/decodes size field in text and label records.
    """
    def __init__(self, original):
        Adapter.__init__(self, original)

    def _encode(self, obj, context):
        size = int(obj.size * 5000)
        (obj.size_high, obj.size_low) = divmod(size, 0x10000)
        return obj

    def _decode(self, obj, ctx):
        obj.size = (obj.size_low + 0x10000 * obj.size_high) / 5000.0;

class RotationAdapter(Adapter):
    """
    Encodes/decodes rotation fields.
    """
    def __init__(self, original, degrees):
        Adapter.__init__(self, original)
        self.degrees = degrees

    def _encode(self, obj, context):
        obj.rotation = round(obj.rotation / self.degrees)
        (obj.rot_high, obj.rot_low) = divmod(obj.rotation, 256)
        return obj

    def _decode(self, obj, ctx):
        # this gives the rotation in degrees
        if hasattr(obj, "rotation"):
            obj.rotation = obj.rotation * self.degrees
        else:
            obj.rotation = (obj.rot_low + 0x100 * obj.rot_high) * self.degrees
        return obj


