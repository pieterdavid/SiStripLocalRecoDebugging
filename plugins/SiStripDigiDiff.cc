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
  edm::LogInfo("SiStripDigiDiff") << "Loading digis from (A) " << inTagA << " and (B) " << inTagB;
}

void SiStripDigiDiff::analyze(const edm::Event& evt, const edm::EventSetup& eSetup)
{
  edm::Handle<edm::DetSetVector<SiStripDigi>> digisA;
  evt.getByToken(m_digiAtoken, digisA);
  edm::Handle<edm::DetSetVector<SiStripDigi>> digisB;
  evt.getByToken(m_digiBtoken, digisB);
  edm::LogInfo("SiStripDigiDiff") << "Loaded digis: " << digisA->size() << " (A) and " << digisB->size() << " (B)";
  std::size_t goodMods{0}, diffMods{0};
  for ( const auto& dsetA : *digisA ) {
    const auto i_dsetB = digisB->find(dsetA.id);
    // A\B
    if ( digisB->end() == i_dsetB ) {
      edm::LogWarning("SiStripDigiDiff") << "No DetSet in B for det " << dsetA.id << " that is in A";
      ++diffMods;
    } else { // A and B: compare
      const auto& dsetB = *i_dsetB;
      if ( dsetB.size() != dsetA.size() ) {
        edm::LogWarning("SiStripDigiDiff") << "Different number of raw digis for det " << dsetA.id << ": " << dsetA.size() << " (A) versus " << dsetB.size() << " (B)";
      } else {
        bool hasDiff{false};
        for ( std::size_t i{0}; i != dsetA.size(); ++i ) {
          if ( dsetA[i].strip() != dsetB[i].strip() ) {
            edm::LogWarning("SistripDigiDiff") << "ADC for different strip at index " << i << " for det " << dsetA.id << ": " << dsetA[i].strip() << "," << dsetA[i].adc() << " (A) versus " << dsetB[i].strip() << "," << dsetB[i].adc() << " (B)";
            hasDiff = true;
          } else if ( dsetA[i].adc() != dsetB[i].adc() ) {
            edm::LogWarning("SistripDigiDiff") << "Different ADC for strip " << dsetA[i].strip() << " in det " << dsetA.id << ": " << dsetA[i].adc() << " (A) versus " << dsetB[i].adc() << " (B)";
            hasDiff = true;
          }
        }
        if ( ! hasDiff ) { ++goodMods; } else { ++diffMods; }
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
  edm::LogInfo("SiStripDigiDiff") << "Found " << goodMods << " dets with identical raw digis and " << diffMods << " with differences";
}
