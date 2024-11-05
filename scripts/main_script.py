import os
import subprocess
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        input_folder = os.path.abspath(request.form["input_folder"])  # Ensure absolute path
        output_folder = os.path.abspath(request.form["output_folder"])  # Ensure absolute path

        # Check if folders exist
        if not os.path.exists(input_folder):
            return "Input folder does not exist. Please try again.", 400
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)  # Create output folder if it doesn't exist

        # Path to the main_script.py in the scripts directory
        main_script_path = os.path.join("G:\\aineer_folder\\scripts", "main_script.py")

        # Run main_script.py with specified folders
        try:
            result = subprocess.run(['python', main_script_path, input_folder, output_folder], check=True, capture_output=True, text=True)
            print(result.stdout)  # Optionally log the script's output
        except subprocess.CalledProcessError as e:
            # Capture and display the error message
            error_msg = f"An error occurred: {e}\nOutput: {e.output}\nError: {e.stderr}"
            print(error_msg)
            return error_msg, 500

        return redirect(url_for("index"))

    return render_template("index.html")
