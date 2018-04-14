from google.cloud import storage
import json


client = storage.Client()
bucket = client.get_bucket('ibvdata')
blob = bucket.get_blob("experiments/2018-04-14-03-06-01/outputs/json/a0.05_r3.00_p0.05_t1.00")
check = json.loads(blob.download_as_string())
print(check)
