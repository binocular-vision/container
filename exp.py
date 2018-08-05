import os
import ibv
import json
import random
import datetime
import argparse
import numpy as np
from google.cloud import storage

def get_parameters(bucket,experiment_id):
    parameters = "experiments/{}/inputs/parameters".format(experiment_id)
    parameter_blob = bucket.get_blob(parameters)
    if parameter_blob == None:
        print("NOT FOUND")
        #add error checking
    else:
        experiment_parameters = json.loads(parameter_blob.download_as_string())
        return experiment_parameters

def run_workload(bucket,experiment_parameters):
    started = []
    total = []
    path = "experiments/{}/outputs/json/".format(experiment_parameters["experiment_id"])
    for lgn_parameters in experiment_parameters["lgn_parameter_set"]:
        total.append(lgn_parameters["name"])
    while len(set(total)) != len(set(started)):
        started = []
        for blob in bucket.list_blobs(prefix=path):
            started.append(os.path.basename(blob.name))
        diff = list(set(total)-set(started))
        if len(diff) == 0:
            break
        selection = random.choice(diff)
        experiment_subparameters = extract_subparameters(experiment_parameters,experiment_parameters["lgn_parameter_set"][total.index(selection)])
        ex = check_log(bucket,experiment_subparameters)
        work(bucket, ex)


def extract_subparameters(experiment_parameters, lgn_parameters):
    #pass index instead of lgn_parameters?
    subparameters = {
    "bucket": experiment_parameters["bucket"],
    "experiment_id": experiment_parameters["experiment_id"],
    "parameter_path": experiment_parameters["parameter_path"],
    "depthmap_path": experiment_parameters["depthmap_path"],
    "autostereogram_path": experiment_parameters["autostereogram_path"],
    "autostereogram_patch": experiment_parameters["autostereogram_patch"],
    "num_filters": experiment_parameters["num_filters"],
    "num_components": experiment_parameters["num_components"],
    "num_patches": experiment_parameters["num_patches"],
    "patch_size": experiment_parameters["patch_size"],
    "lgn_size": experiment_parameters["lgn_size"],
    "lgn_parameters": lgn_parameters,
    "started": None,
    "finished": None,
    "correlation": None,
    "lgn_dump": "experiments/{}/outputs/images/{}/layers".format(experiment_parameters["experiment_id"],lgn_parameters["name"]),
    "patch_dump": "experiments/{}/outputs/images/{}/patches".format(experiment_parameters["experiment_id"],lgn_parameters["name"]),
    "filter_dump": "experiments/{}/outputs/images/{}/filters".format(experiment_parameters["experiment_id"],lgn_parameters["name"]),
    "activity_dump": "experiments/{}/outputs/images/{}/activity".format(experiment_parameters["experiment_id"],lgn_parameters["name"])
    }
    return subparameters


def check_log(bucket, experiment_subparameters):
    experiment_id = experiment_subparameters["experiment_id"]
    lgn_parameter_name = experiment_subparameters["lgn_parameters"]["name"]
    log_path = "experiments/{}/outputs/json/{}".format(experiment_id,lgn_parameter_name)
    log_blob = bucket.get_blob(log_path)
    if log_blob == None:
        if experiment_subparameters["started"] == None:
            created_blob = bucket.blob(log_path)
            experiment_subparameters["started"] = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
            print("started")
            print(experiment_subparameters["lgn_parameters"]["name"])
            print(experiment_subparameters)
            created_blob.upload_from_string(json.dumps(experiment_subparameters,indent=4, separators=(',', ': ')))
            return experiment_subparameters
    else:
        #check this logic
        if experiment_subparameters["correlation"] is not None:
            experiment_subparameters["finished"] = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
            log_blob.upload_from_string(json.dumps(experiment_subparameters,indent=4, separators=(',', ': ')))
            return experiment_subparameters

def work(bucket, experiment_subparameters):
    print(bucket)
    print(experiment_subparameters["depthmap_path"])
    try:
        results = ibv.cloud_experiment(bucket,experiment_subparameters,5,5)
    except ValueError as err:
        results = experiment_subparameters
        results["finished"] = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        # check error and set correlation
        if str(err) == 'LGN: activity less than low bound':
            results["correlation"] = -1.0

        if str(err) == 'LGN: activity greater than high bound':
            results["correlation"] = 2.0

    
    check_log(bucket,results)



def run():
    parser = argparse.ArgumentParser(description="Python script to create ibv experiment parameter file")
    parser.add_argument("experiment_id", help="specify experiment id")
    args = parser.parse_args()
    client = storage.Client()
    bucket = client.get_bucket("ibvdata")
    p = get_parameters(bucket, args.experiment_id)
    run_workload(bucket,p)


run()
