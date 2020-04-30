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
    input = cms.untracked.int32(1000) ## was 100
)

# Input source
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring('file:/nfs/scratch/fynu/pdavid/arawfile/HIMiniumBias2_HIRun2018A-v1_RAW/18AB8C43-D684-A34C-820C-70EDD16E5A58.root'),
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

## from ExportedMenu
process.hltSiStripRawToDigi = cms.EDProducer( "SiStripRawToDigiModule",
    UseDaqRegister = cms.bool( False ),
    ProductLabel = cms.InputTag( "rawDataRepacker" ),
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

process.HLTDoHIStripZeroSuppression = cms.Sequence( process.hltSiStripRawToDigi + process.hltSiStripZeroSuppression + process.hltSiStripZeroSuppressionFaster + process.diffZS)

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

process.MessageLogger = cms.Service(
    "MessageLogger",
    destinations = cms.untracked.vstring(
        "log_checkhybridfaster"
        ),
    log_checkhybridfaster = cms.untracked.PSet(
        threshold = cms.untracked.string("DEBUG"),
        default = cms.untracked.PSet(
            limit = cms.untracked.int32(-1)
            )
        ),
    debugModules = cms.untracked.vstring("hltSiStripZeroSuppression", "hltSiStripZeroSuppressionFaster", "diffZS"),
    categories=cms.untracked.vstring("SiStripZeroSuppression", "SiStripDigiDiff")
    )
