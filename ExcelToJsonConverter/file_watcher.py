import os
import logging
import pandas as pd
import json
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

UPLOAD_FOLDER = 'upload_files'
JSON_FOLDER = 'json_files'
SCAN_INTERVAL = 10  # Interval in seconds to scan for new files manually

# Setup logger
logger = logging.getLogger(__name__)  #creating logger object, used to log msg throughout the script

# File Watcher Event Handler
class WatcherHandler(FileSystemEventHandler):
    # def on_created(self, event): #on-created method is triggered whenever a new file or directory is created in the watched folder.
    #     # Watch for .xlsx files
    #     if not event.is_directory and event.src_path.endswith('.xlsx'):  #ensures the event is triggered only for files, not directories.
    #         logger.info(f"New file detected: {event.src_path}")
    #         self.convert_to_json(event.src_path)  #calls the method convert_to_json to convert the detected Excel file into a JSON file.

    def convert_to_json(self, file_path):
        try:
            # Read Excel and convert to JSON
            df = pd.read_excel(file_path)   #uses pandas to read the Excel file into a DataFrame
            json_data = df.to_dict(orient="records")  # Converts the DataFrame into a list of dictionaries
            json_filename = os.path.splitext(os.path.basename(file_path))[0] + '.json'  #Extracts the file name (without the extension) from the full file path.
            json_filepath = os.path.join(JSON_FOLDER, json_filename)  #Constructs the complete file path for the new JSON file in the JSON_FOLDER

            # Write to JSON file
            with open(json_filepath, 'w') as json_file:  #Opens the JSON file for writing.
                json.dump(json_data, json_file, indent=4)  #Writes the JSON data to the file, using an indentation of 4 spaces for readability.
            logger.info(f"Converted {file_path} to {json_filepath}")
        except Exception as e:
            logger.error(f"Error during file conversion: {str(e)}")

    def scan_for_new_files(self):
        # Periodically scan for new .xlsx files that haven't been converted to JSON
        while True:
            try:
                xlsx_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.xlsx')]   #Filters only .xlsx files in the upload folder.
                json_files = [f.replace('.json', '') for f in os.listdir(JSON_FOLDER)]  #Lists JSON files already converted, removing the .json extension.

                for file in xlsx_files:   #Loops through the detected .xlsx files.
                    file_name_no_ext = os.path.splitext(file)[0]   #Checks if the Excel file has not already been converted to JSON
                    if file_name_no_ext not in json_files:
                        logger.info(f"Detected new file during scan: {file}")
                        self.convert_to_json(os.path.join(UPLOAD_FOLDER, file))  #Converts the new Excel file to JSON.

                time.sleep(SCAN_INTERVAL)
            except Exception as e:
                logger.error(f"Error during manual scan for new files: {str(e)}")

# Start file watcher
def start_file_watcher():
    event_handler = WatcherHandler()
    observer = Observer()
    observer.schedule(event_handler, path=UPLOAD_FOLDER, recursive=False)
    observer.start()
    logger.info("File watcher started.")

    # Start the manual scan in a separate thread
    from threading import Thread
    scan_thread = Thread(target=event_handler.scan_for_new_files)
    scan_thread.daemon = True  # Daemon thread will stop with the main program
    scan_thread.start()

    return observer



