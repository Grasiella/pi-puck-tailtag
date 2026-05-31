# 🤖🏴‍☠️ Tail Tag: Multi-Robot Communication Game

## Overview

Tail Tag is a multi-robot game developed for studying communication and coordination between autonomous robots in a shared environment.

The project simulates multiple Pi-Puck robots moving inside an arena with obstacles. At any given time, one robot possesses a virtual "tail". The objective of the remaining robots is to capture the tail by approaching the current holder.

Whenever a capture occurs, robots communicate the ownership change through message exchange, allowing all agents to maintain a consistent view of the game state.

The project focuses on:

* Multi-robot communication
* Distributed decision making
* Autonomous navigation
* Obstacle avoidance
* Event synchronization between agents

---

## Game Rules

1. A single robot starts the game holding the tail.
2. Robots without the tail attempt to capture it.
3. A capture occurs when a robot reaches a predefined distance threshold from the tail holder.
4. After a successful capture:

   * The previous holder loses the tail.
   * The capturing robot becomes the new holder.
   * A communication message is broadcast to all robots.
5. The game runs for a fixed duration.
6. The robot holding the tail when the timer expires is declared the winner.

---

## Communication Model

Robots communicate ownership changes through broadcast messages.

Example:

```json
{
  "event": "tail_transfer",
  "from": "robot_2",
  "to": "robot_4",
  "timestamp": 125.3
}
```

These messages ensure that all robots maintain a synchronized understanding of the current tail holder.

---

## Robot Behaviors

### Tail Holder

* Avoid obstacles
* Move away from nearby robots
* Attempt to survive until the end of the game

### Chasers

* Navigate toward the current tail holder
* Avoid obstacles
* Attempt to capture the tail

---

## Environment

The simulation consists of:

* Multiple Pi-Puck robots
* A bounded arena
* Static obstacles
* Communication between robots
* Fixed game duration

---

## Project Structure

```text
WIP
```

---

## Objectives

This project aims to demonstrate how communication can be integrated into a simple multi-robot scenario while maintaining clear and observable agent interactions.

The game provides an intuitive environment for experimenting with:

* Communication protocols
* Robot coordination
* Distributed systems concepts
* Multi-agent behavior

---

## Authors

Developed as part of a Robotics course project.
