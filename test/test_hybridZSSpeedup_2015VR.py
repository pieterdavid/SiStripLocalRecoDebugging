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

# Additional output definition

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_hlt_HIon', '')

inputVR = cms.InputTag("siStripDigis", "VirginRaw")

from RecoLocalTracker.SiStripZeroSuppression.SiStripZeroSuppression_cfi import siStripZeroSuppression
from EventFilter.SiStripRawToDigi.SiStripDigiToRaw_cfi import SiStripDigiToRaw
from EventFilter.RawDataCollector.rawDataCollectorByLabel_cfi import rawDataCollector

process.zsHybridEmu = siStripZeroSuppression.clone(
    produceRawDigis=False,
    produceHybridFormat=True,
    Algorithms=siStripZeroSuppression.Algorithms.clone(
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

## from ExportedMenu
process.hltSiStripRawToDigi = cms.EDProducer( "SiStripRawToDigiModule",
    UseDaqRegister = cms.bool( False ),
    ProductLabel = cms.InputTag("hybridRawDataRepacker"),
    MarkModulesOnMissingFeds = cms.bool( True ),
    UnpackCommonModeValues = cms.bool( False ),
    AppendedBytes = cms.int32( 0 ),
    UseFedKey = cms.bool( False ),
    LegacyUnpacker = cms.bool( False ),
    ErrorThreshold = cms.uint32( 7174 ),
    TriggerFedId = cms.int32( 0 ),
    DoAPVEmulatorCheck = cms.bool( False ),
    UnpackBadChannels = cms.bool( False ),
    DoAllCorruptBufferChecks = cms.bool( False )
)

process.hltSiStripZeroSuppression = cms.EDProducer( "SiStripZeroSuppression",
    fixCM = cms.bool( False ),
    produceHybridFormat = cms.bool( False ),
    produceBaselinePoints = cms.bool( False ),
    produceCalculatedBaseline = cms.bool( False ),
    storeInZScollBadAPV = cms.bool( True ),
    Algorithms = cms.PSet( 
      CutToAvoidSignal = cms.double( 2.0 ),
      lastGradient = cms.int32( 10 ),
      slopeY = cms.int32( 4 ),
      slopeX = cms.int32( 3 ),
      PedestalSubtractionFedMode = cms.bool( False ),
      Use10bitsTruncation = cms.bool( False ),
      Fraction = cms.double( 0.2 ),
      minStripsToFit = cms.uint32( 4 ),
      consecThreshold = cms.uint32( 5 ),
      hitStripThreshold = cms.uint32( 40 ),
      Deviation = cms.uint32( 25 ),
      CommonModeNoiseSubtractionMode = cms.string( "IteratedMedian" ),
      filteredBaselineDerivativeSumSquare = cms.double( 30.0 ),
      ApplyBaselineCleaner = cms.bool( True ),
      doAPVRestore = cms.bool( True ),
      TruncateInSuppressor = cms.bool( True ),
      restoreThreshold = cms.double( 0.5 ),
      sizeWindow = cms.int32( 1 ),
      APVInspectMode = cms.string( "Hybrid" ),
      ForceNoRestore = cms.bool( False ),
      useRealMeanCM = cms.bool( False ),
      ApplyBaselineRejection = cms.bool( True ),
      DeltaCMThreshold = cms.uint32( 20 ),
      nSigmaNoiseDerTh = cms.uint32( 4 ),
      nSaturatedStrip = cms.uint32( 2 ),
      SiStripFedZeroSuppressionMode = cms.uint32( 4 ),
      useCMMeanMap = cms.bool( False ),
      discontinuityThreshold = cms.int32( 12 ),
      distortionThreshold = cms.uint32( 20 ),
      filteredBaselineMax = cms.double( 6.0 ),
      Iterations = cms.int32( 3 ),
      CleaningSequence = cms.uint32( 1 ),
      nSmooth = cms.uint32( 9 ),
      APVRestoreMode = cms.string( "BaselineFollower" ),
      MeanCM = cms.int32( 0 ),
      widthCluster = cms.int32( 64 ),
      debugModules = cms.untracked.vuint32()#cms.untracked.vuint32(369125509, 369125678, 369125814, 402672277, 436228945, 436245830, 436299460, 436299492, 436311828, 470050032, 470083428, 470328650)
    ),
    RawDigiProducersList = cms.VInputTag( 'hltSiStripRawToDigi:VirginRaw','hltSiStripRawToDigi:ProcessedRaw','hltSiStripRawToDigi:ScopeMode','hltSiStripRawToDigi:ZeroSuppressed' ),
    storeCM = cms.bool( False ),
    produceRawDigis = cms.bool( False )
)
process.hltSiStripZeroSuppressionFaster = process.hltSiStripZeroSuppression.clone(fasterHybridZS=cms.untracked.bool(True))

process.diffZS = cms.EDAnalyzer("SiStripDigiDiff",
        A = cms.InputTag("hltSiStripZeroSuppression", "ZeroSuppressed"),
        B = cms.InputTag("hltSiStripZeroSuppressionFaster", "ZeroSuppressed"),
        nDiffToPrint=cms.untracked.uint64(100),
        IgnoreAllZeros=cms.bool(False),
        TopBitsToIgnore = cms.uint32(0),
        BottomBitsToIgnore = cms.uint32(0),
        )

process.load("RecoLocalTracker.SiStripClusterizer.SiStripClusterizer_cfi")
process.siStripClustersHybrid = process.siStripClusters.clone(
        DigiProducersList = cms.VInputTag(
            cms.InputTag("hltSiStripZeroSuppression", "ZeroSuppressed"),
            )
        )
process.load("RecoLocalTracker.SiStripClusterizer.SiStripClustersFromRaw_cfi")
process.SiStripRegionalClusterizerHybrid = process.SiStripClustersFromRawFacility.clone(
        Algorithms = process.hltSiStripZeroSuppression.Algorithms.clone(),
        ProductLabel = cms.InputTag("hybridRawDataRepacker"),
        HybridZeroSuppressed = cms.bool(True),
        #referenceDigis = cms.InputTag("hltSiStripZeroSuppression", "ZeroSuppressed")
        )
process.clusterStatDiff = cms.EDAnalyzer("SiStripClusterStatsDiff",
        A = cms.InputTag("siStripClustersHybrid"),
        B = cms.InputTag("SiStripRegionalClusterizerHybrid"),
        )

process.HLTDoHIStripZeroSuppression = cms.Sequence( process.siStripDigis + process.zsHybridEmu + process.SiStripDigiToHybridRaw + process.hybridRawDataRepacker + process.hltSiStripRawToDigi + process.hltSiStripZeroSuppression + process.hltSiStripZeroSuppressionFaster + process.diffZS + process.siStripClustersHybrid + process.SiStripRegionalClusterizerHybrid + process.clusterStatDiff )

process.TFileService = cms.Service("TFileService",
        fileName = cms.string("diffhistos.root"),
        closeFileFast = cms.untracked.bool(True),
        )

# Path and EndPath definitions
process.my_step = cms.Path(process.HLTDoHIStripZeroSuppression)
process.endjob_step = cms.EndPath(process.endOfProcess)

# Schedule definition
process.schedule = cms.Schedule(process.my_step,process.endjob_step)
from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)

# Customisation from command line

# Add early deletion of temporary data products to reduce peak memory need
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
# End adding early deletion

process.load( "HLTrigger.Timer.FastTimerService_cfi" )
process.FastTimerService.printEventSummary         = False
process.FastTimerService.printRunSummary           = False
process.FastTimerService.printJobSummary           = True
process.FastTimerService.writeJSONSummary = cms.untracked.bool(True)
process.FastTimerService.jsonFileName = cms.untracked.string("resources_2015VR.json")

process.MessageLogger = cms.Service(
    "MessageLogger",
    destinations = cms.untracked.vstring(
        "log_checkhybridfasterVR"
        ),
    log_checkhybridfasterVR = cms.untracked.PSet(
        threshold = cms.untracked.string("DEBUG"),
        default = cms.untracked.PSet(
            limit = cms.untracked.int32(-1)
            )
        ),
    debugModules = cms.untracked.vstring("hltSiStripZeroSuppression", "hltSiStripZeroSuppressionFaster", "diffZS", "SiStripRegionalClusterizerHybrid", "clusterStatDiff"),
    categories=cms.untracked.vstring("SiStripZeroSuppression", "SiStripDigiDiff", "SiStripClusterStatsDiff")
    )
