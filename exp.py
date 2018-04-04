import ibv
import numpy as np
from PIL import Image

#need to revise image opening
#add functionality for google cloud storage
auto = ibv.open_norm("shift5_70patch.png",verbose=False)
gt = np.array(Image.open("dm.png").convert("L"))
a = 0.05
r = 3
t = 4
p = ibv.calculate_optimal_p(t,r,a)

x = ibv.run_experiment(2000, 20, 100000, 8, 64, p, r, t, a, auto, 70, gt, "feb27")
print(x)
