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
    rf_samples_per_element = len(data['RF'])
    print("RF len:", rf_samples_per_element, "rows")

    transducer_params = data['transducer_params']
    num_elements = transducer_params['Nelements']

    # Plot the un-beamformed RF
    rf_data = numpy.array(data['RF'])
    rf_data_db = 20 * numpy.log(numpy.abs(rf_data))

    fig1, ax1 = plt.subplots()
    ax1.imshow(rf_data_db, cmap='gray', aspect='auto', vmin=0, vmax=78)
    ax1.set_facecolor("black")
    ax1.set_xlabel('Transducer element number')
    ax1.set_ylabel('Discretized depth')
    fig1.suptitle('Un-beamformed RF')
    plt.show()

    # OK, let's beamform
    beamformed_rf_data = numpy.zeros((rf_samples_per_element, num_elements))

    # First, calculate the transducer element centers along the x axis
    centering_shift = (num_elements - 1) / 2
    element_centers = (numpy.linspace(0, num_elements - 1, num_elements) - centering_shift) * transducer_params['pitch']

    sampling_rate = transducer_params['fs']
    speed_of_sound = 1540; # m/s
    delta_z_per_sample = speed_of_sound / (2 * sampling_rate)

    # For each rx element, we need to calculate the correct delay
    # for each depth from each possible tx element
    for rx_element_index in range(num_elements):
        print('calculating delay matrix for element', rx_element_index, flush=True)
        rx_element_center = element_centers[rx_element_index]
        delay_matrix = numpy.zeros((rf_samples_per_element, num_elements))

        for sample_index in range(rf_samples_per_element):
            sample_depth_z = delta_z_per_sample * sample_index
            for tx_element_index in range(num_elements):
                tx_element_center = element_centers[tx_element_index]

                # Calculate the x distance between the rx and tx elements
                delta_x_tx_rx = abs(rx_element_center - tx_element_center)
                # Calculate the distance between the sample depth below the tx
                # element to the rx element
                total_distance = numpy.sqrt(delta_x_tx_rx * delta_x_tx_rx + sample_depth_z * sample_depth_z)
                # subtract out the z depth so we just get the delta we need
                delta_distance = total_distance - sample_depth_z
                # discretize it to index into the pad correctly
                delay = round(delta_distance / delta_z_per_sample / 2)
                delay_matrix[sample_index, tx_element_index] = delay

        # Now, let's loop over the entire rf_data matrix and apply these delays to
        # build a beamformed_rf_data matrix
        rf_data_shifted = numpy.zeros((rf_samples_per_element, num_elements))

        for sample_index in range(rf_samples_per_element):
            for tx_element_index in range(num_elements):
                delay = delay_matrix[sample_index, tx_element_index]
                if sample_index + delay < rf_samples_per_element:
                     rf_data_shifted[sample_index, tx_element_index] = rf_data[sample_index + round(delay), tx_element_index]

        beamformed_rf_data[:, rx_element_index] = rf_data_shifted.sum(axis=1, dtype='float')

    beamformed_rf_data_db = 20 * numpy.log(numpy.abs(beamformed_rf_data))
    fig2, ax2 = plt.subplots()
    ax2.imshow(beamformed_rf_data_db, cmap='gray', aspect='auto', vmin=0, vmax=beamformed_rf_data_db.max())
    ax2.set_facecolor("black")
    ax2.set_xlabel('Transducer element number')
    ax2.set_ylabel('Discretized depth')
    fig2.suptitle('Beamformed RF')
    plt.show()