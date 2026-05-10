from hub import light_matrix
from hub import port
import runloop
import color
import motor_pair
import color_sensor

motor_pair.pair(motor_pair.PAIR_1, port.D, port.C)

async def main():
    motor_pair.move_tank(motor_pair.PAIR_1, 1000, 1000)

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
            await motor_pair.move_for_degrees(motor_pair.PAIR_1, 120, 0, velocity=280)
            await motor_pair.move_for_degrees(motor_pair.PAIR_1, 100, -100, velocity=280)
            await motor_pair.move_for_degrees(motor_pair.PAIR_1, 60, 0, velocity=280)
        
        # right green turn
        if ((left_col is not color.GREEN) and (right_col is color.GREEN)):
            await motor_pair.move_for_degrees(motor_pair.PAIR_1, 120, 0, velocity=280)
            await motor_pair.move_for_degrees(motor_pair.PAIR_1, 100, 100, velocity=280)
            await motor_pair.move_for_degrees(motor_pair.PAIR_1, 60, 0, velocity=280)








runloop.run(main())
