# Distributed Robotics: Swarm Catcher

A 2D swarm robotics simulation where reactive catcher agents coordinate to intercept Pi-puck targets. Built to study how swarm size and target distribution affect capture efficiency.

---

## Overview

A fixed set of **M** Pi-puck targets are scattered across a bounded field. **N** catcher agents, the independent variable, use a reactive swarm algorithm to find and clear them all. Agents have no global map; they sense only nearby neighbors and act on local rules.

The simulation terminates when all pucks are captured and logs performance metrics for batch analysis.

---

## Parameters

| Parameter    | Description                                              |
|--------------|----------------------------------------------------------|
| `FIELD_SIZE` | Dimensions of the bounded 2D simulation area             |
| `N`          | Number of catcher agents *(independent test variable)*   |
| `M`          | Fixed total number of Pi-puck targets to capture         |
| `SPACING`    | Spatial distribution/variance for puck spawning (slider) |
| `SENSE_RAD`  | Proximity radius `r` for detecting neighboring catchers  |
| `CATCH_RAD`  | Interception threshold distance to clear a puck          |

### Data Structures

- **Agents List** - array of objects: `[x, y, vx, vy]`
- **Pucks List** - array of coordinates: `[[x1, y1], [x2, y2], ..., [xM, yM]]`

---

## Algorithm

### Phase 1 - Initialization

- Spawn **M** pucks using a random distribution scaled by `SPACING`.
- Spawn **N** catcher agents at random or clustered initial positions.

### Phase 2 - Reactive Swarm Loop *(per time-step)*

For each agent **A**:

1. **Neighbor Detection** - find all agents within `SENSE_RAD`.
2. **Swarm Attraction** - if neighbors exist, compute their center of mass and steer toward it:
   ```
   Center_X = mean(neighbor x positions)
   Center_Y = mean(neighbor y positions)
   ```
3. **Capture Check** - if `distance(A, puck P) ≤ CATCH_RAD`, remove **P** from the pucks list.
4. **Kinematics Update** - advance along heading vector; enforce field boundaries.

### Phase 3 - Batch Automation & Metrics

- Run until `len(Pucks List) == 0`.
- Log `[CATCHER_COUNT, PUCK_SPACING, TOTAL_STEPS]` to CSV on termination.
- Automate across multiple (`N`, `SPACING`) combinations to generate report charts.

---

## Project Structure

```text
WIP
```

---

## Authors

Developed as part of a Robotics course project.
