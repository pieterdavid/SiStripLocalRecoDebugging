#!/bin/env python
# python imports
import os
import sys
import argparse
import subprocess
import struct
# to prevent pyroot to hijack argparse we need to go around
tmpargv = sys.argv[:]
sys.argv = []
# ROOT setup
import ROOT
from ROOT import TChain, TH1F, TCanvas
ROOT.gROOT.Reset()
ROOT.gROOT.SetBatch()
ROOT.gStyle.SetOptTitle(0)
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.ProcessLine(".x setTDRStyle.C")
ROOT.TGaxis.SetMaxDigits(3)
ROOT.PyConfig.IgnoreCommandLineOptions = True
sys.argv = tmpargv
# Other global setup things
clusterTreePath = "/home/fynu/obondu/scratch/TRK/LocalReco/clusterTrees/"
color = ROOT.TColor()

def get_options():
    parser = argparse.ArgumentParser(description='Create signal to noise plots for a given list of runs and detID, from ClusterTrees')
    parser.add_argument('--runs', action='store', dest='runs', nargs='+',
                        default=[274968],
                        help='list of runs to process')
    parser.add_argument('--detids', action='store', dest='detids', nargs='+',
                        default=[436249541, 436249545, 436249546, 436249549],
                        help='list of detids to process')
    parser.add_argument('--outdir', action='store', dest='outdir',
                        default='TEST', type=str,
                        help='location of the plot output directory')
    parser.add_argument('-n, --nEntries', action='store', dest='nEntries',
                        default=-1, type=int,
                        help='number of entries to process')
    parser.add_argument('--debug', action='store_true', help='More verbose output', dest='debug')
    options = parser.parse_args()
    return options

def main(runs, detids, outdir, debug = False, nEntries = -1):
    print "List all existing trees"
    listAllClusterTrees = {}
    for GR in ['GR16']:
        listAllClusterTrees[GR] = [os.path.join(clusterTreePath, GR, f) for f in os.listdir(os.path.join(clusterTreePath, GR)) if os.path.isfile(os.path.join(clusterTreePath, GR, f)) and 'root' in f] 
    print "done\n"

    print "Prepping histos to be filled"
    c1 = TCanvas()
    plots = {}
    plots['ston'] = {
        'binning' : '(15, 0, 150)',
        'norm': '1',
        'y-max' : 0.8,
        'log-y': True,
    }
    plots['noise'] = {
        'binning': '(100, 0, 50)',
        'norm': '1',
        'log-y': True,
    }
    plots['charge'] = {
        'binning': '(25, 0, 1000)',
        'norm': '1',
        'y-max': 0.4
    }
    plots['width'] = {
        'binning': '(20, 0, 20)',
        'norm': '1',
        'log-y': True,
        'y-max': 2.0,
    }
    plots['qualityisbad'] = {
        'binning': '(2, 0, 2)',
        'norm': '1',
        'y-max': 1.5,
    }
    plots['variance'] = {
        'binning': '(20, 0, 10)',
        'norm': '1',
        'log-y': True,
    }
    plots['seednoise'] = {
        'binning': '(20, 0, 10)',
        'norm': '1',
        'y-max': 1.5,
    }
    plots['seedgain'] = {
        'binning': '(20, 0, 5)',
        'norm': '1',
        'y-max': 1.5,
    }
    plots['seedcharge'] = {
        'binning': '(13, 0, 260)',
        'norm': '1',
        'y-max': 0.3,
    }
    plots['commonMode'] = {
        'binning': '(40, 0, 400)',
        'norm': '1',
        'y-max': 0.7
    }

    h = {}
    for plot in plots:
        h[plot] = {}
#    for detid in detids:
#        h['chargeoverpath'][detid] = TH1F("h_chargeoverpath_detid-%i" % detid, "h_chargeoverpath_detid-%i" % detid, 200, 0, 2000)
#        h['amplitude'][detid] = TH1F("h_amplitude_detid-%i" % detid, "h_amplitude_detid-%i" % detid, 260, 0, 260)
#        h['gainused'][detid] = TH1F("h_gainused_detid-%i" % detid, "h_gainused_detid-%i" % detid, 50, 0.5, 2)
    print "done\n"

    print "Filling", len(runs) * len(detids), "histos, looping over runs", runs, 'and detids', detids
    GR = ""
    clustertree = ""
    for run in runs:
        GR = "GR16"
        clustertree = "testTree/tree"
#        clusterTreeFiles = [x for x in listAllClusterTrees[GR] if ("clusterTree_" + str(run)) in str(x)]
        clusterTreeFiles = listAllClusterTrees[GR]
        # files are of the type /eos/cms/store/group/dpg_tracker_strip/comm_tracker/Strip/Calibration/calibrationtree/GR15/clusterTree_257400_975.root
        if len(clusterTreeFiles) == 0:
            print "There is no available clusterTree for run #%i" % run
            continue
        # pick only the first file, should be enough for our purposes
        chain = TChain(clustertree)
        chain.Add(clusterTreeFiles[0])
        varprefix = 'cluster'
        for iplot, plot in enumerate(plots):
            print '\tDoing histograms for %s (plot %i / %i)' % (plot, iplot+1, len(plots))
            for detid in detids:
                print '\t\tdetid= %i' % detid
                chain.Draw("%s%s>>h_tmp%s" % (varprefix, plot, plots[plot]['binning']), "%sdetid == %i" % (varprefix, detid))
                h[plot][detid] = ROOT.gDirectory.Get("h_tmp")
                h[plot][detid].SetName('h_%s_detid-%i' % (plot, detid))
                h[plot][detid].SetTitle('h_%s_detid-%i' % (plot, detid))
#                c1.Print(outdir + '/test.pdf')
#                c1.Print(outdir + '/test.png')
    print "done\n"

    print "Plotting and saving histos"
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    for plot in h:
        c1.Clear()
        legend = ROOT.TLegend(0.25, 0.72, 0.80, 0.93, "")
        legend.SetFillColor(ROOT.kWhite)
        legend.SetLineColor(ROOT.kWhite)
        legend.SetShadowColor(ROOT.kWhite)
        for idetid, detid in enumerate(detids):
            drawoptions = ''
            if idetid > 0:
                drawoptions = 'same'
            if 'norm' in plots[plot] and plots[plot]['norm'] == '1':
                h[plot][detid].Scale(1. / h[plot][detid].GetEntries())
                h[plot][detid].GetYaxis().SetTitle('norm. to unity')
            if 'y-max' in plots[plot]:
                h[plot][detid].SetMaximum(plots[plot]['y-max'])
            if 'log-y' in plots[plot] and plots[plot]['log-y']:
                c1.SetLogy(1)
            else:
                c1.SetLogy(0)
            h[plot][detid].GetXaxis().SetTitle(plot)
            h[plot][detid].SetLineWidth(2)
            c = color.GetColor(mycolors(idetid, len(detids)))
            h[plot][detid].SetLineColor(c)
            h[plot][detid].SetMarkerColor(c)
            h[plot][detid].Draw(drawoptions)
            legend.AddEntry(h[plot][detid].GetName(), 'detid #%i' % detid, 'l')
            ROOT.gPad.Modified()
            ROOT.gPad.Update()
        # end of loop over clusters
        legend.Draw()
        c1.Print(outdir + '/' + plot + '.png')
        c1.Print(outdir + '/' + plot + '.pdf')
    print "done\n"
# end of main

def mycolors(i, n):
    if n < 6:
        # color palette from https://stanford.edu/~mwaskom/software/seaborn/tutorial/color_palettes.html#qualitative-color-palettes
        if i == 0:
            return '#4C72B0'
        elif i == 1:
            return '#55A868'
        elif i == 2:
            return '#C44E52'
        elif i == 3:
            return '#8172B2'
        elif i == 4:
            return '#CCB974'
        elif i == 5:
           return '#64B5CD'
        else:
            return '#000000'
    else:
        return '#000000'
# end of mycolors


if __name__ == '__main__':
    options = get_options()
    detids = [int(x) for x in options.detids]
    runs = [int(x) for x in options.runs]
    main(runs, detids, options.outdir, debug = options.debug, nEntries = options.nEntries)
