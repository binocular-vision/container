import numpy as np
import argparse
import datetime


def generate_parameter_steps(min,max,step):
    return np.linspace(min,max,step)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Python script to create ibv experiment parameter file")
    parser.add_argument("-b","--bucket", help="specify google storage bucket", required=False, default="ibvdata")
    parser.add_argument("-dm","--depthmap", help="specify path to depthmap", required=False)
    parser.add_argument("-as","--autostereogram", help="specify path to autostereogram", required=False)
    parser.add_argument("-ap","--autostereogram_patch", help="size of autostereogram patch", type=int, required=False)
    parser.add_argument("-id","--id", help="experiment_id, defaults to current datetime", required=False, default=datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
    parser.add_argument("-nf","--num_filters", help="number of generated v1-like filters", type=int, required=False)
    parser.add_argument("-nc","--num_components", help="number of ICA components (per set of patches)", type=int, required=False)
    parser.add_argument("-np","--num_patches", help="number of patches (per ICA)", type=int, required=False)
    parser.add_argument("-ps","--patch_size", help="size of patches extracted from lgn activity (pixels)", type=int, required=False)
    parser.add_argument("-ls","--lgn_size", help="size of LGN model space", type=int, required=False)
    parser.add_argument("-la","--lgn_a", help="LGN model alpha (min,max,step)", nargs=3, metavar=("min", "max", "step"), type=float, required=False)
    parser.add_argument("-lp","--lgn_p", help="size of LGN model space", nargs=3, metavar=("min", "max", "step"), type=float, required=False)
    parser.add_argument("-lt","--lgn_t", help="size of LGN model space", nargs=3, metavar=("min", "max", "step"), type=float, required=False)
    parser.add_argument("-lr","--lgn_r", help="size of LGN model space", nargs=3, metavar=("min", "max", "step"), type=float, required=False)
    args = parser.parse_args()
    a_array = generate_parameter_steps(args.lgn_a[0],args.lgn_a[1],args.lgn_a[2])
    r_array = generate_parameter_steps(args.lgn_r[0],args.lgn_r[1],args.lgn_r[2])
    p_array = generate_parameter_steps(args.lgn_p[0],args.lgn_p[1],args.lgn_p[2])
    t_array = generate_parameter_steps(args.lgn_t[0],args.lgn_t[1],args.lgn_t[2])

    np.meshgrid(t_array,p_array)
    print("a")
    print(a_array)
    print("t")
    print(t_array)
    print("r")
    print(r_array)
    print("p")
    print(p_array)
