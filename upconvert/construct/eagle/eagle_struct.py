
from construct import *
from fixed_length import strings_map
from fixed_length import FixedLengthRecord
from eagle_adapters import parse_techs
from variable_length import VariableLengthRecord


EAGLE_SCHEMATICS = Struct("schematics",
    FixedLengthRecord("drawing"),
    MetaArray(
        lambda ctx: ctx.drawing.record_count - 1,
        FixedLengthRecord("records"),
    ),
    VariableLengthRecord("strings", "STRINGS"),
    OptionalGreedyRange(VariableLengthRecord("netclasses", "NET_CLASS")),
    OptionalGreedyRange(VariableLengthRecord("rest")), # this part is ignored
)

class EagleFile(Adapter):
    """
    Parses/creates the object format coming from/to EAGLE_SCHEMATICS.
    """
    def __init__(self, original):
        Adapter.__init__(self, original)
    def _encode(self, obj, context):
        # TODO: implement encoding
        # Note for layers: seems the user visible layers start at 91, and
        # there's more than 1 bit set for each flag when saving, but only
        # 1 bit checked when parsing
        result = Container()
        result.drawing = obj.drawing
        return result
    def _decode(self, obj, context):
        self.obj = obj
        self.records = obj.records
        self.string_iter = iter(obj.strings.text)
        self.record_index = 0
        self.layer_stats = {}
        return self.parse()

    def parse(self):
        result = Container()
        result.drawing = self.obj.drawing
        result.settings = self.parse_settings()
        result.grid = self.parse_grid()
        result.layers = self.parse_layers()
        result.schematic = self.parse_schematic()
        result.layer_stats = self.layer_stats
        return result

    def load_strings(self, record):
        string_fields = strings_map.get(record.type_id, [])
        for field in string_fields:
            attribute = record[field]
            if hasattr(attribute, 'address'):
                attribute = self.string_iter.next()
            string_val = attribute.decode('latin-1') if None != attribute else None
            record[field] = '' if string_val == "''" else string_val

    def next_type(self):
        if self.record_index < len(self.records):
            return self.records[self.record_index].type
        else:
            return None

    def next_record(self, type=None):
        record = self.records[self.record_index]
        self.load_strings(record)
        self.get_layer_stats(record)
        if type != None and record.type != type:
            raise ValidationError("Expected {0}, but got: {1}".format(type, record.type), record)
        self.record_index += 1
        return record

    def next_records(self, count):
        result = self.records[self.record_index:self.record_index + count]
        for record in result:
            self.load_strings(record)
            self.get_layer_stats(record)
        self.record_index += count
        return result

    def get_layer_stats(self, record):
        if hasattr(record, "layer"):
            if self.layer_stats.has_key(record.layer):
                stats = self.layer_stats[record.layer]
            else:
                self.layer_stats[record.layer] = stats = {}
            if stats.has_key(record.type):
                stats[record.type] += 1
            else:
                stats[record.type] = 1

    def parse_settings(self):
        layers = []
        while self.next_type() == 'SETTINGS':
            layers.append(self.next_record())
        return layers

    def parse_grid(self):
        return self.next_record('GRID')

    def parse_layers(self):
        layers = []
        while self.next_type() == 'LAYER':
            layer = self.next_record()
            # layers up to number 90 are always inactive and not visible,
            # doesn't matter what the visibility flags say
            if layer.number <= 90:
                layer.visible = layer.active = 0
            # inactive layers are invisible too, regardless of the visibel flag set:
            elif layer.visible and not layer.active:
                layer.visible = 0
            layers.append(layer)
        return layers

    def parse_schematic(self):
        schematic = self.next_record('SCHEMATIC')
        schematic.libraries = self.parse_libraries()
        schematic.attributes = self.parse_attributes()
        schematic.variantdefs = self.parse_variantdefs()
        schematic.netclasses = self.parse_net_classes()
        schematic.sheets = self.parse_sheets()
        return schematic

    def parse_libraries(self):
        libraries = []
        while self.next_type() == 'LIBRARY':
            library = self.next_record()
            libraries.append(library)
            library.device_sets = self.parse_device_sets()
            library.symbols = self.parse_symbols()
            library.packages = self.parse_packages()
        return libraries

    def parse_device_sets(self):
        device_sets = self.next_record("DEVICE_SETS")
        device_sets = []
        while self.next_type() == 'DEVICE_SET':
            device_set = self.next_record()
            device_sets.append(device_set)
            device_set.devices = self.parse_devices()
            device_set.gates=self.next_records(device_set.gate_count)
        return device_sets

    def parse_devices(self):
        devices = []
        while self.next_type() == 'DEVICE':
            device = self.next_record()
            devices.append(device)
            (
                device.techs,device.attr_names,
                device.attr_values,device.attr_const
            ) = parse_techs(device.techstr)
            # parse connects
            connects = []
            # * get minimum number - 1, this will be the power of 2 needed to cover
            #   the max number of pins in a symbol for all the available gates
            #   (perhaps it is set in the device-set record ?);
            minvalue = 256
            for n in range(device.connects_count):
                connect = self.next_record('CONNECTS')
                offset = n * 22
                for (i,x) in enumerate(connect.connects):
                    # * the numbers are listed in the order of the PADs from the package;
                    # * the value "0" means "not connected" !
                    if x == 0:
                        continue
                    connects.append((offset + i, x))
                    minvalue = min(minvalue, x)
            minvalue = minvalue - 1
            device.connects = []
            # * the (number % min) are the index of the PIN from the symbol;
            # * the (number / min) is the gate id;
            for (i,x) in connects:
                connect = Container()
                connect.padid = i + 1
                (connect.gateid, connect.pinid) = divmod(x, minvalue)
                device.connects.append(connect)
        return devices

    def parse_symbols(self):
        symbols = self.next_record("SYMBOLS")
        symbols = []
        while self.next_type() == 'SYMBOL':
            symbol = self.next_record()
            symbols.append(symbol)
            symbol.shapes=self.parse_shapes(symbol.rec_count)
        return symbols

    def parse_packages(self):
        packages = self.next_record("PACKAGES")
        package_count = packages.package_count
        packages = []
        for n in range(package_count):
            package = self.next_record('PACKAGE')
            packages.append(package)
            package.shapes=self.parse_shapes(package.rec_count)
        return packages

    def parse_attributes(self):
        # TODO: implement
        return []

    def parse_variantdefs(self):
        # TODO: implement
        return []

    def parse_net_classes(self):
        result = [x for x in self.obj.netclasses if x.name != '']
        for netclass in result:
            netclass.clearances = [x for x in netclass.clearances if x != 0 and x != -198522.9329]
        return result

    def parse_sheets(self):
        sheets = []
        while self.next_type() == 'SHEET':
            sheet = self.next_record()
            sheets.append(sheet)
            sheet.plain=self.parse_shapes(sheet.rec_count)
            sheet.parts=[]
            while self.next_type() == 'PART':
                sheet.parts.append(self.parse_part())
            sheet.buses=self.parse_buses()
            sheet.nets=[]
            while self.next_type() == 'NET':
                sheet.nets.append(self.parse_net())
        return sheets

    def parse_buses(self):
        buses = []
        while self.next_type() == 'BUS':
            bus = self.next_record()
            buses.append(bus)
            bus.segments = []
            while self.next_type() == 'SEGMENT':
                segment = self.next_record()
                bus.segments.append(segment)
                segment.shapes = self.parse_shapes(segment.rec_count)
        return buses

    def parse_part(self):
        part = self.next_record()
        part.instances=[]
        while self.next_type() == 'INSTANCE':
            instance = self.next_record()
            part.instances.append(instance)
            instance.attributes = self.next_records(instance.attr_count)
        return part

    def parse_net(self):
        net = self.next_record()
        net.segments=[]
        while self.next_type() == 'SEGMENT':
            segment = self.next_record()
            net.segments.append(segment)
            segment.shapes = self.parse_shapes(segment.rec_count)
        return net

    def parse_shapes(self, rec_count):
        shapes=[]
        i = 0
        while i < rec_count:
            shape = self.next_record()
            i += 1
            shapes.append(shape)
            if shape.type == 'POLYGON':
                shape.vertexes = []
                i += shape.vertex_count
                for n in range(shape.vertex_count):
                    shape.vertexes.append(self.next_record('WIRE'))
        return shapes

EAGLE_FILE = EagleFile(EAGLE_SCHEMATICS)

