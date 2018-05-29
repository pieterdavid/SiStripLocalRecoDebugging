#include "FWCore/Framework/interface/stream/EDAnalyzer.h"
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Utilities/interface/InputTag.h"

#include "DataFormats/Common/interface/DetSetVector.h"
#include "DataFormats/SiStripDigi/interface/SiStripRawDigi.h"

class SiStripRawDigiDiff : public edm::stream::EDAnalyzer<>
{
public:
  SiStripRawDigiDiff(const edm::ParameterSet& conf);
  void analyze(const edm::Event& evt, const edm::EventSetup& eSetup) override;
private:
  edm::EDGetTokenT<edm::DetSetVector<SiStripRawDigi>> m_digiAtoken;
  edm::EDGetTokenT<edm::DetSetVector<SiStripRawDigi>> m_digiBtoken;
  uint16_t m_adcMask;
  std::size_t m_nDiffToPrint;
};

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(SiStripRawDigiDiff);

#include "DataFormats/Common/interface/Handle.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"

SiStripRawDigiDiff::SiStripRawDigiDiff(const edm::ParameterSet& conf)
{
  const auto inTagA = conf.getParameter<edm::InputTag>("A");
  m_digiAtoken = consumes<edm::DetSetVector<SiStripRawDigi>>(inTagA);
  const auto inTagB = conf.getParameter<edm::InputTag>("B");
  m_digiBtoken = consumes<edm::DetSetVector<SiStripRawDigi>>(inTagB);
  edm::LogInfo("SiStripRawDigiDiff") << "Loading digis from (A) " << inTagA << " and (B) " << inTagB;
  m_adcMask = 0x03FF & (~((1<<conf.getParameter<uint32_t>("BottomBitsToIgnore"))-1)); // at most 10, ignore N
  edm::LogInfo("SiStripRawDigiDiff") << "ADCs will be compared after applying the mask " << std::hex << std::showbase << m_adcMask;
  m_nDiffToPrint = conf.getUntrackedParameter<unsigned long long>("nDiffToPrint", 0);
}

namespace {
  std::string rawDigiListToString(const edm::DetSet<SiStripRawDigi>& digis)
  {
    std::stringstream out;
    for ( auto digi : digis ) {
      out << " " << std::hex << std::showbase << digi.adc() << std::dec;
    }
    return out.str();
  }
}

void SiStripRawDigiDiff::analyze(const edm::Event& evt, const edm::EventSetup& eSetup)
{
  edm::Handle<edm::DetSetVector<SiStripRawDigi>> digisA;
  evt.getByToken(m_digiAtoken, digisA);
  edm::Handle<edm::DetSetVector<SiStripRawDigi>> digisB;
  evt.getByToken(m_digiBtoken, digisB);
  edm::LogInfo("SiStripRawDigiDiff") << "Loaded digis: " << digisA->size() << " (A) and " << digisB->size() << " (B)";
  std::size_t goodMods{0}, diffMods{0};
  for ( const auto& dsetA : *digisA ) {
    const auto i_dsetB = digisB->find(dsetA.id);
    // A\B
    if ( digisB->end() == i_dsetB ) {
      edm::LogWarning("SiStripRawDigiDiff") << "No DetSet in B for det " << dsetA.id << " that is in A";
      ++diffMods;
    } else { // A and B: compare
      const auto& dsetB = *i_dsetB;
      bool hasDiff{false};
      if ( dsetB.size() != dsetA.size() ) {
        edm::LogWarning("SiStripRawDigiDiff") << "Different number of raw digis for det " << dsetA.id << ": " << dsetA.size() << " (A) versus " << dsetB.size() << " (B)";
        hasDiff = true;
      } else {
        for ( std::size_t i{0}; i != dsetA.size(); ++i ) {
          if ( (dsetA[i].adc()&m_adcMask) != (dsetB[i].adc()&m_adcMask) ) {
            edm::LogWarning("SistripRawDigiDiff") << "Different ADC at index " << i << " for det " << dsetA.id << ": " << dsetA[i].adc() << " (A) versus " << dsetB[i].adc() << " (B)";
            hasDiff = true;
          }
        }
      }
      if ( ! hasDiff ) {
        ++goodMods;
      } else {
        if ( diffMods < m_nDiffToPrint ) {
          edm::LogInfo("SiStripRawDigiDiff") << "A digis: " << rawDigiListToString(dsetA);
          edm::LogInfo("SiStripRawDigiDiff") << "B digis: " << rawDigiListToString(dsetB);
        }
        ++diffMods;
      }
    }
  }
  for ( const auto& dsetB : *digisB ) {
    const auto i_dsetA = digisA->find(dsetB.id);
    // B\A
    if ( digisA->end() == i_dsetA ) {
      edm::LogWarning("SiStripRawDigiDiff") << "No DetSet in A for det " << dsetB.id << " that is in B";
      ++diffMods;
    }
  }
  edm::LogInfo("SiStripRawDigiDiff") << "Found " << goodMods << " dets with identical raw digis and " << diffMods << " with differences";
}
