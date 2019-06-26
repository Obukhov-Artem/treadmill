import triad_openvr
import csv

slovar_trackers = {"tracker_1":'LHR-3A018118',
          "tracker_2":'LHR-9224071E',
          "tracker_3":'LHR-89FBFC40',
          "tracker_4":'LHR-1761CD18'}


def csv_writer(path, fieldnames, data):
    with open(path, "w", newline='') as out_file:
        writer = csv.DictWriter(out_file, delimiter=';', fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def getinfo():
    data = {}
    v = triad_openvr.triad_openvr()
    v.print_discovered_objects()
    n = 0
    for device in v.devices:
        try:
            '''print(device)'''
            position_device = v.devices[device].sample(1, 500)
            if position_device and n > 0:
                csv_writer('p.csv','tracker_1',position_device.get_position())
            """
            for each in v.devices[device].get_pose_euler():
                txt += "%.4f" % each
                txt += " "
            print("\r" + txt, end="")"""
            '''print()'''
        except Exception as e:
            pass

def total():
    pass
getinfo()