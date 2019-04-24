
import os
import cv2
import sys
import numpy as np

def save_complete_map(tiles_dir, output_image_path):
    
    all_imgs = [f for f in os.listdir(tiles_dir) if f[-3:] == 'png']
    tag = all_imgs[0].rsplit('_')[0]
    
    origins = np.array([f.replace('.png', '').rsplit('_')[1:3] for f in all_imgs]).astype(np.float)
    min_w, max_w = np.min(origins[:, 0]), np.max(origins[:, 0])
    min_h, max_h = np.min(origins[:, 1]), np.max(origins[:, 1])

    concated = []
    for h in np.arange(min_h, max_h+50, 50):
        imgs = []
        for w in np.arange(min_w, max_w+50, 50):
            name = tiles_dir + '/%s_%f_%f.png' % (tag, w, h)
            if os.path.exists(name):
                imgs.append(cv2.imread(name))
            else:
                imgs.append(np.ones((500, 500, 3)) * 128)
        concated.append(np.concatenate(imgs, axis=1))
        
    final_map = np.concatenate(concated, axis=0)
    final_map = cv2.flip(final_map, 0)
    cv2.imwrite(output_image_path, final_map)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Use python %s <tiles dir> <image_path>" % sys.argv[0])
    else:
        save_complete_map(sys.argv[1], sys.argv[2])



