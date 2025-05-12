# Server Fleet Management at Scale — Tech Arena 2024 (Phase 1)

This repository contains the solution framework for the **Tech Arena 2024 Phase 1** challenge hosted by **Huawei Ireland Research Center**. The challenge focuses on optimising server deployment strategies across multiple data centres.

## 🧠 Problem Statement

Participants must develop a model that recommends, at each time-step, how many servers of each type (CPU, GPU) to deploy across four data-centres in order to **maximise an objective function** consisting of:

- Server Utilisation
- Normalised Lifespan
- Profit

All decisions must respect capacity constraints and server lifecycle limitations.

## 📘 Problem Overview

- **Four Data-Centres**: Each with unique energy costs, latency sensitivity, and slot capacity.
- **Two Server Types**: CPU and GPU servers, each with evolving generations and multiple attributes (e.g. power consumption, cost, life expectancy).
- **Objective Function**:  
  \( O = U \times L \times P \)  
  where:
  - \( U \): Server utilisation
  - \( L \): Normalised lifespan
  - \( P \): Profit (revenue minus operational cost)

- **Actions Per Time-Step**:
  - `buy`: Acquire and deploy a new server
  - `move`: Relocate a server between data-centres
  - `hold`: Keep a server as-is
  - `dismiss`: Retire a server

- **Timeline**: 168 discrete time-steps with stochastic demand across latency and generation pairs.

## 🧪 Solution

### Format

Solutions are submitted in JSON, specifying server actions per time-step. See `solution_example.json` for structure.

Each JSON entry contains:
- `time_step`
- `datacenter_id`
- `server_generation`
- `server_id`
- `action` (`buy`, `move`, `hold`, `dismiss`)

### Evaluation

The score is calculated over time using the objective function. Solutions are tested against multiple demand scenarios using different random seeds.

### Submission

- Submit one `.json` file per seed (e.g. `seed_123.json`)
- Bundle all JSON files into a `.zip` file for upload
- Use training seeds from `seeds.py`, and test seeds provided before final submission

## 🗃️ Repository Structure

| File | Description |
|------|-------------|
| `solution_example.json` | Sample solution in JSON format |
| `evaluation_example.py` | Evaluates the example solution |
| `mysolution.py` | Template pipeline to generate your solution |
| `evaluation.py` | Main script for evaluating solutions |
| `utils.py` | Helper functions for loading/saving data |
| `seeds.py` | Training and test seed generator |
| `datacenters.csv` | Data-centre specifications |
| `servers.csv` | Server metadata (excluding selling prices) |
| `selling_prices.csv` | Selling prices per server generation |
| `demand.csv` | Baseline demand values |
| `requirements.txt` | Required Python packages |

## ⚠️ Disclaimer

This repository and problem are for **Huawei Tech Arena 2024** participants only. All content is fictional and should not be interpreted as representing real-world systems or organisations.
