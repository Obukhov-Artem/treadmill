s = "z=z+1"
data = [16.1, 10, 16.1, 5, 17.1]
pr = [10,5]
var = []
c = []
def tr(data):
    result = []
    for i in range(len(data)):
            if data[i] == 5:
                result.append([5,[s[i-1],s[i+1],s[i]]])
            if data[i] == 10:
                result.append([10,[s[i - 1], s[i]]])
    result.sort(key=lambda x: x[0])
    for r in result:
        print("".join(r[1]),end="")
tr(data)

