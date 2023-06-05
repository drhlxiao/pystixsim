#!/usr/bin/env python
# coding: utf-8

import sys
import matplotlib.pyplot as plt
from core.stix_imager import StixImager


def main():

    det_idx, sun_x, sun_y, user_phase_front, user_rot_deg_front, user_phase_rear, user_rot_deg_rear, compute_pattern = (
        25, 0, 0, 0, 0, 0, 0, True)

    im = StixImager(det_idx)
    im.create(sun_x, sun_y, user_phase_front, user_rot_deg_front,
              user_phase_rear, user_rot_deg_rear, compute_pattern)
    fig, ax, ax2, ax3, ax4 = im.plot()
    plt.show()


if __name__ == '__main__':
    if sys.argv == 1:
        print('sim det')
    else:
        main()
