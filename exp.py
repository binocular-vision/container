import ibv
import json
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
    for lgn_parameters in experiment_parameters["lgn_parameter_set"]:
        experiment_subparameters = extract_subparameters(experiment_parameters,lgn_parameters)
        job_complete = check_log(bucket, experiment_subparameters)
        if job_complete is not True:
            work(bucket, experiment_subparameters)



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
        created_blob = bucket.blob(log_path)
        experiment_subparameters["started"] = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        created_blob.upload_from_string(json.dumps(experiment_subparameters,indent=4, separators=(',', ': ')))
        return False
    else:
        experiment_subparameters["finished"] = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        log_blob.upload_from_string(json.dumps(experiment_subparameters,indent=4, separators=(',', ': ')))
        return True

def work(bucket, experiment_subparameters):
    print(experiment_subparameters)
    results = ibv.cloud_experiment(bucket,experiment_subparameters,10,3)
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
