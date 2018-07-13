import ibv
import os
import numpy as np
import argparse
import datetime
import json
from google.cloud import storage

"""


python create_experiment_file.py -nf=2000 -nc=20 -np=100000 -ps=8 -ls=64 -la 0.05 0.05 1 -lp 0.5 1.5 10 -lt 1 4 8 -lr 4 4 1

"""

def generate_parameter_steps(min,max,step):
    return np.linspace(min,max,step)

def calculate_optimal_p(t, r, a):
    p = t / (((np.pi * (r**2)/2))*(1+a))
    return p

def generate_lgn_parameter_set(a_array,r_array,p_array,t_array):
    lgn_parameter_set = []
    for lgn_a in a_array:
        for lgn_r in r_array:
            for lgn_t in t_array:
                for lgn_p in p_array:
                    #p = calculate_optimal_p(lgn_t, lgn_r, lgn_a) * lgn_p
                    #switch lgn_p to p and uncomment the above line to handle percentages
                    name = "a{:0.2f}_r{:.2f}_p{:.2f}_t{:.2f}".format(lgn_a,lgn_r,lgn_p,lgn_t)
                    parameter = {
                    "lgn_a": lgn_a,
                    "lgn_r": lgn_r,
                    "lgn_p": lgn_p,
                    "lgn_t": lgn_t,
                    "name" : name,
                    }
                    lgn_parameter_set.append(dict(parameter))
    return lgn_parameter_set

def generate_experiment_set(bucket,experiment_id,depthmap_name,autostereogram_name,autostereogram_patch,num_filters,num_components,num_patches,patch_size,lgn_size,lgn_parameter_set):
    experiment_set = {
    "bucket": bucket,
    "experiment_id": experiment_id,
    "parameter_path": "experiments/{}/inputs/parameters".format(experiment_id),
    "depthmap_path": "experiments/{}/inputs/{}".format(experiment_id, depthmap_name),
    "autostereogram_path": "experiments/{}/inputs/{}".format(experiment_id,autostereogram_name),
    "autostereogram_patch": autostereogram_patch,
    "num_filters": num_filters,
    "num_components": num_components,
    "num_patches": num_patches,
    "patch_size": patch_size,
    "lgn_size": lgn_size,
    "lgn_parameter_set": lgn_parameter_set,
    }
    return experiment_set

def push_inputs(experiment_set, depthmap_filepath, autostereogram_filepath):
    client = storage.Client()
    bucket = client.get_bucket(experiment_set["bucket"])

    created_parameter_blob = bucket.blob(experiment_set["parameter_path"])
    created_parameter_blob.upload_from_string(json.dumps(experiment_set,indent=4, separators=(',', ': ')))

    created_depthmap_blob = bucket.blob(experiment_set["depthmap_path"])
    created_depthmap_blob.upload_from_filename(depthmap_filepath)

    created_autostereogram_blob = bucket.blob(experiment_set["autostereogram_path"])
    created_autostereogram_blob.upload_from_filename(autostereogram_filepath)



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Python script to create ibv experiment parameter file")
    parser.add_argument("-b","--bucket", help="specify google storage bucket", required=False, default="ibvdata")
    parser.add_argument("-dm","--depthmap", help="specify path to depthmap", required=True)
    parser.add_argument("-as","--autostereogram", help="specify path to autostereogram", required=True)
    parser.add_argument("-ap","--autostereogram_patch", help="size of autostereogram patch", type=int, required=True)
    parser.add_argument("-id","--id", help="experiment_id, defaults to current datetime", required=False, default=datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
    parser.add_argument("-nf","--num_filters", help="number of generated v1-like filters", type=int, required=True)
    parser.add_argument("-nc","--num_components", help="number of ICA components (per set of patches)", type=int, required=True)
    parser.add_argument("-np","--num_patches", help="number of patches (per ICA)", type=int, required=True)
    parser.add_argument("-ps","--patch_size", help="size of patches extracted from lgn activity (pixels)", type=int, required=True)
    parser.add_argument("-ls","--lgn_size", help="size of LGN model space", type=int, required=True)
    parser.add_argument("-la","--lgn_a", help="LGN model alpha (min,max,step)", nargs=3, metavar=("min", "max", "step"), type=float, required=True)
    parser.add_argument("-lp","--lgn_p", help="size of LGN model space", nargs=3, metavar=("min", "max", "step"), type=float, required=True)
    parser.add_argument("-lt","--lgn_t", help="size of LGN model space", nargs=3, metavar=("min", "max", "step"), type=float, required=True)
    parser.add_argument("-lr","--lgn_r", help="size of LGN model space", nargs=3, metavar=("min", "max", "step"), type=float, required=True)
    args = parser.parse_args()
    a_array = generate_parameter_steps(args.lgn_a[0],args.lgn_a[1],args.lgn_a[2])
    r_array = generate_parameter_steps(args.lgn_r[0],args.lgn_r[1],args.lgn_r[2])
    p_array = generate_parameter_steps(args.lgn_p[0],args.lgn_p[1],args.lgn_p[2])
    t_array = generate_parameter_steps(args.lgn_t[0],args.lgn_t[1],args.lgn_t[2])

    #add error checking for empty arrays based on np.arange impossible case (1,1,1)
    depthmap_name = os.path.basename(os.path.normpath(args.depthmap))
    autosterogram_name = os.path.basename(os.path.normpath(args.autostereogram))
    pset = generate_lgn_parameter_set(a_array,r_array,p_array,t_array)
    exp = generate_experiment_set(args.bucket, args.id,depthmap_name, autosterogram_name,args.autostereogram_patch, args.num_filters,args.num_components,args.num_patches,args.patch_size,args.lgn_size,pset)
    push_inputs(exp, args.depthmap, args.autostereogram)
    total = []
    for lgn_parameters in exp["lgn_parameter_set"]:
        total.append(lgn_parameters["name"])
    kubefile = """apiVersion: batch/v1
kind: Job
metadata:
  # Unique key of the Job instance
  generateName: "ibv-"
spec:
  backoffLimit: 2
  completions: {}
  parallelism: {}
  template:
    metadata:
      name: ibv
    spec:
      containers:
      - name: ibv
        image: gcr.io/innatelearning/ibv:v18
        resources:
          requests:
            cpu: 300m
        command: ["python"]
        args: ["exp.py", "{}"]
      # Do not restart containers after they exit
      restartPolicy: Never""".format(len(set(total)),len(set(total)),args.id)


    with open("jobs/{}.yaml".format(args.id), "w") as text_file:
        text_file.write(kubefile)

    print("experiment {} created".format(args.id))
    print("To deploy, run:")
    print("kubectl create -f jobs/{}.yaml".format(args.id))
