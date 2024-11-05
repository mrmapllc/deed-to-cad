import math
import re
import sys
from shapely.geometry import Point, LineString
from ezdxf import new
from parse_ai_data import read_ai_data

def parse_bearing(bearing_text):
    """Convert bearing text (e.g., 'N 76°44\'21" E') to a decimal angle in degrees."""
    match = re.match(r'([NSEW])\s*(\d{1,3})°\s*(\d{1,2})\'\s*(\d{1,2})"?\s*([NSEW])?', bearing_text)
    if not match:
        raise ValueError(f"Invalid bearing format: {bearing_text}")
    
    direction1 = match.group(1)
    degrees = int(match.group(2))
    minutes = int(match.group(3))
    seconds = int(match.group(4))
    direction2 = match.group(5) if match.group(5) else ""

    # Convert to decimal degrees
    decimal_degrees = degrees + (minutes / 60.0) + (seconds / 3600.0)

    # Adjust for direction
    if direction1 == 'N' and direction2 == 'E':
        return decimal_degrees
    elif direction1 == 'N' and direction2 == 'W':
        return 360 - decimal_degrees
    elif direction1 == 'S' and direction2 == 'E':
        return 180 - decimal_degrees
    elif direction1 == 'S' and direction2 == 'W':
        return 180 + decimal_degrees
    elif direction1 == 'E':
        return 90 - decimal_degrees if direction2 == 'N' else 90 + decimal_degrees
    elif direction1 == 'W':
        return 270 + decimal_degrees if direction2 == 'S' else 270 - decimal_degrees
    elif direction1 == 'N':
        return 0
    elif direction1 == 'S':
        return 180

    return decimal_degrees

def calculate_distance(point1, point2):
    """Calculate the Euclidean distance between two points."""
    return math.sqrt((point2.x - point1.x) ** 2 + (point2.y - point1.y) ** 2)

def create_dwg_file(starting_coords, bearings_distances, output_path, property_name, owner_name, registration_number):
    current_point = Point(starting_coords['easting'], starting_coords['northing'])
    coordinates = [(current_point.x, current_point.y)]

    print(f"Starting Point: {current_point}")

    for i, entry in enumerate(bearings_distances):
        bearing_text = entry['bearing']
        distance = entry['distance']

        # Parse the bearing text
        try:
            bearing = parse_bearing(bearing_text)
            print(f"Step {i + 1}: Bearing = {bearing} degrees, Distance = {distance} meters")
        except ValueError as e:
            print(f"Error parsing bearing at step {i + 1}: {e}")
            return

        # Calculate new point based on the bearing and distance
        angle_rad = math.radians(bearing)
        delta_x = distance * math.sin(angle_rad)
        delta_y = distance * math.cos(angle_rad)
        next_point = Point(current_point.x + delta_x, current_point.y + delta_y)
        coordinates.append((next_point.x, next_point.y))

        # Update the current point
        current_point = next_point
        print(f"New Point at Step {i + 1}: {current_point}")

    # Check if the polyline should close
    starting_point = Point(starting_coords['easting'], starting_coords['northing'])
    final_point = Point(coordinates[-1])

    # Calculate distance between the final point and the starting point
    distance_to_start = calculate_distance(final_point, starting_point)
    if distance_to_start < 0.01:  # Tolerance for small discrepancies
        print(f"Polyline closes with negligible gap of {distance_to_start} meters.")
        coordinates[-1] = (starting_point.x, starting_point.y)
    else:
        print(f"Warning: Polyline does not close. Gap distance is {distance_to_start} meters.")

    # Create the DWG file
    dwg = new("R2010")
    model_space = dwg.modelspace()

    # Draw the polyline
    model_space.add_lwpolyline(coordinates, close=False)

    # Prepare the multi-line text label with different font sizes
    full_label = f"{{\\H2.5x;{property_name}}}\n{{\\H2.0x;{owner_name}}}\n{{\\H2.0x;reg. no. {registration_number}}}"

    # Add multi-line text at the centroid with middle-center alignment
    centroid = LineString(coordinates).centroid
    model_space.add_mtext(
        full_label,
        dxfattribs={
            'char_height': 2.0,  # Base height, which will be scaled by formatting
            'insert': (centroid.x, centroid.y),
            'attachment_point': 5  # Middle center
        }
    )

    # Save the DWG file
    dwg.saveas(output_path)
    print(f"DWG file created at: {output_path}")

def main():
    # Ensure the JSON and DXF paths are provided
    if len(sys.argv) != 3:
        print("Usage: python create_dwg_from_bearings.py <json_output_path> <dxf_output_path>")
        sys.exit(1)

    json_output_path = sys.argv[1]  # Path to ai_output.json
    dxf_output_path = sys.argv[2]   # Path to save the DXF file

    # Read data from the specified JSON file
    starting_coords, bearings_distances, property_name, owner_name, registration_number = read_ai_data(json_output_path)
    
    # Create the DWG file with the specified output path
    create_dwg_file(starting_coords, bearings_distances, dxf_output_path, property_name, owner_name, registration_number)

if __name__ == "__main__":
    main()
