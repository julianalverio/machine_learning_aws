'''
conda create -n arbitrary_environment_name tensorflow-gpu=1.8
pip install pandas==0.19.2
pip install ggplot
pip install joblib
pip install nltk
pip install sklearn
pip install gensim
pip install h5py
conda install keras-gpu
'''


from ggplot import *
from itertools import product
from joblib import Parallel, delayed
from keras import backend as K
from keras import models
from keras import optimizers
from keras import regularizers
from keras.applications import ResNet50
from keras.applications.resnet50 import preprocess_input
from keras.applications.vgg19 import VGG19
from keras.callbacks import History 
from keras.layers import Conv2D, MaxPooling2D, GlobalAveragePooling2D
from keras.layers import Conv2D, MaxPooling2D, GlobalAveragePooling2D, BatchNormalization
from keras.layers import Dense, Activation, Flatten, Dropout
from keras.layers import Dense, Activation, Flatten, Dropout, Input
from keras.layers import Embedding, Flatten, Dense
from keras.layers import Input, Dense, Reshape, merge, Flatten, Concatenate, Activation, Multiply
from keras.layers import SimpleRNN
from keras.layers.embeddings import Embedding
from keras.layers.merge import Dot
from keras.layers.merge import dot
from keras.models import Model
from keras.models import Sequential
from keras.models import model_from_json
from keras.preprocessing import image
from keras.preprocessing import sequence
from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.sequence import skipgrams
from keras.preprocessing.text import Tokenizer
from keras.utils import np_utils
from nltk import PorterStemmer
from nltk import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import ToktokTokenizer
from nltk.tokenize import word_tokenize
from numpy import split
from numpy.random import permutation
from pathlib import Path
from scipy.ndimage import rotate
from sklearn import model_selection
from sklearn import utils
from sklearn.decomposition import PCA
from sklearn.decomposition import TruncatedSVD
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble.partial_dependence import partial_dependence
from sklearn.ensemble.partial_dependence import plot_partial_dependence
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import SGDClassifier
from sklearn.manifold import TSNE
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import roc_auc_score
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_predict
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.utils.multiclass import unique_labels
import collections
import csv
import gensim
import h5py
import matplotlib
import matplotlib.pyplot as plt
import multiprocessing
import numpy as np
import os
import pandas as pd
import pylab as pl
import random
import re
import scipy.stats as st
import string
import tensorflow as tf
import time
import warnings
