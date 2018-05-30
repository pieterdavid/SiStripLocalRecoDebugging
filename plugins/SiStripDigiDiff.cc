#include "FWCore/Framework/interface/stream/EDAnalyzer.h"
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Utilities/interface/InputTag.h"

#include "DataFormats/Common/interface/DetSetVector.h"
#include "DataFormats/SiStripDigi/interface/SiStripDigi.h"

class SiStripDigiDiff : public edm::stream::EDAnalyzer<>
{
public:
  SiStripDigiDiff(const edm::ParameterSet& conf);
  void analyze(const edm::Event& evt, const edm::EventSetup& eSetup) override;
private:
  edm::EDGetTokenT<edm::DetSetVector<SiStripDigi>> m_digiAtoken;
  edm::EDGetTokenT<edm::DetSetVector<SiStripDigi>> m_digiBtoken;
  uint16_t m_adcMask;
  std::size_t m_nDiffToPrint;
  bool m_ignoreAllZeros;
private:
  // helper, return true if equal
  bool compareDet(const edm::DetSet<SiStripDigi>& detA, const edm::DetSet<SiStripDigi>& detB) const;
};

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(SiStripDigiDiff);

#include "DataFormats/Common/interface/Handle.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"

SiStripDigiDiff::SiStripDigiDiff(const edm::ParameterSet& conf)
{
  const auto inTagA = conf.getParameter<edm::InputTag>("A");
  m_digiAtoken = consumes<edm::DetSetVector<SiStripDigi>>(inTagA);
  const auto inTagB = conf.getParameter<edm::InputTag>("B");
  m_digiBtoken = consumes<edm::DetSetVector<SiStripDigi>>(inTagB);
  m_adcMask = 0x03FF & (~((1<<conf.getParameter<uint32_t>("BottomBitsToIgnore"))-1)); // at most 10, ignore N
  m_nDiffToPrint = conf.getUntrackedParameter<unsigned long long>("nDiffToPrint", 0);
  m_ignoreAllZeros = conf.getParameter<bool>("IgnoreAllZeros");
  edm::LogInfo("SiStripDigiDiff") << "Loading digis from (A) " << inTagA << " and (B) " << inTagB << "\n"
    << "ADCs will be compared after applying the mask " << std::hex << std::showbase << m_adcMask
    << ( m_ignoreAllZeros ? " and removing zero digis" : "");
}

namespace {
  std::string digiListToString(const edm::DetSet<SiStripDigi>& digis)
  {
    std::stringstream out;
    for ( auto digi : digis ) {
      out << " (" << digi.strip() << "," << std::hex << std::showbase << digi.adc() << std::dec << ")";
    }
    return out.str();
  }
}

bool SiStripDigiDiff::compareDet(const edm::DetSet<SiStripDigi>& detA, const edm::DetSet<SiStripDigi>& detB) const
{
  bool hasDiff{false};
  if ( detB.size() != detA.size() ) {
    edm::LogWarning("SiStripDigiDiff") << "Different number of digis for det " << detA.id << ": " << detA.size() << " (A) versus " << detB.size() << " (B)";
    hasDiff = true;
  } else {
    for ( std::size_t i{0}; i != detA.size(); ++i ) {
      if ( ( detA[i].strip() != detB[i].strip() ) || ( (detA[i].adc()&m_adcMask) != (detB[i].adc()&m_adcMask) ) ) {
        hasDiff = true;
      }
    }
  }
  return ! hasDiff;
}

void SiStripDigiDiff::analyze(const edm::Event& evt, const edm::EventSetup& eSetup)
{
  edm::Handle<edm::DetSetVector<SiStripDigi>> digisA;
  evt.getByToken(m_digiAtoken, digisA);
  edm::Handle<edm::DetSetVector<SiStripDigi>> digisB;
  evt.getByToken(m_digiBtoken, digisB);
  //edm::LogInfo("SiStripDigiDiff") << "Loaded digis: " << digisA->size() << " (A) and " << digisB->size() << " (B)";
  std::size_t goodMods{0}, diffMods{0};
  for ( const auto& dsetA : *digisA ) {
    const auto i_dsetB = digisB->find(dsetA.id);
    // A\B
    if ( digisB->end() == i_dsetB ) {
      edm::LogWarning("SiStripDigiDiff") << "No DetSet in B for det " << dsetA.id << " that is in A";
      ++diffMods;
    } else { // A and B: compare
      const auto& dsetB = *i_dsetB;
      bool areEqual;
      if ( m_ignoreAllZeros ) {
        // work around an incompatibility between SiStripFedZeroSuppression and SiStripRawToDigi
        // the former allows some zero Digis (if part of a cluster), the latter removes all zeros
        edm::DetSet<SiStripDigi> dsetA_noz{dsetA.id};
        std::copy_if(std::begin(dsetA), std::end(dsetA), std::back_inserter(dsetA_noz), [] ( SiStripDigi digi ) { return digi.adc() != 0; });
        edm::DetSet<SiStripDigi> dsetB_noz{dsetB.id};
        std::copy_if(std::begin(dsetB), std::end(dsetB), std::back_inserter(dsetB_noz), [] ( SiStripDigi digi ) { return digi.adc() != 0; });
        areEqual = compareDet(dsetA_noz, dsetB_noz);
      } else {
        areEqual = compareDet(dsetA, dsetB);
      }
      if ( areEqual ) {
        ++goodMods;
      } else {
        if ( diffMods < m_nDiffToPrint ) {
          edm::LogInfo("SiStripDigiDiff") << "A digis: " << digiListToString(dsetA);
          edm::LogInfo("SiStripDigiDiff") << "B digis: " << digiListToString(dsetB);
        }
        ++diffMods;
      }
    }
  }
  for ( const auto& dsetB : *digisB ) {
    const auto i_dsetA = digisA->find(dsetB.id);
    // B\A
    if ( digisA->end() == i_dsetA ) {
      edm::LogWarning("SiStripDigiDiff") << "No DetSet in A for det " << dsetB.id << " that is in B";
      ++diffMods;
    }
  }
  edm::LogInfo("SiStripDigiDiff") << "Found " << goodMods << " dets with identical digis and " << diffMods << " with differences";
}
