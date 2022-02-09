##
## maxi.py -- Library of classes and convenience functions for playing
## with maxi data.
##
## 2022.02.09 - liac@umich.edu
##--------------------------------------------------------------------

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import ascii

CAL_THRESH = 10.0

class MaxiData(object):
    def __init__(self, filename):
        data = ascii.read(filename)
        self.mjd   = data['col1'] # MJD of observation
        self.total = data['col2'] # 2-20 keV flux (phot/cm^2/s)
        self.soft  = data['col4'] # 2-4 keV
        self.med   = data['col6'] # 4-10 keV
        self.hard  = data['col8'] # 10-20 keV
        self.yunit = 'flux (phot/cm$^2$/s)'
        self.calibrated = False

    def plot(self, ax, band='total', **kwargs):
        assert band in ['total','soft','med','hard']
        ax.set_xlabel('MJD')
        if band == 'total':
            ax.plot(self.mjd, self.total, **kwargs)
            ax.set_ylabel('2-20 keV {}'.format(self.yunit))
        if band == 'soft':
            ax.plot(self.mjd, self.soft, **kwargs)
            ax.set_ylabel('2-4 keV {}'.format(self.yunit))
        if band == 'med':
            ax.plot(self.mjd, self.med, **kwargs)
            ax.set_ylabel('4-10 keV {}'.format(self.yunit))
        if band == 'hard':
            ax.plot(self.mjd, self.hard, **kwargs)
            ax.set_ylabel('10-20 keV {}'.format(self.yunit))

    def calibrate(self, cal_file="data/Crab_lc_1day_all.dat", thresh=CAL_THRESH):
        cal_data = MaxiData(cal_file)

        # identify outliers in the calibration lc
        def id_outliers(yvals, thresh=thresh):
            return np.abs(yvals - np.median(yvals)) < (thresh * np.std(yvals))

        if not self.calibrated:
            ii = id_outliers(cal_data.total)
            cal_total = self.total / np.interp(self.mjd, cal_data.mjd[ii], cal_data.total[ii])

            ii = id_outliers(cal_data.soft)
            cal_soft = self.total / np.interp(self.mjd, cal_data.mjd[ii], cal_data.soft[ii])

            ii = id_outliers(cal_data.med)
            cal_med = self.total / np.interp(self.mjd, cal_data.mjd[ii], cal_data.med[ii])

            ii = id_outliers(cal_data.hard)
            cal_hard = self.total / np.interp(self.mjd, cal_data.mjd[ii], cal_data.hard[ii])

            self.total = cal_total
            self.soft  = cal_soft
            self.med   = cal_med
            self.hard  = cal_hard
            self.calibrated = True
            self.yunit = 'flux (Crab)'
        else:
            print("This light curve has already been calibrated.")
