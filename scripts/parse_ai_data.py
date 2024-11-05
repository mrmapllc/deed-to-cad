import json

def read_ai_data(file_path):
    # Reading and processing JSON data
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Extract details
    starting_coordinates = data.get('starting_coordinates', {})
    bearings_distances = []
    for item in data.get('bearings_and_distances', []):
        bearing = item['bearing'].replace("\\u00b0", "°").replace("\\'", "'").replace('\\"', '"')
        bearings_distances.append({
            "bearing": bearing,
            "distance": item['distance']
        })

    # Retrieve property name, owner name, and registration number from JSON data
    property_name = data.get('property_name', "Unknown Property")
    owner_name = data.get('owner_name', "Unknown Owner")
    registration_number = data.get('registration_number', "Unknown Registration")

    # Return all necessary values
    return starting_coordinates, bearings_distances, property_name, owner_name, registration_number

# Test function when running parse_ai_data.py directly
if __name__ == "__main__":
    starting_coords, bearings_distances, property_name, owner_name, registration_number = read_ai_data('ai_output.json')
    print("Starting Coordinates:", starting_coords)
    print("Bearings and Distances:", bearings_distances)
    print("Property Name:", property_name)
    print("Owner Name:", owner_name)
    print("Registration Number:", registration_number)
