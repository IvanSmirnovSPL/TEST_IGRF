#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from scipy import interpolate
import igrf_utils as iut
import io_options_simple as ioo
import os
import shutil

# Load in the file of coefficients
IGRF_FILE = r'./official_code/IGRF13.shc'
igrf = iut.load_shcfile(IGRF_FILE, None)


def make_test():
    # make directory for saving results
    shutil.rmtree('../results', ignore_errors=True)
    os.mkdir('../results')
    os.mkdir('../results/results_officially')

    input_file = open('../test_data.txt', 'r')
    num = 0
    for line in input_file:
        num += 1
        LATITUDE, LONGITUDE, ALTITUDE, TIME = line.split()
        iopt = 1
        # Parse the inputs for computing the main field and SV values.
        # Convert geodetic to geocentric coordinates if required
        if iopt == 1:
            date, alt, lat, colat, lon, itype, sd, cd = ioo.option1(LATITUDE, LONGITUDE, ALTITUDE, TIME)
        elif iopt == 2:
            date, alt, lat, colat, lon, itype, sd, cd = ioo.option2()
        else:
            date, alt, lat, colat, lon, itype, sd, cd = ioo.option3()

        # Interpolate the geomagnetic coefficients to the desired date(s)
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
        f = interpolate.interp1d(igrf.time, igrf.coeffs, fill_value='extrapolate')
        coeffs = f(date)

        # Compute the main field B_r, B_theta and B_phi value for the location(s)
        Br, Bt, Bp = iut.synth_values(coeffs.T, alt, colat, lon,
                                      igrf.parameters['nmax'])

        # For the SV, find the 5 year period in which the date lies and compute
        # the SV within that period. IGRF has constant SV between each 5 year period
        # We don't need to subtract 1900 but it makes it clearer:
        epoch = (date - 1900) // 5
        epoch_start = epoch * 5
        # Add 1900 back on plus 1 year to account for SV in nT per year (nT/yr):
        coeffs_sv = f(1900 + epoch_start + 1) - f(1900 + epoch_start)
        Brs, Bts, Bps = iut.synth_values(coeffs_sv.T, alt, colat, lon,
                                         igrf.parameters['nmax'])

        # Use the main field coefficients from the start of each five epoch
        # to compute the SV for Dec, Inc, Hor and Total Field (F)
        # [Note: these are non-linear components of X, Y and Z so treat separately]
        coeffsm = f(1900 + epoch_start);
        Brm, Btm, Bpm = iut.synth_values(coeffsm.T, alt, colat, lon,
                                         igrf.parameters['nmax'])

        # Rearrange to X, Y, Z components
        X = -Bt;
        Y = Bp;
        Z = -Br
        # For the SV
        dX = -Bts;
        dY = Bps;
        dZ = -Brs
        Xm = -Btm;
        Ym = Bpm;
        Zm = -Brm
        # Rotate back to geodetic coords if needed
        if (itype == 1):
            t = X;
            X = X * cd + Z * sd;
            Z = Z * cd - t * sd
            t = dX;
            dX = dX * cd + dZ * sd;
            dZ = dZ * cd - t * sd
            t = Xm;
            Xm = Xm * cd + Zm * sd;
            Zm = Zm * cd - t * sd

        # Compute the four non-linear components
        dec, hoz, inc, eff = iut.xyz2dhif(X, Y, Z)
        # The IGRF SV coefficients are relative to the main field components
        # at the start of each five year epoch e.g. 2010, 2015, 2020
        decs, hozs, incs, effs = iut.xyz2dhif_sv(Xm, Ym, Zm, dX, dY, dZ)

        # Finally, parse the outputs for writing to screen or file
        name = '../results/results_officially/test_' + str(num) + '.txt'
        if iopt == 1:
            ioo.write1(name, date, alt, lat, colat, lon, X, Y, Z, dX, dY, dZ, \
                       dec, hoz, inc, eff, decs, hozs, incs, effs, itype)
            # if name:
            #    print('Written to file: ' + name)

    input_file.close()
