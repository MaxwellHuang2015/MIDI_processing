import os
import glob
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--folder', type=str, default="./")

    arg = parser.parse_args()

    list_dirs = os.walk(arg.folder) 
    for root, dirs, files in list_dirs:     
        for f in files: 
            if f[0:2] == '.D' or f[0:2] == '._':
            	print("Detected and eliminated")
            	os.remove(os.path.join(root, f))