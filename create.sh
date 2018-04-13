#!/bin/bash

XID="$(python create_experiment_file.py -dm=dm.png -as=shift5_70patch.png -ap=70 -nf=5 -nc=5 -np=200 -ps=8 -ls=128 -la 0 0.1 0.05 -lp 0.11 0.15 0.01 -lt 3 3.1 0.05 -lr 3 3.1 0.05)"
python exp.py $XID
