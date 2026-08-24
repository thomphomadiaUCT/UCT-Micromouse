# =========================================================================
# UCT Micromouse - Milestone 1: Run a Square (1m x 1m) (Framework)
# =========================================================================
# ASSIGNMENT DESCRIPTION:
# Implement a control loop to drive the mouse in a 1 meter by 1 meter square,
# turning 90 degrees at each corner, and returning to the start position.
# 
# KEY CONTROLS:
# - uct_mouse.set_motors(left_pwm, right_pwm) -> Set speed (-100 to 100)
# - uct_mouse.get_encoders() -> Returns (left_ticks, right_ticks)
# - uct_mouse.get_tof()      -> Returns (left_mm, center_mm, right_mm)
# - uct_mouse.delay_ms(ms)   -> Suspends execution and updates sensors
#
# GRADING:
# - The autograder applies 8% motor imbalance and 8% wheel slip.
# - Open-loop timing alone will accumulate errors. Use encoder and gyro
#   feedback to compensate.
# =========================================================================


#*
# 
# *#

import uct_mouse
import math

TICK_DIST_M = (2.0 * math.pi * 0.031) / 8.0

def drive_straight(distance_m):
    """Closed-loop straight-line control adjusting motor PWM to equalize wheel speeds.

    Uses encoder feedback to correct for physical motor imbalance.
    """
    print(f"Driving straight for {distance_m}m...")

    # --- System Parameters ---
    TICKS_PER_METER = 5120.0  # Verified encoder ticks per meter
    BASE_SPEED = 70  # Base PWM target

    # --- Control Gains & Timing ---
    KP_SPEED = 0.08  # Gain for speed/distance error compensation
    CONTROL_PERIOD_MS = 20  # Loop interval in milliseconds
    DT = CONTROL_PERIOD_MS / 1000.0  # Time step in seconds

    target_ticks = abs(distance_m * TICKS_PER_METER)

    start_left, start_right = uct_mouse.get_encoders()
    prev_left, prev_right = start_left, start_right

    loops = 0
    MAX_LOOPS = 5000

    while True:
        left_ticks, right_ticks = uct_mouse.get_encoders()

        # 1. Total distance traveled per side
        left_dist = abs(left_ticks - start_left)
        right_dist = abs(right_ticks - start_right)
        avg_ticks = (left_dist + right_dist) / 2.0

        if avg_ticks >= target_ticks:
            break

        loops += 1
        if loops > MAX_LOOPS:
            print("WARNING: Safety limit hit, stopping early.")
            break

        # 2. Instantaneous Speed Calculation (ticks/sec)
        d_left = abs(left_ticks - prev_left)
        d_right = abs(right_ticks - prev_right)

        speed_left = d_left / DT
        speed_right = d_right / DT

        prev_left, prev_right = left_ticks, right_ticks

        # 3. Position & Speed Error
        position_error = left_dist - right_dist
        speed_error = speed_left - speed_right
        total_error = position_error + (speed_error * DT)

        # 4. Dynamic PWM Power Adjustment
        correction = KP_SPEED * total_error

        left_pwm = max(-100, min(100, BASE_SPEED - correction))
        right_pwm = max(-100, min(100, BASE_SPEED + correction))

        uct_mouse.set_motors(int(left_pwm), int(right_pwm))
        uct_mouse.delay_ms(CONTROL_PERIOD_MS)

    # Active Brake
    uct_mouse.set_motors(-20, -20)
    uct_mouse.delay_ms(40)
    uct_mouse.set_motors(0, 0)
    print(f"Done. Traveled ~{avg_ticks / TICKS_PER_METER:.3f} m")


def turn_right_90():

    print("Turning 90 degrees right...")

#agle configuration
    TARGET_ANGLE_DEG = 54.0
    TURN_PWM = 70

    CONTROL_PERIOD_MS = 10
    DT = CONTROL_PERIOD_MS / 1000.0

    current_angle_deg = 0.0
    loops = 0
    MAX_LOOPS = 300  # ~3 second safety timeout

#left turn
    uct_mouse.set_motors(-TURN_PWM, TURN_PWM)

    while True:

        raw_gyro = uct_mouse.get_gyro()

        if isinstance(raw_gyro, (tuple, list)):
            gyro_z = raw_gyro[2]
        elif raw_gyro is not None:
            gyro_z = raw_gyro
        else:
            gyro_z = 0.0

        current_angle_deg += abs(gyro_z) * DT

        if current_angle_deg >= TARGET_ANGLE_DEG:
            break

        loops += 1

        if loops >= MAX_LOOPS:
            print("WARNING: Turn timeout")
            break

        uct_mouse.delay_ms(CONTROL_PERIOD_MS)

    uct_mouse.set_motors(0, 0)

    print("Turn complete:", current_angle_deg)

def run_square():

    if not uct_mouse.init():
        print("Initialization failed.")
        return

    try:
        with open("polarity.txt", "r") as f:
            lines = f.read().strip().split(",")
            uct_mouse.set_polarity(int(lines[0]), int(lines[1]))
    except Exception:
        uct_mouse.set_polarity(-1, 1)

    uct_mouse.delay_ms(1000)

    turn_right_90()


if __name__ == "__main__":
    run_square()