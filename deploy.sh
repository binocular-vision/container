docker build -t gcr.io/innatelearning/ibv:0.1.0 . --no-cache
gcloud docker -- push gcr.io/innatelearning/ibv:0.1.0
kubectl delete jobs --all
