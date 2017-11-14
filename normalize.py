#!/usr/bin/env python 

from sys import argv, stdout 
from os import getenv, system 
from glob import glob 
import numpy as np 
from NH1 import NH1
import json 

infiles = argv[1]
fbasepath = argv[2]
basedir = '/'.join(fbasepath.split('/')[:-1]) 
print '|-',argv[1]
print '|--->',fbasepath
argv = []

branches = { }
bins = { }
cats = ['inclusive', 'singletons', 'parton']
for cat in cats:
    fcat = open(getenv('CMSSW_BASE')+'/src/conversion/txt/'+cat+'.txt')
    branches[cat] = []
    bins[cat] = {}
    for x in fcat.readlines():
        xx = map(lambda a : a.strip(), x.split(':'))
        branches[cat].append(xx[0])
        try:
            bins[cat][xx[0]] = [np.float64(xxx) for xxx in xx[1].split(',')]
        except IndexError:
            pass 
    fcat.close()

hists = {}
sumw = {}
for cat, branches_ in branches.iteritems():
    hists[cat] = {}
    sumw[cat] = {}
    for branch in branches_:
        if branch not in bins[cat]:
            continue 
        lo, hi = bins[cat][branch]
        width = (hi-lo)/100.
        hists[cat][branch] = NH1(np.arange(lo,hi+width,width))
        sumw[cat][branch] = np.float64(0)

fptweight = fbasepath + '_ptweight_scaled.npy'
pt_weight = NH1(); pt_weight.load(fptweight)
idx_pt = branches['singletons'].index('pt')

for cat in cats:
    valid = [x in hists[cat] for x in branches[cat]]
    if not any(valid):
        continue # no branches to normalize in this category
    dim = 1 if cat=='singletons' else 2 
    files = glob(infiles.replace('XXXX', cat))
    nb = len(branches[cat])
    nfiles = len(files)
    ifiles = 0
    for fpath in files:
        if ifiles%10 == 0:
            print 'Processing %i/%i\r'%(ifiles,nfiles),
            stdout.flush()
        ifiles += 1
        arr = np.load(fpath)
        pt_arr = np.load(fpath.replace(cat,'singletons'))[:,idx_pt]
        w = pt_weight.eval_array(pt_arr)
        for ib in xrange(nb):
            bname = branches[cat][ib]
            if bname not in hists[cat]:
                continue 
            if dim == 1:
                xarr = arr[:,ib]
                warr = w
            else:
                xarr = arr[:,:,ib]
                warr = np.array([w for _ in xrange(xarr.shape[1])])
                xarr = xarr.flatten()
                warr = warr.flatten()
            assert(warr.shape == xarr.shape)
            hists[cat][bname].fill_array(xarr, warr)
            sumw[cat][branch] += np.sum(warr)


dumps = {cat : [] for cat in cats}
for cat in cats:
    for branch in branches[cat]:
        if branch not in hists[cat]:
            continue
        hist = hists[cat][branch]
        dumps[cat].append({
                'branch' : branch, 
                'mean'   : hist.mean(),
                'stdev'  : hist.stdev(sheppard=True),
                'median' : hist.median(),
                'width'  : 0.5 * (hist.quantile(0.68) - hist.quantile(0.32))
            })

for cat in cats:
    json.dump(dumps[cat], open(fbasepath+'_'+cat+'.json','w'), indent=2)
