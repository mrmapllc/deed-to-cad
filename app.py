from flask import Flask, render_template, request, redirect, url_for
import subprocess
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get the folder paths from the form
        input_folder = request.form["input_folder"]
        output_folder = request.form["output_folder"]

        # Check if folders exist
        if not os.path.exists(input_folder):
            return "Input folder does not exist. Please try again.", 400
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)  # Create output folder if it doesn't exist

        # Path to the main_script.py in the scripts directory
        main_script_path = os.path.join("G:\\aineer_folder\\scripts", "main_script.py")

        # Run main_script.py with specified folders
        try:
            subprocess.run(['python', main_script_path, input_folder, output_folder], check=True)
        except subprocess.CalledProcessError as e:
            return f"An error occurred: {e}", 500

        return redirect(url_for("index"))

    return render_template("index.html")

if __name__ == "__main__":
    # Get the port from the environment (Render provides this as PORT)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
