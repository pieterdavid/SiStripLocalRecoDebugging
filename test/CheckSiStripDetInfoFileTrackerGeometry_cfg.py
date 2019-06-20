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

process.load('Configuration.Geometry.GeometryExtended2018_cff')
process.TrackerTopologyEP = cms.ESProducer("TrackerTopologyEP")
process.load("Geometry.TrackerGeometryBuilder.trackerParameters_cfi")
process.load("Geometry.TrackerGeometryBuilder.trackerGeometry_cfi")
process.trackerGeometry.applyAlignment = False

process.maxEvents = cms.untracked.PSet(input=cms.untracked.int32(1))

process.checktrackergeometry = cms.EDAnalyzer("CheckSiStripDetInfoFileTrackerGeometry")

process.p = cms.Path(process.checktrackergeometry)
