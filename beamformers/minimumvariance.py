# Minimum Variance Beamformer
# 

import json
import numpy

def run():
    print("GNDN")

    number_of_lines = 204
    number_of_active_elements = 64
    max_samples_per_line = 2122

    # Initialize cf_denominator and cf_numerator to have the same number of
    # rows as v_short and the same number of columns as lines in the image
    cf_denominator = numpy.zeros((max_samples_per_line, number_of_lines))
    cf_numerator = numpy.zeros((max_samples_per_line, number_of_lines))
    cf = numpy.zeros((max_samples_per_line, number_of_lines))

    # for each line in the image
    for line_index in range(number_of_lines): # 0 to 203
        line_number = line_index + 1 # 1 to 204

        # load the data (204 files - one for each line in the 75 degree sector image)
        # each of the 204 line files contain 2122 samples for each of the 64 active transducer elements

        RF_filename = 'linedata/line' + str(line_number) + '.json'
        print('Loading', RF_filename)
        with open(RF_filename, 'r') as f:
            data = json.load(f)

        # TODO validate object shape
        line_number = data['lineNumber']
        t_start = data['t_start']
        v_short_rows = len(data['v_short'])
        v_short = numpy.array(data['v_short'])
        print(t_start)

        # Initialize pline_short to have the same number of
        # rows as v_short and the same number of columns as active elements
        pline_short = numpy.zeros((v_short_rows, number_of_active_elements))

        # for each active element
        for element_index in range(number_of_active_elements): # 0 to 63
            pline_short[:, element_index] = v_short[:, element_index] * v_short[:, element_index]

        cf_denominator[:v_short_rows, line_index] = number_of_active_elements * numpy.sum(pline_short, 1)
        cf_numerator[:v_short_rows, line_index] = numpy.sum(v_short, 1) * numpy.sum(v_short, 1)

        cf[:v_short_rows, line_index] = cf_numerator[:v_short_rows, line_index] / cf_denominator[:v_short_rows, line_index]

        # apply the CF to each element's data
        for element_index in range(number_of_active_elements): # 0 to 63
            v_short[:, element_index] = cf[:v_short_rows, line_index] * v_short[:, element_index]

        # add white noise


        # apply diagonal loading

    # find the envelope

    # normalize the image

    # plot the image

