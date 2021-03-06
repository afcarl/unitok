#!/usr/bin/env python3
import argparse
import sys
import codecs
if sys.version_info[0] == 2:
  from itertools import izip
else:
  izip = zip
from collections import defaultdict as dd
import re
import os.path
import gzip
import unicodedata as ud
import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.cluster import MiniBatchKMeans, KMeans
import collections
import itertools
import pickle
import hierkmeanscluster as hkmc
from hierkmeanscluster import ModelTree

scriptdir = os.path.dirname(os.path.abspath(__file__))


reader = codecs.getreader('utf8')
writer = codecs.getwriter('utf8')

def prepfile(fh, code):
  ret = gzip.open(fh.name, code) if fh.name.endswith(".gz") else fh
  if sys.version_info[0] == 2:
    if code.startswith('r'):
      ret = reader(fh)
    elif code.startswith('w'):
      ret = writer(fh)
    else:
      sys.stderr.write("I didn't understand code "+code+"\n")
      sys.exit(1)
  return ret


def main():
  parser = argparse.ArgumentParser(description="replace hierarchy labels with hand labels, if present",
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("--infile", "-i", nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="input classified file")
  parser.add_argument("--modelfile", "-m", nargs='?', type=argparse.FileType('rb'), default=sys.stdin, help="input model file")
  parser.add_argument("--outfile", "-o", nargs='?', type=argparse.FileType('w'), default=sys.stdout, help="output file")
  parser.add_argument("--debug", "-d", action='store_true', default=False, help="debug mode")


  try:
    args = parser.parse_args()
  except IOError as msg:
    parser.error(str(msg))

  infile = prepfile(args.infile, 'r')
  modelfile = prepfile(args.modelfile, 'rb')
  outfile = prepfile(args.outfile, 'w')

  fullmodel = pickle.load(modelfile)

  features, tokfeatures = hkmc.prepfeatures(fullmodel['settings'])

  for line in infile:
    ln, cn, codestr = line.strip().split('\t')
    codes = codestr.split('.')
    model = fullmodel['model']
    label = None
    for code in codes:
      if model.handlabel is not None and model.handlabel != "r":
        label = model.handlabel
        break
      else:
        model = model.children[int(code)]
    if label is None:
      label = codestr
    outfile.write('\t'.join((ln, cn, label))+"\n")

if __name__ == '__main__':
  main()

