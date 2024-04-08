import pandas as pd
from tqdm import tqdm
from scipy.optimize import linprog
from scipy import sparse

import os
import numpy as np


"""
Pi,t : Puissance installée sur le site i à l’heure t, en MW.
Ei,t : Énergie produite sur le site i à l’heure t, en MWh.

fonction objective: max min_t∈T Sum(Ei,t)

contraintes:
0 ≤ Pi,t ≤ Pi,max ∀i ∈ I, ∀t ∈ T
Ei,t = ηi,t · Pi,t ∀i ∈ I, ∀t ∈ T

sumi∈I Pi,t ≤ Ptotal ∀t ∈ T 

"""



sites = pd.read_csv('Data-partie-1/Sites.csv') #index site,latitude,longitude,pays,couleur,capacite offshore,scores,capacites

rendements_onshore = pd.read_csv('Data-partie-1/Rendements_onshore.csv',header=None) # chaque ligne a 8760 valeurs qui représentent la production en une heure
rendements_offshore = pd.read_csv('Data-partie-1/Rendements_offshore.csv',header=None) # chaque ligne a 8760 valeurs qui représentent la production en une heure
print(len(sites),len(rendements_offshore), len(rendements_onshore))


# Paramètres du problème
P_total = 500000  # Puissance totale à installer en MW
kappa = 0.17  # Fraction de la puissance à consacrer à des sites offshore
T = 3  # Durée de la période pour la définition de la variabilité
delta = 0.02  # Paramètre pour la limite sur la variabilité moyenne

num_sites = len(sites.index)
num_hours = 8760 # Number of hours in a year

# Coefficients of the objective function
c = np.ones(num_sites * num_hours)


# Inequality constraints vector
b = np.array([P_total])

# Inequality constraints matrix
A = sparse.csr_matrix(np.ones((1, num_sites * num_hours)))

# Add constraints for each time period
A_new = -sparse.eye(num_hours)
A_new = sparse.hstack([A_new, sparse.csr_matrix(np.ones((num_hours, 1)))])
A_zero = sparse.csr_matrix((num_hours, num_sites * num_hours - num_hours))
A = sparse.vstack([A_zero, A, A_new])

# Update b
b = np.hstack([np.zeros(num_hours), b, np.zeros(num_hours)])

# Solve the linear programming problem
res = linprog(c, A_ub=A, b_ub=b, method='highs')
print(res)
