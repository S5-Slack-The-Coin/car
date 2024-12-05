import math
import time
from enum import Enum
from xmlrpc.client import boolean


class MainState(Enum):
    START = 1
    NORMAL = 2
    BACKWARD = 3
    AVOIDANCE1 = 4
    AVOIDANCE2 = 5
    AVOIDANCE3 = 6
    AVOIDANCE4 = 7
    AVOIDANCE5 = 8
    STOP = 9
    RETAKE1 = 10
    RETAKE2 = 11
    RETAKE3 = 12
    RETAKE4 = 13

class TurnSide(Enum):
    RIGHT = 1
    LEFT = 2

class Movement():
    def __init__(self, distance: float, target_speed: float, stop  = False):
        self.distance = distance
        self.targetSpeed = target_speed
        self.distanceTravelled = 0
        self.stop = stop


class CarAlgo():
    def __init__(self):
        # Constsants
        self.MAX_ACCELERATION = 110
<<<<<<< Updated upstream
        self.SPEED = 110
=======
        self.SPEED = 150
>>>>>>> Stashed changes
        self.MAX_SPEED = self.SPEED
        self.CURRENT_MAX_SPEED = self.MAX_SPEED
        self.SAFETY_FACTOR = 5
<<<<<<< Updated upstream
        self.RETAKE_TRESHOLD = 3 # time in seconds
        self.SPEED_AVOIDANCE = 84
=======
        self.RETAKE_TRESHOLD = 2.7 # time in seconds
        self.SPEED_AVOIDANCE = 100
>>>>>>> Stashed changes
        # Entree
        self.distance: float = 0
        self.suiveurLigne = [False, False, False, False, False]
        # Sortie
        self.angle = 90
        self.speed: float = 0.0  # mm/s
        # MEF
        self.state = MainState.START
        self.currentStateDone = False
        # Retake system
        self.retakeCounter = 0
        self.lastTurnSide = TurnSide.RIGHT
        self.currentMovement = Movement(0, 0)
        # avoidance timer
        self.avoidanceTimer = 0
        self.set90 = False
        self.Sleeping = False

        self.instantAngle = False

    def getInstantAngle(self):
        if self.instantAngle:
            self.instantAngle = False
            return True
        return False
    
    def mainMETick(self, delta):
        self._stateCalculator()
        self._stateCaller(delta)

    def _stateCalculator(self):
        if self.state == MainState.START:
            self.state = MainState.NORMAL
        elif self.state == MainState.NORMAL:
            if self.retakeCounter >= self.RETAKE_TRESHOLD:
                 self._changeState(MainState.RETAKE1)
            elif self.suiveurLigne == [True, True, True, True, True]:
                self._changeState(MainState.STOP)
            elif 70 <= self.distance <= 125 and self.speed <= 35:
                self._changeState(MainState.BACKWARD)

        elif self.state == MainState.BACKWARD:
            if self.currentStateDone:
                self._changeState(MainState.AVOIDANCE1)

        elif self.state == MainState.AVOIDANCE1:
            if self.currentStateDone:
                self._changeState(MainState.AVOIDANCE2)

        elif self.state == MainState.AVOIDANCE2:
            if self.currentStateDone:
                self._changeState(MainState.AVOIDANCE3)

        elif self.state == MainState.AVOIDANCE3:
            if self.currentStateDone:
                self._changeState(MainState.AVOIDANCE4)
        elif self.state == MainState.AVOIDANCE4:
            if self.currentStateDone or self.suiveurLigne[0] or self.suiveurLigne[1] or self.suiveurLigne[2]:
                self._changeState(MainState.AVOIDANCE5)
        elif self.state == MainState.AVOIDANCE5:
                if self.suiveurLigne[0] or self.suiveurLigne[1] or self.suiveurLigne[2]:
                    self._changeState(MainState.NORMAL)
        elif self.state == MainState.STOP:
            pass
        elif self.state == MainState.RETAKE1: # ARRETE
            if self.currentStateDone:
                self._changeState(MainState.RETAKE2)
        elif self.state == MainState.RETAKE2: # REVIENT
            if self.currentStateDone or self.suiveurLigne[2]:
                self._changeState(MainState.RETAKE3)
        elif self.state == MainState.RETAKE3: # ARRETE
<<<<<<< Updated upstream
            if self.currentStateDone:
                self._changeState(MainState.RETAKE4)
        elif self.state == MainState.RETAKE4: # REPRENDRE LA LIGNE DU COTE PERDU
            if self.suiveurLigne[0] or self.suiveurLigne[1] or self.suiveurLigne[2] or self.suiveurLigne[3] or self.suiveurLigne[4] and self.currentStateDone:
                self._changeState(MainState.NORMAL)
=======
            if self.suiveurLigne[0] or self.suiveurLigne[1] or self.suiveurLigne[2] or self.suiveurLigne[3] or self.suiveurLigne[4] and self.currentStateDone:
                self._changeState(MainState.NORMAL)
            elif self.currentStateDone:
                self._changeState(MainState.RETAKE4)
        elif self.state == MainState.RETAKE4: # REPRENDRE LA LIGNE DU COTE PERDU
            if self.suiveurLigne[0] or self.suiveurLigne[1] or self.suiveurLigne[2] or self.suiveurLigne[3] or self.suiveurLigne[4] and self.currentStateDone:
                self._changeState(MainState.NORMAL)
>>>>>>> Stashed changes
            
                
    def _changeState(self, state):
        if state == MainState.BACKWARD:
<<<<<<< Updated upstream
            self.currentMovement = Movement(235, -self.MAX_SPEED, True)
            self.set90 = True
            self.Sleeping = True
        elif state == MainState.RETAKE2:
            self.currentMovement = Movement(280, -self.MAX_SPEED + 30, True)
        elif state == MainState.RETAKE4:
            self.currentMovement = Movement(280, self.MAX_SPEED + 30, True)
=======
            self.currentMovement = Movement(235, -self.MAX_SPEED*0.7, True)
            self.set90 = True
            self.Sleeping = True
        elif state == MainState.RETAKE2:
            self.currentMovement = Movement(280, -self.MAX_SPEED*0.65, True)
        elif state == MainState.RETAKE4:
            self.currentMovement = Movement(280, self.MAX_SPEED*0.65, True)
>>>>>>> Stashed changes

        self.avoidanceTimer = 0
        self.currentStateDone = False
        self.state = state

    def _stateCaller(self, delta):
        if self.state == MainState.START:
            pass
        elif self.state == MainState.NORMAL:
            self._normalState(delta)
        elif self.state == MainState.BACKWARD:
            self._backwardState(delta)
        elif self.state == MainState.AVOIDANCE1:
            self._avoidance1State(delta)
        elif self.state == MainState.AVOIDANCE2:
            self._avoidance2State(delta)
        elif self.state == MainState.AVOIDANCE3:
            self._avoidance3State(delta)
        elif self.state == MainState.AVOIDANCE4:
            self._avoidance4State(delta)
        elif self.state == MainState.AVOIDANCE5:
            self._avoidance5State()
        elif self.state == MainState.STOP:
            self._stopState(delta)
        elif self.state == MainState.RETAKE1:
            self._stopState(delta)
        elif self.state == MainState.RETAKE2:
            self._retake2(delta)
        elif self.state == MainState.RETAKE3:
            self._stopState(delta)
        elif self.state == MainState.RETAKE4:
            self._retake4(delta)

    def _normalState(self, delta):
        self.angle = self._calculateAngle()
        self.instantAngle = False

        # Count de tick a aucune ligne
        if self.suiveurLigne == [False, False, False, False, False]:
            self.retakeCounter += delta
        else:
            self.retakeCounter = 0

        if self.distance > 300:
            self.speed = self._acceleration(delta, self.CURRENT_MAX_SPEED)
        else:
            wanted_speed = self._calculateColisionSpeed(self.distance)
            #print("caluclated speed", wanted_speed)
            self.speed = self._acceleration(delta, wanted_speed)

    def _backwardState(self, delta):
        if self.Sleeping:
<<<<<<< Updated upstream
            self.Sleeping = False
            time.sleep(2)
        self.angle = 90
        self._movementDone(delta)
=======
            self._wait(delta, 2)
        self.angle = 90
        self._movementDone(delta)
    # wait
    def _wait(self, delta, wanted_time):
        self.avoidanceTimer += delta
        if self.avoidanceTimer >= wanted_time:
            self.Sleeping = False
        
>>>>>>> Stashed changes
    # tourne a gauche
    def _avoidance1State(self, delta):
        self.angle = 55
        self.speed = self.SPEED_AVOIDANCE
<<<<<<< Updated upstream
        self._timerFinished(delta, 2.5)
=======
        self._timerFinished(delta, 2.2)
>>>>>>> Stashed changes
    # tourne a droite
    def _avoidance2State(self, delta):
        self.angle = 125
        self.speed = self.SPEED_AVOIDANCE
<<<<<<< Updated upstream
        self._timerFinished(delta, 2.5)
=======
        self._timerFinished(delta, 2.2)
>>>>>>> Stashed changes
    # tout droit
    def _avoidance3State(self, delta):
        self.angle = 90
        self.speed = self.SPEED_AVOIDANCE
<<<<<<< Updated upstream
        self._timerFinished(delta, 1.8)
    # tourne a droite
    def _avoidance4State(self, delta):
        self.angle = 125
        self.speed = self.SPEED_AVOIDANCE
        self._timerFinished(delta, 1.3)
=======
        self._timerFinished(delta, 1.5)
    # tourne a droite
    def _avoidance4State(self, delta):
        self.angle = 135
        self.speed = self.SPEED_AVOIDANCE
        self._timerFinished(delta, 1.5)
>>>>>>> Stashed changes
    
    def _avoidance5State(self):
        self.angle = 90
        self.speed = self.SPEED_AVOIDANCE

    def _timerFinished(self, delta, wanted_time):
        self.avoidanceTimer += delta
        if self.avoidanceTimer >= wanted_time:
            self.currentStateDone = True

    def _retake2(self, delta):
        if self.lastTurnSide == TurnSide.RIGHT:
            self.angle = 45
        else:
            self.angle = 135
        self.instantAngle = True
        self._movementDone(delta)

    def _retake4(self, delta):
        if self.lastTurnSide == TurnSide.RIGHT:
            self.angle = 135
        else:
            self.angle = 45
        self.instantAngle = True
        self.speed = self.SPEED_AVOIDANCE
        self._timerFinished(delta, 1.4)

    def _moveDistance(self, delta: float):
        self.currentMovement.distanceTravelled += abs(self.speed) * delta
        remaining_distance = self.currentMovement.distance - self.currentMovement.distanceTravelled
        distance_v0 = self.speed ** 2 / (2 * self.MAX_ACCELERATION)

        if distance_v0 >= remaining_distance and self.currentMovement.stop:
            self.currentMovement.targetSpeed = 0.0
        return self._acceleration(delta, self.currentMovement.targetSpeed)

    def _movementDone(self, delta):
        self.speed = self._moveDistance(delta)
        if self.currentMovement.distanceTravelled >= self.currentMovement.distance \
                or (
                self.speed == 0 and self.currentMovement.distanceTravelled >= self.currentMovement.distance - self.SAFETY_FACTOR):
            self.currentStateDone = True

    def _stopState(self, delta):
        self.speed = self._acceleration(delta, 0.0)
        if -10 <= self.speed <= 10:
            self.currentStateDone = True

    def _acceleration(self, delta: float, target_speed: float):
        new_speed: float = 0.0
        is_accelerating: bool = False
        if target_speed < self.speed:
            is_accelerating = False
        else:
            is_accelerating = True
        if is_accelerating:
            new_speed = self.speed + self.MAX_ACCELERATION * delta
            new_speed = min(new_speed, target_speed, self.MAX_SPEED)
        else:
            new_speed = self.speed - self.MAX_ACCELERATION * delta
            new_speed = max(new_speed, -abs(target_speed), -self.MAX_SPEED)
        return new_speed

    def _calculateAngle(self):
        if self.suiveurLigne == [True, False, False, False, False]:
            self.lastTurnSide = TurnSide.LEFT
            self.CURRENT_MAX_SPEED = self.MAX_SPEED*0.85
            return 45
        elif self.suiveurLigne == [True, True, False, False, False]:
            self.lastTurnSide = TurnSide.LEFT
            self.CURRENT_MAX_SPEED = self.MAX_SPEED*0.9
            return 55
        elif self.suiveurLigne == [False, True, False, False, False]:
            self.lastTurnSide = TurnSide.LEFT
<<<<<<< Updated upstream
            return 80
        elif self.suiveurLigne == [False, True, True, False, False]:
            self.lastTurnSide = TurnSide.LEFT
            return 85
=======
            self.CURRENT_MAX_SPEED = self.MAX_SPEED
            return 75
        elif self.suiveurLigne == [False, True, True, False, False]:
            self.lastTurnSide = TurnSide.LEFT
            self.CURRENT_MAX_SPEED = self.MAX_SPEED
            return 82.5
>>>>>>> Stashed changes
        elif self.suiveurLigne == [False, False, True, False, False]:
            self.CURRENT_MAX_SPEED = self.MAX_SPEED
            return 90
        elif self.suiveurLigne == [False, False, True, True, False]:
            self.lastTurnSide = TurnSide.RIGHT
<<<<<<< Updated upstream
            return 95
        elif self.suiveurLigne == [False, False, False, True, False]:
            self.lastTurnSide = TurnSide.RIGHT
            return 100
=======
            self.CURRENT_MAX_SPEED = self.MAX_SPEED
            return 97.5
        elif self.suiveurLigne == [False, False, False, True, False]:
            self.lastTurnSide = TurnSide.RIGHT
            self.CURRENT_MAX_SPEED = self.MAX_SPEED
            return 105
>>>>>>> Stashed changes
        elif self.suiveurLigne == [False, False, False, True, True]:
            self.lastTurnSide = TurnSide.RIGHT
            self.CURRENT_MAX_SPEED = self.MAX_SPEED*0.9
            return 125
        elif self.suiveurLigne == [False, False, False, False, True]:
            self.lastTurnSide = TurnSide.RIGHT
            self.CURRENT_MAX_SPEED = self.MAX_SPEED*0.85
            return 135
        return self.angle

    def _calculateColisionSpeed(self, distance: float):
        return self.MAX_SPEED / 200 * distance + 30 - 0.5 * self.MAX_SPEED

    def setDistance(self, dist):
        self.distance = dist

    def setSuiveurLigne(self, suiveur):
        self.suiveurLigne = suiveur

    def getSpeedDecision(self):
        return self.speed

    def getSteeringDecision(self):
        return self.angle