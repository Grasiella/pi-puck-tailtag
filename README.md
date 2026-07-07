# Decentralized Pursuit-Evasion Swarm (Tail Tag)

A Webots simulation of a decentralized, purely reactive pursuit-evasion task on simulated
Pi-puck robots. A swarm of **catchers** must clear the arena of a fixed number of **runners**
using only local, relative sensing — no global map, no inter-agent communication, no
overhead camera.

---

## Overview

`|C|` catchers pursue `|R|` runners in a bounded 2D arena. Each robot senses only the agents
within its local sensing radius (relative distance + bearing); outside that radius it has no
information about the rest of the arena, aside from short-range IR proximity for walls.
Runners are caught when a catcher comes within one Pi-puck chassis diameter of them, and are
then removed from the simulation.

The experiment varies two independent variables while holding the runner count fixed:

- **Catcher count** `|C|`
- **Initial deployment mixing** `alpha` — `0` = fully segregated (catchers and runners on
  opposite sides), `1` = fully intermixed, `(0,1)` = partial cross-deployment.

and measures two metrics:

- **T50** — time until half of the runners are caught
- **T100** — time until all runners are caught

---

## Project Structure

```text
worlds/tailtag.wbt              World: arena + supervisor
controllers/supervisor/         Spawns robots, relays local sensing, detects captures, logs T50/T100
controllers/catcher/            Reactive pursuit controller
controllers/runner/             Reactive evasion controller
```

## Running a trial

Open `worlds/tailtag.wbt` in Webots and press play. Parameters can be overridden with
environment variables before launching Webots, to support sweeping `|C|` and `alpha` across
batch trials:

| Variable       | Default | Meaning                                   |
|----------------|---------|--------------------------------------------|
| `NUM_CATCHERS` | `10`    | Number of catcher robots                   |
| `NUM_RUNNERS`  | `10`    | Number of runner robots (held constant)    |
| `ALPHA`        | `0.0`   | Initial deployment mixing factor, `[0, 1]` |

Each completed trial appends a row (`num_catchers, num_runners, alpha, t50, t100`) to
`results.csv` at the project root, and pauses the simulation.

## Control logic

Catchers: obstacle/robot avoidance (highest priority) → chase nearest sensed runner →
random-walk search when no runner is in range.

Runners: obstacle avoidance is folded into evasion — when fleeing near a wall, the escape
vector is deflected tangential to the boundary rather than overridden, so a runner skirts
along the wall instead of turning back into an approaching catcher. With no catcher in
range, a runner simply maintains its heading.

---

## Authors

Developed as part of a Robotics course project.
