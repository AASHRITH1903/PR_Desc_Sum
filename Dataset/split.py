import sys
sys.path.append('.')
sys.path.append('..')

import random
import Constants


filenames = open('data.txt').readlines()
random.shuffle(filenames)

fns_train = filenames[:Constants.TRAIN_SIZE]
fns_valid = filenames[Constants.TRAIN_SIZE:Constants.TRAIN_SIZE+Constants.VALID_SIZE]
fns_test = filenames[Constants.TRAIN_SIZE+Constants.VALID_SIZE:Constants.TRAIN_SIZE+Constants.VALID_SIZE+Constants.TEST_SIZE]

open('data_train.txt', 'w+').write(''.join(fns_train))
open('data_valid.txt', 'w+').write(''.join(fns_valid))
open('data_test.txt', 'w+').write(''.join(fns_test))