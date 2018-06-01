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

##siStripDigis.FedEventDumpFreq = cms.untracked.int32(1) ## dump all FED events - HUGE
## siStripZeroSuppression

origVRDigis = cms.InputTag("siStripDigis", "VirginRaw")

process.siStripRepackVR = cms.EDProducer("SiStripDigiToRawModule",
        InputDigis       = origVRDigis,
        FedReadoutMode   = cms.string('Virgin raw'),
        ## PacketCode is set below
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
        nDiffToPrint=cms.untracked.uint64(10),
        IgnoreBadChannels=cms.bool(True),
        TopBitsToIgnore = cms.uint32(0),
        BottomBitsToIgnore = cms.uint32(0),
        )

process.siStripRepackZS = cms.EDProducer("SiStripDigiToRawModule",
        InputDigis       = cms.InputTag("siStripZeroSuppression", "VirginRaw"),
        ## FedReadoutMode and PacketCode set below
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
        nDiffToPrint=cms.untracked.uint64(10),
        IgnoreAllZeros=cms.bool(True), ## workaround for packer removing all zero strips for ZS
        TopBitsToIgnore = cms.uint32(0),
        BottomBitsToIgnore = cms.uint32(0),
        )

### SWITCH THE MODES HERE
vrToTest = "10"

if vrToTest == "16":
    process.siStripRepackVR.PacketCode = cms.string("VIRGIN_RAW")
elif vrToTest == "8BOTBOT":
    process.siStripRepackVR.PacketCode = cms.string("VIRGIN_RAW8_BOTBOT")
    process.diffVR.BottomBitsToIgnore = cms.uint32(2)
elif vrToTest == "8TOPBOT":
    process.siStripRepackVR.PacketCode = cms.string("VIRGIN_RAW8_TOPBOT")
    process.diffVR.TopBitsToIgnore = cms.uint32(1)
    process.diffVR.BottomBitsToIgnore = cms.uint32(1)
elif vrToTest == "10":
    process.siStripRepackVR.PacketCode = cms.string("VIRGIN_RAW10")

zsToTest = "lite10"
if zsToTest == "8":
    process.siStripRepackZS.FedReadoutMode = cms.string("Zero suppressed")
    process.siStripRepackZS.PacketCode = cms.string("ZERO_SUPPRESSED")
elif zsToTest == "8BOTBOT":
    process.siStripRepackZS.FedReadoutMode = cms.string("Zero suppressed")
    process.siStripRepackZS.PacketCode = cms.string("ZERO_SUPPRESSED8_BOTBOT")
    process.diffZS.BottomBitsToIgnore = cms.uint32(2)
elif zsToTest == "8TOPBOT":
    process.siStripRepackZS.FedReadoutMode = cms.string("Zero suppressed")
    process.siStripRepackZS.PacketCode = cms.string("ZERO_SUPPRESSED8_TOPBOT")
    process.diffZS.TopBitsToIgnore = cms.uint32(1)
    process.diffZS.BottomBitsToIgnore = cms.uint32(1)
elif zsToTest == "10":
    process.siStripRepackZS.FedReadoutMode = cms.string("Zero suppressed")
    process.siStripRepackZS.PacketCode = cms.string("ZERO_SUPPRESSED10")
elif zsToTest == "lite8":
    process.siStripRepackZS.FedReadoutMode = cms.string("Zero suppressed lite8")
elif zsToTest == "lite8BOTBOT":
    process.siStripRepackZS.FedReadoutMode = cms.string("Zero suppressed lite8 BotBot")
    process.diffZS.BottomBitsToIgnore = cms.uint32(2)
elif zsToTest == "lite8TOPBOT":
    process.siStripRepackZS.FedReadoutMode = cms.string("Zero suppressed lite8 TopBot")
    process.diffZS.TopBitsToIgnore = cms.uint32(1)
    process.diffZS.BottomBitsToIgnore = cms.uint32(1)
elif zsToTest == "lite10":
    process.siStripRepackZS.FedReadoutMode = cms.string("Zero suppressed lite10")

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
