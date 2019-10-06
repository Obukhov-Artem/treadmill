import csv
coord_y_1 = []
coord_y_2 = []
def csv_reader(file_obj,y1,y2):
    x = csv.reader(file_obj, delimiter=';')
    for row in x:
        y_1 = row[4]
        coord_y_1.append(y_1)
        y_2 = row[7]
        coord_y_2.append(y_2)
    y1_null = coord_y_1[1]
    y2_null = coord_y_2[1]
    y1_min = min(coord_y_1)
    y2_min = min(coord_y_2)
    coord_y_1.pop(0)
    coord_y_2.pop(0)
    for i in coord_y_1:
        print(i)
    for i in coord_y_2:
        print(i)

if __name__ == "__main__":
    csv_path = "data5.csv"
    x = csv.reader(csv_path, delimiter=';')
    with open(csv_path, "r") as f_obj:
        csv_reader(f_obj)
