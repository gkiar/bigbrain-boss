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

    result = parser.parse_args()

    synboss = SynaptomesBoss(result.collection, result.experiment,
		             result.channel, result.res)

    file_format = "pm%04do.png"
    f_imgs = os.listdir(result.imdir)
    zmin = int(result.z[0])
    zmax = int(result.z[1])
    zstart = 1 # In BigBrain, Z starts at 1
    x = int(result.x[1])
    y = int(result.y[1])

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
            # Upload slice
            synboss.post(imarr, result.x, result.y, [z, z+1])
            print("Uploaded z={}".format(z))

    else:
        print("Don't use this mode... current error:")
        error = """
        Input buffer size cannot exceed 2147483631 bytes
        Error:
        <built-in function compress> returned NULL without setting an error
        """
        print(error)
        return -1 

        # Uploads 16 slices at a time
        # Move from image origin (assumed to be 0) up in steps of 16
        for z in np.arange(zstart, zmax, 16):
            # Initialize empty 16-slice matrix
            im = np.zeros((x, y, 16))
            # Look at each slice in the 16
            for idx, slic in enumerate(np.arange(z, z+16)):
                fhandle = file_format % slic
                if slic >= zmax:
                    break; # Stop if we're over max
                elif slic < zmin:
                    continue; # Try next if we're under min

                # Verify file exists
                if fhandle in f_imgs:
                    # Load in-bounds slice
                    tmp_im = Image.open(os.path.join(result.imdir, fhandle))
                    im[:, :, idx] = np.asarray(tmp_im).T
                    print("Loaded Image={}".format(fhandle))
                else:
                    raise(IndexError, "Image within z-range not found: {}".format(fhandle))

            # Ensure array is contiguous, upload slices
            imarr = np.ascontiguousarray(im)
            synboss.post(imarr, result.x, result.y, [z, z+16])
            print("Uploaded z={}".format(z))


if __name__ == '__main__':
    main()
