from multiprocessing import Pool
from  pipeline import extraction_process
import requests
import json

def check_dataset(url):
    req = requests.get(url)
    content = json.loads(req.content)
    files = content['rows']

    return files


if __name__ == "__main__":
    url = input('Enter api url: ')
    files = check_dataset(url)
    extraction_process(files[50])