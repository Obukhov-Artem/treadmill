import triad_openvr
import time
import sys
data = {}
v = triad_openvr.triad_openvr()
v.print_discovered_objects()

if len(sys.argv) == 1:
    interval = 1/1000
elif len(sys.argv) == 2:
    interval = 1/float(sys.argv[1])
else:
    print("Invalid number of arguments")
    interval = False

n = 0
if interval:
    while(True):
        start = time.time()
        txt = ""

        for device in v.devices:
            try:
                print(device)
                position_device = v.devices[device].sample(1, 5000)
                if position_device and n>0:
                    data[device]
                print(position_device.get_position())
                """
                for each in v.devices[device].get_pose_euler():
                    txt += "%.4f" % each
                    txt += " "
                print("\r" + txt, end="")"""
                print()
            except Exception as e:
                print(e)
        sleep_time = interval-(time.time()-start)
        if sleep_time>0:
            time.sleep(sleep_time)
        n +=1