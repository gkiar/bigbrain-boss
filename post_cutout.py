import os
import sys
import numpy as np 
import requests
import argparse
from PIL import Image 

from intern.remote.boss import BossRemote
from intern.resource.boss.resource import * 
from requests import HTTPError 

rmt = BossRemote('neurodata.cfg')

class SynaptomesBoss:
    def __init__(self, collection, experiment, channel, resolution):
        self.collection = collection 
        self.experiment = experiment
        self.channel = channel
        self.res = resolution

        # Note: An annotation channel must have a source channel. For now we use a blank channel called "image".
        chan_setup = ChannelResource(self.channel, self.collection, self.experiment, 'image', '', datatype='uint8')
        try:
            self.chan_actual = rmt.get_project(chan_setup)
        except HTTPError:
            self.chan_actual = rmt.create_project(chan_setup)
    def post(self, data, x_rng, y_rng, z_rng):
        try:
            rmt.create_cutout(self.chan_actual, self.res, x_rng, y_rng, z_rng, data)
        except Exception as e:
            print("Error: ")
            print(e)

def main():
    parser = argparse.ArgumentParser('Post tiff stack to the boss')
    parser.add_argument('imdir', type=str, help='Directory of PNGs')
    parser.add_argument('collection', type=str, help='BOSS Collection')
    parser.add_argument('experiment', type=str, help='BOSS Experiment')
    parser.add_argument('channel', type=str, help='BOSS Channel')
    parser.add_argument('--x', type=int, nargs=2, help='X range')
    parser.add_argument('--y', type=int, nargs=2, help='Y range')
    parser.add_argument('--z', type=int, nargs=2, help='Z range')
    parser.add_argument('--res', type=int, default=0,
		        help='Resolution at which we post data.')
    parser.add_argument('--sixteen', '-s', action="store_true",
                        help='16 stacks in Z or nah')
    parser.add_argument('--debug', '-d', action="store_true",
                        help='debugging or nah')

    result = parser.parse_args()

    synboss = SynaptomesBoss(result.collection, result.experiment,
		             result.channel, result.res)

    file_format = "pm%04do.png"
    f_imgs = os.listdir(result.imdir)
    zmin = int(result.z[0])
    zmax = int(result.z[1])
    zstart = 1 # In BigBrain, Z starts at 1
    zstart = zmin - zmin % 16 + zstart
    x = int(result.x[1])
    y = int(result.y[1])
    debug = result.debug

    if not result.sixteen:
        # Naively uploads a single slice at a time
        for f_im in f_imgs:
            # Get slice number....
            z = int(f_im.split('pm')[1].split('o')[0])
            if z < zmin or z >= zmax:
                continue; # Skip file if out-of-bounds

            # Load in-bounds slices, ensure 3D and contiguous
            im = Image.open(os.path.join(result.imdir, f_im))
            tmp_im = np.asarray(im)[:, :, np.newaxis]
            imarr = np.ascontiguousarray(tmp_im)
            print("Shape: {},{},{}".format(*imarr.shape))
            print("Shape: {}:{},{}:{},{}:{}".format(result.x[0], result.x[1],
                                                    result.y[0], result.y[1],
                                                    z, z+1))
            # Upload slice
            synboss.post(imarr, result.x, result.y, [z, z+1])
            print("Uploaded z={}".format(z))

    else:
#         print("Don't use this mode... current error:")
#         error = """
#         Input buffer size cannot exceed 2147483631 bytes
#         Error:
#         <built-in function compress> returned NULL without setting an error
#         """
#         print(error)
#         return -1 

        # Uploads 16 slices at a time
        # Move from image origin (assumed to be 0) up in steps of 16
        for z in np.arange(zstart, zmax, 16):
            # Initialize empty 16-slice matrix
            bigim = np.zeros((x-1, y-1, 16), dtype=np.dtype('uint16'))
            # Look at each slice in the 16
            for idx, slic in enumerate(np.arange(z, z+16)):
                fhandle = file_format % slic
                if slic >= zmax:
                    break; # Stop if we're over max
                elif slic < zmin:
                    continue; # Try next if we're under min

                if debug:
                    break;
                # Verify file exists
                if fhandle in f_imgs:
                    # Load in-bounds slice
                    tmp_im = Image.open(os.path.join(result.imdir, fhandle))
                    bigim[:, :, idx] = np.asarray(tmp_im).T
                    print("Loaded Image={}".format(fhandle))
                else:
                    raise(IndexError, "Image within z-range not found: {}".format(fhandle))

            cutx = np.arange(0, bigim.shape[0]+1024, 1024)
            cuty = np.arange(0, bigim.shape[1]+1024, 1024)
            cutx[-1] = np.min((cutx[-1], bigim.shape[0]))
            cuty[-1] = np.min((cuty[-1], bigim.shape[1]))

            for ix, x_ in enumerate(cutx[:-1]):
                for iy, y_ in enumerate(cuty[:-1]):
                    xl1 = cutx[ix]
                    xl2 = cutx[ix+1]
                    yl1 = cuty[iy]
                    yl2 = cuty[iy+1]

                    im = bigim[xl1:xl2, yl1:yl2, :]
                    print("Shape: {},{},{}".format(*im.shape))
                    print("Uploading: {}:{}, {}:{}, {}:{}".format(xl1, xl2,
                                                                  yl1, yl2,
                                                                  z, z+16))
                    print("D-type: {}".format(im.dtype))
                    # Ensure array is contiguous, upload slices
                    if not debug:
                        imarr = np.ascontiguousarray(im)
                        synboss.post(imarr, [xl1, xl2], [yl1, yl2], [z, z+16])


if __name__ == '__main__':
    main()
