from datetime import datetime, timedelta
import os
import requests

def get_date_7_days_before_today():
    # Get today's date
    today = datetime.today()
    # Subtract 7 days from today's date
    past_date = today - timedelta(days=7)
    # Format the date as a string in the format 'YYYY-MM-DD'
    return past_date.strftime('%Y-%m-%d')

def download_file(url, save_dir='./', filename=None):
    """
    Downloads a file from the given URL and saves it locally.

    Parameters:
    - url (str): The URL of the file to download.
    - save_dir (str): The directory where the file should be saved. Default is current directory.
    - filename (str): The name to save the file as. If None, uses the name from the URL.

    Returns:
    - str: The path to the saved file.
    """
    # Create the save directory if it doesn't exist
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # Use the filename from the URL if not provided
    if filename is None:
        filename = os.path.basename(url)

    # Construct the full path to save the file
    file_path = os.path.join(save_dir, filename)

    # Download the file
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    else:
        response.raise_for_status()  # Raise an error on bad status

    return file_path