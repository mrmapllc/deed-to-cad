import os
import subprocess
from flask import Flask, render_template, request, redirect, url_for
from flask_cors import CORS
from ai_extraction import process_pdf_files
from werkzeug.utils import secure_filename


app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        input_folder = os.path.abspath(request.form["input_folder"])
        output_folder = os.path.abspath(request.form["output_folder"])

        # Debug print statements to verify paths received
        print("Received Input Folder:", input_folder)
        print("Received Output Folder:", output_folder)

        # Check if folders exist
        if not os.path.isdir(input_folder):
            print("Input folder does not exist.")
            return "Input folder does not exist. Please try again.", 400
        if not os.path.isdir(output_folder):
            os.makedirs(output_folder)  # Create output folder if it doesn't exist

        # Path to the main_script.py in the scripts directory
        main_script_path = os.path.join("G:\\aineer_folder\\scripts", "main_script.py")

        # Process each PDF file in the input folder
        for filename in os.listdir(input_folder):
            if filename.endswith(".pdf"):
                pdf_path = os.path.join(input_folder, filename)

                try:
                    result = subprocess.run(
                        ['python', main_script_path, pdf_path, output_folder],
                        check=True,
                        capture_output=True,
                        text=True
                    )
                    print(result.stdout)  # Log the script's output
                except subprocess.CalledProcessError as e:
                    error_msg = f"An error occurred while processing {filename}: {e}\nOutput: {e.output}\nError: {e.stderr}"
                    print(error_msg)
                    return error_msg, 500

        return redirect(url_for("index"))

    return render_template("index.html")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Render uses PORT environment variable
    app.run(host='0.0.0.0', port=port)
