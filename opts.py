"""Desiding whether need to Calibrate or not through otps. Default is set to True
 """
import argparse

def get_opts():
    parser = argparse.ArgumentParser(description='Colony Picking')
    parser.add_argument('--Calibrate', type=bool, default=True,help="Wheter to use a empty plate image to calibrate or not")
    opts = parser.parse_args()
    return opts