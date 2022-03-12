# Minimum Variance Beamformer
# 

import json
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy

def run():
    number_of_lines = 204
    number_of_active_elements = 64
    max_samples_per_line = 2122 # TODO calculate from lines in the data, don't hardcode
    line_sampling_rate = 40000000

    # Initialize cf_denominator and cf_numerator to have the same number of
    # rows as v_short and the same number of columns as lines in the image
    cf_denominator = numpy.zeros((max_samples_per_line, number_of_lines))
    cf_numerator = numpy.zeros((max_samples_per_line, number_of_lines))
    cf = numpy.zeros((max_samples_per_line, number_of_lines))

    final_image = numpy.zeros((max_samples_per_line, number_of_lines))
    line_start_time = numpy.zeros(number_of_lines)

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

        # Initialize pline_short to have the same number of
        # rows as v_short and the same number of columns as active elements
        pline_short = numpy.zeros((v_short_rows, number_of_active_elements))

        # for each active element
        for element_index in range(number_of_active_elements): # 0 to 63
            pline_short[:, element_index] = v_short[:, element_index] * v_short[:, element_index]

        cf_denominator[:v_short_rows, line_index] = number_of_active_elements * numpy.sum(pline_short, 1)
        cf_numerator[:v_short_rows, line_index] = numpy.sum(v_short, 1) * numpy.sum(v_short, 1)

        cf[:v_short_rows, line_index] = cf_numerator[:v_short_rows, line_index] / cf_denominator[:v_short_rows, line_index]
        # TBD TODO zero NaN in the cf matrix

        # apply the CF to each element's data
        for element_index in range(number_of_active_elements): # 0 to 63
            v_short[:, element_index] = cf[:v_short_rows, line_index] * v_short[:, element_index]

        # add white noise
        # skipped for now, surprisingly not used in reference MATLAB project

        # array steering vector (all ones)
        a = numpy.zeros((number_of_active_elements, 1)) + 1

        # calculate the spatial correlation matrix
        # and build the image line
        v = numpy.zeros((v_short_rows, 1))
        for apo_i in range(v_short_rows):
            u = numpy.zeros((number_of_active_elements, 1))
            u[:,0] = v_short[apo_i, :]
            u = u[:] # u is 64x1
            ut = numpy.transpose(u) # ut is 1x64
            R = u @ numpy.transpose(u) # R is 64x64

            # apply diagonal loading
            delta = 1.0 / number_of_active_elements
            R_diagonal_sum = numpy.trace(R)
            R = R + (delta * R_diagonal_sum) * numpy.eye(number_of_active_elements) # R is 64x64
            Rinv = numpy.linalg.inv(R) # Ri is 64x64

            # Careful! The * operator on two Numpy matrices is equivalent to the .* operator in Matlab
            # Use numpy.dot or @ for matrix multiplication!
            at = numpy.transpose(a)
            at_Rinv_a = at @ Rinv @ a # 1x1

            Rinv_a = Rinv @ a
            w = Rinv_a / at_Rinv_a # 64x1
            v[apo_i, :] = numpy.transpose(w) @ u

        # Add this line to the image
        line_start_time[line_index] = t_start
        final_image[:v_short_rows, [line_index]] = v

    # normalize the image
    final_image = numpy.nan_to_num(final_image)
    max_image = numpy.max(numpy.max(final_image))
    final_image = final_image / max_image

    # Time align each line
    final_image_time_aligned = numpy.zeros((max_samples_per_line * 2, number_of_lines))
    for line_index in range(number_of_lines): # 0 to 203
        time_offset = int(numpy.trunc(line_start_time[line_index] * line_sampling_rate))
        final_image_time_aligned[time_offset:time_offset + v_short_rows, line_index] = final_image[:, line_index]

    # do logarithmic compression
    final_image_array = numpy.array(final_image_time_aligned)
    final_image_db = 20 * numpy.log(numpy.abs(final_image_array))
    final_image_db = final_image_db + 60 # dynamic range

    # plot the image
    fig1, ax1 = plt.subplots()
    ax1.imshow(final_image_db, cmap='gray', aspect='auto', vmin=0, vmax=60)
    ax1.set_facecolor("black")
    ax1.set_xlabel('Line number')
    ax1.set_ylabel('Discretized depth')
    fig1.suptitle('Beamformed RF')
    plt.show()
