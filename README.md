# Robot Continuity Network (RCN)
### Identity, Memory, and Skills That Survive the Robot Body

[![Test Suite](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()
[![Specification](https://img.shields.io/badge/spec-RCN--01%20%7C%20RCN--02-blue.svg)]()
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-yellowgreen.svg)](LICENSE)

---

## ⚡ Executive Summary

A robot body is replaceable hardware. Today, when a \$100k+ industrial robot or Autonomous Mobile Robot (AMR) experiences a motor burnout, sensor breakdown, or hardware replacement:
1. **Costly Downtime (MTTR)**: Field technicians spend 3 to 6 hours re-mapping facility boundaries, re-teaching waypoints, re-configuring door access tokens, and debugging local odometry.
2. **Loss of Operational Experience**: Subtle site-specific lessons (e.g. wet threshold traction heuristics, docking approach angles, obstacle workarounds) are wiped with the old unit.

**The Robot Continuity Network (RCN)** decouples a robot's persistent operational identity, environmental memory, and task state from physical hardware embodiments. When a robot body fails, a verified replacement chassis authenticates, verifies compatibility, adapts kinematic parameters, and resumes work **in under 60 seconds without re-mapping**.

---

## 🚀 The 3-Minute Proof of Concept

This repository provides an immediate, hands-on demonstration of cross-embodiment continuity.

### Scenario:
* **Robot Alpha (`Forklift-Titan-04`)** is actively transporting a 340 kg pallet to Cold Storage Rack 14 in facility `FRA-03`.
* **Hardware Fault**: Left drive actuator suffers an unrecoverable thermal stall.
* **Instant Snapshot**: RCN creates an atomic, cryptographically signed Memory Vault snapshot (`sha256:...`) and securely wipes local storage on the retired body.
* **Compatibility Gating**: RCN scans available spare bodies. Candidate 1 (lightweight carrier) is rejected due to payload and sensor deficits. Candidate 2 (`MiR-600-Rev2 #882`) is approved.
* **Target Adaptation**: Angular velocities and sensor buses are adapted to Candidate 2's wheelbase and camera positions.
* **Resumption**: Robot Beta inherits the passport, verifies credentials, and completes the pallet delivery to Rack 14 with **zero facility re-mapping**.

---

## 🛠️ Quickstart & Demonstration

### 1. Interactive Terminal Walkthrough (CLI)
Run the automated step-by-step continuity simulation:
```bash
python3 -m rcn.demo
```

### 2. Interactive Visual Web Dashboard
Launch the visual 2D simulation in your browser:
```bash
# Serve locally
python3 -m http.server 8000
# Open http://localhost:8000/demo/ in your browser
```
Or open `demo/index.html` directly in any web browser.

### 3. Run Test Suite
```bash
python3 -m unittest discover tests
```

---

## 📐 Architecture & Specification

```
┌─────────────────────────────────────────────────────────────┐
│                    Robot Passport (RCN-01)                   │
│   • Persistent ID (URN)       • Security & Door Tokens      │
│   • Org Ownership & Proof     • Installed Skills & Versions │
│   • Capability Requirements   • Tamper-Evident Audit Trail  │
└──────────────────────────────┬──────────────────────────────┘
                               │
               ┌───────────────┴───────────────┐
               ▼                               ▼
┌─────────────────────────────┐ ┌─────────────────────────────┐
│    Memory Vault (RCN-02)    │ │   Hardware Compatibility    │
│ • Decoupled Semantic Maps   │ │ • Payload & Kinematic Check │
│ • Active Task Queue Cursors │ │ • Mandatory Sensor Matrix   │
│ • Learned Site Heuristics   │ │ • Compute Tier Verification │
└──────────────┬──────────────┘ └──────────────┬──────────────┘
               │                               │
               └───────────────┬───────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             Target Adaptation Layer (Body vs. ID)           │
│   • Re-scales velocity/turn limits for new wheelbase         │
│   • Maps logical sensor topics to physical driver endpoints  │
│   • Resumes mission cursor seamlessly                       │
└─────────────────────────────────────────────────────────────┘
```

* **`spec/robot_passport_schema.json`**: Formal JSON Schema for persistent robot identity, capabilities, permissions, and cryptographic signatures.
* **`spec/memory_vault_schema.json`**: Schema for decoupling portable meaning (semantic maps, task cursors, heuristics) from body-specific sensor calibrations.

---

## 🤝 30-Day Design Partner Pilot Proposal

We are looking for **one commercial fleet operator or RaaS robotics company** (AMRs, cleaning, delivery, or field robotics) to pilot RCN:

* **Zero Production Risk**: Tested on 2 bench/lab units or simulated ROS 2 nodes.
* **Timeline**: 4-week structured trial.
* **Deliverable**: Benchmark report measuring reduction in RMA swap time and re-provisioning costs.
* **Contact**: [Insert Contact Email or LinkedIn]

---

## 📤 Pushing to GitHub

To publish this repository to your GitHub account (`Aztecbird`):

```bash
# Create a new repository named 'robot-continuity-network' on GitHub first, then:
cd /Users/aztecbirdmac.com/.gemini/antigravity/scratch/robot-continuity-network
git remote add origin https://github.com/Aztecbird/robot-continuity-network.git
git branch -M main
git push -u origin main
```
