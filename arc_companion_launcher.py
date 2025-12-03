import tkinter as tk
from tkinter import PhotoImage, font, ttk
import requests
import zipfile
import os
import sys
import shutil
import threading
import hashlib
import subprocess
import json
from pathlib import Path

# Global variables
root = None
progress_bar = None
progress_label = None
download_thread = None

# Load configuration
CONFIG_PATH = Path(__file__).parent / "config.json"
DEFAULT_CONFIG = {
    "update_server": "https://ghostworld073.pythonanywhere.com",
    "max_download_size_mb": 500,
    "enable_hash_verification": True,
    "connection_timeout_seconds": 30
}

def load_config():
    """Load configuration from config.json or return defaults."""
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Merge with defaults to ensure all keys exist
                return {**DEFAULT_CONFIG, **config}
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config: {e}. Using defaults.")
    return DEFAULT_CONFIG.copy()

CONFIG = load_config()

def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')

def check_for_update(current_version):
    try:
        # Use timeout and verify SSL certificates
        url = f"{CONFIG['update_server']}/latest_arc_companion"
        response = requests.get(
            url,
            timeout=CONFIG['connection_timeout_seconds'],
            verify=True
        )
        response.raise_for_status()  # Check for HTTP errors
        latest_version = response.json()[0]  # Assuming JSON response instead of text eval
        if latest_version != current_version:
            print(f"New version available: {latest_version}")
            return True
        else:
            print("No new version available.")
            return False
    except requests.RequestException as e:
        print(f"Error checking for updates: {e}")
        return False

def download_update():
    global download_thread
    download_thread = threading.Thread(target=download_update_thread)
    download_thread.start()
    # Start a periodic UI update
    root.after(100, check_download_thread)

def download_update_thread():
    try:
        # Download with timeout and SSL verification
        url = f"{CONFIG['update_server']}/download_latest_arc_companion"
        response = requests.get(
            url,
            stream=True,
            timeout=CONFIG['connection_timeout_seconds'],
            verify=True
        )
        response.raise_for_status()  # Check for HTTP errors
        total_size = int(response.headers.get('content-length', 0))
        
        # Validate file size (prevent zip bombs)
        max_size = CONFIG['max_download_size_mb'] * 1024 * 1024
        if total_size > max_size:
            print(f"Update file too large: {total_size} bytes (max: {max_size})")
            root.after(0, launch_application)
            return
        
        block_size = 1024
        downloaded_size = 0
        sha256_hash = hashlib.sha256()

        # Prepare progress bar for the download
        progress_bar['maximum'] = total_size

        with open("arc_companion_update.zip", "wb") as file:
            for data in response.iter_content(block_size):
                file.write(data)
                if CONFIG['enable_hash_verification']:
                    sha256_hash.update(data)
                downloaded_size += len(data)
                # Update progress variables
                mb_downloaded = downloaded_size / (1024 * 1024)
                mb_total = total_size / (1024 * 1024)
                # Schedule UI update
                root.after(0, update_progress_ui, downloaded_size, total_size, mb_downloaded, mb_total)
        
        # Verify downloaded file hash (implement when server provides checksums)
        if CONFIG['enable_hash_verification']:
            file_hash = sha256_hash.hexdigest()
            print(f"Downloaded file SHA256: {file_hash}")
            # TODO: Verify against expected hash from server
        
        print("File downloaded and saved as arc_companion_update.zip")
        # Start extraction in a separate thread
        root.after(0, apply_update)
    except requests.RequestException as e:
        print(f"Error downloading update: {e}")
        root.after(0, launch_application)
    except Exception as e:
        print(f"Unexpected error during download: {e}")
        root.after(0, launch_application)

def update_progress_ui(downloaded_size, total_size, mb_downloaded, mb_total):
    progress_bar['value'] = downloaded_size
    progress_label.config(text=f"Updating: {mb_downloaded:.2f} MB / {mb_total:.2f} MB")

def check_download_thread():
    if download_thread.is_alive():
        # Reschedule this check
        root.after(100, check_download_thread)
    else:
        # Download thread has finished
        pass  # Do nothing here; apply_update will be called from the download thread

def apply_update():
    extract_thread = threading.Thread(target=apply_update_thread)
    extract_thread.start()
    # Start a periodic check for the extraction thread
    root.after(100, check_extract_thread, extract_thread)

def apply_update_thread():
    try:
        # Safely extract zip with path traversal protection
        with zipfile.ZipFile('arc_companion_update.zip', 'r') as zip_ref:
            # Validate all file paths before extraction
            for file_info in zip_ref.infolist():
                # Normalize path and check for directory traversal
                file_path = os.path.normpath(os.path.join('.', file_info.filename))
                if file_path.startswith('..' + os.sep) or os.path.isabs(file_info.filename):
                    print(f"Suspicious file path in zip: {file_info.filename}")
                    raise zipfile.BadZipFile("Zip contains unsafe file paths")
            
            # Extract to current directory
            zip_ref.extractall('.')
        
        # Clean up downloaded zip file
        try:
            os.remove('arc_companion_update.zip')
        except OSError:
            pass
        
        print("Update extracted successfully.")
    except zipfile.BadZipFile as e:
        print(f"Error extracting update: {e}")
    except Exception as e:
        print(f"Unexpected error during extraction: {e}")
    finally:
        # Proceed to launch the application
        root.after(0, launch_application)

def check_extract_thread(extract_thread):
    if extract_thread.is_alive():
        # Reschedule this check
        root.after(100, check_extract_thread, extract_thread)
    else:
        # Extraction thread has finished
        pass  # Do nothing here; launch_application will be called from the extraction thread

def launch_application():
    try:
        if os.path.isfile('arc_companion.exe'):
            # Use subprocess instead of os.system for security
            # On Windows, use subprocess with proper shell handling
            if sys.platform == 'win32':
                subprocess.Popen(['arc_companion.exe'], shell=False)
            else:
                # For other platforms, adjust accordingly
                subprocess.Popen(['./arc_companion.exe'], shell=False)
        else:
            print("Executable not found.")
    except subprocess.SubprocessError as e:
        print(f"Error launching application: {e}")
    except Exception as e:
        print(f"Unexpected error launching application: {e}")

    # Exit the updater
    if root:
        root.quit()
        root.destroy()
    sys.exit()

def update_app():
    try:
        with open('arc_companion_version.txt', 'r') as version_file:
            current_version = version_file.read().strip()
        if check_for_update(current_version):
            global root, progress_bar, progress_label
            root = tk.Tk()
            root.title("Updating ARC Companion")
            root.configure(bg='black')
            root.minsize(400, 200)

            frame = tk.Frame(root, bg='black')
            frame.pack(fill='both', expand=True)

            custom_font = font.Font(family="Helvetica", size=14)
            progress_label = tk.Label(frame, text="Updating...", bg='black', fg='white', font=custom_font)
            progress_label.pack(padx=20, pady=30)

            progress_bar = ttk.Progressbar(frame, orient='horizontal', length=300, mode='determinate')
            progress_bar.pack(pady=10)

            center_window(root)

            try:
                icon = PhotoImage(file='Companion.png')
                root.iconphoto(False, icon)
            except tk.TclError:
                print("Icon file not found.")

            # Start the download in a separate thread
            download_update()
            root.mainloop()
        else:
            launch_application()
    except FileNotFoundError:
        print("Version file not found.")
        launch_application()

update_app()
