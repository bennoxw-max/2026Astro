from hub import light_matrix
from hub import port
import runloop
import motor_pair
import color_sensor

motor_pair.pair(motor_pair.PAIR_1, port.D, port.C)

async def main():
    motor_pair.move_tank(motor_pair.PAIR_1, 1000, 1000)

    while True:
        left_ref = color_sensor.reflection(port.B)
        right_ref = color_sensor.reflection(port.A)

        # error = round((left_ref - right_ref) * 1.2 + 5)

        # motor_pair.move(motor_pair.PAIR_1, error, velocity = 350)

        if (left_ref < 70 and right_ref > 70):
            motor_pair.move_tank(motor_pair.PAIR_1, -150, 400)
        elif (left_ref > 70 and right_ref < 70):
            motor_pair.move_tank(motor_pair.PAIR_1, 400, -150)
        else:
            motor_pair.move_tank(motor_pair.PAIR_1, 300, 300)






runloop.run(main())
