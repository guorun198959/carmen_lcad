import os

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from datetime import datetime
import os.path
import sys
import time
import glob    

import numpy as np
from six.moves import xrange
import tensorflow as tf
from PIL import Image

from config import *
from imdb import kitti
from utils.util import *
from nets import *

FLAGS = tf.app.flags.FLAGS

tf.app.flags.DEFINE_string(
        'checkpoint', './data/SqueezeSegV2/model.ckpt-30700',
        """Path to the model parameter file.""")
tf.app.flags.DEFINE_string(
        'input_path', './data/samples/*',
        """Input lidar scan to be detected. Can process glob input such as """
        """./data/samples/*.npy or single input.""")
tf.app.flags.DEFINE_string(
        'out_dir', './data/samples_out/', """Directory to dump output.""")
tf.app.flags.DEFINE_string('gpu', '0', """gpu id.""")

def _normalize(x):
  return (x - x.min())/(x.max() - x.min())

def squeeze_seg_process_point_cloud(carmen_lidar_point_cloud):

  os.environ['CUDA_VISIBLE_DEVICES'] = FLAGS.gpu

  with tf.Graph().as_default():
    mc = kitti_squeezeSeg_config()
    mc.LOAD_PRETRAINED_MODEL = False
    mc.BATCH_SIZE = 1 # TODO(bichen): fix this hard-coded batch size.
    model = SqueezeSeg(mc)

    saver = tf.train.Saver(model.model_params)
    with tf.Session(config=tf.ConfigProto(allow_soft_placement=True)) as sess:
      saver.restore(sess, FLAGS.checkpoint)
      for f in glob.iglob(FLAGS.input_path):
        lidar = np.loadtxt(f, delimiter = '\t')
        print (lidar.shape)
        lidar = lidar.reshape((mc.ZENITH_LEVEL,mc.AZIMUTH_LEVEL,5))
        # print (lidar.shape)
        # lidar = np.load(f).astype(np.float32, copy=False)[:, :, :5]
        # save_txt(lidar, f)
        lidar_mask = np.reshape(
            (lidar[:, :, 4] > 0),
            [mc.ZENITH_LEVEL, mc.AZIMUTH_LEVEL, 1]
        )
        print(lidar_mask.shape)
        lidar = (lidar - mc.INPUT_MEAN)/mc.INPUT_STD
        lidar = np.append(lidar, lidar_mask, axis=2)
        pred_cls = sess.run(
            model.pred_cls,
            feed_dict={
                model.lidar_input:[lidar],
                model.keep_prob: 1.0,
                model.lidar_mask:[lidar_mask]
            }
        )

        return pred_cls

        # save the data
#        file_name = f.strip('.npy').split('/')[-1]
        # np.save(
        #     os.path.join(FLAGS.out_dir, 'pred_'+file_name+'.npy'),
        #     pred_cls[0]
        # )
        #np.savetxt('foo'+file_name+'.csv', pred_cls[0].shape, delimiter=",")

        # save the plot
#        depth_map = Image.fromarray(
#            (255 * _normalize(lidar[:, :, 3])).astype(np.uint8))
#        depth_map.save(
#            os.path.join(FLAGS.out_dir, 'in_'+file_name+'.png'))

#        label_map = Image.fromarray(
#            (255 * visualize_seg(pred_cls, mc)[0]).astype(np.uint8))

#        blend_map = Image.blend(
#            depth_map.convert('RGBA'),
#            label_map.convert('RGBA'),
#            alpha=0.4
#        )

#        blend_map.save(
#            os.path.join(FLAGS.out_dir, 'out_'+file_name+'.png'))


#def main(argv=None):
#  if not tf.gfile.Exists(FLAGS.out_dir):
#    tf.gfile.MakeDirs(FLAGS.out_dir)
#  detect()
#  print('Detection output written to {}'.format(FLAGS.out_dir))

#if __name__ == '__main__':
#    tf.app.run()
