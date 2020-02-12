#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/one/EDAnalyzer.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "CondFormats/SiStripObjects/interface/SiStripApvGain.h"
#include "CondFormats/DataRecord/interface/SiStripApvGainRcd.h"

#include "CalibFormats/SiStripObjects/interface/SiStripGain.h"
#include "CalibFormats/SiStripObjects/interface/SiStripQuality.h"
#include "CalibTracker/Records/interface/SiStripDependentRecords.h"

#include "CalibTracker/SiStripCommon/interface/SiStripDetInfoFileReader.h"

class PrintSiStripGain : public edm::one::EDAnalyzer<> {
public:
  explicit PrintSiStripGain(const edm::ParameterSet&);
  ~PrintSiStripGain() override;
private:
  void analyze(const edm::Event&, const edm::EventSetup&) override;

  std::unique_ptr<SiStripDetInfoFileReader> m_reader;

  std::vector<uint32_t> m_dets;
};

PrintSiStripGain::PrintSiStripGain(const edm::ParameterSet& conf) {
  m_dets = conf.getParameter<std::vector<uint32_t>>("modules");
  m_reader = std::make_unique<SiStripDetInfoFileReader>(edm::FileInPath("CalibTracker/SiStripCommon/data/SiStripDetInfo.dat").fullPath());
}

PrintSiStripGain::~PrintSiStripGain() {}


void PrintSiStripGain::analyze(const edm::Event& event, const edm::EventSetup& eventSetup)
{
  edm::ESHandle<TrackerTopology> tTopo;
  eventSetup.get<TrackerTopologyRcd>().get(tTopo);

  edm::ESHandle<SiStripQuality> quality;
  eventSetup.get<SiStripQualityRcd>().get(quality);

  edm::ESHandle<SiStripGain> gain;
  eventSetup.get<SiStripGainRcd>().get(gain);

  edm::ESHandle<SiStripApvGain> tickmarkGain, particleGain;
  eventSetup.get<SiStripApvGainRcd>().get(tickmarkGain);
  eventSetup.get<SiStripApvGain2Rcd>().get(particleGain);

  for ( const auto det : m_dets ) {
    const auto nAPVs = m_reader->getNumberOfApvsAndStripLength(det).first;
    edm::LogWarning("PrintSiStripGain") << "Checking module " << det << ": " << tTopo->print(det);
    const auto gainRange = gain->getRange(det);
    const auto g1Range = tickmarkGain->getRange(det);
    const auto g2Range = particleGain->getRange(det);
    if ( quality->IsModuleBad(det) ) {
      edm::LogWarning("PrintSiStripGain") << "Module " << det << " is bad (from SiStripQuality)";
    } else {
      for ( std::size_t iAPV{0}; iAPV != nAPVs; ++iAPV ) {
        if ( quality->IsFiberBad(det, iAPV/2) ) {
          edm::LogWarning("PrintSiStripGain") << "Module " << det << " APV " << iAPV << " is bad (fiber #" << iAPV/2 << ")";
        } else if ( quality->IsApvBad(det, iAPV) ) {
          edm::LogWarning("PrintSiStripGain") << "Module " << det << " APV " << iAPV << " is bad";
        } else {
          edm::LogWarning("PrintSiStripGain") << "Gain values for module " << det << " APV#" << iAPV << ": "
            << "Gain=G1(" << SiStripApvGain::getApvGain(iAPV, g1Range) << ")*"
            << "G2(" << SiStripApvGain::getApvGain(iAPV, g2Range) << ")="
            << SiStripGain::getApvGain(iAPV, gainRange);
        }
      }
    }
  }
  // scan all dets for Gain>3
  for ( const auto det : m_reader->getAllDetIds() ) {
    const auto nAPVs = m_reader->getNumberOfApvsAndStripLength(det).first;
    for ( std::size_t iAPV{0}; iAPV != nAPVs; ++iAPV ) {
      if ( ( ! quality->IsFiberBad(det, iAPV/2) ) && ( ! quality->IsApvBad(det, iAPV) ) ) {
        const auto gainRange = gain->getRange(det);
        const auto g1Range = tickmarkGain->getRange(det);
        const auto g2Range = particleGain->getRange(det);
        if ( SiStripGain::getApvGain(iAPV, gainRange) > 3. ) {
          edm::LogWarning("PrintSiStripGain") << "Gain values for module " << det << " APV#" << iAPV << ": "
            << "Gain=G1(" << SiStripApvGain::getApvGain(iAPV, g1Range) << ")*"
            << "G2(" << SiStripApvGain::getApvGain(iAPV, g2Range) << ")="
            << SiStripGain::getApvGain(iAPV, gainRange)
            << "\n" << tTopo->print(det);
        }
      }
    }
  }
}

DEFINE_FWK_MODULE(PrintSiStripGain);
