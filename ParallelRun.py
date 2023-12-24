import multiprocessing
from  pipeline import extraction_process
import requests
import json

link = "https://datasets-server.huggingface.co/rows?dataset=TaylorAI%2Fpubmed_commercial&config=default&split=train&offset=0&length=100"
req = requests.get(link)
content = json.loads(req.content)
files = content['rows']


if __name__ == "__main__":
    extraction_process(files[1])