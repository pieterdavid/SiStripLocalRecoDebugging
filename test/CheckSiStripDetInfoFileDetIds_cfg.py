import FWCore.ParameterSet.Config as cms

process = cms.Process("TEST")
process.MessageLogger = cms.Service("MessageLogger",
        out = cms.untracked.PSet(threshold = cms.untracked.string('INFO')),
        destinations = cms.untracked.vstring('out')
        )

process.source = cms.Source("EmptyIOVSource",
        firstValue = cms.uint64(109574),
        lastValue = cms.uint64(109574),
        timetype = cms.string('runnumber'),
        interval = cms.uint64(1)
        )

# the DB Geometry is NOT used because in this cfg only one tag is taken from the DB and no GT is used. To be fixed if this is a problem
process.load('Configuration.Geometry.GeometryExtended2018_cff')

process.maxEvents = cms.untracked.PSet(input=cms.untracked.int32(1))

process.checkdetids = cms.EDAnalyzer("CheckSiStripDetInfoFileDetIds")

process.p = cms.Path(process.checkdetids)
