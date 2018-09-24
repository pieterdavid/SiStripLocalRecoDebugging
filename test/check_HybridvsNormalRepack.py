import FWCore.ParameterSet.Config as cms

from Configuration.StandardSequences.Eras import eras

process = cms.Process('CHECK',eras.Run2_HI)

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContentHeavyIons_cff')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_AutoFromDBCurrent_cff')
process.load('Configuration.StandardSequences.RawToDigi_Data_cff')
###process.load('Configuration.StandardSequences.DigiToRaw_Repack_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(100) ## was 100
)

# Input source
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring('/store/hidata/HIRun2015/HITrackerVirginRaw/RAW/v1/000/263/400/00000/40322926-4AA3-E511-95F7-02163E0146A8.root'),
    secondaryFileNames = cms.untracked.vstring()
)

process.options = cms.untracked.PSet(

)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('step1 nevts:100'),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

# Output definition

process.RAWoutput = cms.OutputModule("PoolOutputModule",
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('RAW'),
        filterName = cms.untracked.string('')
    ),
    fileName = cms.untracked.string('whatever.root'),
    outputCommands = process.RAWEventContent.outputCommands,
    splitLevel = cms.untracked.int32(0)
)

# Additional output definition

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_hlt_hi', '')

from EventFilter.RawDataCollector.rawDataCollectorByLabel_cfi import rawDataCollector
process.load("RecoLocalTracker.SiStripZeroSuppression.SiStripZeroSuppression_cfi")
from RecoLocalTracker.SiStripZeroSuppression.SiStripZeroSuppression_cfi import siStripZeroSuppression
process.load("EventFilter.SiStripRawToDigi.SiStripDigiToRaw_cfi")
from EventFilter.SiStripRawToDigi.SiStripDigiToRaw_cfi import SiStripDigiToRaw

##
## WF 1: emulate hybrid, repack, unpack, zero-suppress, repack
##
inputVR = cms.InputTag("siStripDigis", "VirginRaw")
# step1
process.zsHybridEmu = process.siStripZeroSuppression.clone(
    produceRawDigis=False,
    produceHybridFormat=True,
    Algorithms=process.siStripZeroSuppression.Algorithms.clone(
        APVInspectMode = "HybridEmulation",
        APVRestoreMode = "",
        CommonModeNoiseSubtractionMode = 'Median',
        ##CommonModeNoiseSubtractionMode = 'IteratedMedian',
        ##CutToAvoidSignal    = 1., ## 2./2
        MeanCM = 0,
        Use10bitsTruncation = True
        ),
    RawDigiProducersList=cms.VInputTag(inputVR)
    )
process.SiStripDigiToHybridRaw = SiStripDigiToRaw.clone(
    InputDigis = cms.InputTag('zsHybridEmu', 'VirginRaw'),
    FedReadoutMode = cms.string('ZERO_SUPPRESSED'),
    PacketCode = cms.string('ZERO_SUPPRESSED10'),
    CopyBufferHeader = cms.bool(True),
    RawDataTag = cms.InputTag('rawDataCollector')
    )
process.hybridRawDataRepacker = rawDataCollector.clone(
    verbose = cms.untracked.int32(0),
    RawCollectionList = cms.VInputTag(
        cms.InputTag('SiStripDigiToHybridRaw'),
        cms.InputTag('source'),
        cms.InputTag('rawDataCollector'))
    )
# step2
process.unpackHybridEmu = process.siStripDigis.clone(ProductLabel=cms.InputTag('hybridRawDataRepacker'))
process.zsHybrid = process.siStripZeroSuppression.clone(
    RawDigiProducersList = cms.VInputTag(
        cms.InputTag("unpackHybridEmu", "VirginRaw"),
        cms.InputTag("unpackHybridEmu", "ProcessedRaw"),
        cms.InputTag("unpackHybridEmu", "ScopeMode"),
        cms.InputTag("unpackHybridEmu", "ZeroSuppressed")
        ),
    Algorithms=process.siStripZeroSuppression.Algorithms.clone(
        APVInspectMode = "Hybrid",
        ),
    )
process.hybridSiStripDigiToZSRaw = SiStripDigiToRaw.clone(
    InputDigis = cms.InputTag('zsHybrid', 'ZeroSuppressed'),
    FedReadoutMode = cms.string('ZERO_SUPPRESSED'),
    PacketCode = cms.string('ZERO_SUPPRESSED'),
    CopyBufferHeader = cms.bool(True),
    RawDataTag = cms.InputTag('hybridRawDataRepacker')
    )
process.hybridZSRawDataRepacker = rawDataCollector.clone(
    verbose = cms.untracked.int32(0),
    RawCollectionList = cms.VInputTag(
        cms.InputTag('hybridSiStripDigiToZSRaw'),
        cms.InputTag('source'),
        cms.InputTag('hybridRawDataRepacker'))
    )
##
## WF 2: zero-suppress, repack
##
# ZS:       process.siStripZeroSuppression
process.SiStripDigiToZSRaw = SiStripDigiToRaw.clone(
    InputDigis = cms.InputTag('siStripZeroSuppression', 'VirginRaw'),
    FedReadoutMode = cms.string('ZERO_SUPPRESSED'),
    PacketCode = cms.string('ZERO_SUPPRESSED'),
    CopyBufferHeader = cms.bool(True),
    RawDataTag = cms.InputTag('rawDataCollector')
    )
process.rawDataRepacker = rawDataCollector.clone(
    verbose = cms.untracked.int32(0),
    RawCollectionList = cms.VInputTag(
        cms.InputTag('SiStripDigiToZSRaw'),
        cms.InputTag('source'),
        cms.InputTag('rawDataCollector'))
    )

##
## Modify some settings for consistenc between the two
##
process.siStripZeroSuppression.Algorithms = process.siStripZeroSuppression.Algorithms.clone(
        CommonModeNoiseSubtractionMode = 'Median',
        )

## unpack both

process.unpackRepackedZS1 = process.siStripDigis.clone(ProductLabel=cms.InputTag('hybridZSRawDataRepacker'))
process.unpackRepackedZS2 = process.siStripDigis.clone(ProductLabel=cms.InputTag('rawDataRepacker'))
process.diffRepackedZS = cms.EDAnalyzer("SiStripDigiDiff",
        A = cms.InputTag("unpackRepackedZS1", "ZeroSuppressed"),
        B = cms.InputTag("unpackRepackedZS2", "ZeroSuppressed"),
        nDiffToPrint=cms.untracked.uint64(100),
        IgnoreAllZeros=cms.bool(True), ## workaround for packer removing all zero strips for ZS
        TopBitsToIgnore = cms.uint32(0),
        BottomBitsToIgnore = cms.uint32(1),
        )
process.digiStatDiff = cms.EDAnalyzer("SiStripDigiStatsDiff",
        A = cms.InputTag("unpackRepackedZS2", "ZeroSuppressed"),
        B = cms.InputTag("unpackRepackedZS1", "ZeroSuppressed"),
        )
process.load("RecoLocalTracker.SiStripClusterizer.SiStripClusterizer_RealData_cfi")
process.clusterizeRepackedZS1 = process.siStripClusters.clone(DigiProducersList=cms.VInputTag(cms.InputTag("unpackRepackedZS1", "ZeroSuppressed")))
process.clusterizeRepackedZS2 = process.siStripClusters.clone(DigiProducersList=cms.VInputTag(cms.InputTag("unpackRepackedZS2", "ZeroSuppressed")))
process.clusterStatDiff = cms.EDAnalyzer("SiStripClusterStatsDiff",
        A = cms.InputTag("clusterizeRepackedZS2"),
        B = cms.InputTag("clusterizeRepackedZS1"),
        )
process.DigiToRawRepack = cms.Sequence(
        process.siStripZeroSuppression * process.SiStripDigiToZSRaw * process.rawDataRepacker *
        process.zsHybridEmu * process.SiStripDigiToHybridRaw * process.hybridRawDataRepacker * 
            process.unpackHybridEmu * process.zsHybrid * process.hybridSiStripDigiToZSRaw * process.hybridZSRawDataRepacker *
        ## analyze
        process.unpackRepackedZS1 * process.unpackRepackedZS2 * process.diffRepackedZS * process.digiStatDiff *
            process.clusterizeRepackedZS1 * process.clusterizeRepackedZS2 * process.clusterStatDiff
        )
process.TFileService = cms.Service("TFileService",
        fileName = cms.string("diffhistos.root"),
        closeFileFast = cms.untracked.bool(True),
        )

# Path and EndPath definitions
process.raw2digi_step = cms.Path(process.RawToDigi)
process.digi2repack_step = cms.Path(process.DigiToRawRepack)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.RAWoutput_step = cms.EndPath(process.RAWoutput)

# Schedule definition
process.schedule = cms.Schedule(process.raw2digi_step,process.digi2repack_step,process.endjob_step,process.RAWoutput_step)
from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)

# Customisation from command line

# Add early deletion of temporary data products to reduce peak memory need
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
# End adding early deletion

process.MessageLogger = cms.Service(
    "MessageLogger",
    destinations = cms.untracked.vstring(
        "log_checkhybrid"
        ),
    debugModules = cms.untracked.vstring("diffRepackedZS", "zsHybridEmu", "zsHybrid", "siStripZeroSuppression"),
    categories=cms.untracked.vstring("SiStripZeroSuppression", "SiStripDigiDiff")
    )
