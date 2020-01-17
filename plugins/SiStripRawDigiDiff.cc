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
  bool m_ignoreBadChannel;
private:
  // helper, return true if equal
  bool compareDet(const edm::DetSet<SiStripRawDigi>& detA, const edm::DetSet<SiStripRawDigi>& detB) const;
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
  const uint32_t bbIg = conf.getParameter<uint32_t>("BottomBitsToIgnore");
  const uint32_t tbIg = conf.getParameter<uint32_t>("TopBitsToIgnore");
  m_adcMask = ( bbIg || tbIg ) ? ( ((1<<(10-tbIg-bbIg))-1) << bbIg ) : -1; // 0xffff if 0 and 0
  m_nDiffToPrint = conf.getUntrackedParameter<unsigned long long>("nDiffToPrint", 0);
  m_ignoreBadChannel = conf.getParameter<bool>("IgnoreBadChannels");
  edm::LogInfo("SiStripRawDigiDiff") << "Loading digis from (A) " << inTagA << " and (B) " << inTagB << "\n"
    << "ADCs will be compared after applying the mask " << std::hex << std::showbase << m_adcMask
    << (m_ignoreBadChannel?" and differences in trailing zeros (bad channels) will be ignored":"");
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

bool SiStripRawDigiDiff::compareDet(const edm::DetSet<SiStripRawDigi>& detA, const edm::DetSet<SiStripRawDigi>& detB) const
{
  bool hasDiff{false};
  if ( detB.size() != detA.size() ) {
    if ( m_ignoreBadChannel ) { // accept as equal based on the common part if one has only zeros beyond that
      if ( detA.size() < detB.size() ) {
        if ( std::all_of(std::begin(detB)+detA.size(), std::end(detB), [] ( SiStripRawDigi digi ) { return digi.adc() == 0; }) ) {
          edm::DetSet<SiStripRawDigi> detB_short{detB.id};
          std::copy_n(std::begin(detB), detA.size(), std::back_inserter(detB_short));
          hasDiff = ! compareDet(detA, detB_short);
        } else {
          hasDiff = true;
        }
      } else { // detA.size > detB.size
        if ( std::all_of(std::begin(detA)+detB.size(), std::end(detA), [] ( SiStripRawDigi digi ) { return digi.adc() == 0; }) ) {
          edm::DetSet<SiStripRawDigi> detA_short{detA.id};
          std::copy_n(std::begin(detA), detB.size(), std::back_inserter(detA_short));
          hasDiff = ! compareDet(detA_short, detB);
        } else {
          hasDiff = true;
        }
      }
    } else {
      hasDiff = true;
    }
    if ( hasDiff ) {
      edm::LogWarning("SiStripRawDigiDiff") << "Different number of raw digis for det " << detA.id << ": " << detA.size() << " (A) versus " << detB.size() << " (B)";
    }
  } else {
    for ( std::size_t i{0}; i != detA.size(); ++i ) {
      if ( (detA[i].adc()&m_adcMask) != (detB[i].adc()&m_adcMask) ) {
        hasDiff = true;
      }
    }
  }
  return ! hasDiff;
}

void SiStripRawDigiDiff::analyze(const edm::Event& evt, const edm::EventSetup& eSetup)
{
  edm::Handle<edm::DetSetVector<SiStripRawDigi>> digisA;
  evt.getByToken(m_digiAtoken, digisA);
  edm::Handle<edm::DetSetVector<SiStripRawDigi>> digisB;
  evt.getByToken(m_digiBtoken, digisB);
  //edm::LogInfo("SiStripRawDigiDiff") << "Loaded digis: " << digisA->size() << " (A) and " << digisB->size() << " (B)";
  std::size_t goodMods{0}, diffMods{0};
  for ( const auto& dsetA : *digisA ) {
    const auto i_dsetB = digisB->find(dsetA.id);
    // A\B
    if ( digisB->end() == i_dsetB ) {
      if ( ! ( ( m_ignoreBadChannel ) && ( std::all_of(std::begin(dsetA), std::end(dsetA), [] ( SiStripRawDigi digi ) { return digi.adc() == 0; }) ) ) ) {
        edm::LogWarning("SiStripRawDigiDiff") << "No DetSet in B for det " << dsetA.id << " that is in A";
        if ( diffMods < m_nDiffToPrint ) {
          edm::LogInfo("SiStripRawDigiDiff") << "A digis: " << rawDigiListToString(dsetA);
        }
        ++diffMods;
      }
    } else { // A and B: compare
      const auto& dsetB = *i_dsetB;
      if ( compareDet(dsetA, dsetB) ) {
        ++goodMods;
      } else {
        if ( diffMods < m_nDiffToPrint ) {
          edm::LogInfo("SiStripRawDigiDiff") << "Differences for det " << dsetA.id;
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
      if ( ! ( ( m_ignoreBadChannel ) && ( std::all_of(std::begin(dsetB), std::end(dsetB), [] ( SiStripRawDigi digi ) { return digi.adc() == 0; }) ) ) ) {
        edm::LogWarning("SiStripRawDigiDiff") << "No DetSet in A for det " << dsetB.id << " that is in B";
        if ( diffMods < m_nDiffToPrint ) {
          edm::LogInfo("SiStripRawDigiDiff") << "B digis: " << rawDigiListToString(dsetB);
        }
        ++diffMods;
      }
    }
  }
  edm::LogInfo("SiStripRawDigiDiff") << "Found " << goodMods << " dets with identical raw digis and " << diffMods << " with differences";
}
