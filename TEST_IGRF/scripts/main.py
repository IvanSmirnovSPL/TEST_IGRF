import sys
import os
import numpy as np

# insert at 1, 0 is the script path (or '' in REPL)
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
        LATITUDE *= np.pi / 180
        LONGITUDE *= np.pi / 180
        ALTITUDE = ALTITUDE * 1000 + 6371000
        B = IGRF.magn_field(TIME, ALTITUDE, LATITUDE, LONGITUDE)
        output = open('../results/results_testing/test_' + str(num) + '.txt', 'w')
        output.write('Magnetic fields components in South-East-Up geographical frame:\n')
        output.write(str(B[0]) + ' ' + str(B[1]) + ' ' + str(B[2]) + ' nT \n')
        output.write('\nIntensity of the field: '+ str(np.linalg.norm(B)) + ' nT \n')
        B_ECEF = IGRF.magn_field_ECEF(TIME, ALTITUDE, LATITUDE, LONGITUDE)
        output.write('\nMagnetic fields components in ECEF: \n')
        output.write(str(B_ECEF[0]) + ' ' + str(B_ECEF[1]) + ' ' + str(B_ECEF[2]) + ' nT \n')

        year = int(TIME)
        month = (TIME - year) * 365 // 12 + 1
        day = (TIME - year) * 365 % 30
        TIME = IGRF.greg_to_julian((year, month, day, 0, 0, 0))
        # B_ECI = IGRF.magn_field_ECI(TIME, ALTITUDE, LATITUDE, LONGITUDE)
        # output.write('\nMagnetic fields components in ECI: \n')
        # output.write(str(B_ECI[0]) + ' ' + str(B_ECI[1]) + ' ' + str(B_ECI[2]) + ' nT \n')
        output.close()



pyIGRF_simple.make_test()

make_IGRF_test()
