#!/usr/bin/env python

# make_tiles.py
# Created by Greg Kiar on 2017-06-14.
# Email: gkiar07@gmail.com
# Copyright (c) 2017. All rights reserved.

from argparse import ArgumentParser
from PIL import Image
import numpy as np
import os


def ims_to_tiles(indir, outdir, N=3584, M=3072):
    f_ims = os.listdir(indir)

    for f_im in f_ims:
        im = Image.open(os.path.join(indir, f_im))
        xs = list(np.arange(0, im.size[0], N)) + [im.size[0]]
        ys = list(np.arange(0, im.size[1], M)) + [im.size[1]]

        print "Image: {}".format(f_im)
        print "Image size: {}".format(im.size)
        for idx1 in range(len(xs)-1):
            for idx2 in range(len(ys)-1):
                tup = (xs[idx1],   ys[idx2],
                       xs[idx1+1], ys[idx2+1])
                # print "Cropped ({},{}): {}".format(idx1, idx2,
                #                                    im.crop(tup).size)
                tim = im.crop(tup)
                fname = "{}_x{}_y{}.png".format(f_im.split('.')[0], idx1, idx2)
                tim.save(os.path.join(outdir, fname), format='png')


def main():
    parser = ArgumentParser(description="Turns large slices into ingestible"
                            " tiles")
    parser.add_argument("indir", action="store", help="")
    parser.add_argument("outdir", action="store", help="")
    result = parser.parse_args()

    ims_to_tiles(result.indir, result.outdir)

if __name__ == "__main__":
    main()
