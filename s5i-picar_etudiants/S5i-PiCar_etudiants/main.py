# main.py
import time

import packet
import control
import CarAlgo

def main():
    #ctrl = control.Control() # Classe de controle pour le hardware du picar
    # Classe de controle pour la prise de decision
    decision = CarAlgo.CarAlgo()
    last_time = time.time()
    while True:
        # Obtenir les valeurs des capteurs
        distance = ctrl.get_distance()
        suiveur = ctrl.get_line_position()

        # distance = 400
        # suiveur = [False, False, True, False, False]

        # Calculer les nouveaux controles
        current_time = time.time()
        delta_time = current_time - last_time # TODO transformer en seconds
        last_time = current_time

        decision.setDistance(distance)
        decision.setSuiveurLigne(suiveur)

        decision.mainMETick(delta_time) # T

        speed = decision.getSpeedDecision()
        angle = decision.getSteeringDecision()

        # Appliquer les nouveau controles
        ctrl.set_speed(speed)
        ctrl.set_angle(angle)


if __name__ == "__main__":
    main()