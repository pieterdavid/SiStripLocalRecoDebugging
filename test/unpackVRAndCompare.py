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

process.maxEvents = uc.PSet(
    input = uc.int32(-1)
    #input = uc.int32(1)
)

# Input source
# output of: cmsDriver.py test --conditions auto:run2_data -s RAW2DIGI --runUnscheduled --process reRECO --data --era Run2_2018 --eventcontent FEVTDEBUGHLT --hltProcess reHLT --scenario pp --datatier RECO -n 100 --filein /store/hidata/HIRun2015/HITrackerVirginRaw/RAW/v1/000/263/400/00000/40322926-4AA3-E511-95F7-02163E0146A8.root --customise_command 'process.FEVTDEBUGHLToutput.outputCommands.append("keep *_siStripDigis_*_*")' --fileout file:/nfs/scratch/fynu/pdavid/arawfile/localreco_HI2015VR_dbgWithUnpackedVR.root
process.source = cms.Source("PoolSource",
    fileNames=uc.vstring(
        ## 2018 VR
          "file:/nfs/scratch/fynu/pdavid/arawfile/localreco_HI2015VR_dbgWithUnpackedVR.root"
        ),
    secondaryFileNames = uc.vstring()
)

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_data', '')

refVR10 = cms.InputTag("siStripDigis", "VirginRaw")

process.load("RecoLocalTracker.SiStripZeroSuppression.SiStripZeroSuppression_cfi")
process.siStripZeroSuppression.RawDigiProducersList = cms.VInputTag(refVR10)
seq = process.siStripZeroSuppression

refZS = cms.InputTag("siStripZeroSuppression", "VirginRaw")

from EventFilter.SiStripRawToDigi.SiStripDigis_cfi import siStripDigis
process.siStripDigisNew = siStripDigis.clone()
unpVR10 = cms.InputTag("siStripDigisNew", "VirginRaw")

process.diffVR10OldNew = cms.EDAnalyzer("SiStripRawDigiDiff",
        A = refVR10,
        B = unpVR10,
        nDiffToPrint=uc.uint64(10),
        IgnoreBadChannels=cms.bool(False),
        TopBitsToIgnore = cms.uint32(0),
        BottomBitsToIgnore = cms.uint32(0),
        )

seq *= process.siStripDigisNew*process.diffVR10OldNew

modes = {
    "VR16"       : ("VIRGIN_RAW", "VIRGIN_RAW"        , (0, 0)),
    "VR8BOTBOT"  : ("VIRGIN_RAW", "VIRGIN_RAW8_BOTBOT", (0, 2)),
    "VR8TOPBOT"  : ("VIRGIN_RAW", "VIRGIN_RAW8_TOPBOT", (1, 1)),
   #"VR10"       : ("VIRGIN_RAW", "VIRGIN_RAW10"      , (0, 0)) ## already tested by diffVR10
    "ZS8"        : ("ZERO_SUPPRESSED", "ZERO_SUPPRESSED", (0, 0)), ## ??? (0, 2) more likely
    "ZS8BOTBOT"  : ("ZERO_SUPPRESSED", "ZERO_SUPPRESSED8_BOTBOT", (0, 2)),
    "ZS8TOPBOT"  : ("ZERO_SUPPRESSED", "ZERO_SUPPRESSED8_TOPBOT", (1, 1)),
    "ZS10"       : ("ZERO_SUPPRESSED", "ZERO_SUPPRESSED10", (0, 0)),
    "ZSL8"       : ("ZERO_SUPPRESSED_LITE8", None, (0, 0)), ## ??? (0, 2) more likely
    "ZSL8BOTBOT" : ("ZERO_SUPPRESSED_LITE8_BOTBOT", None, (0, 2)),
    "ZSL8TOPBOT" : ("ZERO_SUPPRESSED_LITE8_TOPBOT", None, (1, 1)),
    "ZSL10"      : ("ZERO_SUPPRESSED_LITE10", None, (0, 0)),
    }

for uModeName, (readoutMode, packetCode, (nTop, nBot)) in modes.items():
    isVirgin = "VIRGIN" in readoutMode.upper()
    ## repack in this mode
    repackName = "siStripRepack{0}".format(uModeName)
    setattr(process, repackName, cms.EDProducer("SiStripDigiToRawModule",
        InputDigis       = (refVR10 if isVirgin else refZS),
        FedReadoutMode   = cms.string(readoutMode),
        PacketCode       = cms.string(packetCode if packetCode else ""),
        UseFedKey        = cms.bool(False),
        UseWrongDigiType = cms.bool(False),
        CopyBufferHeader = cms.bool(False),
        RawDataTag       = cms.InputTag('rawDataCollector')
        ))
    seq *= getattr(process, repackName)
    ## unpack
    unpackName = "siStripDigisRepacked{0}".format(uModeName)
    setattr(process, unpackName, siStripDigis.clone(ProductLabel=cms.InputTag(repackName)))
    seq *= getattr(process, unpackName)
    ## diff
    diffName = "siStripDigiDiff{0}".format(uModeName)
    diffParams = {
        "A" : (refVR10 if isVirgin else refZS),
        "B" : cms.InputTag(unpackName, "VirginRaw" if isVirgin else "ZeroSuppressed"),
        "nDiffToPrint" : uc.uint64(10),
        "BottomBitsToIgnore" : cms.uint32(nBot),
        "TopBitsToIgnore" : cms.uint32(nTop)
        }
    if isVirgin:
        diffParams["IgnoreBadChannels"] = cms.bool(True)
    else:
        diffParams["IgnoreAllZeros"] = cms.bool(True) ## workaround for packer removing all zero strips for ZS
    setattr(process, diffName, cms.EDAnalyzer(("SiStripRawDigiDiff" if isVirgin else "SiStripDigiDiff"), **diffParams))
    seq *= getattr(process, diffName)

process.path = cms.Path(seq)

process.MessageLogger = cms.Service(
    "MessageLogger",
    destinations = uc.vstring(
        "critical",
    ##    "detailedInfo",
        ),
    ##detailedInfo = uc.PSet(
    ##    threshold = uc.string("DEBUG")
    ##    ),
    ##debugModules = uc.vstring("siStripDigisNew", "diffVR10"),
    ##debugModules = uc.vstring("siStripDigisRepackedZS8"),
    ##categories=uc.vstring("FEDBuffer", "SiStripRawToDigi")
    )

#process.siStripDigisRepackedZS8.FedEventDumpFreq = uc.int32(1) ## dump all FED events - HUGE
