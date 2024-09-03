import numpy as np
import pandas as pd
from seeds import known_seeds
from utils import save_solution
from evaluation import get_actual_demand, evaluation_function

def allocate_initial_servers(datacenters, servers):
    solution = []
    active_servers = {}
    server_id_counter = 0

    # Allocate initial servers based on latency sensitivity and available slots
    for index, datacenter in datacenters.iterrows():
        available_servers = servers[servers['release_time'].apply(lambda rt: 1 in eval(rt))]
        
        for _, server in available_servers.iterrows():
            max_servers = datacenter['slots_capacity'] // server['slots_size']
            purchase_count = min(10, max_servers)  # Adjust based on initial demand

            for _ in range(purchase_count):
                server_id = f"{server['server_generation']}_{server_id_counter}"
                solution.append({
                    "time_step": 1,
                    "datacenter_id": datacenter['datacenter_id'],
                    "server_generation": server['server_generation'],
                    "server_id": server_id,
                    "action": "buy"
                })
                active_servers[server_id] = {
                    "datacenter_id": datacenter['datacenter_id'],
                    "server_generation": server['server_generation'],
                    "slots_size": server['slots_size'],
                    "capacity": server['capacity'],
                    "life_expectancy": server['life_expectancy'],
                    "energy_consumption": server['energy_consumption'],
                    "purchase_price": server['purchase_price'],
                    "average_maintenance_fee": server['average_maintenance_fee'],
                    "cost_of_moving": server['cost_of_moving'],
                    "lifespan": 0
                }
                server_id_counter += 1

    return solution, active_servers, server_id_counter

def manage_fleet_over_time(demand, datacenters, servers, selling_prices, seed, active_servers, server_id_counter):
    solution = []
    np.random.seed(seed)

    for ts in range(2, 169):
        current_demand = demand[demand['time_step'] == ts]

        for _, row in current_demand.iterrows():
            for latency in ['high', 'medium', 'low']:
                if row[latency] > 0:
                    # Prioritize fulfilling demand for high latency first, then medium, then low
                    datacenter = datacenters[datacenters['latency_sensitivity'] == latency].iloc[0]
                    available_servers = servers[
                        (servers['server_type'] == 'CPU') & 
                        (servers['release_time'].apply(lambda rt: ts in eval(rt)))
                    ]

                    if not available_servers.empty:
                        # Calculate total slots currently used in the datacenter
                        total_slots_used = sum([
                            server['slots_size'] for server in active_servers.values()
                            if server['datacenter_id'] == datacenter['datacenter_id']
                        ])

                        # Check how many slots are available
                        available_slots = datacenter['slots_capacity'] - total_slots_used
                        if available_slots <= 0:
                            continue  # No slots available, cannot add more servers

                        # Buy new servers if demand exceeds current capacity
                        capacity_needed = row[latency]
                        available_capacity = sum([
                            server['capacity'] for server in active_servers.values()
                            if server['datacenter_id'] == datacenter['datacenter_id']
                        ])

                        if capacity_needed > available_capacity:
                            # Calculate the number of servers needed to meet the demand
                            server = available_servers.iloc[0]
                            num_servers_to_buy = (capacity_needed - available_capacity) // server['capacity']
                            
                            # Calculate the slots needed for these servers
                            slots_needed = num_servers_to_buy * server['slots_size']

                            # Adjust the number of servers to buy based on available slots
                            if slots_needed > available_slots:
                                num_servers_to_buy = available_slots // server['slots_size']

                            for _ in range(num_servers_to_buy):
                                server_id = f"{server['server_generation']}_{server_id_counter}"
                                solution.append({
                                    "time_step": ts,
                                    "datacenter_id": datacenter['datacenter_id'],
                                    "server_generation": server['server_generation'],
                                    "server_id": server_id,
                                    "action": "buy"
                                })
                                active_servers[server_id] = {
                                    "datacenter_id": datacenter['datacenter_id'],
                                    "server_generation": server['server_generation'],
                                    "slots_size": server['slots_size'],
                                    "capacity": server['capacity'],
                                    "life_expectancy": server['life_expectancy'],
                                    "energy_consumption": server['energy_consumption'],
                                    "purchase_price": server['purchase_price'],
                                    "average_maintenance_fee": server['average_maintenance_fee'],
                                    "cost_of_moving": server['cost_of_moving'],
                                    "lifespan": 0
                                }
                                server_id_counter += 1

        # Periodically dismiss old servers to free up slots
        for server_id, server_data in list(active_servers.items()):
            server_data['lifespan'] += 1
            if server_data['lifespan'] >= server_data['life_expectancy']:
                solution.append({
                    "time_step": ts,
                    "datacenter_id": server_data['datacenter_id'],
                    "server_generation": server_data['server_generation'],
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
        save_solution(pd.DataFrame(final_solution), f'./output/{seed}.json')

# Main execution
seeds = known_seeds('training')
demand = pd.read_csv('./data/demand.csv')
datacenters = pd.read_csv('./data/datacenters.csv')
servers = pd.read_csv('./data/servers.csv')
selling_prices = pd.read_csv('./data/selling_prices.csv')

generate_solutions(seeds, demand, datacenters, servers, selling_prices)
