"""
Script interativo para testar o classificador.

Comando para executar:
    python testar_pln.py

Permite digitar feedbacks e ver a classificação em tempo real.
"""

import sys
from pln_nb import classificar

def main() -> None:

    exemplos = [
        "Não entendi nada, tô completamente perdido",
        "Foi ok, deu pra fazer com algum esforço",
        "Mandei muito bem, achei fácil demais",
        "Travei na parte da recursão, muito difícil",
        "Resolvi tranquilo, gostei do exercício",
        "Achei meio chato mas consegui terminar",
    ]
    print("Exemplos:\n")
    for texto in exemplos:
        try:
            classe, prob = classificar(texto)
        except FileNotFoundError as e:
            print(f"ERRO: {e}")
            sys.exit(1)
        print(f"  [{classe:10s}] (conf_score={prob:.3f}) {texto}")

    print("\n" + "-" * 64)
    print("Modo interativo:\n")

    while True:
        try:
            texto = input("Feedback> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nEncerrando.")
            break

        if not texto:
            continue
        if texto.lower() in {"sair", "exit", "quit", "q"}:
            print("Encerrando.")
            break

        classe, prob = classificar(texto)
        barra = "#" * int(prob * 30)
        print(f"  classe:        {classe}")
        print(f"  conf_score:    {prob:.3f}  |{barra:<30}|")
        print(f"  >> esse valor (conf_score) será a variável 'sentimento'")
        print(f"     na entrada do sistema Fuzzy (Camada II).\n")


if __name__ == "__main__":
    main()
