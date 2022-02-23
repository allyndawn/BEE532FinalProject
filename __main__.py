import numpy

# Constants
speed_of_sound = 1540 # m/s

# Configuration
num_elements = 128
pitch = 0.01 # m

# Points
class Position:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

if __name__ == "__main__":
    # Calculate the element centers as an array of num_elements
    # Center the elements along the x axis
    array_width = (num_elements - 1) * pitch
    element_positions = []
    for el in range(num_elements):
        x = (el * pitch) + (-array_width / 2)
        element_positions.append(Position(x, 0, 0))

    for position in element_positions:
        print(position.x, position.y, position.z)

