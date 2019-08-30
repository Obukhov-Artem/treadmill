import openvr
import triad_openvr
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
    slovar_trackers = {"Правое_колено": right_knee,  # tracker_1
                       "Левое_колено": left_knee,  # tracker_2
                       "Правая_голень": right_leg,  # tracker_3
                       "Левая_голень": left_leg,  # tracker_4
                       "Правая_перчатка": right_hand,  # tracker_5
                       "Левая_перчатка": left_hand}  # tracker_6
    print(slovar_trackers)
