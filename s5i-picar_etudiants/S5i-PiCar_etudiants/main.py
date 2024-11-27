# main.py
import time

import packet
import control
import CarAlgo


def main():
    ctrl = control.Control() # Classe de controle pour le hardware du picar
    # Classe de controle pour la prise de decision
    decision = CarAlgo.CarAlgo()
    last_time = time.time()
    total_time = 0

    while total_time < 2:
        current_time = time.time()
        delta_time = current_time - last_time
        last_time = current_time
        total_time +=delta_time
        time.sleep(0.58)
        ctrl.get_distance()

    while True:
        # Obtenir les valeurs des capteurs
        distance = ctrl.get_distance()
        suiveur = ctrl.get_line_position()
        # Calculer les nouveaux controles
        current_time = time.time()
        delta_time = current_time - last_time
        last_time = current_time
        print(delta_time)

        decision.setDistance(distance)
        decision.setSuiveurLigne(suiveur)
        decision.mainMETick(delta_time)

        print("MainSate: ", decision.state)
        print("Distance: ", distance)
        # print("AvoidanceState: ", decision.evitementMEState)

        speed = decision.getSpeedDecision()
        angle = decision.getSteeringDecision()

        # Appliquer les nouveaux controles
        ctrl.set_speed(speed)
        ctrl.set_angle(angle)



if __name__ == "__main__":
    main()