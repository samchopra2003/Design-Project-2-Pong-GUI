import time

import numpy as np
from ursina import *

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService


def update():
    global dx, dz, score_A, score_B
    computer_paddle_speed = abs(1.0 * dx)
    if paddle_A.x < ball.x:
        if paddle_A.x < 0.36:
            paddle_A.x = paddle_A.x + computer_paddle_speed * time.dt
    else:
        if paddle_A.x > -0.36:
            paddle_A.x = paddle_A.x - computer_paddle_speed * time.dt

    try:
        line = uart.readline()
        line = line.decode()
        end_idx = line.find('end')
        line = line[:end_idx]

        end_pos_x = line.find(',')
        x = line[:end_pos_x]
        x = int(x)
        print("x = ", x)
        # print("dt = ", time.dt * 0.01)
        if paddle_B.x < 0.36:
            # paddle_B.x = paddle_B.x + held_keys['d'] * time.dt
            if x > 150:
                paddle_B.x = paddle_B.x + time.dt * 0.1
                print("Move right")
        if paddle_A.x > -0.36:
            # paddle_B.x = paddle_B.x - held_keys['a'] * time.dt
            if x < -150:
                paddle_B.x = paddle_B.x - time.dt * 0.1
                print("Move left")
    except:
        pass

    ball.x = ball.x + time.dt * dx
    ball.z = ball.z + time.dt * dz

    # Boundary checking
    # Left and right
    if abs(ball.x) > 0.4:
        dx = -dx

    # Top and Bottom
    if ball.z > 0.25:
        # Audio('sounds/whistle.wav')
        score_B += 1
        print_on_screen(f"Player A : Player B = {score_A} : {score_B}", position=(-0.85, .45), scale=2, duration=2)
        reset('B')

    if ball.z < -0.65:
        # Audio('sounds/whistle.wav')
        score_A += 1
        print_on_screen(f"Player A : Player B = {score_A} : {score_B}", position=(-0.85, .45), scale=2, duration=2)
        reset('A')

    # Collisions
    hit_info = ball.intersects()
    if hit_info.hit:
        if hit_info.entity == paddle_B:
            if paddle_A.x < 0:
                uart.write(b"2")
            else:
                uart.write(b"1")


        if abs(dz) > 0.4:
            dz = -dz * np.random.choice([0.8, 1, 1.2])
        else:
            dz = -dz * np.random.choice([1, 1.2])
        if abs(dx) > 0.05:
            dx = dx * np.random.choice([0.8, 1, 1.2])
        else:
            dx = dx * np.random.choice([1, 1.2])


def reset(winner):
    ball.x = 0
    ball.z = -0.3
    paddle_B.x = 0

    global dx, dz
    dx = 0.04 * np.random.choice([-1, 1])
    if winner == 'A':
        dz = -0.08
    else:
        dz = 0.08


if __name__ == "__main__":
    # bluetooth setup
    ble = BLERadio()
    uart_service = UARTService()
    advertisement = ProvideServicesAdvertisement(uart_service)
    connection = None
    uart = None
    for entry in ble.start_scan(timeout=60, minimum_rssi=-80):
        if entry.address.string == "F2:91:47:A5:73:76":
            print("Bluetooth device found")
            connection = ble.connect(entry)
            print("Connected")
            uart = connection[UARTService]
            break

    uart.write(b"2")
    print("Game starting in 10 seconds!")
    time.sleep(10.0)

    app = Ursina()
    window.color = color.orange

    table = Entity(model='cube', color=color.green, scale=(10, 0.5, 14),
                   position=(0, 0, 0), texture="white_cube")

    paddle_A = Entity(parent=table, color=color.black, model='cube', scale=(0.1, 0.03, 0.05),
                      position=(0, 3.7, 0.22), collider='box')
    paddle_B = Entity(parent=table, color=color.dark_gray, model='cube', scale=(0.1, 0.03, 0.05),
                      position=(0, 3.7, -0.62), collider='box')

    Text(text="Player A", scale=2, position=(-0.1, 0.32))
    Text(text="Player B", scale=2, position=(-0.1, -0.4))

    line = Entity(parent=table, model='quad', scale=(0.88, 0.2, 0.1), position=(0, 3.5, -0.20))
    ball = Entity(parent=table, model='sphere', color=color.red, scale=0.05,
                  position=(0, 3.71, -0.20), collider='box')

    dx = 0.04
    dz = 0.08
    score_A = 0
    score_B = 0

    camera.position = (0, 15, -26)
    camera.rotation_x = 30

    # paddle_A.x = paddle_A.x + time.dt * 10

    while True:
        app.step()