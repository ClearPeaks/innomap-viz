import sys
import os

# Ensure the src directory is in the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, send_from_directory, request
import yaml
from sharepoint import SharePoint
import webbrowser

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Flask app setup
app = Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, "..", "static"),
    template_folder=os.path.join(BASE_DIR, "..", "templates")
)

def read_config() -> dict:
    """
    Read YAML configuration with the SharePoint information.
    Extract required credentials to read SharePoint files and folders.
    """
    config_path = os.path.join(BASE_DIR, "..", "config.yml")
    with open(config_path) as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise Exception("Error reading configuration file", exc)

def download_excel():
    """
    Downloads the SynvertInnoMapTracker Excel file from SharePoint
    and saves it to the static folder.
    """
    config = read_config()
    sp = SharePoint(
        config["SharePoint"]["hostname"],
        config["SharePoint"]["site_name"],
        config["SharePoint"]["app_registration"]["client_id"],
        os.environ[config["SharePoint"]["app_registration"]["client_secret"]],
        config["SharePoint"]["app_registration"]["tenant_id"]
    )

    file_url = config["SharePoint"]["innomap_doc"]["sp_link"]
    save_path = os.path.join(BASE_DIR, "..", "static", "SynvertInnoMapTracker.xlsx")

    if os.path.exists(save_path):
        os.remove(save_path)
        print(f"Deleted existing file: {save_path}")

    sp.download_xlsx(file_url, save_path)
    print(f"Downloaded file to: {save_path}")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/SynvertInnoMapTracker.xlsx")
def serve_excel():
    static_dir = os.path.join(BASE_DIR, "..", "static")
    return send_from_directory(static_dir, "SynvertInnoMapTracker.xlsx")

@app.route("/refresh-data")
def refresh_data():
    token = request.args.get("token")
    if token != os.environ.get("REFRESH_TOKEN"):
        return "Unauthorized", 403

    try:
        download_excel()
        return "Excel updated successfully!"
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    download_excel()
    #webbrowser.open("http://localhost:8000")
    app.run()
