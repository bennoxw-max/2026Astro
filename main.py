from hub import light_matrix
from hub import port
import runloop
import color
import motor_pair
import color_sensor

motor_pair.pair(motor_pair.PAIR_1, port.D, port.C)

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

    # realign with the line
    await motor_pair.move_for_degrees(motor_pair.PAIR_1, 40, -100, velocity=280)

    # go forward
    await motor_pair.move_for_degrees(motor_pair.PAIR_1, 50, 0, velocity=280)

async def main():
    while True:
        # fetch colour and reflection from the left and right colour sensors - port A and B
        left_ref = color_sensor.reflection(port.B)
        right_ref = color_sensor.reflection(port.A)
        left_col = color_sensor.color(port.B)
        right_col = color_sensor.color(port.A)

        # line following
        error = round((left_ref - right_ref) * 1.2 + 5)
        motor_pair.move(motor_pair.PAIR_1, error, velocity = 350)

        # check for and do green turns

        # left green turn
        if ((left_col is color.GREEN) and (right_col is not color.GREEN)):
            runloop.run(left_green_turn())
        
        # right green turn
        if ((left_col is not color.GREEN) and (right_col is color.GREEN)):
            runloop.run(right_green_turn())



runloop.run(main())
