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
calibTreePath = "/store/group/dpg_tracker_strip/comm_tracker/Strip/Calibration/calibrationtree/"
xrootdServer = "eoscms.cern.ch"
xrootdPrefix = "/eos/cms"
color = ROOT.TColor()

def get_options():
    parser = argparse.ArgumentParser(description='Create signal to noise plots for a given list of runs and detID, from CalibTrees')
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
    print "List all existing calibTrees"
    listAllCalibTrees = {}
    listAllCalibTrees["GR15"] = subprocess.Popen(['xrdfs', xrootdServer, 'ls', xrootdPrefix + calibTreePath + "GR15"], stdout=subprocess.PIPE).stdout.read().split('\n')
    listAllCalibTrees["GR16"] = subprocess.Popen(['xrdfs', xrootdServer, 'ls', xrootdPrefix + calibTreePath + "GR16"], stdout=subprocess.PIPE).stdout.read().split('\n')
    print "done\n"

    print "Prepping histos to be filled"
    c1 = TCanvas()
    plots = {}
#    plots['chargeoverpath'] = {
#        'binning' : '(30, 0, 900)',
#        'norm' : '1',
#        'y-max' : 0.24,
#    }
    plots['amplitude'] = {
        'binning' : '(100, 0, 100)',
        'norm' : '1',
        'y-max' : 0.1,
    }
#    plots['gainused'] = {
#        'binning' : '(30, 0.9, 1.2)',
#        'norm' : '1',
#        'y-max' : 1.2,
#    }
    h = {}
    for plot in plots:
        h[plot] = {}
#    for detid in detids:
#        h['chargeoverpath'][detid] = TH1F("h_chargeoverpath_detid-%i" % detid, "h_chargeoverpath_detid-%i" % detid, 200, 0, 2000)
#        h['amplitude'][detid] = TH1F("h_amplitude_detid-%i" % detid, "h_amplitude_detid-%i" % detid, 260, 0, 260)
#        h['gainused'][detid] = TH1F("h_gainused_detid-%i" % detid, "h_gainused_detid-%i" % detid, 50, 0.5, 2)
    print "done\n"

    print "Filling", len(runs) * len(detids), "histos, looping over runs", runs, 'and detids', detids
    # Latest CalibTree in GR15 is 263757 (271045 is also present)
    # First CalibTree in GR16 is 271045
    GR = ""
    gaintree = ""
    for run in runs:
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
            print '\tDoing histograms for %s' % plot
            for detid in detids:
                print '\t\tdetid= %i' % detid
                chain.Draw("GainCalibration%s>>h_tmp%s" % (plot, plots[plot]['binning']), "GainCalibrationrawid == %i" % detid)
                h[plot][detid] = ROOT.gDirectory.Get("h_tmp")
                h[plot][detid].SetName('h_%s_detid-%i' % (plot, detid))
                h[plot][detid].SetTitle('h_%s_detid-%i' % (plot, detid))
#                c1.Print(outdir + '/test.pdf')
#                c1.Print(outdir + '/test.png')

#        if debug:
#            nEntries = 1
#        nEntries = min(nEntries, chain.GetEntries())
#        if nEntries < 0:
#            nEntries = chain.GetEntries()
#        print "Running on %s, with nEntries = %i" % (calibTreeFiles[0], nEntries)
#        for ientry in xrange(0, nEntries):
#            chain.GetEntry(ientry)
#            if (ientry == 0) or (ientry % 1000 == 0):
#                print "# Processing event %i / %i" % (ientry + 1, nEntries)
#            if debug:
#                print "Entry #%i: run= %i, ls= %i, event= %i, bx= %i, nclusters= %i" % (ientry, chain.run, chain.lumi, chain.event, chain.bx, len(chain.GainCalibrationrawid))
#                strtoprint = "len(trackindex)= %i" % len(chain.GainCalibrationtrackindex)
#                strtoprint += "\tlen(rawid)= %i" % len(chain.GainCalibrationrawid)
#                strtoprint += "\tlen(localdirx)= %i" % len(chain.GainCalibrationlocaldirx)
#                strtoprint += "\tlen(localdiry)= %i" % len(chain.GainCalibrationlocaldiry)
#                strtoprint += "\tlen(localdirz)= %i" % len(chain.GainCalibrationlocaldirz)
#                strtoprint += "\tlen(firststrip)= %i" % len(chain.GainCalibrationfirststrip)
#                strtoprint += "\tlen(nstrips)= %i" % len(chain.GainCalibrationnstrips)
#                strtoprint += "\tlen(saturation)= %i" % len(chain.GainCalibrationsaturation)
#                strtoprint += "\tlen(overlapping)= %i" % len(chain.GainCalibrationoverlapping)
#                strtoprint += "\tlen(farfromedge)= %i" % len(chain.GainCalibrationfarfromedge)
#                strtoprint += "\tlen(charge)= %i" % len(chain.GainCalibrationcharge)
#                strtoprint += "\tlen(path)= %i" % len(chain.GainCalibrationpath)
#                strtoprint += "\tlen(chargeoverpath)= %i" % len(chain.GainCalibrationchargeoverpath)
#                strtoprint += "\tlen(amplitude)= %i" % len(chain.GainCalibrationamplitude)
#                strtoprint += "\tlen(gainused)= %i" % len(chain.GainCalibrationgainused)
#                if GR == 'GR16':
#                    strtoprint += "\tlen(gainusedTick)= %i" % len(chain.GainCalibrationgainusedTick)
#                print strtoprint
#            # end of if debug
#            nClusters = len(chain.GainCalibrationrawid)
#            nClusters = 10
#            indexfirstamplitude = 0
#            for icluster in xrange(0, nClusters):
##                if chain.GainCalibrationrawid[icluster] not in detids:
##                    continue
#                detid = chain.GainCalibrationrawid[icluster]
#                indexfirstamplitude += chain.GainCalibrationnstrips[icluster]
#                if debug:
#                    strtoprint = "\trawid= %i" % chain.GainCalibrationrawid[icluster]
#                    strtoprint += "\tcharge= %i" % chain.GainCalibrationcharge[icluster]
#                    strtoprint += "\tpath= %f" % chain.GainCalibrationpath[icluster]
#                    strtoprint += "\tchargeoverpath= %f" % chain.GainCalibrationchargeoverpath[icluster]
##                    strtoprint += "\tamplitude= %i" % amplitude
#                    strtoprint += "\tgainused= %f" % chain.GainCalibrationgainused[icluster]
#                    strtoprint += "\tfirststrip= %i" % chain.GainCalibrationfirststrip[icluster]
#                    strtoprint += "\tnstrips= %i" % chain.GainCalibrationnstrips[icluster]
#                    if "GR16" in GR:
#                        strtoprint += "\tgainusedTick= %f" % chain.GainCalibrationgainusedTick[icluster]
#                    strtoprint += '\n'
#                    sumamplitudes = 0
#                    for istrip in xrange(0, chain.GainCalibrationnstrips[icluster]):
#                        amplitude = struct.unpack('<B', chain.GainCalibrationamplitude[indexfirstamplitude - chain.GainCalibrationnstrips[icluster] + istrip])[0] # from https://docs.python.org/2/c-api/arg.html using https://docs.python.org/2/library/struct.html
#                        strtoprint += '\t\tstrip #%i amplitude= %i\n' % (istrip, amplitude)
#                        sumamplitudes += amplitude
#                    print strtoprint
#                    print "\tcharge= %i sum= %i\n" % (chain.GainCalibrationcharge[icluster], sumamplitudes)
##                h['chargeoverpath'][detid].Fill(chain.GainCalibrationchargeoverpath[icluster])
##                h['amplitude'][detid].Fill(amplitude)
##                h['gainused'][detid].Fill(chain.GainCalibrationgainused[icluster])
#            # end of loop over clusters
#        # end of loop over events
#    # end of loop over runs
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
