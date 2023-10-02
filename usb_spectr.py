from array import array

import usb.core
import usb.util
import usb.backend.libusb1
import time

# backend = usb.backend.libusb1.get_backend(find_library=lambda x: "C:\\Users\\VladWin\\PycharmProjects\\spectr-parser\\venv\\Lib\\site-packages\\libusb\\_platform\_windows\\x64\\libusb-1.0.dll")
# usb_devices = usb.core.find(backend=backend, find_all=True)



vendor_id = 0x0547
product_id = 0x1002

#
# for cfg in device:
#     sys.stdout.write(str(cfg.bConfigurationValue) + '\n')
#     for intf in cfg:
#         sys.stdout.write('\t' + \
#                          str(intf.bInterfaceNumber) + \
#                          ',' + \
#                          str(intf.bAlternateSetting) + \
#                          '\n')
#         for ep in intf:
#             sys.stdout.write('\t\t' + \
#                              str(ep.bEndpointAddress) + \
#                              '\n')


# Define the endpoint

# device.ctrl_transfer(0x40, 201, 0, 0, None)
# device.ctrl_transfer(0x40, 193, 0, 0, None)
# device.ctrl_transfer(0x40, 194, 1, 0, None)
# device.ctrl_transfer(0x40, 195, 0, 0, None)
# device.ctrl_transfer(0x40, 197, 1, 0, None)
# data = device.read(endpoint.bEndpointAddress, endpoint.wMaxPacketSize)
# print("Data read:", data)

def init_usb():
    device = usb.core.find(idVendor=vendor_id, idProduct=product_id)
    device.set_configuration()
    endpoint = device[0][(0, 0)][0]
    return device, endpoint.bEndpointAddress, endpoint.wMaxPacketSize


def get_data(device, bEndpointAddress, wMaxPacketSize):
    device.ctrl_transfer(0x40, 201, 0, 0, None)
    device.ctrl_transfer(0x40, 193, 0, 0, None)
    device.ctrl_transfer(0x40, 194, 1, 0, None)
    device.ctrl_transfer(0x40, 195, 0, 0, None)
    device.ctrl_transfer(0x40, 197, 1, 0, None)
    full_data = array('B')
    for i in range(15):
        data = device.read(bEndpointAddress, wMaxPacketSize)
        full_data.extend(data)
    return full_data


def parse_data(data):
    points_number = int(len(data) / 2)
    all_points = [int.from_bytes((data[i*2], data[i*2 + 1]), byteorder='little') for i in range(points_number)]
    ch2_values = all_points[:1824]
    ch1_values = all_points[1824:3648]
    ch2_values.reverse()
    ch1_values.reverse()
    return ch1_values, ch2_values
