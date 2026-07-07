from controller import Robot
import ast
import random


robot = Robot()

TIME_STEP = int(robot.getBasicTimeStep())

MAX_SPEED = 6.28
LINEAR_SPEED = 3.1
TURN_SPEED = 4

left_motor = robot.getDevice("left wheel motor")
right_motor = robot.getDevice("right wheel motor")

left_motor.setPosition(float("inf"))
right_motor.setPosition(float("inf"))

left_motor.setVelocity(0)
right_motor.setVelocity(0)

ps = []

for i in range(8):
    sensor = robot.getDevice(
        f"ps{i}"
    )

    sensor.enable(TIME_STEP)
    ps.append(sensor)

turn_timer = 0
random_turn = 0

def move(linear, angular):
    left = linear - angular
    right = linear + angular

    left = max(
        min(left, MAX_SPEED),
        -MAX_SPEED
    )

    right = max(
        min(right, MAX_SPEED),
        -MAX_SPEED
    )

    left_motor.setVelocity(left)
    right_motor.setVelocity(right)

def obstacle_detected():
    values = [
        sensor.getValue()
        for sensor in ps
    ]

    front = (
        values[0]
        +
        values[7]
    ) / 2

    return front > 80

def avoid_obstacle():
    move(
        0.2,
        TURN_SPEED
    )

def random_walk():
    global turn_timer
    global random_turn

    if turn_timer <= 0:
        random_turn = random.uniform(
            -1,
            1
        )

        turn_timer = random.randint(
            20,
            80
        )
    turn_timer -= 1

    move(
        LINEAR_SPEED,
        random_turn
    )

def chase(target):
    """
    target:
        distance
        angle
    """

    distance, angle = target
    angular = angle * 3
    move(
        LINEAR_SPEED,
        angular
    )

def nearest_runner():
    raw = robot.getCustomData()

    if not raw:
        return None

    try:
        targets = ast.literal_eval(raw)
    except (SyntaxError, ValueError):
        return None

    if not targets:
        return None

    return min(targets, key=lambda t: t[0])

while robot.step(TIME_STEP) != -1:
    if obstacle_detected():
        avoid_obstacle()
        continue

    target = nearest_runner()

    if target is not None:
        chase(
            target
        )
        continue

    random_walk()
