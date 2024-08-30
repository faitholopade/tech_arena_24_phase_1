import numpy as np
import pandas as pd
from seeds import known_seeds
from utils import save_solution
from evaluation import get_actual_demand, evaluation_function

def allocate_initial_servers(datacenters, servers):
    solution = []
    active_servers = {}
    server_id_counter = 0

    available_servers = servers[servers['release_time'].apply(lambda rt: 1 in eval(rt))]

    for datacenter in datacenters['datacenter_id']:
        for index, server in available_servers.iterrows():
            max_servers = datacenters.loc[datacenters['datacenter_id'] == datacenter, 'slots_capacity'].values[0] // server['slots_size']
            for _ in range(min(20, max_servers)):
                server_id = f"{server['server_generation']}_{server_id_counter}"
                solution.append({
                    "time_step": 1,
                    "datacenter_id": datacenter,
                    "server_generation": server['server_generation'],
                    "server_id": server_id,
                    "action": "buy"
                })
                active_servers[server_id] = datacenter
                server_id_counter += 1

    return solution, active_servers, server_id_counter

def manage_fleet_over_time(demand, datacenters, servers, selling_prices, seed, active_servers, server_id_counter):
    solution = []
    np.random.seed(seed)

    for ts in range(2, 169):  # Start from timestep 2
        current_demand = demand[demand['time_step'] == ts]

        for index, row in current_demand.iterrows():
            for latency in ['high', 'medium', 'low']:
                if row[latency] > 0:
                    datacenter = datacenters[datacenters['latency_sensitivity'] == latency].iloc[0]['datacenter_id']
                    available_servers = servers[(servers['server_type'] == 'CPU') & (servers['release_time'].apply(lambda rt: ts in eval(rt)))]

                    if not available_servers.empty:
                        available_server = available_servers.iloc[0]
                        server_id = f"{available_server['server_generation']}_{server_id_counter}"

                        if np.random.rand() > 0.5:
                            solution.append({
                                "time_step": ts,
                                "datacenter_id": datacenter,
                                "server_generation": available_server['server_generation'],
                                "server_id": server_id,
                                "action": "buy"
                            })
                            active_servers[server_id] = datacenter
                            server_id_counter += 1
                        elif active_servers:
                            # Move an existing server
                            server_to_move = np.random.choice(list(active_servers.keys()))
                            if active_servers[server_to_move] != datacenter:
                                solution.append({
                                    "time_step": ts,
                                    "datacenter_id": datacenter,
                                    "server_generation": server_to_move.split('_')[0],
                                    "server_id": server_to_move,
                                    "action": "move"
                                })
                                active_servers[server_to_move] = datacenter

        # Periodically dismiss old servers
        if ts % 10 == 0:
            for server_id, dc_id in list(active_servers.items()):
                server_generation = server_id.split('_')[0]
                solution.append({
                    "time_step": ts,
                    "datacenter_id": dc_id,
                    "server_generation": server_generation,
                    "server_id": server_id,
                    "action": "dismiss"
                })
                del active_servers[server_id]

    return solution

def generate_solutions(seeds, demand, datacenters, servers, selling_prices):
    for seed in seeds:
        np.random.seed(seed)
        actual_demand = get_actual_demand(demand)
        initial_solution, active_servers, server_id_counter = allocate_initial_servers(datacenters, servers)
        full_solution = manage_fleet_over_time(actual_demand, datacenters, servers, selling_prices, seed, active_servers, server_id_counter)

        final_solution = initial_solution + full_solution
        save_solution(final_solution, f'./output/{seed}.json')

# Main execution
seeds = known_seeds('training')
demand = pd.read_csv('./data/demand.csv')
datacenters = pd.read_csv('./data/datacenters.csv')
servers = pd.read_csv('./data/servers.csv')
selling_prices = pd.read_csv('./data/selling_prices.csv')

generate_solutions(seeds, demand, datacenters, servers, selling_prices)
