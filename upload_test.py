from google.cloud import storage
from PIL import Image


client = storage.Client()
bucket = client.get_bucket('ibvdata')
blob = bucket.blob('identhash/images/dm.png')
dm = Image.open("dm.png").convert("L")
blob.upload_from_file(dm)
