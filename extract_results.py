import json
import numpy as np
from google.cloud import storage
from scipy.interpolate import griddata
import matplotlib.pyplot as plt



client = storage.Client()
bucket = client.get_bucket('ibvdata')
experiment_id = "2018-04-14-06-00-26"
path = "experiments/{}/outputs/json/".format(experiment_id)

T = []
P = []
C = []

for blob in bucket.list_blobs(prefix=path):
    result =  json.loads(blob.download_as_string())
    T.append(result["lgn_parameters"]["lgn_t"])
    P.append(result["lgn_parameters"]["lgn_p"])
    C.append(result["correlation"])


T = np.array(T)
P = np.array(P)
C = np.array(C)

print(T)
print(P)
print(C)


column = np.column_stack((T,P))
xi = np.linspace(T.min(), T.max(), 100)
yi = np.linspace(P.min(), P.max(), 100)
xi, yi = np.meshgrid(xi, yi)

# interpolate
zi = griddata(column, C, (xi, yi), method="cubic")

plt.contourf(xi, yi, zi)
plt.show()
