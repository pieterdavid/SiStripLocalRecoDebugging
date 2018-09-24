#!/usr/bin/env python2
"""
A few quick (ZS) digi and cluster statistics comparison plots
"""
__author__ = "Pieter David <pieter.david@uclouvain.be>"
__date__ = "22 September 2018"

import os.path
import ROOT
from matplotlib import pyplot as plt
import mplbplot.decorateAxes
from mplbplot.plothelpers import AxesWithPull

def addOverflows(histo):
    histo.SetBinContent(1, histo.GetBinContent(0)+histo.GetBinContent(1))
    nB = histo.GetNbinsX()
    histo.SetBinContent(nB, histo.GetBinContent(nB)+histo.GetBinContent(nB+1))

if __name__ == "__main__":
    _gbl = set()
    hFile = ROOT.TFile.Open("diffhistos.root", "READ")
    refSuffix = "A"
    newSuffix = "B"
    outpath = "comparisonPlots"
    histoList = ["digiStatDiff/nDigis", "clusterStatDiff/nClus",
            "clusterStatDiff/clusCharge", "clusterStatDiff/clusWidth", "clusterStatDiff/clusBary", "clusterStatDiff/clusVar"]
    for hName in histoList:
        hName_n = hName.replace("/", "_")
        hRef = hFile.Get(hName+refSuffix)
        hNew = hFile.Get(hName+newSuffix)
        hRatio = hNew.Clone(hName+"Ratio")
        hRatio.Divide(hRef)
        _gbl.add(hRatio)
        #
        fig,ax = plt.subplots(num=hName)
        padAx = AxesWithPull(fig, ax, vFracPull=.13, vFracMargin=.02, vFracTopMargin=.1)
        padAx.dataAxes.semilogy()
        padAx.dataAxes.rhist(hRef, histtype="step", color="k")
        padAx.dataAxes.rhist(hNew, histtype="step", color="r")
        padAx.dataAxes.set_xlim(hRef.GetXaxis().GetXmin(), hRef.GetXaxis().GetXmax())
        padAx.pullAxes.rplot(hRatio, fmt="ko", markersize=1.5)
        padAx.pullAxes.set_xlim(hRef.GetXaxis().GetXmin(), hRef.GetXaxis().GetXmax())
        padAx.pullAxes.set_ylim(.5, 1.5)
        fig.savefig(os.path.join("plot{0}.pdf".format(hName_n)))
        ##
        hDiff = hFile.Get(hName+"Diff")
        hRelDiff = hFile.Get(hName+"RelDiff")
        #
        if hDiff or hRelDiff:
            if hDiff and hRelDiff:
                addOverflows(hDiff)
                addOverflows(hRelDiff)
                fig,ax = plt.subplots(1,2,num=hName+"Diff")
                ax[0].semilogy()
                ax[0].rhist(hDiff   , histtype="step", color="k")
                ax[0].set_xlim(hDiff.GetXaxis().GetXmin(), hDiff.GetXaxis().GetXmax())
                ax[1].semilogy()
                ax[1].rhist(hRelDiff, histtype="step", color="k")
                ax[1].set_xlim(hRelDiff.GetXaxis().GetXmin(), hRelDiff.GetXaxis().GetXmax())
            else:
                fig,ax = plt.subplots(num=hName+"Diff")
                ax.semilogy()
                if hDiff:
                    addOverflows(hDiff)
                    ax.rhist(hDiff, histtype="step", color="k")
                    ax.rhist(hDiff   , histtype="step", color="k")
                elif hrelDiff:
                    addOverflows(hRelDiff)
                    ax.rhist(hRelDiff, histtype="step", color="k")
                    ax.set_xlim(hRelDiff.GetXaxis().GetXmin(), hRelDiff.GetXaxis().GetXmax())
            fig.savefig("plot{0}Diff.pdf".format(hName_n))
    ##
    plt.show()
