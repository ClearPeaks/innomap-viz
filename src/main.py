import sys
import os

# Ensure the src directory is in the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'external', 'innohub-backend')))

from flask import Flask, render_template, send_from_directory, request
import yaml
from innohub_backend.services.sharepoint import SharePoint
from common.keyvault import KeyVaultClient
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

    # Initialize SharePoint object to get token, site_id, and drive_id
    key_vault_client = KeyVaultClient()
    sp = SharePoint(
        key_vault_client.get_secret("SP_HOSTNAME"),
        key_vault_client.get_secret("SP_SITE_NAME"),
        key_vault_client.get_secret("SP_DELEGATED_APP_ID"),
        key_vault_client.get_secret("SP_TENANT_ID")
    )

    file_url = config["SharePoint"]["innomap_doc"]["sp_link"]
    save_path = os.path.join(BASE_DIR, "..", "static", "SynvertInnoMapTracker.xlsx")

    if os.path.exists(save_path):
        os.remove(save_path)
        print(f"Deleted existing file: {save_path}")

    if not save_path.endswith(".xlsx"):
        raise ValueError("Only .xlsx files are supported.")

    print(f"Attempting to download file from SharePoint: {file_url}")
    file_bytes = sp._get_file_content(file_url)

    if file_bytes is None:
        raise FileNotFoundError(f"File not found or unsupported drive in SharePoint URL: {file_url}")

    dir_path = os.path.dirname(save_path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    with open(save_path, "wb") as f:
        f.write(file_bytes)

    print(f"File successfully saved to: {save_path}")

    print(f"Downloaded file to: {save_path}")

@app.route("/")
def home():
    try:
        download_excel()
        return render_template("index.html")
    except Exception as e:
        return f"Error: {str(e)}", 500

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
    webbrowser.open("http://127.0.0.1:5000")
    app.run()
