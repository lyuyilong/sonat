"""Test script for module :mod:`pyarm.stack`
"""
import os
import sys
import numpy as N
import MV2

from util import (LOGGER, assert_allclose, create_mv2_gridder_xyzt,
    create_mv2_scattered_xyzt)

from pyarm.stack import Stacker


def test_stack_mv2_with_record():

    # Fake data
    # - first array
    nt = 5
    data0 = create_mv2_gridder_xyzt(nt=nt, rotate=30)
    data0[:, :, 3:5, 2:4] = MV2.masked
    raxis = data0.getTime()
    del raxis.axis
    del raxis.units
    raxis.id = 'member'
    # - second array
    data1 = create_mv2_gridder_xyzt(rotate=0, nx=10, ny=9, nz=4)
    data1[:, :, 5:7, 6:7] = MV2.masked
    data1.setAxis(0, raxis)

    # Stack
    stacker = Stacker([data0, data1], nordim=False, logger=LOGGER)

    # Unstack
    unstacked0, unstacked1 = stacker.unstack(stacker.stacked_data)
    unstacked0b, unstacked1b = stacker.unstack(stacker.stacked_data[:, :nt/2])

    # Restack
    restacked = stacker.restack([data0, data1])

    # Checks
    assert_allclose(stacker.stacked_data.shape,
        ((~data0[0].mask).sum()+(~data1[0].mask).sum(), data0.shape[0]))
    assert_allclose(unstacked0, data0)
    assert_allclose(unstacked1, data1)
    assert_allclose(unstacked0[:nt/2], unstacked0b)
    assert_allclose(unstacked1[:nt/2], unstacked1b)
    assert_allclose(restacked, stacker.stacked_data)

    return stacker

def test_stack_mv2_scattered_without_record_fixed_norm():

    # Fake data
    # - first array
    norm0 = 20.
    lons, lats, data0 = create_mv2_scattered_xyzt(nt=0)
    data0[:, 3:5] = MV2.masked
    # - second array
    norm1 = 8.
    lons, lats, data1 = create_mv2_scattered_xyzt(nt=0, np=20, nz=0)
    data1[10:12] = MV2.masked

    # Stack: fixed norm, no record dim, no anomaly
    stacker = Stacker([data0, data1], norms=[norm0, norm1], nordim=True,
        mean=False, logger=LOGGER)

    # Unstack
    unstacked0, unstacked1 = stacker.unstack(stacker.stacked_data)

    # Restack
    restacked = stacker.restack([data0, data1])

    # Checks
    assert_allclose(stacker.stacked_data.shape,
        ((~data0.mask).sum()+(~data1.mask).sum(),))
    assert_allclose(stacker.stacked_data,
        N.concatenate((data0.compressed()/norm0, data1.compressed()/norm1)))
    assert_allclose(unstacked0, data0)
    assert_allclose(unstacked1, data1)
    assert_allclose(restacked, stacker.stacked_data)

    return stacker

if __name__=='__main__':
    test_stack_mv2_with_record()
    test_stack_mv2_scattered_without_record_fixed_norm()
