from picar import front_wheels
from picar import back_wheels
import time
import picar

class Control():
    def __init__(self):
        self.angleTable = {45: 45, 60: 68, 75: 85, 90: 104, 105: 120, 120: 138, 135: 155}
        self.angle = 90
        self.speed = 0
        self.fw = front_wheels.Front_Wheels(db='config')
        self.bw = back_wheels.Back_Wheels(db='config')
        self.fw.ready()
        self.bw.ready()
        self.fw.turning_max = 65
        self.set_speed(0)
        self.set_angle(90)

    def get_speed(self):
        return self.speed
    
    def test(self):
        self.bw.forward()
        for i in range(0,10):
            self.bw.speed = i*10
            time.sleep(0.1)
        for i in range(10,1, -1):
            self.bw.speed = i*10
            time.sleep(0.1)
        self.bw.backward()
        for i in range(0,10):
            self.bw.speed = i*10
            time.sleep(0.1)
        for i in range(10,1, -1):
            self.bw.speed = i*10
            time.sleep(0.1)

    def set_speed(self, speed, useDelta = False):
        if useDelta: self.speed += speed
        else: self.speed = speed
        self.bw.backward()
        self.bw.speed = speed

    def get_angle(self):
        return self.angle

    def set_angle(self, angle, useDelta = False):
        if useDelta: self.angle += angle
        else: self.angle = angle

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
                if angleID < angle < angleID+15:
                    lower_bound = self.angleTable[angleID]
                    upper_bound = self.angleTable[angleID+15]
                    delta = (angle - angleID)/15
                    return int(lower_bound + (upper_bound - lower_bound)*delta)
        print("Error in angle computing")


if __name__ == "__main__":
    ctrl = Control()
    angle_test = False
    ctrl.set_angle(90)
    ctrl.set_speed(0)
    time.sleep(2)
    while angle_test:
        
        # Testing angles
        for i in range(11):
            angle = 10*i + 40
            print(f"(hard) Angle: {angle}, Computed angle: {ctrl.set_angle(angle)}")
            time.sleep(1)

        print("")
        print(f"(soft) Angle: {40}, Computed angle: {ctrl.set_angle(-90, True)}")
        time.sleep(1)
        print(f"(soft) Angle: {50}, Computed angle: {ctrl.set_angle(5, True)}")
        time.sleep(1)
        for i in range(9):
            angle = 10*i + 60
            print(f"(soft) Angle: {angle}, Computed angle: {ctrl.set_angle(10, True)}")
            time.sleep(1)
