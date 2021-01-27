from charm4py import *
from numba import cuda
import numpy as np
from argparse import ArgumentParser
from enum import Enum
from functools import reduce
import time

class Defaults(Enum):
    GRID_WIDTH = 512,
    GRID_HEIGHT = 512,
    GRID_DEPTH = 512,
    NUM_ITERS = 512,
    WARMUP_ITERS = 10,
    USE_ZEROCOPY = False
    PRINT_ELEMENTS = False


def main(args):
    Defaults.NUM_CHARES = charm.numPes()
    argp = ArgumentParser(description ="Jacobi3D implementation in Charm4Py using "
                          "CUDA and GPU-Direct communication"
                          )
    argp.add_argument('-x', '--grid_width', help = "Grid width",
                      default = Defaults.GRID_WIDTH.value
                      )
    argp.add_argument('-y', '--grid_height', help = "Grid height",
                       default = Defaults.GRID_HEIGHT.value
                       )
    argp.add_argument('-z', '--grid_depth', help = "Grid depth",
                      default = Defaults.GRID_DEPTH.value
                      )
    argp.add_argument('-c', '--num_chares', help = "Number of chares",
                       default = Defaults.NUM_CHARES
                       )
    argp.add_argument('-i', '--iterations', help = "Number of iterations",
                      default = Defaults.NUM_ITERS.value
                      )
    argp.add_argument('-w', '--warmup_iterations', help = "Number of warmup iterations",
                      default = Defaults.WARMUP_ITERS.value
                      )
    argp.add_argument('-d', '--use_zerocopy', action = "store_true",
                      help = "Use zerocopy when performing data transfers",
                      default = Defaults.USE_ZEROCOPY.value
                      )
    argp.add_argument('-p', '--print_blocks', help = "Print blocks",
                      action = "store_true",
                      default = Defaults.PRINT_ELEMENTS.value
                      )
    args = argp.parse_args()

    num_chares_per_dim = calc_num_chares_per_dim(num_chares,
                                                                 grid_width,
                                                                 grid_height,
                                                                 grid_depth
                                                                 )
    n_chares_x, n_chares_y, n_chares_z = num_chares_per_dim

    if reduce(lambda x, y: x*y, n_chares_per_dim) != num_chares:
        print(f"ERROR: Bad grid of chares: {n_chares_x} x {n_chares_y} x "
              f"{n_chares_z} != {num_chares}"
              )
        charm.exit(-1)

    # Calculate block size
    block_width = grid_width // n_chares_x
    block_height = grid_height // n_chares_y
    block_depth = grid_depth // n_chares_z

    # Calculate surf count, sizes
    x_surf_count = block_height * block_depth
    y_surf_count = block_width * block_depth
    z_surf_count = block_width * block_height
    x_surf_size = x_surf_count * np.dtype(np.float64).itemsize
    y_surf_size = y_surf_count * np.dtype(np.float64).itemsize
    z_surf_size = z_surf_count * np.dtype(np.float64).itemsize


    # print configuration
    print("\n[CUDA 3D Jacobi example]n")
    print(f"Grid: {grid_width} x {grid_height} x {grid_depth}, "
          f"Block: {block_width} x {block_height} x {block_depth}, "
          f"Chares: {n_chares_x} x {n_chares_y} x {n_chares_z}, "
          f"Iterations: {n_iters}, Warm-up: {warmup_iters}, "
          f"Zerocopy: {use_zerocopy}, Print: {print_elements}\n\n",
          )


def calc_num_chares_per_dim(num_chares_total, grid_w, grid_h, grid_d):
    n_chares = [0, 0, 0]
    area = [0.0, 0.0, 0.0]
    area[0] = grid_w * grid_h
    area[1] = grid_w * grid_d
    area[2] = grid_h * grid_d

    bestsurf = 2.0 * sum(area)

    ipx = 1

    while ipx <= num_chares:
        if not num_chares % ipx:
            nremain = num_chares // ipx
            ipy = 1

            while ipy <= nremain:
                if not nremain % ipy:
                    ipz = nremain // ipy
                    surf = area[0] / ipx / ipy + area[1] / ipz + area[2] / ipy / ipz

                    if surf < bestsuf:
                        bestsurf = surf
                        n_chares[0] = ipx
                        n_chares[1] = ipy
                        n_chares[2] = ipz
                ipy += 1
        ipx += 1

    return n_chares

# charm.start(main)
if __name__ == '__main__':
    main(None)
