import triad_openvr
import time
import sys
import csv


def csv_dict_writer(path, fieldnames, data):
    """
    Writes a CSV file using DictWriter
    """
    with open(path, "w", newline='') as out_file:
        writer = csv.writer(out_file, delimiter=';')
        writer.writerow(fieldnames)
        for row in data:
            writer.writerow(row)


trackers = {'LHR-3A018118': ["tracker_4", 3],
            'LHR-9224071E': ["tracker_3", 2],
            'LHR-89FBFC40': ["tracker_2", 1],
            'LHR-1761CD18': ["tracker_1", 0]}
print(trackers.keys())
v = triad_openvr.triad_openvr()
v.print_discovered_objects()
data = []
if len(sys.argv) == 1:
    interval = 1 / 500
elif len(sys.argv) == 2:
    interval = 1 / float(sys.argv[1])
else:
    print("Invalid number of arguments")
    interval = False

n = 0
if interval:
    while (n < 20):
        start = time.time()
        txt = ""
        data_current = []
        for serial in trackers.keys():
            device, num_device = trackers[serial]
            try:

                '''print(device)'''
                position_device = v.devices[device].sample(1, 500)
                if position_device and n > 0:
                    print(v.devices[device].get_serial())
                    print(position_device.get_position())
                    #переделать пришедшие данные - если по 1 х у z, то сразу в data_current
                    #переделать пришедшие данные - если пришло много, то сразу в data
                    data_current.append(position_device.get_position())
                """
                for each in v.devices[device].get_pose_euler():
                    txt += "%.4f" % each
                    txt += " "
                print("\r" + txt, end="")"""
                '''print()'''
            except Exception as e:
                if n > 0:
                    data_current.append(data_current[n - 1][num_device])
                    pass
        data.append(data_current)
        sleep_time = interval - (time.time() - start)
        if sleep_time > 0:
            time.sleep(sleep_time)
        n += 1
print(len(data))
print(data)
fieldnames = ["tracker_1_x",
              "tracker_1_y",
              "tracker_1_z",
              "tracker_2_x",
              "tracker_2_y",
              "tracker_2_z",
              "tracker_3_x",
              "tracker_3_y",
              "tracker_3_z",
              "tracker_4_x",
              "tracker_4_y",
              "tracker_4_z" ]
data = [[1,2,3,4,5,6,7,8,9,10,11,12],
        [1,2,3,4,5,6,7,8,9,10,11,12],
        [1,2,3,4,5,6,7,8,9,10,11,12],]
csv_dict_writer('p.csv', fieldnames, data)
