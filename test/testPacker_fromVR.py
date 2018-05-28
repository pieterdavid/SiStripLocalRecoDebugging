import FWCore.ParameterSet.Config as cms
uc = cms.untracked

from Configuration.StandardSequences.Eras import eras

process = cms.Process('TestSiStripPacker', eras.Run2_HI)

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_AutoFromDBCurrent_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(5)
)

# Input source
process.source = cms.Source("PoolSource",
    fileNames=cms.untracked.vstring(
        ## 2018 VR
          "/store/hidata/HIRun2015/HITrackerVirginRaw/RAW/v1/000/263/400/00000/40322926-4AA3-E511-95F7-02163E0146A8.root"
        ),
    secondaryFileNames = cms.untracked.vstring()
)

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_data', '')

process.load('EventFilter.SiStripRawToDigi.SiStripDigis_cfi')
process.load("RecoLocalTracker.SiStripZeroSuppression.SiStripZeroSuppression_cfi")

from EventFilter.SiStripRawToDigi.SiStripDigis_cfi import siStripDigis
from RecoLocalTracker.SiStripZeroSuppression.SiStripZeroSuppression_cfi import siStripZeroSuppression
##process.load('RecoLocalTracker.Configuration.RecoLocalTracker_cff')
##from RecoLocalTracker.Configuration.RecoLocalTracker_cff import trackerlocalreco, striptrackerlocalreco, siStripZeroSuppression, siStripClusters, siStripMatchedRecHits

# siStripDigis.FedEventDumpFreq = cms.untracked.int32(1) ## dump all FED events - HUGE
## siStripZeroSuppression

origVRDigis = cms.InputTag("siStripDigis", "VirginRaw")

process.siStripRepackVR = cms.EDProducer("SiStripDigiToRawModule",
        InputDigis       = origVRDigis,
        FedReadoutMode   = cms.string('Virgin raw'),
        PacketCode       = cms.string("Virgin raw"),
        UseFedKey        = cms.bool(False),
        UseWrongDigiType = cms.bool(False),
        CopyBufferHeader = cms.bool(False),
        RawDataTag       = cms.InputTag('rawDataCollector')
        )
process.siStripUnpackRepackedVR = siStripDigis.clone(
        ProductLabel     = cms.InputTag('siStripRepackVR'),
        )
repackedVRDigis = cms.InputTag("siStripUnpackRepackedVR", "VirginRaw")
process.diffVR = cms.EDAnalyzer("SiStripRawDigiDiff",
        A = origVRDigis,
        B = repackedVRDigis,
        BottomBitsToIgnore = cms.uint32(0)
        )

process.siStripRepackZS = cms.EDProducer("SiStripDigiToRawModule",
        InputDigis       = cms.InputTag("siStripZeroSuppression", "VirginRaw"),
        FedReadoutMode   = cms.string('ZERO_SUPPRESSED'),
        UseFedKey        = cms.bool(False),
        UseWrongDigiType = cms.bool(False),
        CopyBufferHeader = cms.bool(False),
        RawDataTag       = cms.InputTag('rawDataCollector')
        )
process.siStripUnpackRepackedZS = siStripDigis.clone(
        ProductLabel     = cms.InputTag('siStripRepackZS'),
        )
process.diffZS = cms.EDAnalyzer("SiStripDigiDiff",
        A = cms.InputTag("siStripZeroSuppression", "VirginRaw"),
        B = cms.InputTag("siStripUnpackRepackedZS", "ZeroSuppressed"),
        BottomBitsToIgnore = cms.uint32(0)
        )

process.path = cms.Path(siStripDigis*process.siStripRepackVR*process.siStripUnpackRepackedVR*process.diffVR
        *siStripZeroSuppression*process.siStripRepackZS*process.siStripUnpackRepackedZS*process.diffZS)

process.MessageLogger = cms.Service(
    "MessageLogger",
    destinations = cms.untracked.vstring(
        "detailedInfo",
        "critical"
        ),
    detailedInfo = cms.untracked.PSet(
        threshold = cms.untracked.string("DEBUG")
        ),
    #debugModules = cms.untracked.vstring("siStripDigis", "siStripRepackVR", "siStripUnpackRepackedVR"),
    #categories=cms.untracked.vstring("SiStripRawToDigiModule", "SiStripDigiToRawModule", "SiStripDigiToRaw")
    ##debugModules = cms.untracked.vstring("siStripZeroSuppression"),
    ##categories=cms.untracked.vstring("SiStripZeroSuppression")
    )
