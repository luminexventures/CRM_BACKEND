# Import required standard libraries
import os                 # For file and directory operations
import time              # For adding delay between checks
import json              # For reading JSON configuration
from datetime import datetime  # For timestamp logging

def load_config():
    """Load directory path from JSON configuration file"""
    with open('config/config.json', 'r') as file:
        return json.load(file)

def read_file(filepath):
    """
    Read and display the contents of a file
    Args:
        filepath (str): Full path to the file to be read
    """
    try:
        with open(filepath, 'r') as file:
            content = file.read()
            # Extract and display only the filename from the full path using split
            print(f"{filepath.split('\\')[1]}:\n{content}\n")
    except Exception as e:
        print(f"Error reading file: {e}")

def get_file_info(directory):
    """
    Get information about all files in the specified directory
    Args:
        directory (str): Path to the directory to monitor
    Returns:
        dict: Dictionary with filenames as keys and modification times as values
    """
    file_info = {}
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):  # Only track files, not subdirectories
            file_info[filename] = os.path.getmtime(filepath)
    return file_info

def watch_directory():
    """Main function to monitor directory for file changes"""
    # Load directory path from config
    config = load_config()
    directory = config['watch_directory']
    
    # Initialize file tracking with current state
    previous_files = get_file_info(directory)
    
    # Display startup message
    print(f"Started watching directory: {directory}")
    print("Press Ctrl+C to stop...")
    
    try:
        while True:
            # Get current state of directory
            current_files = get_file_info(directory)
            
            # Detect new files by finding differences between current and previous states
            new_files = set(current_files.keys()) - set(previous_files.keys())
            if new_files:
                for file in new_files:
                    filepath = os.path.join(directory, file)
                    print(f"{datetime.now()} - New file created: {file}")
                    print("Reading new file content:")
                    read_file(filepath)
            
            # Detect modified files by comparing modification timestamps
            for file in set(current_files.keys()) & set(previous_files.keys()):
                if current_files[file] != previous_files[file]:
                    filepath = os.path.join(directory, file)
                    print(f"{datetime.now()} - File modified: {file}")
                    print("Reading modified file content:")
                    read_file(filepath)
            
            # Detect deleted files
            deleted_files = set(previous_files.keys()) - set(current_files.keys())
            if deleted_files:
                for file in deleted_files:
                    print(f"{datetime.now()} - File deleted: {file}")
            
            # Update the previous state for next iteration
            previous_files = current_files
            
            # Pause before next check to prevent excessive CPU usage
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStoping watchdog service")

# Entry point of the script
if __name__ == "__main__":
    watch_directory()