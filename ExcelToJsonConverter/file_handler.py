import os
import glob
import logging
import pandas as pd
import json
from flask import jsonify, request
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'upload_files'
JSON_FOLDER = 'json_files'

# Setup logger
logger = logging.getLogger(__name__)

# Ensure directories exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(JSON_FOLDER):
    os.makedirs(JSON_FOLDER)

# Handle file upload for POST method
def upload_file_handler(request):
    try:
        if 'file' not in request.files:
            logger.error("No file part in the request.")
            return jsonify({"error": "No file part in the request"}), 400

        file = request.files['file']
        if file.filename == '':
            logger.error("No file selected for uploading.")
            return jsonify({"error": "No file selected"}), 400

        if file and file.filename.endswith('.xlsx'):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            logger.info(f"File uploaded successfully: {filename}")
            return jsonify({"message": f"File {filename} uploaded successfully."}), 200
        else:
            logger.error("Invalid file format. Only .xlsx files are allowed.")
            return jsonify({"error": "Invalid file format. Only .xlsx files are allowed."}), 400

    except Exception as e:
        logger.error(f"Error during file upload: {str(e)}")
        return jsonify({"error": "An error occurred during file upload."}), 500

# Handle getting the latest JSON file for GET method
def get_latest_json():
    try:
        # Get all JSON files and find the latest one
        json_files = glob.glob(os.path.join(JSON_FOLDER, '*.json'))
        if not json_files:
            logger.error("No JSON files found.")
            return jsonify({"error": "No JSON files found."}), 404

        latest_file = max(json_files, key=os.path.getctime)
        logger.info(f"Reading data from {latest_file}")

        # Read and return the content of the latest JSON file
        with open(latest_file, 'r') as json_file:
            data = json.load(json_file)
        return jsonify(data), 200

    except Exception as e:
        logger.error(f"Error fetching JSON data: {str(e)}")
        return jsonify({"error": "An error occurred while fetching the JSON data.", "details": str(e)}), 500

# Handle deleting old files for DELETE method
def delete_old_files():
    try:
        # Delete all old Excel and JSON files except the latest ones
        def retain_latest(folder):
            files = glob.glob(os.path.join(folder, '*'))
            if not files:
                logger.warning(f"No files found in {folder}.")
                return
            latest_file = max(files, key=os.path.getctime)
            logger.info(f"Retaining latest file: {latest_file}")
            for file in files:
                if file != latest_file:
                    os.remove(file)
                    logger.info(f"Deleted file: {file}")

        retain_latest(UPLOAD_FOLDER)
        retain_latest(JSON_FOLDER)

        return jsonify({"message": "Old files deleted, latest files retained."}), 200

    except Exception as e:
        logger.error(f"Error deleting files: {str(e)}")
        return jsonify({"error": "An error occurred while deleting the files.", "details": str(e)}), 500