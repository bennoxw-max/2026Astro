from hub import light_matrix
from hub import port
from hub import motion_sensor
import runloop
import color
import motor_pair
import motor
import color_sensor
import distance_sensor
import math
import time

motor_pair.pair(motor_pair.PAIR_1, port.D, port.C)


async def chemical_spill():
    runloop.run(square_off())

    motion_sensor.reset_yaw(0)
    yaw = motion_sensor.tilt_angles()[0]/10

    await motor_pair.move_tank_for_degrees(motor_pair.PAIR_1, 540, 600, 600)
    
    offset = time.ticks_ms()
    timer = time.ticks_ms() - offset

    ultrasonic_dist = distance_sensor.distance(port.E)

    while ((ultrasonic_dist) > 270 or (ultrasonic_dist) < 0) and ((timer < 11000) or (yaw < -3 or yaw > 3)):
        motor_pair.move_tank(motor_pair.PAIR_1, 80, -80)
        # print(ultrasonic_dist)
        ultrasonic_dist = distance_sensor.distance(port.E)
        yaw = motion_sensor.tilt_angles()[0]/10
        timer = time.ticks_ms() - offset

    print("found can")
    motor_pair.stop(motor_pair.PAIR_1)



async def square_off():
    offset = time.ticks_ms()
    timer = time.ticks_ms() - offset

    while timer < 3000:
        left_rr = color_sensor.rgbi(port.A)[0]
        right_rr = color_sensor.rgbi(port.B)[0]

        if left_rr > 500:
            motor.run(port.C, 200)
        else:
            motor.run(port.C, -100)

        if right_rr > 500:
            motor.run(port.D, -200)
        else:
            motor.run(port.D, 100)

        timer = time.ticks_ms() - offset


    motor.stop(port.C)
    motor.stop(port.D)


async def turn_to_yaw(target_yaw, speed):
    print("FUNC: TURN_TO_YAW()")
    yaw = motion_sensor.tilt_angles()[0]/10
    aim = -target_yaw

    print("yaw: ", yaw, " target_yaw: ", aim)

    if yaw < aim:
        while (yaw < (aim - 3)) or (yaw > (aim + 3)):
            motor_pair.move_tank(motor_pair.PAIR_1, -speed, speed)
            yaw = motion_sensor.tilt_angles()[0]/10


        motor_pair.stop(motor_pair.PAIR_1)
    else:
        while (yaw < (aim - 3)) or (yaw > (aim + 3)):
            motor_pair.move_tank(motor_pair.PAIR_1, speed, -speed)
            yaw = motion_sensor.tilt_angles()[0]/10


        motor_pair.stop(motor_pair.PAIR_1)

async def left_green_turn():
    # go forward
    await motor_pair.move_for_degrees(motor_pair.PAIR_1, 120, 0, velocity=280)

    # turn left
    await motor_pair.move_for_degrees(motor_pair.PAIR_1, 90, -100, velocity=280)

    # turn left until right sensor sees black
    right_ref = color_sensor.reflection(port.A)
    while (right_ref > 40):
        right_ref = color_sensor.reflection(port.A)
        motor_pair.move(motor_pair.PAIR_1, -100, velocity=280)

    # realign with the line
    await motor_pair.move_for_degrees(motor_pair.PAIR_1, 40, 100, velocity=280)

    # go forward
    await motor_pair.move_for_degrees(motor_pair.PAIR_1, 50, 0, velocity=280)

async def right_green_turn():
    # go forward
    await motor_pair.move_for_degrees(motor_pair.PAIR_1, 120, 0, velocity=280)

    # turn right
    await motor_pair.move_for_degrees(motor_pair.PAIR_1, 90, 100, velocity=280)

    # turn right until left sensor sees black
    left_ref = color_sensor.reflection(port.B)
    while (left_ref > 40):
        left_ref = color_sensor.reflection(port.B)
        motor_pair.move(motor_pair.PAIR_1, 100, velocity=280)

    # realign with theline
    await motor_pair.move_for_degrees(motor_pair.PAIR_1, 40, -100, velocity=280)

    # go forward
    await motor_pair.move_for_degrees(motor_pair.PAIR_1, 50, 0, velocity=280)

async def bottle():
    print("bottle")

    motion_sensor.reset_yaw(0)

    # go backwards
    await motor_pair.move_for_degrees(motor_pair.PAIR_1, 150, 0, velocity=-280)

    # turn right
    await motor_pair.move_for_degrees(motor_pair.PAIR_1, 260, 40, velocity=300)

    # arc around the bottle
    right_col = color_sensor.color(port.A)

    while (right_col is color.WHITE):
        motor_pair.move(motor_pair.PAIR_1, -18, velocity=500)
        right_col = color_sensor.color(port.A)

    # go forward
    await motor_pair.move_for_degrees(motor_pair.PAIR_1, 50, 0, velocity=280)

    runloop.run(turn_to_yaw(0, 200))





async def main():
    while True:
        # fetch colour and reflection from the left and right colour sensors - port A and B
        left_ref = color_sensor.reflection(port.B)
        right_ref = color_sensor.reflection(port.A)
        left_col = color_sensor.color(port.B)
        right_col = color_sensor.color(port.A)
        left_rr = color_sensor.rgbi(port.A)[0]
        right_rr = color_sensor.rgbi(port.B)[0]
        ultrasonic_dist = distance_sensor.distance(port.E)

        # line following
        error = round((left_ref - right_ref) * 1.2 + 5)
        motor_pair.move(motor_pair.PAIR_1, error, velocity = 350)

        if ((left_rr > 750) and (right_rr > 750)):
            await motor_pair.move_for_degrees(motor_pair.PAIR_1, 90, 0, velocity=280)

            runloop.run(chemical_spill())

        # check for green
        if ((left_col is color.GREEN) or (right_col is color.GREEN)):
            # left green turn
            if ((left_col is color.GREEN) and (right_col is not color.GREEN)):
                runloop.run(left_green_turn())

            # right green turn
            if ((left_col is not color.GREEN) and (right_col is color.GREEN)):
                runloop.run(right_green_turn())

        if ((ultrasonic_dist < 50) and (ultrasonic_dist > -1)):
            runloop.run(bottle())



runloop.run(main())