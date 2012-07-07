__author__="csaba"
__date__ ="$May 7, 2012 7:29:42 PM$"

from construct import Adapter
from construct import Container

_printable = dict((chr(i), ".") for i in range(256))
_printable.update((chr(i), chr(i)) for i in range(32, 128))

def to_bin(num, bit_count=None):
    result = 2**bit_count + num if num < 0 and bit_count else abs(num)
    result = bin(result)[2:]
    if bit_count:
        return ('0' * (bit_count - len(result))) + result
    if num < 0:
        return '-' + result
    return result

def hex_line(obj):
    value = str(obj)
    hextext = " ".join(b.encode("hex") for b in value)
    rawtext = "".join(_printable[b] for b in value)
    return hextext + "  " + rawtext

class HexLineAdapter(Adapter):
    """
    Adapter for hex-dumping strings. It returns the hex dump of the string.
    """
    def __init__(self, text):
        Adapter.__init__(self, text)
    def _encode(self, obj, context):
        return obj
    def _decode(self, obj, context):
        return hex_line(obj)

def pretty_str(obj):
    if obj == None:
        return "None"
    if isinstance(obj, dict) or isinstance(obj, Container):
        elements = [
            key + ': ' + pretty_str(value)
            for (key, value) in obj.iteritems()
            if not str(key).startswith('_')
        ]
        return '{' + ', '.join(elements) + '}'
    elif isinstance(obj, list):
        elements = [pretty_str(value) for value in obj]
        return '[' + ', '.join(elements) + ']'
    else:
        try:
            return str(obj)
        except:
            return repr(obj)


def pretty_print(out, obj, line_length=170, prefix='', indent=' '):
    if isinstance(obj, dict) or isinstance(obj, Container):
        is_recursive = False
        for key, value in obj.iteritems():
            if str(key).startswith('_'):
                continue
            if isinstance(value, dict) or isinstance(value, list):
                is_recursive = True
                break
        if not is_recursive:
            str_value = pretty_str(obj)
            if len(str_value) <= line_length - len(prefix):
                out.write(str_value)
                return
        out.write('{\n')
        new_prefix = prefix + indent
        for (key, value) in obj.iteritems():
            if str(key).startswith('_'):
                continue
            out.write(new_prefix)
            out.write(str(key))
            out.write(': ')
            pretty_print(out, value, line_length, new_prefix, indent)
            out.write(',\n')
        out.write(prefix)
        out.write('}')
    elif isinstance(obj, list):
        is_recursive = False
        for value in obj:
            if isinstance(value, dict) or isinstance(value, list):
                is_recursive = True
                break
        if not is_recursive:
            str_value = pretty_str(obj)
            if len(str_value) <= line_length - len(prefix):
                out.write(str_value)
                return
        new_prefix = prefix + indent
        out.write('[\n')
        for value in obj:
            out.write(new_prefix)
            pretty_print(out, value, line_length, new_prefix, indent)
            out.write(',\n')
        out.write(prefix)
        out.write(']')
    else:
        out.write(pretty_str(obj))

def pretty_println(out, obj, line_length=170, prefix='', indent=' '):
    pretty_print(out, obj, line_length, prefix, indent)
    out.write('\n')


