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

    result = parser.parse_args()

    synboss = SynaptomesBoss(result.collection, result.experiment,
		             result.channel, result.res)

    f_imgs = os.listdir(result.imdir)
    for f_im in f_imgs:
        z = int(f_im.split('pm')[1].split('o')[0])
        if z < result.z[0] or z > result.z[1]:
            print("Skipping image (out of range [{}, {}]): {}".format(z[0], z[1], f_im))
            continue
        im = Image.open(os.path.join(result.imdir, f_im))
        tmp_im = np.asarray(im)[:, :, np.newaxis]
        imarr = np.ascontiguousarray(tmp_im)
        synboss.post(imarr, result.x, result.y, [z, z+1])
        print("Uploaded z={}".format(z))

if __name__ == '__main__':
    main()
