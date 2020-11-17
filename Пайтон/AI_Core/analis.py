import pandas
data = pandas.read_csv("treker.csv", sep=";")
data = data.values
print(data.shape)
d = {}
k = {}
for i in range(data.shape[0]):
    key = data[i][9]
    d[key] = d.get(key,0)+data[i][12]
    k[key] = k.get(key,0)+1

res = {}
for i in d.keys():
    res[i] = d[i]/k[i]
del res[0.0]
t = len(res.keys())
ssum = 0
import matplotlib.pyplot as plt
plt.scatter(res.keys(), res.values())
plt.show()
y = []
for i in res.keys():
    print(i,res[i])
    y.append(res[i]/abs(i))
print(sum(y)/t)

plt.bar(res.keys(),y)
plt.show()