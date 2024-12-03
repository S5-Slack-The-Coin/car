from picar import front_wheels
from picar import back_wheels
import time
import picar
from ultrasonic_module import Ultrasonic_Avoidance
import Line_Follower
import sys


class Control():
    def __init__(self):
        # CONSTANTE
        self.ANGLE_SPEED = 100 # Degres par secondes
        # controle d'angle
        self.angle = 90
        self.wanted_angle = 90
        self.MARGIN = 3


        self.angleTable = {45: 45, 60: 68, 75: 85, 90: 104, 105: 120, 120: 138, 135: 155}
        self.speed = 0
        self.fw = front_wheels.Front_Wheels(db='config')
        self.bw = back_wheels.Back_Wheels(db='config')
        self.fw.ready()
        self.bw.ready()
        self.fw.turning_max = 65
        self.set_speed(0)
        self.set_angle(90, 1)
        

        self.UA = Ultrasonic_Avoidance(20)
        self.buffer_size = 4  # Change this value to adjust filtering
        self.buffer = [0] * self.buffer_size
        self.buffer_index = 0

        self.lf = Line_Follower.Line_Follower(references=[90] * 5)

    def get_distance(self):
        current_dist = (self.UA.distance() + 4) * 10
        if current_dist > 2500: current_dist = 2500
        self.buffer[self.buffer_index] = current_dist
        if self.buffer_index < self.buffer_size - 1:
            self.buffer_index += 1
        else:
            self.buffer_index = 0
        avg = sum(self.buffer) / self.buffer_size
        return avg

    def print_line_follower(self):
        print(self.lf.read_analog())
        print(self.lf.read_digital())
        time.sleep(0.2)

    def get_line_position(self):
        return self.lf.read_digital()

    def get_speed(self):
        return self.speed

    def set_speed(self, speed, useDelta=False):
        if (speed < 0):
            self.bw.forward()  # Accel negative
        else:
            self.bw.backward()
        percent_speed = self.convert_speed(speed)
        ## Non testé avec la formule de convertion mm/s -> % mais j'assume qu'on aura pas besoin du delta any way
        if useDelta:
            self.speed += percent_speed
        else:
            self.speed = percent_speed
        # self.speed = percent_speed

        self.bw.speed = percent_speed
        return percent_speed

    def convert_speed(self, x):
        y = abs(x / 1000) * 358.81 + 12.45  # Équation de la droite
        if y < 25:
            y = 0
        elif y > 100:
            y = 100
        return int(y)

    def get_angle(self):
        return self.angle

    def set_angle(self, angle, delta, instant_angle = False):
        if instant_angle:
            self.angle = angle
        else:
            self.wanted_angle = angle

            if self.angle + self.ANGLE_SPEED * delta < self.wanted_angle:
                self.angle += self.ANGLE_SPEED * delta
            elif self.angle - self.ANGLE_SPEED * delta > self.wanted_angle:
                self.angle -= self.ANGLE_SPEED * delta
            else:
                self.angle = self.wanted_angle
        
        if self.angle in self.angleTable:
            computedAngle = self.angleTable[self.angle]
        else:
            computedAngle = self.compute_angle(self.angle)
        self.fw.turn(computedAngle)
        return computedAngle

    def compute_angle(self, angle):
        # check upper and lower cap
        if angle < 45:
            self.angle = 45
            return self.angleTable[45]
        elif angle > 135:
            self.angle = 135
            return self.angleTable[135]
        else:
            for angleID in self.angleTable.keys():
                if angleID < angle < angleID + 15:
                    lower_bound = self.angleTable[angleID]
                    upper_bound = self.angleTable[angleID + 15]
                    delta = (angle - angleID) / 15
                    return int(lower_bound + (upper_bound - lower_bound) * delta)
        print("Error in angle computing")

    def bw_test(self):
        self.bw.forward()
        for i in range(0, 10):
            self.bw.speed = i * 10
            time.sleep(0.1)
        for i in range(10, 1, -1):
            self.bw.speed = i * 10
            time.sleep(0.1)
        self.bw.backward()
        for i in range(0, 10):
            self.bw.speed = i * 10
            time.sleep(0.1)
        for i in range(10, 1, -1):
            self.bw.speed = i * 10
            time.sleep(0.1)

    def backward_30(self):
        self.set_speed(-50)
        time.sleep(6)
        self.set_speed(0)


if __name__ == "__main__":
    ctrl = Control()
    print(sys.argv[1])
    if (sys.argv[1] == "stop"):
        ctrl.set_speed(0)
        ctrl.set_angle(90, 1)
        sys.exit()
    angle_test = False
    # ctrl.backward_30()
    while True:
        print(ctrl.get_line_position())
        time.sleep(0.3)
    while angle_test:
        print("forward")
        ctrl.set_speed(150)
        time.sleep(2)
        print("backward")
        ctrl.set_speed(-150)
        time.sleep(2)
        ctrl.set_speed(0)

        # Testing angles
        for i in range(11):
            angle = 10 * i + 40
            print(f"(hard) Angle: {angle}, Computed angle: {ctrl.set_angle(angle)}")
            time.sleep(1)
