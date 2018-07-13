docker build -t gcr.io/innatelearning/ibv:v18 .
gcloud docker -- push gcr.io/innatelearning/ibv:v18
kubectl delete jobs --all
