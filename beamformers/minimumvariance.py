# Minimum Variance Beamformer
# 

import json
import numpy

def run():
    print("GNDN")

    number_of_lines = 204
    number_of_active_elements = 64
    samples_per_line = 2122

    for line_number in range(number_of_lines):
        line_index = line_number + 1
        # load the data (204 files - one for each line in the 75 degree sector image)
        # each of the 204 line files contain 2122 samples for each of the 64 active transducer elements

        RF_filename = 'linedata/line' + str(line_index) + '.json'
        print('Loading', RF_filename)
        with open(RF_filename, 'r') as f:
            data = json.load(f)

        # TODO validate object shape
        line_number = data['lineNumber']
        t_start = data['t_start']
        line_rf_samples = numpy.array(data['v_short'])
        print(t_start)

        # calculate coherence factor for each element for this line
        product_of_line_rf_samples = numpy.zeros((samples_per_line, number_of_active_elements))
        for element_number in range(number_of_active_elements):
            element_index = element_number - 1
            line_rf_samples_for_element = line_rf_samples[:, element_index]
            product_of_line_rf_samples[:,element_index] = line_rf_samples[:, element_index] * line_rf_samples[:, element_index]

        # apply the CF to each line

        # add white noise

        # apply diagonal loading

    # find the envelope

    # normalize the image

    # plot the image

