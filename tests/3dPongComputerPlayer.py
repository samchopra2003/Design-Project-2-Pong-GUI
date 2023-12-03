import cv2
import numpy as np
from ursina import *


def update():
    global dx, dz, score_A, score_B
    computer_paddle_speed = abs(1.0 * dx)
    if paddle_B.x < ball.x:
        if paddle_B.x < 0.36:
            paddle_B.x = paddle_B.x + computer_paddle_speed * time.dt
            # print(paddle_B.x, "RIGHT")
    else:
        if paddle_B.x > -0.36:
            paddle_B.x = paddle_B.x - computer_paddle_speed * time.dt
            # print(paddle_B.x, "LEFT")

    # if (-0.36 <= paddle_A.x <= 0.36) or (paddle_A.x > 0.36 and held_keys['a'] == 1) \
    #         or (paddle_A.x < -0.36 and held_keys['d'] == 1):
    #     paddle_A.x = paddle_A.x + held_keys['d'] * time.dt
    #     paddle_A.x = paddle_A.x - held_keys['a'] * time.dt
    if paddle_A.x < 0.36:
        paddle_A.x = paddle_A.x + held_keys['d'] * time.dt
    if paddle_A.x > -0.36:
        paddle_A.x = paddle_A.x - held_keys['a'] * time.dt

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

    global last_hit
    # Collisions
    hit_info = ball.intersects()
    if hit_info.hit:
        # if hit_info.entity == paddle_A or hit_info.entity == paddle_B:
        #     if hit_info.entity == paddle_A and last_hit == 'A':
        #         score_B += 1
        #         print_on_screen(f"Player A : Player B = {score_A} : {score_B}", position=(-0.85, .45), scale=2,
        #                         duration=2)
        #         reset('B')
        #     elif hit_info.entity == paddle_B and last_hit == 'B':
        #         score_A += 1
        #         print_on_screen(f"Player A : Player B = {score_A} : {score_B}", position=(-0.85, .45), scale=2,
        #                         duration=2)
        #         reset('A')

        # Audio('sounds/pong_sound.wav')
        if abs(dz) > 0.4:
            # dz = -dz * np.random.choice([0.8, 1, 1.2])
            dz = -dz * np.random.choice([1, 1.2])
        else:
            dz = -dz * np.random.choice([1, 1.2])
        if abs(dx) > 0.05:
            # dx = dx * np.random.choice([0.8, 1, 1.2])
            dx = dx * np.random.choice([1, 1.2])
        else:
            dx = dx * np.random.choice([1, 1.2])

        if hit_info.entity == paddle_A:
            last_hit = 'A'
        else:
            last_hit = 'B'

    # base.graphicsEngine.renderFrame()
    dr = base.camNode.getDisplayRegion(0)
    tex = dr.getScreenshot()
    data = tex.getRamImage()
    # v = memoryview(data).tolist()
    img = np.array(data, dtype=np.uint8)
    img = img.reshape((tex.getYSize(), tex.getXSize(), 4))
    img = img[::-1]
    img = cv2.cvtColor(img, cv2.COLOR_RGBA2GRAY)

    downsampled_img = img
    for _ in range(3):
        downsampled_img = cv2.pyrDown(downsampled_img)

    print("dt = ", time.dt)
    # trimmed_image = downsampled_img[80:-60, 110:-110]
    # trimmed_image[trimmed_image > 100] = 255
    # condition = (trimmed_image > 20) & (trimmed_image < 40)
    # trimmed_image[condition] = 125

    trimmed_image = downsampled_img[40:-20, 40:-40]
    trimmed_image[trimmed_image > 100] = 255
    condition = (trimmed_image > 20) & (trimmed_image < 40)
    trimmed_image[condition] = 125

    cv2.imshow('img', trimmed_image)
    print(trimmed_image.shape)


def reset(winner):
    ball.x = 0
    ball.z = -0.3
    paddle_B.x = 0
    # paddle_A.x = 0

    global dx, dz
    dx = 0.3 * np.random.choice([-1, 1])
    if winner == 'A':
        dz = -0.5
    else:
        dz = 0.5

    global last_hit
    last_hit = ''


if __name__ == "__main__":
    # app = Ursina(window_type='offscreen')
    app = Ursina()
    window.color = color.orange

    table = Entity(model='cube', color=color.green, scale=(10, 0.5, 14),
                   position=(0, 0, 0), texture="white_cube")

    # paddle_A = Entity(parent=table, color=color.black, model='cube', scale=(0.20, 0.03, 0.05),
    #                   position=(0, 3.7, 0.22), collider='box')
    paddle_A = Entity(parent=table, color=color.black, model='cube', scale=(0.1, 0.03, 0.05),
                                        position=(0, 3.7, 0.22), collider='box')
    # paddle_B = duplicate(paddle_A, z=-0.62)
    paddle_B = Entity(parent=table, color=color.dark_gray, model='cube', scale=(0.1, 0.03, 0.05),
                      position=(0, 3.7, -0.62), collider='box')

    Text(text="Player A", scale=2, position=(-0.1, 0.32))
    Text(text="Player B", scale=2, position=(-0.1, -0.4))

    line = Entity(parent=table, model='quad', scale=(0.88, 0.2, 0.1), position=(0, 3.5, -0.20))
    ball = Entity(parent=table, model='sphere', color=color.red, scale=0.05,
                  position=(0, 3.71, -0.20), collider='box')

    dx = 0.3
    dz = -0.5
    score_A = 0
    score_B = 0

    camera.position = (0, 15, -26)
    camera.rotation_x = 30

    i = 0
    last_hit = ''
    while True:
        app.step()
        i += 1
        print(i)
