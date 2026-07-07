from controller import Supervisor
import random
import math
import os
import csv


robot = Supervisor()

TIME_STEP = int(robot.getBasicTimeStep())
NUM_CATCHERS = int(os.environ.get("NUM_CATCHERS", 10))
NUM_RUNNERS = int(os.environ.get("NUM_RUNNERS", 10))

ALPHA = float(os.environ.get("ALPHA", 0.0))

ARENA_X = 2.0
ARENA_Y = 1.0

SENSOR_RANGE = 0.35
CAPTURE_RADIUS = 0.071

RESULTS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "results.csv",
)

root = robot.getRoot()
children = root.getField(
    "children"
)

catchers = []
runners = []
runner_caught = []

def random_position(left_side=True):
    margin = 0.12

    if left_side:
        x = random.uniform(
            -ARENA_X/2 + margin,
            -0.05
        )

    else:
        x = random.uniform(
            0.05,
            ARENA_X/2 - margin
        )

    y = random.uniform(
        -ARENA_Y/2 + margin,
        ARENA_Y/2 - margin
    )

    return x, y

def deployment(team):
    if ALPHA == 0:
        return team == "catcher"

    if ALPHA == 1:
        return random.random() < 0.5

    if team == "catcher":
        return random.random() > ALPHA

    else:
        return random.random() < ALPHA

def spawn_robot(name, controller, left_side):
    x, y = random_position(
        left_side
    )

    theta = random.uniform(
        0,
        2*math.pi
    )

    vrml = f"""
    DEF {name} E-puck {{
        translation {x} {y} 0
        rotation 0 0 1 {theta}
        controller "{controller}"
        name "{name}"
        version "2"
        turretSlot [
            Pi-puck {{
            }}
        ]
    }}
    """

    children.importMFNodeFromString(
        -1,
        vrml
    )

    node = robot.getFromDef(
        name
    )

    return node

for i in range(NUM_CATCHERS):
    node = spawn_robot(
        f"catcher_{i}",
        "catcher",
        deployment("catcher")
    )
    
    catchers.append(node)

for i in range(NUM_RUNNERS):
    node = spawn_robot(
        f"runner_{i}",
        "runner",
        deployment("runner")
    )

    runners.append(node)
    runner_caught.append(False)

def yaw_of(node):
    orientation = node.getOrientation()
    return math.atan2(
        orientation[3],
        orientation[0]
    )

def normalize_angle(angle):
    return (angle + math.pi) % (2 * math.pi) - math.pi

def relative_position(observer, target):
    obs_pos = observer.getPosition()
    tar_pos = target.getPosition()

    dx = tar_pos[0] - obs_pos[0]
    dy = tar_pos[1] - obs_pos[1]

    distance = math.sqrt(
        dx*dx +
        dy*dy
    )

    angle = math.atan2(
        dy,
        dx
    )

    relative_angle = normalize_angle(
        angle - yaw_of(observer)
    )

    return distance, relative_angle

def update_detection():
    for catcher in catchers:
        if catcher is None:
            continue

        targets = []

        for runner in runners:
            if runner is None:
                continue

            distance, angle = relative_position(
                catcher,
                runner
            )

            if distance < SENSOR_RANGE:

                targets.append(
                    (
                        distance,
                        angle
                    )
                )

        catcher.getField(
            "customData"
        ).setSFString(
            str(targets)
        )

    for runner in runners:
        if runner is None:
            continue

        threats = []

        for catcher in catchers:
            if catcher is None:
                continue

            distance, angle = relative_position(
                runner,
                catcher
            )

            if distance < SENSOR_RANGE:
                threats.append(
                    (
                        distance,
                        angle
                    )
                )

        runner.getField(
            "customData"
        ).setSFString(
            str(threats)
        )

def check_captures():
    for i, runner in enumerate(runners):
        if runner is None:
            continue

        runner_pos = runner.getPosition()

        for catcher in catchers:
            if catcher is None:
                continue

            catcher_pos = catcher.getPosition()

            dx = runner_pos[0] - catcher_pos[0]
            dy = runner_pos[1] - catcher_pos[1]

            distance = math.sqrt(dx*dx + dy*dy)

            if distance <= CAPTURE_RADIUS:

                runner.remove()

                runners[i] = None
                runner_caught[i] = True

                break

t50 = None
t100 = None

half_target = math.ceil(NUM_RUNNERS / 2)

def log_results():
    file_exists = os.path.isfile(RESULTS_PATH)

    with open(RESULTS_PATH, "a", newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(
                ["num_catchers", "num_runners", "alpha", "t50", "t100"]
            )

        writer.writerow(
            [NUM_CATCHERS, NUM_RUNNERS, ALPHA, t50, t100]
        )

while robot.step(TIME_STEP) != -1:
    check_captures()
    update_detection()
    caught_count = sum(runner_caught)
    now = robot.getTime()

    if t50 is None and caught_count >= half_target:
        t50 = now
        print(f"[tailtag] T50 = {t50:.2f}s")

    if t100 is None and caught_count >= NUM_RUNNERS:
        t100 = now
        print(f"[tailtag] T100 = {t100:.2f}s")

        log_results()

        robot.simulationSetMode(Supervisor.SIMULATION_MODE_PAUSE)
