import subprocess
import os
import sys

def main(input_folder, output_folder):
    # Paths to scripts
    ai_extraction_script = os.path.join("G:\\aineer_folder\\scripts", "ai_extraction.py")
    create_dwg_script = os.path.join("G:\\aineer_folder\\scripts", "create_dwg_from_bearings.py")
    
    # Check if the given folder exists
    if not os.path.exists(input_folder):
        print(f"Error: The folder '{input_folder}' does not exist.")
        return
    
    # Check if the output folder exists, if not, create it
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created output folder: {output_folder}")

    # List all PDF files in the given folder
    pdf_paths = [os.path.join(input_folder, file) for file in os.listdir(input_folder) if file.lower().endswith('.pdf')]

    if not pdf_paths:
        print(f"No PDF files found in folder '{input_folder}'.")
        return

    # Process each PDF file found in the folder
    for pdf_path in pdf_paths:
        print(f"Processing file: {pdf_path}")

        # Define the path for ai_output.json in the output folder
        json_output_path = os.path.join(output_folder, "ai_output.json")

        # Run AI Extraction Script with the specified output path for ai_output.json
        subprocess.run(['python', ai_extraction_script, pdf_path, json_output_path])

        # Define the DXF output file path
        dxf_output_path = os.path.join(output_folder, os.path.splitext(os.path.basename(pdf_path))[0] + ".dxf")
        
        # Run DWG Creation Script with the paths to the JSON output file and DXF output file
        subprocess.run(['python', create_dwg_script, json_output_path, dxf_output_path])

if __name__ == "__main__":
    # Ensure both input and output paths are provided
    if len(sys.argv) != 3:
        print("Usage: python main_script.py <input_folder> <output_folder>")
        sys.exit(1)

    input_folder = sys.argv[1]
    output_folder = sys.argv[2]
    main(input_folder, output_folder)
