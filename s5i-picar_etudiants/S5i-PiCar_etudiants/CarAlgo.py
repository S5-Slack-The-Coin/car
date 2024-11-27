import math
from enum import Enum
class MainState(Enum):
    NORMAL = 1
    AVOIDANCE = 2
    RETAKE_LINE = 3
    STOP = 4

class AvoidanceState(Enum):
    RECULON_VIRAGE = 1
    AVANCEMENT_2VIRAGE = 2

class Movement():
    def __init__(self ,distance: float, target_speed: float):
        self.distance = distance
        self.targetSpeed = target_speed
        self.distanceTravelled = 0


class CarAlgo():
    def __init__(self):
        # Constsants
        self.MAX_ACCELERATION = 200
        self.SPEED = math.sqrt(self.MAX_ACCELERATION * 140)
        self.MAX_SPEED = self.SPEED
        self.SAFETY_FACTOR = 10

        self.cmdSpeed: float = 0.0  # mm/s
        self.distance: float = 0
        self.suiveurLigne = [False, False, False, False, False]
        self.steering = [False, False, False, False, False]
        self.cmdAngle = 90
        self.movementQueue = [] ## Verifier
        self.advancing: bool = True
        self.obstacle: bool = False
        self.stopTime = 1
        self.obsTimer = 0

        self.mainMEState = MainState.NORMAL

        # State system for avoidance algo
        self.evitementMEState = 1
        self.mouvementQueued: bool = False

        # Orientation for left line taking
        self.isRetakeOrientationLef: bool = False

        # Line lost
        self.lineLostCounter = 0
        # Facteur de safety pour le movement
        self.safetyFactor = 10


    def setDistance(self, dist):
        self.distance = dist

    def setSuiveurLigne(self, suiveur):
        self.suiveurLigne = suiveur

    def getSpeedDecision(self):
        return self.cmdSpeed

    def getSteeringDecision(self):
        return self.cmdAngle

    def _start(self):
        self.advancing = True

    def _stop(self):
        self.advancing = False


    def mainMETick(self, delta):
        if self.mainMEState == MainState.NORMAL:
            self._calculateAngle()
            self._calculateDesicion(delta)
            self._checkEnd()
        elif self.mainMEState == MainState.AVOIDANCE:
            self._evitementMETick(delta)
        elif self.mainMEState == MainState.RETAKE_LINE:
            self._retakeLine(delta)
        else:
            self._stop()
            self._move(delta, self.advancing)

    def _evitementMETick(self, delta):
        if self.mouvementQueued == False:
            self._addMovement(200, -100)
            self._addMovement(1000, 200)
            self.mouvementQueued = True

        if len(self.movementQueue) == 1:
            if self.movementQueue[0].distanceTravelled <= 170:
                cmd_angle = 67.5
            elif self.movementQueue[0].distanceTravelled <= 400:
                cmd_angle = 90
            elif self.movementQueue[0].distanceTravelled <= 580:
                cmd_angle = 135
            elif self.movementQueue[0].distanceTravelled <= 1000:
                cmd_angle = 112.5
                if self.suiveurLigne[1] == True or \
                        self.suiveurLigne[2] == True or \
                        self.suiveurLigne[3] == True:
                    self.movementQueue.clear()
                    self._start()
                    self.evitementMEState = AvoidanceState.RECULON_VIRAGE
                    self.mainMEState = MainState.AVOIDANCE
                    self.mouvementQueued = False

    def _retakeLine(self, delta):
        if self.isRetakeOrientationLef:
            self._acceleration(delta, -self.MAX_SPEED)
            if self.cmdSpeed < 0:
                self.cmdAngle = 112.5
        else:
            self._acceleration(delta, -self.MAX_SPEED)
            if self.cmdSpeed < 0:
                self.cmdAngle = 67.5

        if self.suiveurLigne[2] == True:
            self._start()
            self.mainMEState = MainState.NORMAL


    def _checkEnd(self):
        if self.suiveurLigne == [True, True, True, True, False] \
            or self.suiveurLigne == [True, True, True, True, True] \
            or self.suiveurLigne == [False, True, True, True, True]:
            self.mainMEState= MainState.RETAKE_LINE.STOP

    # calcule la décision de mouvement et d'état pour l'etat 1

    def _calculateDesicion(self, delta):
        self._move(delta, self.advancing)
        if self.distance <= 300 and self.distance != 0.0 and not self.obstacle:
            self.obstacle = True
            self._addMovement(self.distance - 100, self.MAX_SPEED)
            self._stop()

        if self.obstacle and self.cmdSpeed < 1 and self.obsTimer < self.stopTime:
            self.obsTimer += delta
        elif self.obsTimer >= self.stopTime:
            self.movementQueue.clear()
            self.mainMEState = MainState.AVOIDANCE
            self.obsTimer = 0
            self.obstacle = False
        elif not self.obstacle:
            self.obsTimer = 0


    def _calculateAngle(self):
        if self.suiveurLigne == [True, False, False, False, False]:
            self.cmdAngle = 45
            self.isRetakeOrientationLef = True
            self.lineLostCounter = 0
        elif self.suiveurLigne == [True, True, False, False, False]:
            self.cmdAngle = 56.25
            self.lineLostCounter = 0
        elif self.suiveurLigne == [False, True, False, False, False]:
            self.cmdAngle = 67.5
            self.lineLostCounter = 0
        elif self.suiveurLigne == [False, True, True, False, False]:
            self.cmdAngle = 78.75
            self.lineLostCounter = 0
        elif self.suiveurLigne == [False, False, True, False, False]:
            self.cmdAngle = 90
            self.lineLostCounter = 0
        elif self.suiveurLigne == [False, False, True, True, False]:
            self.cmdAngle = 101.25
            self.lineLostCounter = 0
        elif self.suiveurLigne == [False, False, False, True, False]:
            self.cmdAngle = 112.5
            self.lineLostCounter = 0
        elif self.suiveurLigne == [False, False, False, True, True]:
            self.cmdAngle = 123.75
            self.lineLostCounter = 0
        elif self.suiveurLigne == [False, False, False, False, True]:
            self.cmdAngle = 135
            self.lineLostCounter = 0
            self.isRetakeOrientationLef = False
        elif self.suiveurLigne == [False, False, False, False, False]:
            if self.lineLostCounter >= 5:
                self.lineLostCounter= 0
                self.mainMEState = MainState.RETAKE_LINE
                self._stop()
        else:
            self.lineLostCounter += 1

    # Applique la liste de mouvement ou l'accélération

    def _move(self, delta: float, accelerating: bool):
        if len(self.movementQueue) >= 1:
            self._moveDistance(delta)
        elif accelerating:
            self._acceleration(delta, self.MAX_SPEED)
        else:
            self._acceleration(delta, 0.0)
        return

    # Permet le controle de l'accélération
    def _acceleration(self, delta: float, target_speed: float):
        new_speed: float = 0.0
        is_accelerating: bool = False
        if target_speed < self.cmdSpeed:
            is_accelerating = False
        else:
            is_accelerating = True
        if is_accelerating:
            new_speed = self.cmdSpeed + self.MAX_ACCELERATION * delta
            new_speed = min(new_speed, target_speed, self.MAX_SPEED)
        else:
            new_speed = self.cmdSpeed - self.MAX_ACCELERATION * delta
            new_speed = max(new_speed, -abs(target_speed), -self.MAX_SPEED)
        self.cmdSpeed = new_speed


    def _moveDistance(self ,delta: float):
        current_movement = self.movementQueue[0]
        if current_movement.distanceTravelled >= current_movement.distance \
                or (self.cmdSpeed == 0 and current_movement.distanceTravelled >= current_movement.distance - self.safetyFactor):  # to prevent glitch
            self.movementQueue.pop(0)

        if len(self.movementQueue) >= 1:
            current_movement = self.movementQueue[0]
            current_movement.distanceTravelled += abs(self.cmdSpeed) * delta
            remaining_distance = current_movement.distance - current_movement.distanceTravelled
            distance_v0 = self.cmdSpeed ** 2 / (2 * self.MAX_ACCELERATION)

            if distance_v0 >= remaining_distance:
                current_movement.targetSpeed = 0.0

            self._acceleration(delta, current_movement.targetSpeed)

    # ajoute un mouvement dans la liste
    def _addMovement(self ,distance: float, target_speed: float):
        mov = Movement(distance,target_speed)
        self.movementQueue.append(mov)