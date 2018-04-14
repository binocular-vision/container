docker build  -t gcr.io/innatelearning/ibv:v15 .
gcloud docker -- push gcr.io/innatelearning/ibv:v15
kubectl delete jobs --all
