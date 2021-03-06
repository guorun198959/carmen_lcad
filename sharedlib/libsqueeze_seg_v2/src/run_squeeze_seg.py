from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from datetime import datetime

#Activating virtualenv
import os

def activate_virtual_environment(environment_root):
    """Configures the virtual environment starting at ``environment_root``."""
    activate_script = os.path.join(
        environment_root, 'bin', 'activate_this.py')
    execfile(activate_script, {'__file__': activate_script})

carmen_home = os.getenv("CARMEN_HOME")
virtualenv_root = carmen_home + "/sharedlib/libsqueeze_seg_v2/squeezeseg_env"
activate_virtual_environment(virtualenv_root)
#virtualenv activated

import os.path
import sys
import time
import glob
import cv2

import numpy as np
from six.moves import xrange
import tensorflow as tf
from PIL import Image

from config import *
from imdb import kitti
from utils.util import *
from nets import *
from setuptools.sandbox import ExceptionSaver
from IN import MCAST_BLOCK_SOURCE

os.environ['CUDA_VISIBLE_DEVICES'] =''

'''Defining global variables'''
global mc
global model
global sess
global zenith_resolution

'''Initialize tensorflow and model within specific vertical resolution and number shots to squeeze'''
def initialize(vertical_resolution, shots_to_squeeze):
    global mc
    global model
    global sess
    global zenith_resolution
    '''Loads squeezeseg config and changes the zenith and azimuth level'''
    mc = kitti_squeezeSeg_config()
    zenith_resolution = vertical_resolution
    mc.ZENITH_LEVEL = vertical_resolution
    #mc.AZIMUTH_LEVEL = shots_to_squeeze
 
    mc.LOAD_PRETRAINED_MODEL = False
    mc.BATCH_SIZE = 1
    model = SqueezeSeg(mc)
     
    '''Loads tensorflow'''
    tf.Graph().as_default()
    sess = tf.Session(config=tf.ConfigProto(allow_soft_placement=True))
    saver = tf.train.Saver(model.model_params)
    saver.restore(sess, os.getenv("CARMEN_HOME") + '/sharedlib/libsqueeze_seg_v2/data/SqueezeSegV2/model.ckpt-30700')  
     
    print ("\n\n-------------------------------------------------------")
    print ("       Pretrained Model and Tensorflow loaded!")
    print ("-------------------------------------------------------\n\n")


def _normalize(x):
    return (x - x.min())/(x.max() - x.min())

def save_txt(data, file_name, tag):
  # Write the array to disk
  with open(os.path.join(os.getenv("CARMEN_HOME") + '/sharedlib/libsqueeze_seg_v2/data/samples_IARA/', file_name+ tag +'.txt'), 'w') as outfile:
    # I'm writing a header here just for the sake of readability
    # Any line starting with "#" will be ignored by numpy.loadtxt
    outfile.write('# Array shape: {0}\n'.format(data.shape))

    # Iterating through a ndimensional array produces slices along
    # the last axis. This is equivalent to data[i,:,:] in this case
    for data_slice in data:

        # The formatting string indicates that I'm writing out
        # the values in left-justified columns 7 characters in width
        # with 2 decimal places.  
        np.savetxt(outfile, data_slice, fmt='%-7.2f', delimiter='\t')

        # Writing out a break to indicate different slices...
        outfile.write('# New slice\n')
        
def save_lidar_image(img_file, timestamp, tag):
    lidar_save = Image.fromarray(img_file).convert('RGBA')
    lidar_save.save(os.path.join(os.getenv("CARMEN_HOME") + '/sharedlib/libsqueeze_seg_v2/data/samples_out/', str(timestamp.item(0)) + tag + '.png'))

def generate_lidar_images(lidar, pred_cls):
    global mc
    alpha = 0.4
    beta = (1.0 - alpha)
    src1 = (255 * _normalize(lidar[:, :, 3])).astype(np.uint8)
    src2 = (255 * visualize_seg(pred_cls, mc)[0]).astype(np.uint8)
    dst = np.uint8(alpha*(src1[:,:,None])+beta*(src2))
    arr = np.zeros_like(dst)
    arr[:,:,0] = src1[:,:]
    arr[:,:,1] = src1[:,:]
    arr[:,:,2] = src1[:,:]
    img = np.concatenate((arr, dst), axis=0)
    #resize img
    scale_percent = 200 # percent of original size
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100) * 2
    dim = (width, height)
    resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
    return resized

def run_model(lidar):
    global mc
    global model
    global sess
    lidar_mask = np.reshape(
        (lidar[:, :, 4] > 0),
        [mc.ZENITH_LEVEL, mc.AZIMUTH_LEVEL, 1]
    )
    lidar = (lidar - mc.INPUT_MEAN)/mc.INPUT_STD
    lidar = np.append(lidar, lidar_mask, axis=2)
    pred_cls = sess.run(
        model.pred_cls,
        feed_dict={
            model.lidar_input: [lidar],
            model.keep_prob: 1.0,
            model.lidar_mask: [lidar_mask]
        }
    )
    return pred_cls

def vertical_interpolation(lidar):
    s = (lidar.shape[0]*2, lidar.shape[1], lidar.shape[2])
    lidar_new = np.zeros(s, dtype=np.int64)
    i = 0
    for x in range(lidar.shape[0]-1):
        first_set = lidar[x,:,:]
        second_set = lidar[x+1,:,:]
        middle_set = (first_set + second_set) / 2.0
        lidar_new[i] = first_set
        lidar_new[i+1] = middle_set
        lidar_new[i+2] = second_set
        i = i + 2
    return lidar_new

def vertical_doubled(lidar):
    s = (lidar.shape[0]*2, lidar.shape[1], lidar.shape[2])
    lidar_new = np.zeros(s, dtype=np.int64)
    i = 0
    for x in range(lidar.shape[0]-1):
        first_set = lidar[x,:,:]
        second_set = lidar[x+1,:,:]
        lidar_new[i] = first_set
        lidar_new[i+1] = first_set
        lidar_new[i+2] = second_set
        i = i + 2
    return lidar_new

def vertical_desinterpolation(lidar):
    s = (lidar.shape[0], lidar.shape[1]//2, lidar.shape[2])
    lidar_new = np.zeros(s, dtype=np.int64)
    for x in range(lidar_new.shape[1]):
        lidar_new[:,x] = lidar[:,x*2]
    return lidar_new

def horizontal_interpolation(lidar):
    s = (lidar.shape[0], lidar.shape[1]*2, lidar.shape[2])
    s2 = (1, 5)
    lidar_new = np.zeros(s, dtype=np.int64)
    line = np.zeros(s2, dtype=np.int64)
    #print(lidar_new.shape)
    for x in range(lidar.shape[0]):
        first_line = lidar[x,:,:]
        sum_line = lidar[x,1:,:]
        horizontal_line = np.concatenate((sum_line, line),axis=0)
        mean = (first_line + horizontal_line)/2.0
        i = 0
        for y in range(lidar.shape[1]):
            lidar_new[x][i] = first_line[y]
            lidar_new[x][i+1] = mean[y]
            i = i + 2
    #print(lidar_new.shape)
    return lidar_new

def horizontal_desinterpolation(lidar):
    s = (lidar.shape[0], lidar.shape[1], lidar.shape[2]//2)
    lidar_new = np.zeros(s, dtype=np.int64)
    for x in range(lidar_new.shape[1]):
        lidar_new[:,:,x] = lidar[:,:,x*2]
    return lidar_new

def squeeze_seg_process_point_cloud_interpolations(lidar, timestamp):
    tag = "_VerticalHorizontalInterpolation"
    save_txt(lidar, str(timestamp.item(0)), tag)
    #lidar1 = lidar[:,271:783,:]
    lidar_interpolated = vertical_interpolation(lidar)
    lidar_horizontal = horizontal_interpolation(lidar_interpolated)
    #lidar1 = lidar_interpolated[:,271:783,:]
    lidar1 = lidar_horizontal[:,798:1310,:]
    
    #lidar1 = scipy.ndimage.zoom(x, 0.5)
    print("lidar1.shape={}".format(
        lidar1.shape))
    pred_cls_lidar1 = run_model(lidar1)
    img_lidar1 = generate_lidar_images(lidar1,pred_cls_lidar1)
    save_lidar_image(img_lidar1, timestamp, tag)
    cv2.imshow("Slice doubling", img_lidar1)
    cv2.waitKey(100)
    return pred_cls_lidar1

def squeeze_seg_process_point_cloud(lidar, timestamp):
    #save_txt(lidar, str(timestamp.item(0)), "")
    lidar1 = lidar[:,288:800,:]
    lidarp1 = lidar[:,826:,:]
    shape_last_part = lidar.shape[1] - 826
    shape_to_complete = mc.AZIMUTH_LEVEL - shape_last_part
    lidarp2 = lidar[:,:shape_to_complete,:]
    lidar2 = np.concatenate((lidarp1, lidarp2),axis=1)
    
    pred_cls_lidar1 = run_model(lidar1)
    pred_cls_lidar2 = run_model(lidar2)
    
    #img_lidar1 = generate_lidar_images(lidar1,pred_cls_lidar1)
    #img_lidar2 = generate_lidar_images(lidar2,pred_cls_lidar2)
     
    #cv2.imshow("Front View", img_lidar1)
    #cv2.imshow("Rear View", img_lidar2)
    #cv2.waitKey(100)
    #save_lidar_image(img_lidar1, timestamp, tag)
    #save_lidar_image(img_lidar2, timestamp, "_r")
    
    s = (zenith_resolution, 26)
    lidar_test_1 = np.zeros(s, dtype=np.int64)
    s2 = (zenith_resolution, (288-shape_to_complete))
    lidar_test_2 = np.zeros(s2, dtype=np.int64)
    pred_cls = np.concatenate((pred_cls_lidar2[0][:,shape_last_part:],lidar_test_2,pred_cls_lidar1[0], lidar_test_1, pred_cls_lidar2[0][:,:shape_last_part]), axis=1)
    #print("pred_cls.shape={}".format(
    #    pred_cls.shape)) 
    return pred_cls

