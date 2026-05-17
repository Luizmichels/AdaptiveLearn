import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

sentimento = ctrl.Antecedent(np.arange(0, 11, 1), 'sentimento')
taxaAcerto = ctrl.Antecedent(np.arange(0, 101, 1), 'taxaAcerto')
tempoGasto = ctrl.Antecedent(np.arange(0, 61, 1), 'tempoGasto')
nivelIdeal = ctrl.Consequent(np.arange(0, 11, 1), 'nivelIdeal')

#Sentimento
sentimento['frustrado'] = fuzz.trimf(sentimento.universe, [0, 0, 5])
sentimento['neutro'] = fuzz.trimf(sentimento.universe, [2, 5, 8])
sentimento['confiante'] = fuzz.trimf(sentimento.universe, [5, 10, 10])

#taxa
taxaAcerto['baixa'] = fuzz.trimf(taxaAcerto.universe, [0, 0, 50])
taxaAcerto['media'] = fuzz.trimf(taxaAcerto.universe, [25, 50, 75])
taxaAcerto['alta'] = fuzz.trimf(taxaAcerto.universe, [50, 100, 100])

#tempo gasto
tempoGasto['rapido'] = fuzz.trimf(tempoGasto.universe, [0, 0, 20])
tempoGasto['medio'] = fuzz.trimf(tempoGasto.universe, [10, 30, 50])
tempoGasto['lento'] = fuzz.trimf(tempoGasto.universe, [40, 60, 60])

#nivel
nivelIdeal['facil'] = fuzz.trimf(nivelIdeal.universe, [0, 0, 5])
nivelIdeal['medio'] = fuzz.trimf(nivelIdeal.universe, [2, 5, 8])
nivelIdeal['dificil'] = fuzz.trimf(nivelIdeal.universe, [5, 10, 10])

#regras
regra1 = ctrl.Rule(
    sentimento['frustrado'] &
    taxaAcerto['baixa'] &
    tempoGasto['lento'],
    nivelIdeal['facil']
)

regra2 = ctrl.Rule(
    sentimento['confiante'] &
    taxaAcerto['alta'] &
    tempoGasto['rapido'],
    nivelIdeal['dificil']
)

regra3 = ctrl.Rule(
    sentimento['neutro'] &
    taxaAcerto['media'],
    nivelIdeal['medio']
)

regra4 = ctrl.Rule(
    sentimento['frustrado'] &
    taxaAcerto['media'],
    nivelIdeal['facil']
)

regra5 = ctrl.Rule(
    sentimento['confiante'] &
    taxaAcerto['media'],
    nivelIdeal['medio']
)

regra6 = ctrl.Rule(
    sentimento['neutro'] &
    taxaAcerto['alta'],
    nivelIdeal['dificil']
)

regra7 = ctrl.Rule(
    sentimento['neutro'] &
    taxaAcerto['baixa'],
    nivelIdeal['facil']
)

regra8 = ctrl.Rule(
    sentimento['confiante'] &
    tempoGasto['lento'],
    nivelIdeal['medio']
)

regra9 = ctrl.Rule(
    sentimento['frustrado'] &
    tempoGasto['rapido'],
    nivelIdeal['medio']
)

#sistema fuzzy
controleSistema = ctrl.ControlSystem([
    regra1,
    regra2,
    regra3,
    regra4,
    regra5,
    regra6,
    regra7,
    regra8,
    regra9
])

def inferir_nivel(valorSentimento, taxa, tempo):

    #defuzzificação
    sistema = ctrl.ControlSystemSimulation(controleSistema)

    sistema.input['sentimento'] = valorSentimento
    sistema.input['taxaAcerto'] = taxa
    sistema.input['tempoGasto'] = tempo

    sistema.compute()

    return sistema.output['nivelIdeal']