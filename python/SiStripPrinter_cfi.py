import FWCore.ParameterSet.Config as cms

printCMValues = cms.EDAnalyzer('SiStripCommonModeValuesPrinter')
printNofClusters = cms.EDAnalyzer('SiStripClustersPrinter')
