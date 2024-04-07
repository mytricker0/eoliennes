import pandas as pd
import pulp

from tqdm import tqdm
 
 
for i in tqdm(range(int(9e6))):
    pass

# Assuming P_total and other required parameters are defined
P_total = 500000  # Total power to be installed in MW

# Load the CSV files into pandas DataFrames
sites_df = pd.read_csv('Data-partie-1/Sites.csv')
onshore_efficiency = pd.read_csv('Data-partie-1/Rendements_onshore.csv')
offshore_efficiency = pd.read_csv('Data-partie-1/Rendements_offshore.csv')

# Define a function to get the efficiency based on the offshore status and hour
def get_efficiency(is_offshore, index, hour):
    if is_offshore == 'Non':  # Assuming 'Non' means onshore
        return onshore_efficiency.iloc[index, hour]
    else:  # Assuming any other value means offshore
        return offshore_efficiency.iloc[index, hour]

# Define the optimization model
model = pulp.LpProblem("Wind_Farm_Optimization", pulp.LpMaximize)

# Assume I is the set of site indices, T is the set of time periods
I = range(len(sites_df) - 1)
T = range(8760)  # Number of hours in a year

# Decision variables for power
P_vars = pulp.LpVariable.dicts("Power", (I, T), lowBound=0)
# Decision variables for energy
E_vars = pulp.LpVariable.dicts("Energy", (I, T), lowBound=0)
# Variable for minimum energy production
min_energy = pulp.LpVariable("Min_Energy", lowBound=0)

# Add the objective function
model += min_energy

# Constraints for the power capacities and energy production
for i in tqdm(I):
    is_offshore = sites_df.loc[i, 'capacite offshore']  # 'Oui' or 'Non'
    capacity_max = sites_df.loc[i, 'capacites']  # Actual column name for max capacity
    for t in T:
        efficiency = get_efficiency(is_offshore, i, t)
        model += P_vars[i][t] <= capacity_max
        model += E_vars[i][t] == efficiency * P_vars[i][t]

# Constraint for the total installed power
model += pulp.lpSum([P_vars[i][t] for i in I for t in T]) <= P_total

# Constraint to ensure min_energy is the least of the energies produced in any hour
for t in tqdm(T):
    model += min_energy <= pulp.lpSum([E_vars[i][t] for i in I])
print("Model created")
# Solve the model
model.solve()
print("Model solved")

# Output results
for v in model.variables():
    print(v.name, "=", v.varValue)

print("The maximal minimum hourly energy production is:", pulp.value(model.objective))


power_capacities = {(i, t): pulp.value(P_vars[i][t]) for i in I for t in T}
energy_productions = {(i, t): pulp.value(E_vars[i][t]) for i in I for t in T}

# To get an idea of the energy production per site, you might sum over all hours:
total_energy_per_site = {i: sum(energy_productions[(i, t)] for t in T) for i in I}

# Print the total installed power and energy production for each site
for i in I:
    print(f"Site {i}: Installed Power = {power_capacities[(i, 0)]}, Total Energy Production = {total_energy_per_site[i]} MWh")

# Post-processing for analysis and visualization will go here
