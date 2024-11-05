import openai
import os
import json
import sys
import re
from google.cloud import vision
from pdf2image import convert_from_path

# Load environment variables from a .env file (for local development)
load_dotenv()

# Retrieve the OpenAI API key from the environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Retrieve Google Vision credentials path from the environment variable
google_creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if google_creds_path:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_creds_path
else:
    print("Warning: GOOGLE_APPLICATION_CREDENTIALS environment variable is not set.")

def process_with_openai(extracted_text):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "user",
                "content": (
                    "Analyze the following text for property boundary descriptions, directions, distances, and coordinate systems. "
                    "If you find all the necessary information, structure the output in the following JSON format:\n\n"
                    "{\n"
                    "    \"property_name\": \"<Property Name>\",\n"
                    "    \"starting_coordinates\": {\n"
                    "        \"northing\": <Northing Value>,\n"
                    "        \"easting\": <Easting Value>\n"
                    "    },\n"
                    "    \"bearings_and_distances\": [\n"
                    "        {\n"
                    "            \"bearing\": \"<Bearing>\",\n"
                    "            \"distance\": <Distance Value>\n"
                    "        },\n"
                    "        ...\n"
                    "    ],\n"
                    "    \"coordinate_system\": \"<Coordinate System>\"\n"
                    "}\n\n"
                    "If you cannot find all the necessary information, summarize what is missing instead."
                    f"\n\n{extracted_text}"
                )
            }
        ],
        max_tokens=1000,
    )
    
    return response['choices'][0]['message']['content']

def extract_text_with_google_vision(image_path):
    client = vision.ImageAnnotatorClient()
    with open(image_path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.document_text_detection(image=image)

    if response.error.message:
        raise Exception(f'{response.error.message}')
    
    return response.full_text_annotation.text

def save_json(data, json_path):
    with open(json_path, 'w') as file:
        json.dump(data, file, indent=4)

def extract_details_from_filename(filename):
    # Extract details using regular expressions
    pattern = r"^(.*?) - (.*?) \(reg\. no\. (\d+)\)\.pdf$"
    match = re.match(pattern, filename)
    
    if match:
        property_name = match.group(1).strip()
        owner_name = match.group(2).strip()
        registration_number = match.group(3).strip()
        return property_name, owner_name, registration_number
    else:
        return "Unknown Property", "Unknown Owner", "Unknown Registration"

def main():
    # Ensure the correct number of command-line arguments
    if len(sys.argv) != 3:
        print("Usage: python ai_extraction.py <path_to_pdf> <output_json_path>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_json_path = sys.argv[2]  # Specify where ai_output.json should be saved

    # Extract details from the PDF file name
    pdf_filename = os.path.basename(pdf_path)
    property_name, owner_name, registration_number = extract_details_from_filename(pdf_filename)
    print(f"Extracted from filename - Property Name: {property_name}, Owner: {owner_name}, Registration No.: {registration_number}")

    if not os.path.exists(pdf_path):
        print(f"Error: The file {pdf_path} does not exist.")
        sys.exit(1)

    images = convert_from_path(pdf_path)

    search_phrases = ["Schedule A", "ALL THAT piece or parcel of land"]
    found_all_data = False

    for i, image in enumerate(images):
        image_path = f"page_{i + 1}.png"
        image.save(image_path, "PNG")
        print(f"Image saved for Page {i + 1}.")

        try:
            extracted_text = extract_text_with_google_vision(image_path)
            print(f"\nExtracted Text from Page {i + 1}:\n", extracted_text)

            found_phrase = next((phrase for phrase in search_phrases if phrase in extracted_text), None)
            if found_phrase:
                print(f"Found '{found_phrase}' in Page {i + 1}.\n")
                openai_response = process_with_openai(extracted_text)
                print(f"\nGPT-4 Response for Page {i + 1}:\n", openai_response)

                try:
                    # Attempt to load JSON directly from AI response
                    json_data = json.loads(openai_response)
                    
                    # Add extracted details from filename to JSON data
                    json_data['property_name'] = property_name
                    json_data['owner_name'] = owner_name
                    json_data['registration_number'] = registration_number

                    if "starting_coordinates" in json_data and "bearings_and_distances" in json_data:
                        save_json(json_data, output_json_path)
                        print(f"Data saved to JSON file at: {output_json_path}")
                        found_all_data = True
                        break
                    else:
                        print("Incomplete data in JSON response.")

                except json.JSONDecodeError:
                    print("AI response was not in valid JSON format.")
            else:
                print(f"No relevant property description found in Page {i + 1}.")
        except Exception as e:
            print(f"Error processing Page {i + 1}: {e}")
            continue

    if not found_all_data:
        print("Warning: Did not find all necessary information to create the polyline.")

if __name__ == "__main__":
    main()
