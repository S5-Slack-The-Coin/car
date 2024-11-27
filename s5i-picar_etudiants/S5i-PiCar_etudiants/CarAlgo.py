import math
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
    STOP = 8
    RETAKE = 9

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
        self.MAX_ACCELERATION = 120
        self.SPEED = math.sqrt(self.MAX_ACCELERATION * 140)
        self.MAX_SPEED = self.SPEED
        self.SAFETY_FACTOR = 10
        self.RETAKE_TRESHOLD = 20
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

    def mainMETick(self, delta):
        self._stateCalculator()
        self._stateCaller(delta)

    def _stateCalculator(self):
        if self.state == MainState.START:
            self.state = MainState.NORMAL
        elif self.state == MainState.NORMAL:
            if self.retakeCounter >= self.RETAKE_TRESHOLD:
                 self._changeState(MainState.RETAKE)
            elif self.suiveurLigne == [True, True, True, True, True] or self.suiveurLigne == [False, True, True, True,
                                                                                            True] or self.suiveurLigne == [
                True, True, True, True, False]:
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
                if self.currentStateDone:
                    self._changeState(MainState.NORMAL)

        elif self.state == MainState.STOP:
            pass

    def _changeState(self, state):
        if state == MainState.BACKWARD:
            self.currentMovement = Movement(220, -self.MAX_SPEED, True)
        elif state == MainState.AVOIDANCE1:
            self.currentMovement = Movement(150, self.MAX_SPEED)
        elif state == MainState.AVOIDANCE2:
            self.currentMovement = Movement(260, self.MAX_SPEED)
        elif state == MainState.AVOIDANCE3:
            self.currentMovement = Movement(200, self.MAX_SPEED)
        elif state == MainState.AVOIDANCE4:
            self.currentMovement = Movement(200, self.MAX_SPEED)
        elif state == MainState.RETAKE:
            self.currentMovement = Movement(220, -self.MAX_SPEED, True)

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
        elif self.state == MainState.STOP:
            self._stopState(delta)
        elif self.state == MainState.RETAKE:
            self._retake(delta)

    def _normalState(self, delta):
        self.angle = self._calculateAngle()

        # Count de tick a aucune ligne
        if self.suiveurLigne == [False, False, False, False, False]:
            self.retakeCounter += 1
        else:
            self.retakeCounter = 0
        # calcul de la vitesse
        wanted_spped = 0
        if self.distance > 300:
            self.speed = self._acceleration(delta, self.MAX_SPEED)
        else:
            wanted_speed = self._calculateColisionSpeed(self.distance)
            #print("caluclated speed", wanted_speed)
            self.speed = self._acceleration(delta, wanted_speed)

    def _backwardState(self, delta):
        self.angle = 90
        self._movementDone(delta)

    def _avoidance1State(self, delta):
        self.angle = 55
        self._movementDone(delta)

    def _avoidance2State(self, delta):
        self.angle = 90
        self._movementDone(delta)

    def _avoidance3State(self, delta):
        self.angle = 135
        self._movementDone(delta)

    def _avoidance4State(self, delta):
        self.angle = 90
        self._movementDone(delta)
        # Condition de fin
        self.currentStateDone = self.suiveurLigne == [False, False, True, False, False] or self.suiveurLigne == [False, False, True, True, False] or self.suiveurLigne == [False, True, True, False, False] or self.suiveurLigne == [False, True, True, True, False]

    def _retake(self, delta):
        if self.lastTurnSide == TurnSide.RIGHT:
            self.angle = 135
        else:
            self.angle = 65
        self._movementDone(delta)
        self.currentStateDone = self.suiveurLigne == [False, False, True, False, False] or self.suiveurLigne == [False, False, True, True, False] or self.suiveurLigne == [False, True, True, False, False] or self.suiveurLigne == [False, True, True, True, False]

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
            return 50
        elif self.suiveurLigne == [True, True, False, False, False]:
            self.lastTurnSide = TurnSide.LEFT
            return 56.25
        elif self.suiveurLigne == [False, True, False, False, False]:
            self.lastTurnSide = TurnSide.LEFT
            return 67.5
        elif self.suiveurLigne == [False, True, True, False, False]:
            self.lastTurnSide = TurnSide.LEFT
            return 78.75
        elif self.suiveurLigne == [False, False, True, False, False]:
            return 90
        elif self.suiveurLigne == [False, False, True, True, False]:
            self.lastTurnSide = TurnSide.RIGHT
            return 101.25
        elif self.suiveurLigne == [False, False, False, True, False]:
            self.lastTurnSide = TurnSide.RIGHT
            return 112.5
        elif self.suiveurLigne == [False, False, False, True, True]:
            self.lastTurnSide = TurnSide.RIGHT
            return 123.75
        elif self.suiveurLigne == [False, False, False, False, True]:
            self.lastTurnSide = TurnSide.RIGHT
            return 130
        elif self.suiveurLigne == [False, False, False, False, False]:
            self.lastTurnSide = TurnSide.RIGHT
            return 0
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