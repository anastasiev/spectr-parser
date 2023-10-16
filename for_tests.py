import usb.core
# import usb.backend.libusb0

vendor_id = 0x10c4
product_id = 0x8105
try:
    # backend = usb.backend.libusb0.get_backend()
    dev = usb.core.find(idVendor=vendor_id, idProduct=product_id)

    print(dev)

    print('setting configuration...')

    try:
        dev.set_configuration()
        print('completed!')
    except Exception as e:
        print(str(e))

    input("Press Enter to continue...")
except Exception as e:
    print(str(e))
    input("Error...")