"""
Module containing code to commplete multithreaded downloads using python. 
"""
import logging
from tqdm import tqdm
 
from pathlib import Path
from urllib.request import urlretrieve
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger("__name__")

def download_file(url, output_path,raise_error=False):
    """Downloads a file using urllib and saves it to the output directory."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True,exist_ok=True)
    try:
        urlretrieve(url, output_path)
    except Exception as e:
        if raise_error:
            raise e
        else:
            logger.error(f"error downloading file {e}")

def download_urls(url_map, max_threads=4):
    """Downloads multiple files concurrently using threads."""

    with ThreadPoolExecutor(max_threads) as executor:
        futures = {executor.submit(download_file, url, output_path): url for url,output_path in url_map.items()}
        results = []
        for future in tqdm(futures, desc="Downloading files"):
            try:
                results.append(future.result())
            except Exception as e:
                logger.errors(f"Error during download: {e}")
        return results