import numpy as np
import pandas as pd
import glob

files = glob.glob("H:\AI_Core\Kirill\*.csv")
x, element = [], []
k = 0.005 / 50
data = None
for f in files:
    if data is None:
        data = pd.read_csv(f, sep=";", header=0, index_col=None)
    else:
        df = pd.read_csv(f, sep=";", header=0, index_col=None)
        data = data.append(df)

data = data.values

print(data.shape)

for i in data[:, :29]:
    t11 = np.concatenate(([i[-2] * k], i[0:3], i[6:9]))
    t12 = np.concatenate(([i[-2] * k], i[9:12], i[15:18]))
    t13 = np.concatenate(([i[-2] * k], i[18:21], i[24:27]))
    x.append([t11, t12, t13])

x = np.array(x)
print(x.shape)
print(x[6660])