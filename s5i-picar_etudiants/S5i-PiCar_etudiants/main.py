# main.py
import time

import packet
import control
import CarAlgo
from simple_pid import PID

steering_kp = 3.5
steering_ki = 14
steering_kd = 0.035


def main():
    ctrl = control.Control() # Classe de controle pour le hardware du picar
    # Classe de controle pour la prise de decision
    decision = CarAlgo.CarAlgo()
    last_time = time.time()
    total_time = 0

    #steering pid setup
    current_angle = 90 #starting steering
    steering_pid = PID(steering_kp, steering_ki, steering_kd, setpoint=current_angle)
    steering_pid.output_limits = (45, 135)

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

        # distance = 400
        # suiveur = [False, False, True, False, False]

        # Calculer les nouveaux controles
        current_time = time.time()
        delta_time = current_time - last_time
        last_time = current_time

        decision.setDistance(distance)
        decision.setSuiveurLigne(suiveur)
        decision.mainMETick(delta_time)

        print("MainSate: ", decision.state)
        print("Distance: ", distance)
        # print("AvoidanceState: ", decision.evitementMEState)

        speed = decision.getSpeedDecision()
        steering_pid.setpoint = decision.getSteeringDecision()
        current_angle = steering_pid(current_angle)

        # Appliquer les nouveaux controles
        ctrl.set_speed(speed)
        ctrl.set_angle(current_angle)

        looptime = time.time() - current_time
        print("looptime: "+str(looptime))



if __name__ == "__main__":
    main()