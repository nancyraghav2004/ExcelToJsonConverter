from flask import Flask, request, jsonify, Response
import logging
from flasgger import Swagger 
from file_handler import upload_file_handler, get_latest_json, delete_old_files
from file_watcher import start_file_watcher

# Initialize Flask app
app = Flask(__name__)
swagger = Swagger(app)

# Setup logging
log_file_path = 'app_log.txt'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# POST method to upload Excel file
@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Upload an Excel file
    ---
    consumes:
      - multipart/form-data
    parameters:
      - name: file
        in: formData
        type: file
        required: true
        description: The Excel file to upload
    responses:
      200:
        description: File uploaded successfully
      400:
        description: Bad request
      500:
        description: Server error
    """
    return upload_file_handler(request)

# GET method to retrieve the latest JSON data
@app.route('/data', methods=['GET'])
def get_json_data():
    """
    Retrieve data from the latest JSON file
    ---
    responses:
      200:
        description: JSON data retrieved successfully
      404:
        description: No files found
      500:
        description: Server error
    """
    return get_latest_json()

# DELETE method to delete all files except the latest one
@app.route('/delete', methods=['DELETE'])
def delete_old_files_route():
    """
    Delete all old files except the latest one
    ---
    responses:
      200:
        description: Old files deleted successfully
      500:
        description: Server error
    """
    return delete_old_files()

if __name__ == '__main__':
    # Start the file watcher
    observer = start_file_watcher()
    
    try:
        app.run(debug=True)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()