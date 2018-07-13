import json
from datetime import datetime,timedelta
import time
import urllib

import numpy as np
from google.cloud import storage
from scipy.interpolate import griddata
import matplotlib.pyplot as plt

client = storage.Client()
bucket = client.get_bucket('ibvdata')
experiment_id = "2018-04-26-13-38-46"
path = "experiments/{}/outputs/json".format(experiment_id)
names = []
response = urllib.urlopen("https://storage.googleapis.com/ibvdata/experiments/{}/inputs/parameters".format(experiment_id))
parameter_set = json.load(response)
for params in parameter_set["lgn_parameter_set"]:
    names.append(params["name"])

timedeltas = []
started = 0
completed = 0
for blob in bucket.list_blobs(prefix=path):
    result =  json.loads(blob.download_as_string())
    if result["finished"] == None:
        started += 1
        #print(result["lgn_parameters"]["name"])
        #blob.delete()
    if result["finished"] is not None:
        completed += 1
        timedeltas.append(datetime.strptime(result["finished"],"%Y-%m-%d_%H:%M:%S") - datetime.strptime(result["started"],"%Y-%m-%d_%H:%M:%S"))

if completed > 0:
    average_timedelta = sum(timedeltas, timedelta(0)) / len(timedeltas)
    print(average_timedelta)

print("{} started".format(started))
print("{} parameters in total".format(len(set(names))))



print("{0:.2f} complete".format(float(completed) / len(set(names))))
