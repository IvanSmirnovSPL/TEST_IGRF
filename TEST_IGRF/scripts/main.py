import sys
import os
import numpy as np


def compare(a, b, name):
    # b - official
    delta = abs(a - b)
    rel_err = delta / b
    print(name + ':', 'delta:', "{:10.4e}".format(delta),
          'relative error:', "{:10.4e}".format(rel_err))


def switch(j, A, B):
    if j == 0:
        return A.X, B.X, 'X'
    if j == 1:
        return A.Y, B.Y, 'Y'
    if j == 2:
        return A.Z, B.Z, 'Z'
    if j == 3:
        return A.Total, B.Total, 'T'


def check_results(A, B):
    for j in range(4):
        a, b, name = switch(j, A, B)
        compare(a, b, name)


class Result:

    def __init__(self):
        self.X = 0
        self.Y = 0
        self.Z = 0
        self.Total = 0

    def upgrade_field(self, array):
        self.X = float(array[0])
        self.Y = float(array[1])
        self.Z = float(array[2])

    def show(self):
        print('Field:', '[', "{:10.4e}".format(self.X),
              "{:10.4e}".format(self.Y), "{:10.4e}".format(self.Z), '] nT')
        print('Total:', "{:10.4e}".format(self.Total), 'nT')


sys.path.insert(1, './official_code/')
import pyIGRF_simple

sys.path.insert(1, './testing_code/')
import IGRF


def make_IGRF_test():
    os.mkdir('../results/results_testing')
    input_file = open('../test_data.txt', 'r')
    num = 0
    for line in input_file:
        num += 1
        data = line.split()
        LATITUDE, LONGITUDE, ALTITUDE, TIME = map(float, data)
        LATITUDE = np.radians(LATITUDE) - np.pi / 2
        LONGITUDE = np.radians(LONGITUDE) - np.pi
        ALTITUDE *= 1000
        B = IGRF.magn_field(TIME, ALTITUDE, LATITUDE, LONGITUDE)
        output = open('../results/results_testing/test_' + str(num) + '.txt', 'w')
        output.write('Magnetic fields components in South-East-Up geographical frame:\n')
        output.write(str(B[0]) + ' ' + str(B[1]) + ' ' + str(B[2]) + ' nT \n')
        output.write('Intensity of the field: ' + str(np.linalg.norm(B)) + ' nT \n')
        B_ECEF = IGRF.magn_field_ECEF(TIME, ALTITUDE, LATITUDE, LONGITUDE)
        output.write('\nMagnetic fields components in ECEF: \n')
        output.write(str(B_ECEF[0]) + ' ' + str(B_ECEF[1]) + ' ' + str(B_ECEF[2]) + ' nT \n')
        output.write('Intensity of the field: ' + str(np.linalg.norm(B_ECEF)) + ' nT \n')

        year = int(TIME)
        month = int((TIME - year) * 365 // 30) + 1
        day = int((TIME - year) * 365 % 30)
        TIME = IGRF.greg_to_julian((year, month, day, 0, 0, 0))
        B_ECI = IGRF.magn_field_ECI(TIME, ALTITUDE, LATITUDE, LONGITUDE)
        output.write('\nMagnetic fields components in ECI: \n')
        output.write(str(B_ECI[0]) + ' ' + str(B_ECI[1]) + ' ' + str(B_ECI[2]) + ' nT \n')
        output.write('Intensity of the field: ' + str(np.linalg.norm(B_ECI)) + ' nT \n')
        output.close()


pyIGRF_simple.make_test()

make_IGRF_test()

# compare results
num_of_tests = len(next(os.walk('../results/results_testing'))[2])

for i in range(num_of_tests):
    test_res = Result()
    official_res = Result()
    with open('../results/results_testing/test_' + str(i + 1) + '.txt') as f:
        lines = f.readlines()
        tmp = lines[1].split()
        test_res.upgrade_field(tmp[:3])
        tmp = lines[2].split()
        test_res.Total = float(tmp[4])

    with open('../results/results_officially/test_' + str(i + 1) + '.txt') as f:
        lines = f.readlines()
        tmp = [lines[4], lines[5],
               lines[6], lines[7]]
        official_res.Total = float(tmp[0][-10 :-3] )
        official_res.X = float(tmp[1][-10 :-3])
        official_res.Y = - float(tmp[2][-10 :-3])
        official_res.Z = - float(tmp[3][-10 :-3])

    print('Test ' + str(i + 1))
    check_results(test_res, official_res)
    print()
