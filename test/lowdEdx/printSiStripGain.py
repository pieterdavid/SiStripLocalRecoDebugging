import FWCore.ParameterSet.Config as cms

process = cms.Process("CheckSiStripConditions")
process.load("Configuration.Geometry.GeometryRecoDB_cff")
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

from FWCore.ParameterSet.VarParsing import VarParsing

options = VarParsing('analysis')
options.register('run', 0, VarParsing.multiplicity.singleton, VarParsing.varType.int, "Run number")
options.register('globalTag', "auto:run2_data", VarParsing.multiplicity.singleton, VarParsing.varType.string, "Global tag")
options.register("det", [], VarParsing.multiplicity.list, VarParsing.varType.int, "DetId")
options.parseArguments()

from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_data', '')

# Fake DetVOff
process.load("CalibTracker.SiStripESProducers.SiStripQualityESProducer_cfi")
process.load("CalibTracker.SiStripESProducers.fake.SiStripDetVOffFakeESSource_cfi")
process.es_prefer_fakeSiStripDetVOff = cms.ESPrefer("SiStripDetVOffFakeESSource", "siStripDetVOffFakeESSource")

process.source = cms.Source("EmptyIOVSource",
    firstValue = cms.uint64(options.run),
    lastValue = cms.uint64(options.run),
    timetype = cms.string('runnumber'),
    interval = cms.uint64(1)
)
process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(-1)
)

process.stat = cms.EDAnalyzer("PrintSiStripGain",
        modules = cms.vuint32(*options.det),
        )
process.p = cms.Path(process.stat)

process.MessageLogger = cms.Service("MessageLogger",
    destinations = cms.untracked.vstring('cout'),
    categories=cms.untracked.vstring("PrintSiStripGain"),
    cout = cms.untracked.PSet(
        threshold = cms.untracked.string('WARNING')
    )
)
