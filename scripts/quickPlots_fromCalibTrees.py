#!/usr/bin/env python
# python imports
import os
import sys
import argparse
import subprocess
import collections
import json
# to prevent pyroot to hijack argparse we need to go around
tmpargv = sys.argv[:]
sys.argv = []
# ROOT setup
import ROOT
from ROOT import TChain, TH1F, TCanvas, TFile
ROOT.gROOT.Reset()
ROOT.gROOT.SetBatch()
ROOT.gStyle.SetOptTitle(0)
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.ProcessLine(".x setTDRStyle.C")
ROOT.TGaxis.SetMaxDigits(3)
ROOT.PyConfig.IgnoreCommandLineOptions = True
sys.argv = tmpargv
# Other global setup things
calibTreePath = "/store/group/dpg_tracker_strip/comm_tracker/Strip/Calibration/calibrationtree/"
xrootdServer = "eoscms.cern.ch"
xrootdPrefix = "/eos/cms"
color = ROOT.TColor()

def get_options():
    parser = argparse.ArgumentParser(description='Create signal to noise plots for a given list of runs and detID, from CalibTrees. The calibTree content itself can be found at https://github.com/cms-sw/cmssw/blob/CMSSW_8_0_X/CalibTracker/SiStripCommon/plugins/ShallowGainCalibration.cc In addition to the plot themselves all created histograms are saved to a file histos.root')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--perRun', action='store_true', dest='perRun', help='integrate over detIDs and compare histograms on a per-run basis',)
    group.add_argument('--perDetid', action='store_true', dest='perDetid', help='integrate over runs and compare histograms on a per-detID basis',)

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
    parser.add_argument('--plots', action='store', dest='inputJsons',
                        default=['plots_perCluster.json'], type=str, nargs='+', metavar='FILE',
                        help='json file of the plots to be done')
    parser.add_argument('--debug', action='store_true', help='More verbose output', dest='debug')
    options = parser.parse_args()
    return options

def main(perRun, perDetid, runs, detids, outdir, inputJsons, debug=False, nEntries=-1):
    print "List all existing calibTrees"
    listAllCalibTrees = {}
    listAllCalibTrees["GR15"] = subprocess.Popen(['xrdfs', xrootdServer, 'ls', xrootdPrefix + calibTreePath + "GR15"], stdout=subprocess.PIPE).stdout.read().split('\n')
    listAllCalibTrees["GR16"] = subprocess.Popen(['xrdfs', xrootdServer, 'ls', xrootdPrefix + calibTreePath + "GR16"], stdout=subprocess.PIPE).stdout.read().split('\n')
    print "\tFound %i calibTrees for GR15" % len(listAllCalibTrees["GR15"])
    print "\tFound %i calibTrees for GR16" % len(listAllCalibTrees["GR16"])
    print "done\n"

    print "Prepping histos to be filled"
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    tfile = TFile('%s/histos.root' % outdir, 'recreate')
    c1 = TCanvas()
    plots = {}
    for j in inputJsons:
        with open(j) as f:
            plots.update(json.load(f))
    h = {}
    h_summed = {}
    for plot in plots:
        h[plot] = {}
        h_summed[plot] = collections.OrderedDict()  # Need an ordered dict to have a consistent legend for plots produced in the same run
        for run in runs:
            h[plot][run] = {}
    print "done\n"

    print "Filling", len(runs) * len(detids), "histos, looping over runs", runs, 'and detids', detids
    # Latest CalibTree in GR15 is 263757 (271045 is also present)
    # First CalibTree in GR16 is 271045
    GR = ""
    gaintree = ""
    for run in runs:
        print '\tProcessing run %i' % run
        if run < 270000:
            GR = "GR15"
            gaintree = "gainCalibrationTree/tree"
        elif run > 270000:
            GR = "GR16"
            gaintree = "gainCalibrationTreeStdBunch/tree"
        calibTreeFiles = [x for x in listAllCalibTrees[GR] if ("calibTree_" + str(run)) in str(x)]
        # files are of the type /eos/cms/store/group/dpg_tracker_strip/comm_tracker/Strip/Calibration/calibrationtree/GR15/calibTree_257400_975.root
        if len(calibTreeFiles) == 0:
            print "There is no available calibTree for run #%i" % run
            continue
        # pick only the first file, should be enough for our purposes
        chain = TChain(gaintree)
        chain.Add("root://eoscms.cern.ch/" + calibTreeFiles[0])
        for plot in plots:
            print '\t\tDoing histograms for %s' % plot
            for detid in detids:
                print '\t\t\tdetid= %i' % detid
                chain.Draw("GainCalibration%s>>h_tmp%s" % (plot, plots[plot]['binning']), "GainCalibrationrawid == %i" % detid)
                h[plot][run][detid] = ROOT.gDirectory.Get("h_tmp")
                h[plot][run][detid].SetName('h_%s_run-%i_detid-%i' % (plot, run, detid))
                h[plot][run][detid].SetTitle('h_%s_run-%i_detid-%i' % (plot, run, detid))
                h[plot][run][detid].Write()
            # end of loop over detids
        # end of loop over plots
    # end of loop over runs
    print "done\n"

    print "Plotting and saving histos %s" % ('per Run (summing over detids)' if perRun else 'per detID (summing over runs)')
    for plot in plots:
        if perRun:
            for run in runs:
                for idetid, detid in enumerate(detids):
                    if idetid == 0:
                        h_summed[plot][run] = TH1F(h[plot][run][detid])
                        h_summed[plot][run].SetName('h_%s_run-%i_detid-all' % (plot, run))
                        h_summed[plot][run].SetTitle('h_%s_run-%i_detid-all' % (plot, run))
                    else:
                        h_summed[plot][run].Add(h[plot][run][detid])
                    if idetid == len(detids) - 1:
                        h_summed[plot][run].Write()
        if perDetid:
            for detid in detids:
                for irun, run in enumerate(runs):
                    if irun == 0:
                        h_summed[plot][detid] = TH1F(h[plot][run][detid])
                        h_summed[plot][detid].SetName('h_%s_run-all_detid-%i' % (plot, detid))
                        h_summed[plot][detid].SetTitle('h_%s_run-all_detid-%i' % (plot, detid))
                    else:
                        h_summed[plot][detid].Add(h[plot][run][detid])
                    if irun == len(runs) - 1:
                        h_summed[plot][detid].Write()
    for plot in plots:
        c1.Clear()
        legend = ROOT.TLegend(0.25, 0.72, 0.80, 0.93, "")
        legend.SetFillColor(ROOT.kWhite)
        legend.SetLineColor(ROOT.kWhite)
        legend.SetShadowColor(ROOT.kWhite)
        for ihist, hist in enumerate(h_summed[plot]):
            drawoptions = ''
            if ihist > 0:
                drawoptions = 'same'
            if 'norm' in plots[plot] and plots[plot]['norm'] == '1':
                h_summed[plot][hist].Scale(1. / h_summed[plot][hist].GetEntries())
                h_summed[plot][hist].GetYaxis().SetTitle('norm. to unity')
            if 'y-max' in plots[plot]:
                h_summed[plot][hist].SetMaximum(plots[plot]['y-max'])
            h_summed[plot][hist].GetXaxis().SetTitle(plot)
            h_summed[plot][hist].SetLineWidth(2)
            c = color.GetColor(mycolors(ihist, len(h_summed[plot])))
            h_summed[plot][hist].SetLineColor(c)
            h_summed[plot][hist].SetMarkerColor(c)
            h_summed[plot][hist].Draw(drawoptions)
            legend.AddEntry(h_summed[plot][hist].GetName(), ('detid #%i' % hist) if perDetid else ('run #%i' % run), 'l')
            ROOT.gPad.Modified()
            ROOT.gPad.Update()
        # end of loop over histos
        legend.Draw()
        c1.Print('%s/%s_%s.png' % (outdir, plot, 'perRun' if perRun else 'perDetid'))
        c1.Print('%s/%s_%s.pdf' % (outdir, plot, 'perRun' if perRun else 'perDetid'))
    # end of loop over plots
    print "done\n"

    print '##### ##### #####'
    print '##### ##### #####'
    print 'Summary for runs ', runs, ' and detids ', detids
    print 'Histograms are %s' % ('per Run (summing over detids)' if perRun else 'per detID (summing over runs)')
    for plot in plots:
        print '##### ##### #####'
        print 'For plot %s' % plot
        for hist in h_summed[plot]:
            print '\t%s\tmean= %.2e +- %.2e\trms= %.2e +- %.2e' % (
                ('detid #%i' % hist) if perDetid else ('run #%i' % run),
                h_summed[plot][hist].GetMean(),
                h_summed[plot][hist].GetMeanError(),
                h_summed[plot][hist].GetRMS(),
                h_summed[plot][hist].GetRMSError()
                )
        print ''
    print '##### ##### #####'


    tfile.Close()
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
    main(options.perRun, options.perDetid, runs, detids, options.outdir, options.inputJsons, debug=options.debug, nEntries=options.nEntries)
