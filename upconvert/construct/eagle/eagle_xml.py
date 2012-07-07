
from operator import attrgetter
from xml.sax import saxutils

""" Returns a float or an int depending on the value given """
def f_or_i(f_value):
    i_value = int(f_value)
    if i_value == f_value:
        return i_value
    else:
        return f_value

def calc_rot(shape):
    rotation = [ 'R', str(f_or_i(round(shape.rotation, 1))) ]
    if hasattr(shape, "mirror") and shape.mirror:
        rotation.insert(0, 'M')
    if hasattr(shape, "swap") and shape.swap:
        rotation.insert(0, 'S')
    return ''.join(rotation)

def escape_attr(attribute):
    return saxutils.escape(attribute).replace('"', '&quot;')

DEFAULT_SPACING = 1.27

WIRE_TAG='<wire x1="{0}" y1="{1}" x2="{2}" y2="{3}" width="{4}" layer="{5}"{6}{7}{8}/>\n'
CIRCLE_TAG='<circle x="{0}" y="{1}" radius="{2}" width="{3}" layer="{4}"/>\n'
PAD_TAG='<pad name="{0}" x="{1}" y="{2}" drill="{3}"{4}{5}{6}{7}{8}{9}/>\n'
SMD_TAG='<smd name="{0}" x="{1}" y="{2}" dx="{3}" dy="{4}" layer="{5}"{6}{7}{8}{9}/>\n'
TEXT_TAG='<text x="{0}" y="{1}" size="{2}" layer="{3}"{5}{6}{7}>{4}</text>\n'
RECTANGLE_TAG='<rectangle x1="{0}" y1="{1}" x2="{2}" y2="{3}" layer="{4}"{5}/>\n'
POLYGON_TAG='<polygon width="{0}" layer="{1}"{2}>\n'
VERTEX_TAG='<vertex x="{0}" y="{1}"{2}/>\n'
HOLE_TAG='<hole x="{0}" y="{1}" drill="{2}"/>\n'
PIN_TAG='<pin name="{0}" x="{1}" y="{2}"{3}{4}{5}{6}{7}{8}/>\n'
PINREF_TAG='<pinref part="{0}" gate="{1}" pin="{2}"/>\n'
JUNCTION_TAG='<junction x="{0}" y="{1}"/>\n'
LABEL_TAG='<label x="{0}" y="{1}" size="{2}" layer="{3}"{4}/>\n'
FRAME_TAG='<frame x1="{0}" y1="{1}" x2="{2}" y2="{3}" columns="{4}" rows="{5}" layer="{6}"{7}{8}{9}{10}/>\n'

def print_shapes(out, shapes, schematic=None, sheet=None):
    for shape in [x for x in shapes if x.type == 'WIRE']:
        out.write(WIRE_TAG.format(
            f_or_i(shape.x1), f_or_i(shape.y1), f_or_i(shape.x2), f_or_i(shape.y2),
            f_or_i(shape.width), shape.layer,
            ' curve="{0}"'.format(f_or_i(round(shape.curve, 6))) if shape.curve else '',
            ' style="{0}"'.format(shape.style) if shape.style != 'plain' else '',
            ' cap="{0}"'.format(shape.cap) if shape.cap != 'default0' else '',
        ))
    for shape in [x for x in shapes if x.type == 'CIRCLE']:
        out.write(CIRCLE_TAG.format(
            f_or_i(shape.x), f_or_i(shape.y), f_or_i(shape.radius),
            f_or_i(shape.width), shape.layer
        ))
    for shape in [x for x in shapes if x.type == 'PAD']:
        rotation = calc_rot(shape)
        out.write(PAD_TAG.format(
            escape_attr(shape.name), f_or_i(shape.x), f_or_i(shape.y), f_or_i(shape.drill),
            ' diameter="{0}"'.format(f_or_i(shape.diameter)) if shape.diameter != 0 else '',
            ' shape="{0}"'.format(shape.shape) if shape.shape != 'round' else '',
            ' first="{0}"'.format(shape.first) if shape.first != 'no' else '',
            ' rot="{0}"'.format(rotation) if rotation != 'R0' else '',
            ' stop="{0}"'.format(shape.stop) if shape.stop != 'yes' else '',
            ' thermals="{0}"'.format(shape.thermals) if shape.thermals != 'yes' else '',
        ))
    for shape in [x for x in shapes if x.type == 'SMD']:
        rotation = calc_rot(shape)
        out.write(SMD_TAG.format(
            escape_attr(shape.name),
            f_or_i(shape.x), f_or_i(shape.y),
            f_or_i(shape.dx), f_or_i(shape.dy),
            shape.layer,
            ' roundness="{0}"'.format(f_or_i(shape.roundness)) if shape.roundness != 0 else '',
            ' rot="{0}"'.format(rotation) if rotation != 'R0' else '',
            ' stop="{0}"'.format(shape.stop) if shape.stop != 'yes' else '',
            ' cream="{0}"'.format(shape.cream) if shape.cream != 'yes' else '',
        ))
    for shape in [x for x in shapes if x.type == 'TEXT']:
        rotation = calc_rot(shape)
        out.write(TEXT_TAG.format(
            f_or_i(shape.x), f_or_i(shape.y), f_or_i(shape.size), shape.layer,
            saxutils.escape(shape.text),
            ' font="{0}"'.format(shape.font) if shape.font != 'off' else '',
            ' ratio="{0}"'.format(shape.ratio) if f_or_i(shape.ratio) != 8 else '',
            ' rot="{0}"'.format(rotation) if rotation != 'R0' else '',
        ))
    for shape in [x for x in shapes if x.type == 'RECTANGLE']:
        rotation = calc_rot(shape)
        # seems that eagle normalizes the rectangle coordinates, so do it too:
        x1 = min(shape.x1, shape.x2)
        x2 = max(shape.x1, shape.x2)
        y1 = min(shape.y1, shape.y2)
        y2 = max(shape.y1, shape.y2)
        out.write(RECTANGLE_TAG.format(
            f_or_i(x1), f_or_i(y1), f_or_i(x2), f_or_i(y2),
            shape.layer,
            ' rot="{0}"'.format(rotation) if rotation != 'R0' else '',
        ))
    for shape in [x for x in shapes if x.type == 'HOLE']:
        out.write(HOLE_TAG.format(
            f_or_i(shape.x), f_or_i(shape.y), f_or_i(shape.drill),
        ))
    for shape in [x for x in shapes if x.type == 'PIN']:
        rotation = calc_rot(shape)
        out.write(PIN_TAG.format(
            escape_attr(shape.name),
            f_or_i(shape.x), f_or_i(shape.y),
            ' visible="{0}"'.format(shape.visible) if shape.visible != 'on' else '',
            ' length="{0}"'.format(shape.length.lower()) if shape.length.lower() != 'long' else '',
            ' direction="{0}"'.format(shape.direction.lower()) if shape.direction.lower() != 'none' else '',
            ' swaplevel="{0}"'.format(shape.swaplevel) if shape.swaplevel != 0 else '',
            ' function="{0}"'.format(shape.function) if shape.function != 'none' else '',
            ' rot="{0}"'.format(rotation) if rotation != 'R0' else '',
        ))
    for shape in [x for x in shapes if x.type == 'POLYGON']:
        out.write(POLYGON_TAG.format(
            f_or_i(shape.width), shape.layer,
            ' spacing="{0}"'.format(f_or_i(shape.spacing)) if shape.spacing != DEFAULT_SPACING else '',
        ))
        for vertex in shape.vertexes:
            out.write(VERTEX_TAG.format(
                f_or_i(vertex.x1), f_or_i(vertex.y1),
                ' curve="{0}"'.format(
                    f_or_i(round(vertex.curve, 6))
                ) if vertex.curve else ''
            ))
        out.write('</polygon>\n')
    for shape in [x for x in shapes if x.type == 'JUNCTION']:
        out.write(JUNCTION_TAG.format(
            f_or_i(shape.x), f_or_i(shape.y),
        ))
    for shape in [x for x in shapes if x.type == 'LABEL']:
        rotation = calc_rot(shape)
        out.write(LABEL_TAG.format(
            f_or_i(shape.x), f_or_i(shape.y), f_or_i(shape.size),
            shape.layer,
            ' rot="{0}"'.format(rotation) if rotation != 'R0' else '',
        ))
    for shape in [x for x in shapes if x.type == 'PIN_REF']:
        part = sheet.parts[shape.part - 1]
        library = schematic.libraries[part.library - 1]
        deviceset = library.device_sets[part.deviceset - 1]
        gate = deviceset.gates[shape.gate - 1]
        symbol = library.symbols[gate.symbol - 1]
        pins = [i for i in symbol.shapes if i.type == 'PIN']
        out.write(PINREF_TAG.format(
            escape_attr(part.name), escape_attr(gate.name),
            escape_attr(pins[shape.pin - 1].name),
        ))
    for shape in [x for x in shapes if x.type == 'FRAME']:
        out.write(FRAME_TAG.format(
            f_or_i(shape.x1), f_or_i(shape.y1), f_or_i(shape.x2), f_or_i(shape.y2),
            shape.columns, shape.rows, shape.layer,
            ' border-left="no"' if not shape.bleft else '',
            ' border-top="no"' if not shape.btop else '',
            ' border-right="no"' if not shape.bright else '',
            ' border-bottom="no"' if not shape.bbottom else '',
        ))
    
def print_xml(out, obj):
    out.write('<?xml version="1.0" encoding="utf-8"?>\n')
    out.write('<!DOCTYPE eagle SYSTEM "eagle.dtd">\n')
    out.write('<eagle version="6.1">\n')
    out.write('<drawing>\n')
    out.write('<settings>\n')
    out.write('<setting alwaysvectorfont="{0}"/>\n'.format(obj.drawing.alwaysvectorfont))
    # "verticaltext" is likely another flag in the DRAWING record,
    # but it seems to be dependent on some other data in the file and
    # just setting the flag makes eagle break up loading due to inconsistency,
    # so I couldn't figure out which one is the flag
    out.write('<setting verticaltext="up"/>\n')
    out.write('</settings>\n')
    grid = obj.grid
    out.write(('<grid distance="{0}" unitdist="{5}" unit="{6}" ' +
           'style="{4}" multiple="{2}" display="{3}" altdistance="{1}" ' +
           'altunitdist="{7}" altunit="{8}"/>\n'
          ).format(
              f_or_i(grid.distance), f_or_i(grid.altdistance),
              grid.multiple, grid.display, grid.style,
              grid.unitdist, grid.unit,
              grid.altunitdist, grid.altunit,
          ))
    out.write('<layers>\n')
    for layer in obj.layers:
        out.write(u'<layer number="{0}" name="{1}" color="{2}" fill="{3}" visible="{4}" active="{5}"/>\n'.format(
            layer.number, escape_attr(layer.name), layer.color, layer.fill,
            'yes' if layer.visible else 'no',
            'yes' if layer.active else 'no',
        ))
    out.write('</layers>\n')
    schematic = obj.schematic
    xrefinfo = schematic.xrefinfo.split('\t')
    out.write(u'<schematic{0}{1}>\n'.format(
        u' xreflabel="{0}"'.format(xrefinfo[0]) if schematic.xrefinfo else '',
        u' xrefpart="{0}"'.format(xrefinfo[1]) if len(xrefinfo) > 1 else '',
    ))
    out.write('<libraries>\n')
    for library in schematic.libraries:
        out.write(u'<library name="%s">\n' % escape_attr(library.name))
        out.write('<packages>\n')
        for package in library.packages:
            out.write(u'<package name="{0}">\n'.format(
                escape_attr(package.name)
            ))
            if package.description:
                out.write(u'<description>{0}</description>\n'.format(
                    saxutils.escape(package.description)
                ))
            print_shapes(out, package.shapes, schematic)
            out.write('</package>\n')
        out.write('</packages>\n')
        out.write('<symbols>\n')
        symbolpins = []
        for symbol in library.symbols:
            symbolpins.append(
                [shape for shape in symbol.shapes if shape.type == 'PIN']
            )
            out.write(u'<symbol name="{0}">\n'.format(
                escape_attr(symbol.name)
            ))
            print_shapes(out, symbol.shapes, schematic)
            out.write('</symbol>\n')
        out.write('</symbols>\n')
        out.write('<devicesets>\n')
        for device_set in library.device_sets:
            out.write(u'<deviceset name="{0}"{1}{2}>\n'.format(
                escape_attr(device_set.name),
                u' prefix="{0}"'.format(escape_attr(device_set.prefix)) if device_set.prefix else '',
                u' uservalue="{0}"'.format(device_set.uservalue) if device_set.uservalue != 'no' else '',
            ))
            if device_set.description:
                out.write(u'<description>{0}</description>\n'.format(
                    saxutils.escape(device_set.description)
                ))
            out.write('<gates>\n')
            for gate in device_set.gates:
                symbol = library.symbols[gate.symbol - 1]
                out.write(u'<gate name="{0}" symbol="{1}" x="{2}" y="{3}"{4}{5}/>\n'.format(
                    escape_attr(gate.name), escape_attr(symbol.name),
                    f_or_i(gate.x), f_or_i(gate.y),
                    ' addlevel="{0}"'.format(gate.addlevel) if gate.addlevel != 'none' else '',
                    ' swaplevel="{0}"'.format(gate.swaplevel) if gate.swaplevel != 0 else '',
                ))
            out.write('</gates>\n')
            out.write('<devices>\n')
            for device in device_set.devices:
                if device.package:
                    package = library.packages[device.package - 1]
                else:
                    package = ''
                out.write(u'<device name="{0}"{1}>\n'.format(
                    escape_attr(device.name),
                    u' package="{0}"'.format(escape_attr(package.name)) if package else '',
                ))
                if device.connects:
                    pads = [element for element in package.shapes
                            if element.type == 'PAD' or element.type == 'SMD']
                    ord_conn = []
                    for connect in device.connects:
                        gate = device_set.gates[connect.gateid - 1]
                        pin = symbolpins[gate.symbol - 1][connect.pinid - 1]
                        pad = pads[connect.padid-1]
                        ord_conn.append((gate.name, pin.name, pad.name))
                    # the xml tags are ordered alphabetically by PIN name;
                    ord_conn.sort()
                    out.write('<connects>\n')
                    for (gate, pin, pad) in ord_conn:
                        out.write('<connect gate="{0}" pin="{1}" pad="{2}"/>\n'.format(
                            escape_attr(gate), escape_attr(pin),
                            escape_attr(pad),
                        ))
                    out.write('</connects>\n')
                out.write('<technologies>\n')
                if len(device.attr_names) > 0:
                    tech_attributes = sorted(
                        enumerate(device.attr_names),
                        key=lambda x: x[1]
                    )
                    for i, tech in enumerate(sorted(device.techs)):
                        attr_values = device.attr_values[i]
                        attr_const = device.attr_const[i]
                        out.write('<technology name="{0}">\n'.format(tech))
                        for tech_attr in tech_attributes:
                            out.write(
                                u'<attribute name="{0}" value="{1}"{2}/>\n'.format(
                                    tech_attr[1], attr_values[tech_attr[0]],
                                    ' constant="no"' if not attr_const[tech_attr[0]] else ''
                                )
                            )
                        out.write('</technology>\n')
                else:
                    for tech in device.techs:
                        out.write(u'<technology name="{0}"/>\n'.format(tech))
                out.write('</technologies>\n')
                out.write('</device>\n')
            out.write('</devices>\n')
            out.write('</deviceset>\n')
        out.write('</devicesets>\n')
        out.write('</library>\n')
    out.write('</libraries>\n')
    out.write('<attributes>\n')
    out.write('</attributes>\n')
    out.write('<variantdefs>\n')
    out.write('</variantdefs>\n')
    out.write('<classes>\n')
    for net_class in [x for x in schematic.netclasses]:
        out.write(
            '<class number="{0}" name="{1}" width="{2}" drill="{3}">\n'.format(
                net_class.number, escape_attr(net_class.name),
                f_or_i(net_class.width), f_or_i(net_class.drill),
            )
        )
        for clearance in net_class.clearances:
            out.write(
                '<clearance class="{0}" value="{1}"/>\n'.format(
                    net_class.number, f_or_i(clearance)
                )
            )
        out.write('</class>\n')
    out.write('</classes>\n')
    out.write('<parts>\n')
    for sheet in schematic.sheets:
        for part in sheet.parts:
            library = schematic.libraries[part.library - 1]
            device_set = library.device_sets[part.deviceset - 1]
            device = device_set.devices[part.device - 1]
            technologies = device.techs
            use_tech = len(technologies) > 1
            technology = technologies[part.technology - 1] if use_tech else ''
            trivial_format = device_set.name.replace('?','{1}')
            if len(trivial_format) == len(device_set.name):
                trivial_format += '{1}'
            trivial_format = trivial_format.replace('*','{0}')
            trivial_value = trivial_format.format(technology,device.name)
            use_value = (use_tech or part.value) and part.value != trivial_value
            out.write(u'<part name="{0}" library="{1}" deviceset="{2}" device="{3}"{4}{5}/>\n'.format(
                escape_attr(part.name),
                escape_attr(library.name),
                escape_attr(device_set.name),
                escape_attr(device.name),
                u' technology="{0}"'.format(technology) if use_tech else '',
                u' value="{0}"'.format(part.value) if use_value else '',
            ))
    out.write('</parts>\n')
    out.write('<sheets>\n')
    for sheet in schematic.sheets:
        out.write('<sheet>\n')
        out.write('<plain>\n')
        print_shapes(out, sheet.plain, schematic)
        out.write('</plain>\n')
        out.write('<instances>\n')
        for part in sheet.parts:
            library = schematic.libraries[part.library - 1]
            device_set = library.device_sets[part.deviceset - 1]
            for instance in part.instances:
                gate = device_set.gates[instance.gate - 1]
                rotation = calc_rot(instance)
                out.write(u'<instance part="{0}" gate="{1}" x="{2}" y="{3}"{4}{5}'.format(
                    escape_attr(part.name), escape_attr(gate.name),
                    f_or_i(instance.x), f_or_i(instance.y),
                    ' smashed="{0}"'.format(instance.smashed) if instance.smashed != 'no' else '',
                    ' rot="{0}"'.format(rotation) if rotation != 'R0' else '',
                ))
                if instance.attributes:
                    out.write(">\n")
                    for attribute in sorted(instance.attributes, key=attrgetter('type_id')):
                        rotation = calc_rot(attribute)
                        out.write(u'<attribute name="{0}" x="{1}" y="{2}" size="{3}" layer="{4}"{5}{6}/>\n'.format(
                            attribute.type, f_or_i(attribute.x), f_or_i(attribute.y),
                            f_or_i(attribute.size), attribute.layer,
                            ' font="{0}"'.format(attribute.font) if attribute.font != 'off' else '',
                            ' rot="{0}"'.format(rotation) if rotation != 'R0' else '',
                        ))
                    out.write("</instance>\n")
                else:
                    out.write("/>\n")
        out.write('</instances>\n')
        out.write('<busses>\n')
        for bus in sheet.buses:
            out.write(u'<bus name="{0}">\n'.format(
                escape_attr(bus.name),
            ))
            for segment in bus.segments:
                out.write('<segment>\n')
                print_shapes(out, segment.shapes, schematic, sheet)
                out.write('</segment>\n')
            out.write('</bus>\n')
        out.write('</busses>\n')
        out.write('<nets>\n')
        for net in sheet.nets:
            out.write(u'<net name="{0}" class="{1}">\n'.format(
                escape_attr(net.name), net.net_class,
            ))
            for segment in net.segments:
                out.write('<segment>\n')
                print_shapes(out, segment.shapes, schematic, sheet)
                out.write('</segment>\n')
            out.write('</net>\n')
        out.write('</nets>\n')
        out.write('</sheet>\n')
    out.write('</sheets>\n')
    out.write('</schematic>\n')
    out.write('</drawing>\n')
    out.write('</eagle>\n')
