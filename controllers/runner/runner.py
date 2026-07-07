from controller import Robot
import ast
import math


robot = Robot()

TIME_STEP = int(robot.getBasicTimeStep())
MAX_SPEED = 6.28
ESCAPE_SPEED = 3.1
TURN_SPEED = 4

left_motor = robot.getDevice(
    "left wheel motor"
)

right_motor = robot.getDevice(
    "right wheel motor"
)

left_motor.setPosition(
    float("inf")
)

right_motor.setPosition(
    float("inf")
)

left_motor.setVelocity(0)
right_motor.setVelocity(0)

ps = []

for i in range(8):
    sensor = robot.getDevice(
        f"ps{i}"
    )

    sensor.enable(TIME_STEP)
    ps.append(sensor)

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

def normalize_angle(angle):
    return (angle + math.pi) % (2 * math.pi) - math.pi

def front_intensity():
    values = [
        sensor.getValue()
        for sensor in ps
    ]

    return (values[0] + values[7]) / 2

def obstacle_detected():
    return front_intensity() > 80

def wall_side():
    """
    Returns which side the nearby wall leans toward, using the
    asymmetry between the left and right proximity sensor clusters.
    Positive means the wall is more to the right, negative more to
    the left.
    """
    values = [
        sensor.getValue()
        for sensor in ps
    ]

    left = values[5] + values[6]
    right = values[1] + values[2]

    return right - left

def wall_deflection():
    """
    Proportional repulsive turn away from a wall directly ahead, sized
    by how head-on the wall is. Unlike a fixed +/-90 degree override,
    this decays to zero as the robot turns away (the front sensors drop
    out), so it settles into a heading tangential to the boundary
    instead of spinning in place beside it.
    """

    front = front_intensity()

    if front <= 80:
        return 0.0

    turn_away = -1 if wall_side() > 0 else 1
    magnitude = min(front / 400.0, 1.0) * TURN_SPEED

    return turn_away * magnitude

def threat_centroid(threats):
    """
    threats: list of (distance, angle) tuples relative to this robot

    Returns the relative bearing pointing away from the combined
    threat, i.e. the average direction of the detected catchers,
    rotated by 180 degrees.
    """

    dx = sum(math.cos(angle) for _, angle in threats)
    dy = sum(math.sin(angle) for _, angle in threats)

    threat_angle = math.atan2(dy, dx)

    return normalize_angle(threat_angle + math.pi)

def escape(threats):
    escape_angle = threat_centroid(threats)

    # boundary trapping mitigation: deflect (not replace) the evasion
    # vector to be tangential to a nearby wall, so the runner skirts
    # along it instead of stalling or turning back into the threat.
    angular = escape_angle * 3 + wall_deflection()

    move(
        ESCAPE_SPEED,
        angular
    )

def maintain_heading():
    if obstacle_detected():
        angular = TURN_SPEED if wall_side() < 0 else -TURN_SPEED
        move(0.2, angular)
        return

    move(ESCAPE_SPEED * 0.5, 0)

def nearby_threats():
    raw = robot.getCustomData()

    if not raw:
        return []

    try:
        threats = ast.literal_eval(raw)
    except (SyntaxError, ValueError):
        return []

    return threats

while robot.step(TIME_STEP) != -1:
    threats = nearby_threats()

    if threats:
        escape(threats)
        continue

    maintain_heading()
