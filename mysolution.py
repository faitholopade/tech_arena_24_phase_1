import numpy as np
import pandas as pd
from seeds import known_seeds
from utils import save_solution
from evaluation import get_actual_demand, evaluation_function

def allocate_initial_servers(datacenters, servers):
    solution = []
    server_id_counter = 0

    for datacenter in datacenters['datacenter_id']:
        available_servers = servers[servers['release_time'].apply(lambda rt: 1 in eval(rt))]

        for index, server in available_servers.iterrows():
            server_count = datacenters.loc[datacenters['datacenter_id'] == datacenter, 'slots_capacity'].values[0] // server['slots_size']
            for _ in range(min(20, server_count)):
                solution.append({
                    "time_step": 1,
                    "datacenter_id": datacenter,
                    "server_generation": server['server_generation'],
                    "server_id": f"server_{server_id_counter}",
                    "action": "buy"
                })
                server_id_counter += 1

    return solution

def manage_fleet_over_time(demand, datacenters, servers, selling_prices, seed):
    solution = []
    np.random.seed(seed)
    server_id_counter = len(solution)

    for ts in range(1, 169):
        current_demand = demand[demand['time_step'] == ts]

        for index, row in current_demand.iterrows():
            for latency in ['high', 'medium', 'low']:
                if row[latency] > 0:
                    datacenter = datacenters[datacenters['latency_sensitivity'] == latency].iloc[0]['datacenter_id']
                    available_servers = servers[(servers['server_type'] == 'CPU') & (servers['release_time'].apply(lambda rt: ts in eval(rt)))]

                    if not available_servers.empty:
                        available_server = available_servers.iloc[0]

                        # Strategy to decide on action: move servers if already bought
                        if np.random.rand() > 0.5:
                            solution.append({
                                "time_step": ts,
                                "datacenter_id": datacenter,
                                "server_generation": available_server['server_generation'],
                                "server_id": f"server_{server_id_counter}",
                                "action": "buy"
                            })
                            server_id_counter += 1
                        else:
                            solution.append({
                                "time_step": ts,
                                "datacenter_id": datacenter,
                                "server_generation": available_server['server_generation'],
                                "server_id": f"server_{server_id_counter - 1}",
                                "action": "move"  # Move to respond to changing demand
                            })

        # Dismiss servers as they near end of life to optimize lifespan
        if ts % 10 == 0:
            for datacenter in datacenters['datacenter_id']:
                old_servers = [s for s in solution if s['action'] == 'buy' and s['datacenter_id'] == datacenter and ts - s['time_step'] > 80]
                for server in old_servers:
                    solution.append({
                        "time_step": ts,
                        "datacenter_id": datacenter,
                        "server_generation": server['server_generation'],
                        "server_id": server['server_id'],
                        "action": "dismiss"
                    })

    return solution

def generate_solutions(seeds, demand, datacenters, servers, selling_prices):
    for seed in seeds:
        np.random.seed(seed)
        actual_demand = get_actual_demand(demand)
        initial_solution = allocate_initial_servers(datacenters, servers)
        full_solution = manage_fleet_over_time(actual_demand, datacenters, servers, selling_prices, seed)

        # Combine the initial and time-step solutions
        final_solution = initial_solution + full_solution
        save_solution(final_solution, f'./output/{seed}.json')

# Main execution
seeds = known_seeds('training')
demand = pd.read_csv('./data/demand.csv')
datacenters = pd.read_csv('./data/datacenters.csv')
servers = pd.read_csv('./data/servers.csv')
selling_prices = pd.read_csv('./data/selling_prices.csv')

generate_solutions(seeds, demand, datacenters, servers, selling_prices)
