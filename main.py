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
    print("FUNC: chemical_spill()")
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
    motor_pair.stop(motor_pair.PAIR_1)

    if timer > 6000 and (yaw > -10 and yaw < 10):
        await motor_pair.move_tank_for_degrees(
            motor_pair.PAIR_1, 540, -600, -600 # Move backwards to sqaure off with the silver tape
        ) # move back to silver tape
        runloop.run(square_off()) # Square off with the silver tape
        await motor_pair.move_tank_for_degrees(
            motor_pair.PAIR_1, 120, 600, 600 # move forward 6 cm
        )
        await motor.run_for_degrees(port.C, 260, 500)
        motor.reset_relative_position(port.C, 0)

        ultrasonic_dist = distance_sensor.distance(port.E)
        while ((ultrasonic_dist) > 270 or (ultrasonic_dist) < 0):
            motor_pair.move(motor_pair.PAIR_1, 20, velocity=300) # Keep on repeating donut action until ultrasonic sees the can
            ultrasonic_dist = distance_sensor.distance(port.E)
        motor_pair.stop(motor_pair.PAIR_1)

        donut_degree = motor.relative_position(port.C)

        motor.reset_relative_position(port.C, 0)

        left_col = color_sensor.color(port.B)
        right_col = color_sensor.color(port.A)
        while (left_col is not color.WHITE) or (right_col is not color.WHITE):
            motor_pair.move(motor_pair.PAIR_1, 0, velocity=300) # Keep moving forward (pushing the can out of the oil spill) until both colour sensors see white
            left_col = color_sensor.color(port.B)
            right_col = color_sensor.color(port.A)
        motor_pair.stop(motor_pair.PAIR_1)

        # print(motor.relative_position(port.C))
        while (motor.relative_position(port.C) > 1):
            motor_pair.move(motor_pair.PAIR_1, 0, velocity=-300) # Reverse to the same spot where we found the can (the position where the wheel position was reset)
        motor_pair.stop(motor_pair.PAIR_1)

        motor.reset_relative_position(port.C, donut_degree) # Restore degree of the wheel to the position where we found the can so we can reverse the donut action

        while (motor.relative_position(port.C) >= -50):
            motor_pair.move(motor_pair.PAIR_1, 20, velocity=-500)
        motor_pair.stop(motor_pair.PAIR_1)

        runloop.run(turn_to_yaw(0, 300))
        runloop.run(square_off())
        runloop.run(turn_to_yaw(179, 200))

        await motor_pair.move_tank_for_degrees(
            motor_pair.PAIR_1, 80, 400, 400
        )
        runloop.run(turn_to_yaw(-90, 300))

        await motor_pair.move_tank_for_degrees(
            motor_pair.PAIR_1, 120, -600, -600
        )

        # move forward until either colour sensor detects black
        left_col = color_sensor.color(port.B)
        right_col = color_sensor.color(port.A)
        while (left_col is not color.BLACK) and (right_col is not color.BLACK):
            motor_pair.move(motor_pair.PAIR_1, 0, velocity=300)
            left_col = color_sensor.color(port.B)
            right_col = color_sensor.color(port.A)
        motor_pair.stop(motor_pair.PAIR_1)

        # move forward 2 cm
        await motor_pair.move_tank_for_degrees(
            motor_pair.PAIR_1, 60, 300, 300
        )

        runloop.run(turn_to_yaw(179, 200))

        # move backwards 3 cm
        await motor_pair.move_tank_for_degrees(
            motor_pair.PAIR_1, 90, -600, -600
        )

    else:
        # motor_pair.stop(motor_pair.PAIR_1)
        motor.reset_relative_position(port.C, 0) # Reset the relative position

        # move forward until either sensor detects white
        left_col = color_sensor.color(port.B)
        right_col = color_sensor.color(port.A)
        while (left_col is not color.WHITE) and (right_col is not color.WHITE):
            motor_pair.move_tank(motor_pair.PAIR_1, 500, 500)
            left_col = color_sensor.color(port.B)
            right_col = color_sensor.color(port.A)
        motor_pair.stop(motor_pair.PAIR_1)

        # reverse to the position where the wheel position was reset
        while (motor.relative_position(port.C) > 5):
            motor_pair.move_tank(motor_pair.PAIR_1, -500, -500)
        motor_pair.stop(motor_pair.PAIR_1)

        # rotate until the robot's yaw is close to zero -------------------------- REPLACED WITH TURN TO YAW COMMAND
        #yaw = motion_sensor.tilt_angles()[0] / 10
        #while not (-2 <= yaw <= 2):
        #    motor_pair.move_tank(motor_pair.PAIR_1, 150, -150)
        #    yaw = motion_sensor.tilt_angles()[0] / 10
        #motor_pair.stop(motor_pair.PAIR_1)
        runloop.run(turn_to_yaw(0, 200))

        # reverse until either colour sensor's raw red value exceeds 500
        left_rr = color_sensor.rgbi(port.B)[0]
        right_rr = color_sensor.rgbi(port.A)[0]
        while (left_rr <= 500) and (right_rr <= 500):
            motor_pair.move_tank(motor_pair.PAIR_1, -500, -500)
            left_rr = color_sensor.rgbi(port.B)[0]
            right_rr = color_sensor.rgbi(port.A)[0]
        motor_pair.stop(motor_pair.PAIR_1)

        runloop.run(square_off())
        runloop.run(turn_to_yaw(179, 200))

        # move forward 4 cm
        await motor_pair.move_tank_for_degrees(
            motor_pair.PAIR_1, 120, 300, 300
        )

        runloop.run(turn_to_yaw(-90, 300))

        # move backwards
        await motor_pair.move_tank_for_degrees(
            motor_pair.PAIR_1, 120, -300, -300
        )

        # move forward until either sensor detects black
        left_col = color_sensor.color(port.B)
        right_col = color_sensor.color(port.A)
        while (left_col is not color.BLACK) and (right_col is not color.BLACK):
            motor_pair.move(motor_pair.PAIR_1, 0, velocity=300)
            left_col = color_sensor.color(port.B)
            right_col = color_sensor.color(port.A)
        motor_pair.stop(motor_pair.PAIR_1)

        # move forward 2 cm
        await motor_pair.move_tank_for_degrees(
            motor_pair.PAIR_1, 60, 400, 400
        )

        runloop.run(turn_to_yaw(179, 200))

        # move backwards 3 cm
        await motor_pair.move_tank_for_degrees(
            motor_pair.PAIR_1, 90, -300, -300
        )


async def square_off():
    print("FUNC: square_off()")
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
    print("FUNC: turn_to_yaw()")
    yaw = motion_sensor.tilt_angles()[0]/10
    aim = -target_yaw

    print("yaw: ", yaw, " target_yaw: ", aim)

    if yaw < aim:
        while (yaw < (aim - 3)) or (yaw > (aim + 3)):
            motor_pair.move_tank(
                motor_pair.PAIR_1, -speed, speed
            )
            yaw = motion_sensor.tilt_angles()[0]/10
        motor_pair.stop(motor_pair.PAIR_1)

    else:
        while (yaw < (aim - 3)) or (yaw > (aim + 3)):
            motor_pair.move_tank(
                motor_pair.PAIR_1, speed, -speed
            )
            yaw = motion_sensor.tilt_angles()[0]/10
        motor_pair.stop(motor_pair.PAIR_1)


async def left_green_turn():
    print("FUNC: left_green_turn()")

    # go forward
    await motor_pair.move_for_degrees(
        motor_pair.PAIR_1, 120, 0, velocity=280
    )

    # turn left
    await motor_pair.move_for_degrees(
        motor_pair.PAIR_1, 90, -100, velocity=280
    )

    # turn left until right sensor sees black
    right_ref = color_sensor.reflection(port.A)
    while (right_ref > 40):
        right_ref = color_sensor.reflection(port.A)
        motor_pair.move(
            motor_pair.PAIR_1, -100, velocity=280
        )

    # realign with the line
    await motor_pair.move_for_degrees(
        motor_pair.PAIR_1, 40, 100, velocity=280
    )

    # go forward
    #await motor_pair.move_for_degrees(
    #    motor_pair.PAIR_1, 50, 0, velocity=280
    #)

    # go forward until no sensors are detecting green
    left_col = color_sensor.color(port.B)
    right_col = color_sensor.color(port.A)
    while ((left_col is color.GREEN) or (right_col is color.GREEN)):
        motor_pair.move(
            motor_pair.PAIR_1, 0, velocity=280
        )

async def right_green_turn():
    print("FUNC: right_green_turn()")

    # go forward
    await motor_pair.move_for_degrees(
        motor_pair.PAIR_1, 120, 0, velocity=280
    )

    # turn right
    await motor_pair.move_for_degrees(
        motor_pair.PAIR_1, 90, 100, velocity=280
    )

    # turn right until left sensor sees black
    left_ref = color_sensor.reflection(port.B)
    while (left_ref > 40):
        left_ref = color_sensor.reflection(port.B)
        motor_pair.move(
            motor_pair.PAIR_1, 100, velocity=280
        )

    # realign with theline
    await motor_pair.move_for_degrees(
        motor_pair.PAIR_1, 40, -100, velocity=280
    )

    # go forward
    #await motor_pair.move_for_degrees(
    #    motor_pair.PAIR_1, 50, 0, velocity=280
    #)

    # go forward until no sensors are detecting green
    left_col = color_sensor.color(port.B)
    right_col = color_sensor.color(port.A)
    while ((left_col is color.GREEN) or (right_col is color.GREEN)):
        motor_pair.move(
            motor_pair.PAIR_1, 0, velocity=280
        )

async def bottle():
    print("FUNC: bottle()")

    motion_sensor.reset_yaw(0)

    # go backwards
    await motor_pair.move_for_degrees(
        motor_pair.PAIR_1, 150, 0, velocity=-280
    )

    # turn right
    await motor_pair.move_for_degrees(
        motor_pair.PAIR_1, 260, 40, velocity=300
    )

    # arc around the bottle
    right_col = color_sensor.color(port.A)

    while (right_col is color.WHITE):
        motor_pair.move(motor_pair.PAIR_1, -18, velocity=500)
        right_col = color_sensor.color(port.A)

    # go forward
    await motor_pair.move_for_degrees(
        motor_pair.PAIR_1, 50, 0, velocity=280
    )

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
        motor_pair.move(motor_pair.PAIR_1, error, velocity = 300)

        if ((left_rr > 850) and (right_rr > 850)):
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
