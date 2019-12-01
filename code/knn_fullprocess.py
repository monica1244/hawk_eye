import os 
import os.path as op
import numpy as np
import cv2
import matplotlib.pyplot as plt
from scipy import ndimage

#descriptors
descriptors = ['hog', 'distance_transform']

hog = cv2.HOGDescriptor()

query_path = './pix2pix_code/results/rgb2edge/test_latest/images'
query_files = os.listdir(query_path)
query_files = [op.join(query_path, file) for file in query_files if file[-8:] == 'fake.png'][23]
query_files = [query_files]

database_path = '/home/rohit/Documents/Sem1_Gatech/cv/cv_project/train_augmented_data'
database_folders = ['pan', 'tilt', 'zoom', 'normal']

database_files = []
for folder in database_folders:
    dpath = op.join(database_path, 'train_' + folder)
    files = os.listdir(dpath)
    files = [op.join(dpath, file) for file in files if file[-4:] == '.png' or file[-4:] == '.jpg']
    database_files.append(files)

database_files = sum(database_files, [])

for descriptor in descriptors:
    
    plt.suptitle(descriptor)
    
    for query_file in query_files:
    
        im_query_gray = cv2.imread(query_file, cv2.IMREAD_GRAYSCALE)
        thresh = 127
        query_bw = cv2.threshold(im_query_gray, thresh, 255, cv2.THRESH_BINARY)[1]
        
        best_files = ["" for i in range(5)]
        errors = [100000000 for i in range(5)]

        for i, train_file in enumerate(database_files):
            
            im_gray = cv2.imread(train_file, cv2.IMREAD_GRAYSCALE)
            im_gray = cv2.resize(im_gray, (256, 256))
            thresh = 127
            train_bw = cv2.threshold(im_gray, thresh, 255, cv2.THRESH_BINARY)[1]
            
            if descriptor == 'distance_transform':
                train_feat = ndimage.distance_transform_edt(train_bw)
                query_feat = query_bw
                
                error = 1 / ((np.sum(query_feat * train_feat)) / (np.linalg.norm(query_feat, ord=1)))
                
            elif descriptor == 'hog':
                train_feat = hog.compute(train_bw)
                query_feat = hog.compute(query_bw)
            
                error = np.sum(np.abs(train_feat - query_feat))
                
            print(train_file, error)
            max_curr_error = np.max(errors)
            if error < max_curr_error:
                for k in range(5):
                    if errors[k] == max_curr_error:
                        best_files[k] = train_file
                        errors[k] = error
                        break;
            
        errors = np.array(errors)
        idx = np.argsort(errors)
    
        plt.subplot(3, 2, 1)
        plt.title('query')
        plt.imshow(query_bw, cmap='gray')

        for z in range(5):
            imname = best_files[idx[z]]
            im_gray = cv2.imread(imname, cv2.IMREAD_GRAYSCALE)
            im_gray = cv2.resize(im_gray, (256, 256))
            plt.subplot(3, 2, z + 1 + 1).set_title('Rank' + str(z + 1) + ": " + str(errors[idx[z]]))
            plt.imshow(im_gray, cmap='gray')      
            
        plt.show()