from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

ble = BLERadio()
uart_service = UARTService()
advertisement = ProvideServicesAdvertisement(uart_service)
connection = None
uart = None
for entry in ble.start_scan(timeout=60, minimum_rssi=-80):
    print(entry, entry.address.string)
    if entry.address.string == "F2:91:47:A5:73:76":
        print("Bluetooth device found")
        connection = ble.connect(entry)
        print("Connected")
        uart = connection[UARTService]
        break

init_x, init_y, init_z = 0, 0, 0
for i in range(200):
    if i % 2 == 0:
        uart.write(b"1")
    else:
        uart.write(b"2")
    try:
        if i == 0 or (init_x == 0 and init_y == 0 and init_z == 0):
            line = uart.readline()

            line = line.decode()
            end_idx = line.find('end')
            line = line[:end_idx]

            end_pos_x = line.find(',')
            init_x = line[:end_pos_x]

            end_pos_y = line[end_pos_x + 1:].find(',')
            init_y = line[end_pos_x + 1:end_pos_x + 1 + end_pos_y]

            init_z = line[end_pos_x + 1 + end_pos_y + 1:]

            try:
                init_x = int(init_x)
                init_y = int(init_y)
                init_z = int(init_z)
                # print("inits x, y, z= ", init_x, init_y, init_z)
            except:
                init_x, init_y, init_z = 0, 0, 0
    except:
        connection.disconnect()
    if line and i > 0:
        line = uart.readline()
        line = line.decode()
        end_idx = line.find('end')
        line = line[:end_idx]
        # print(line)

        end_pos_x = line.find(',')
        x = line[:end_pos_x]
        # print("x = ", x)

        end_pos_y = line[end_pos_x + 1:].find(',')
        y = line[end_pos_x + 1:end_pos_x + 1 + end_pos_y]
        # print("y = ", y)

        z = line[end_pos_x + 1 + end_pos_y + 1:]
        # print("z = ", z)

        try:
            # x = int(x) - init_x
            # y = int(y) - init_y
            # z = int(z) - init_z
            # print("x, y, z =", x, y, z, '\n')
            print(f"x = {int(x)}, y = {int(y)}, xy sum = {int(x) + int(y)}")
            if int(x) > 200:
                print("Move right")
            elif int(x) < -200:
                print("Move left")

        except:
            pass

connection.disconnect()




