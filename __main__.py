from math import ceil
import numpy

# Constants
speed_of_sound = 1540 # m/s

# Transducer Config, e.g. ATL L7-4
center_frequency = 5.2E6 # frequency in MHz
sampling_rate = 4 * center_frequency # sampling rate in MHz
num_elements = 128
pitch = 0.000245 # pitch in m, e.g. 0.000245 = 0.245 mm

# Scan Config
theta = numpy.deg2rad(0)
beta = numpy.deg2rad(30)
scan_depth = 0.10 # scan depth in m, e.g. 0.10 = 10 cm

class Point:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __init__(self, x:float, y:float, z:float):
        self.x = x
        self.y = y
        self.z = z

def distance_between_two_points(p1:Point, p2:Point) -> float:
    dx = p1.x - p2.x
    dy = p1.y - p2.y
    dz = p1.z - p2.z
    return numpy.sqrt(dx * dx + dy * dy + dz * dz)

def heaviside(a:float) -> float:
    if a > 0:
        return 1.0
    return 0.0

def generate_complex_2d_array(num_rows:int, num_columns:int):
    result = numpy.zeros((num_rows, num_columns)).astype(complex)
    # TODO - include something reflecting a signal in the 2d space 
    return result

if __name__ == "__main__":
    # First, calculate the number of samples we expect per line. To do so, take the max scan depth, multiply it
    # by 2 (for round trip) divide that by the speed of sound to get the max round trip time.
    # Multiply that by the sampling rate to get the max number of samples for a line.
    num_samples_per_line = ceil(scan_depth * (2 / speed_of_sound) * sampling_rate)

    # Now, generate a complex input signal. It should be two dimensional when the 1st dimension is element number
    # and the 2nd dimension is the (un-beamformed) RF sample index for that element
    input_signal = generate_complex_2d_array(num_elements, num_samples_per_line)

    # TODO plot the un-beamformed signal

    # Calculate the transducer element centers as an array of num_elements
    # Center the elements along the x axis
    array_width = (num_elements - 1) * pitch

    element_positions = []
    for el in range(num_elements):
        x = (el * pitch) + (-array_width / 2)
        element_positions.append(Point(x, 0, 0))

    # Define a virtual source
    # Let theta be the desired tilt from the z axis in radians
    # Let beta be the desired beamwidth in radians
    # For now, don't allow the virtual source y to be non zero
    # theta = numpy.deg2rad(0)
    # beta = numpy.deg2rad(30)

    virtual_source_x = (array_width / 2) * numpy.sin(2 * theta) / numpy.sin(beta)
    virtual_source_y = 0.0
    virtual_source_z = (-array_width / 2) * (numpy.cos(beta) + numpy.cos(2 * theta)) / numpy.sin(beta)

    virtual_source_position = Point(virtual_source_x, virtual_source_y, virtual_source_z)

    # Define a (single) focus centered 5 cm below the face of the transducer
    # For now, don't allow the focus y to be non zero
    focus_position = Point(0, 0, 0.05)

    # Quick and dirty f-number needed for that depth
    f_number = focus_position.z / array_width

    # Calculate distances_rx from the focus_position to each transducer element
    rx_distances = []
    for el in range(num_elements):
        rx_distance = distance_between_two_points(focus_position, element_positions[el])
        rx_distances.append(rx_distance)

    # Calculate tx_distance from the virtual source to the focus_position
    # adjusting for the distance from the end of the array
    unadjusted_tx_distance = distance_between_two_points(virtual_source_position, focus_position)

    virtual_source_x_distance_to_end_element = abs(virtual_source_position.x) - array_width / 2
    adjustment = numpy.sqrt(heaviside(virtual_source_x_distance_to_end_element) * \
        virtual_source_x_distance_to_end_element * virtual_source_x_distance_to_end_element + \
            virtual_source_position.z * virtual_source_position.z)
    tx_distance = unadjusted_tx_distance - adjustment

    # Calculate the two way travel times (tau) for each element
    two_way_travel_times = []
    for el in range(num_elements):
        two_way_travel_time = (tx_distance + rx_distances[el]) / speed_of_sound
        two_way_travel_times.append(two_way_travel_time)

    # Convert each two way travel time into the corresponding fast-time index
    # by multiplying the sampling frequency (e.g. 20E6 samples/sec) by the
    # time offset
    fast_time_indices = []
    for el in range(num_elements):
        fast_time_index = two_way_travel_times[el] * sampling_rate
        fast_time_indices.append(fast_time_index)

    # Generate a true/false vector based on whether each element's fast time index is within bounds
    fast_time_index_in_bounds_array = []
    for el in range(num_elements):
        fast_time_index_in_bounds = fast_time_indices[el] < num_samples_per_line
        fast_time_index_in_bounds_array.append(fast_time_index_in_bounds)

    # Generate a true/false vector based on whether the focus is within the element's field of view
    focus_in_element_field_of_view_array = []
    for el in range(num_elements):
        delta_x = abs(focus_position.x - element_positions[el].x)
        scaled_z = focus_position.z / 2.0 / f_number
        focus_in_element_field_of_view = delta_x < scaled_z
        focus_in_element_field_of_view_array.append(focus_in_element_field_of_view)

    # Combine these into a single vector on whether those two constains are both met
    element_is_viable_for_beamforming_to_focus_array = []
    for el in range(num_elements):
        element_is_viable_for_beamforming_to_focus = fast_time_index_in_bounds_array[el] and \
            focus_in_element_field_of_view_array[el]
