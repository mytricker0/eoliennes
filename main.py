import pandas as pd
from pulp import *
from tqdm import tqdm
import os

# Charger les données
sites = pd.read_csv('Data-partie-1/Sites.csv')
rendements_onshore = pd.read_csv('Data-partie-1/Rendements_onshore.csv',header=None)
rendements_offshore = pd.read_csv('Data-partie-1/Rendements_offshore.csv',header=None)
print(len(sites),len(rendements_offshore), len(rendements_onshore))

# os._exit(0)
# Paramètres du problème
P_total = 500000  # Puissance totale à installer en MW
kappa = 0.17  # Fraction de la puissance à consacrer à des sites offshore
T = 3  # Durée de la période pour la définition de la variabilité
delta = 0.02  # Paramètre pour la limite sur la variabilité moyenne

# Création du modèle d'optimisation
model = LpProblem("Optimisation_Capacité_Éolienne", LpMaximize)
print("Modèle créé")

# Variables de décision
# Puissance installée sur le site i au temps t
P_vars = LpVariable.dicts("Puissance", [(i,t) for i in sites.index for t in range(8760)], lowBound=0, upBound=None)
print("Variables de décision créées")
# Énergie produite sur le site i au temps t
E_vars = LpVariable.dicts("Energie", [(i,t) for i in sites.index for t in range(8760)], lowBound=0, upBound=None)
print("Variables de décision créées")
# Minimiser la puissance installée
model += lpSum([P_vars[i,t] for i in sites.index for t in range(8760)])
print("Objectif ajouté")
# Contraintes
# Puissance totale installée ne doit pas dépasser P_total
model += lpSum([P_vars[i,t] for i in sites.index for t in range(8760)]) <= P_total
print("Contrainte ajoutée")
# Fraction de la puissance à consacrer à des sites offshore
model += lpSum([P_vars[i,t] for i in sites.index if sites['capacite offshore'][i] == 'Oui' for t in range(8760)]) >= kappa * P_total
print("Contrainte ajoutée")

# Contraintes de production d'énergie
for i in tqdm(sites.index):
    for t in range(min(8760, len(rendements_offshore))):
        # Onshore
        if sites['capacite offshore'][i] == 'Non':
            model += E_vars[i,t] == rendements_onshore.iloc[i,t] * P_vars[i,t]
        # Offshore
        else:
            model += E_vars[i,t] == rendements_offshore.iloc[i,t] * P_vars[i,t]
print("Contraintes ajoutées")
print("Contraintes ajoutées")
# Résoudre le modèle
model.solve()
print("Modèle résolu")
# Affichage des résultats
for v in model.variables():
    if v.varValue > 0:
        print(v.name, "=", v.varValue)
print("Énergie totale produite:", value(model.objective), "MWh")
# Énergie totale produite
energie_totale = sum([E_vars[i,t].varValue for i in sites.index for t in range(8760)])
print("Énergie totale produite:", energie_totale, "MWh")

# Commentaires sur le résultat et le temps de résolution
# ... (à rédiger en français)
