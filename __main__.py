import json
from marshmallow import EXCLUDE, Schema, fields, ValidationError
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy

RF_filename = 'L11-5V.json'

class ScatterersSchema(Schema):
    x = fields.List(fields.Float())
    z = fields.List(fields.Float())
    RC = fields.List(fields.Float())

class TransducerParamsSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    fc = fields.Integer(required=True)
    Nelements = fields.Integer(required=True)
    fs = fields.Integer(required=True)

class ImportSchema(Schema):
    transducer_name = fields.Str(required=True, allow_none=False)
    transmit_delays = fields.List(fields.Float())
    scatterers = fields.Nested(ScatterersSchema)
    transducer_params = fields.Nested(TransducerParamsSchema)
    RF = fields.List(fields.List(fields.Float))

if "__main__" == __name__:
    with open(RF_filename, 'r') as f:
        data = json.load(f)

    try:
        result = ImportSchema().load(data)
    except ValidationError as err:
        print("Processing halted. There are errors in the import file:")
        print(err.messages)
        exit(0)

    print("###############################################################")
    print("Transducer name:", data['transducer_name'])
    print("RF len:", len(data['RF']), "rows")

    # Plot the un-beamformed RF
    RF = numpy.array(data['RF'])
    RF = 20 * numpy.log(numpy.abs(RF))

    fig, ax = plt.subplots()
    ax.imshow(RF, cmap='gray', aspect='auto', vmin=0, vmax=78)
    ax.set_facecolor("black")
    ax.set_xlabel('Transducer element number')
    ax.set_ylabel('Discretized depth')
    fig.suptitle('Un-beamformed RF')
    plt.show()