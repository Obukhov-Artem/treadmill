import triad_openvr
import csv

slovar_trackers = {"tracker_1": 'LHR-3A018118',
                   "tracker_2": 'LHR-9224071E',
                   "tracker_3": 'LHR-89FBFC40',
                   "tracker_4": 'LHR-1761CD18',
                   "tracker_5": 'right_hand',
                   "tracker_6": 'left_hand'}
fieldnames = ['x_tracker_1', 'y_tracker_1', 'z_tracker_1',
              'x_tracker_2', 'y_tracker_2', 'z_tracker_2',
              'x_tracker_3', 'y_tracker_3', 'z_tracker_3',
              'x_tracker_4', 'y_tracker_4', 'z_tracker_4',
              'data_on_treadmill']


def csv_writer(path, fieldnames, data):
    with open(path, "w", newline='') as out_file:
        writer = csv.DictWriter(out_file, delimiter=';', fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def getinfo():
    v = triad_openvr.triad_openvr()
    v.print_discovered_objects()
    n = 0
    for device in v.devices:
        try:
            '''print(device)'''
            position_device = v.devices[device].sample(1, 500)
            if position_device and n > 0:
                csv_writer('p.csv', fieldnames, position_device.get_position())
            """
            for each in v.devices[device].get_pose_euler():
                txt += "%.4f" % each
                txt += " "
            print("\r" + txt, end="")"""
            '''print()'''

        except Exception as e:
            pass


def getinfo_console():
    v = triad_openvr.triad_openvr()
    v.print_discovered_objects()
    n = 0
    for device in v.devices:
        try:
            '''print(device)'''
            position_device = v.devices[device].sample(1, 500)
            if position_device and n > 0:
                """csv_writer('p.csv', fieldnames, position_device.get_position())"""
                return fieldnames,position_device.get_position()

            """
            for each in v.devices[device].get_pose_euler():
                txt += "%.4f" % each
                txt += " "
            print("\r" + txt, end="")"""
            '''print()'''

        except Exception as e:
            pass


def calibration():
    v = triad_openvr.triad_openvr()
    for device in v.devices:
        position_device = v.devices[device].sample(1, 500)
        if position_device.get_position_x > 0 and position_device.get_position_y > 0.3 and position_device.get_position_y < 1:
            right_knee = v.devices[device].get_serial()
        if position_device.get_position_x < 0 and position_device.get_position_y > 0.3 and position_device.get_position_y < 1:
            left_knee = v.devices[device].get_serial()
        if position_device.get_position_x > 0 and position_device.get_position_y < 0.3:
            right_leg = v.devices[device].get_serial()
        if position_device.get_position_x < 0 and position_device.get_position_y < 0.3:
            left_leg = v.devices[device].get_serial()
        if position_device.get_position_x > 0 and position_device.get_position_y > 1:
            right_hand = v.devices[device].get_serial()
        if position_device.get_position_x < 0 and position_device.get_position_y > 1:
            left_hand = v.devices[device].get_serial()
        slovar_trackers = {"tracker_1": right_knee,
                           "tracker_2": left_knee,
                           "tracker_3": right_leg,
                           "tracker_4": left_leg,
                           "tracker_5": right_hand,
                           "tracker_6": left_hand}
    return slovar_trackers

