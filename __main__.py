from cmath import sqrt
import numpy

# Constants
speed_of_sound = 1540 # m/s

# Configuration, e.g. ATL L7-4
center_frequency = 5.2E6 # frequency in MHz
sampling_frequency = 4 * center_frequency # sampling rate in MHz
num_elements = 128
pitch = 0.000245 # pitch in m, e.g. 0.000245 = 0.245 mm

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

if __name__ == "__main__":
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
    theta = numpy.deg2rad(0)
    beta = numpy.deg2rad(30)

    virtual_source_x = (array_width / 2) * numpy.sin(2 * theta) / numpy.sin(beta)
    virtual_source_y = 0.0
    virtual_source_z = (-array_width / 2) * (numpy.cos(beta) + numpy.cos(2 * theta)) / numpy.sin(beta)

    virtual_source_position = Point(virtual_source_x, virtual_source_y, virtual_source_z)

    # Define a (single) focus centered 5 cm below the face of the transducer
    # For now, don't allow the focus y to be non zero
    focus_position = Point(0, 0, 0.05)

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
    index_times = []
    for el in range(num_elements):
        index_time = two_way_travel_times[el] * sampling_frequency
        index_times.append(index_time)

    for index_time in index_times:
        print(index_time)

