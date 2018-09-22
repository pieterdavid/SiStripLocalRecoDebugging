#include "FWCore/Framework/interface/stream/EDAnalyzer.h"
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Utilities/interface/InputTag.h"

#include "DataFormats/Common/interface/DetSetVector.h"
#include "DataFormats/SiStripDigi/interface/SiStripDigi.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

class SiStripDigiStatsDiff : public edm::stream::EDAnalyzer<>
{
public:
  SiStripDigiStatsDiff(const edm::ParameterSet& conf);
  void analyze(const edm::Event& evt, const edm::EventSetup& eSetup) override;
private:
  edm::EDGetTokenT<edm::DetSetVector<SiStripDigi>> m_digiAtoken;
  edm::EDGetTokenT<edm::DetSetVector<SiStripDigi>> m_digiBtoken;
  TH1F* h_nDigisA, * h_nDigisB, * h_nDigisDiff, * h_nDigisRelDiff;
};

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(SiStripDigiStatsDiff);

#include "DataFormats/Common/interface/Handle.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"

SiStripDigiStatsDiff::SiStripDigiStatsDiff(const edm::ParameterSet& conf)
{
  const auto inTagA = conf.getParameter<edm::InputTag>("A");
  m_digiAtoken = consumes<edm::DetSetVector<SiStripDigi>>(inTagA);
  const auto inTagB = conf.getParameter<edm::InputTag>("B");
  m_digiBtoken = consumes<edm::DetSetVector<SiStripDigi>>(inTagB);
  edm::LogInfo("SiStripDigiStatsDiff") << "Loading digis from (A) " << inTagA << " and (B) " << inTagB;
  edm::Service<TFileService> fs;
  h_nDigisA = fs->make<TH1F>("nDigisA", ("nDigis per module in collection "+inTagA.encode()).c_str(), 400, 0., 400.);
  h_nDigisB = fs->make<TH1F>("nDigisB", ("nDigis per module in collection "+inTagB.encode()).c_str(), 400, 0., 400.);
  h_nDigisDiff = fs->make<TH1F>("nDigisDiff", ("Differences in nDigis per module between the collections "+inTagA.encode()+" and "+inTagB.encode()).c_str(), 200, -100., 100.);
  h_nDigisRelDiff = fs->make<TH1F>("nDigisRelDiff", ("Relative ifferences in nDigis per module between the collections "+inTagA.encode()+" and "+inTagB.encode()+" (B-A)").c_str(), 100, -.2, .2);
}

void SiStripDigiStatsDiff::analyze(const edm::Event& evt, const edm::EventSetup& eSetup)
{
  edm::Handle<edm::DetSetVector<SiStripDigi>> digisA;
  evt.getByToken(m_digiAtoken, digisA);
  edm::Handle<edm::DetSetVector<SiStripDigi>> digisB;
  evt.getByToken(m_digiBtoken, digisB);
  //edm::LogInfo("SiStripDigiStatsDiff") << "Loaded digis: " << digisA->size() << " (A) and " << digisB->size() << " (B)";
  for ( const auto& dsetA : *digisA ) {
    h_nDigisA->Fill(dsetA.size());
    const auto i_dsetB = digisB->find(dsetA.id);
    if ( digisB->end() != i_dsetB ) { // A and B: compare
      const auto& dsetB = *i_dsetB;
      h_nDigisDiff->Fill(dsetB.size()-dsetA.size());
      h_nDigisRelDiff->Fill(.5*(dsetB.size()-dsetA.size())/(dsetB.size()+dsetA.size()));
    } else { // A\B
      h_nDigisDiff->Fill(-dsetA.size());
      h_nDigisRelDiff->Fill(-1.);
    }
  }
  for ( const auto& dsetB : *digisB ) {
    h_nDigisB->Fill(dsetB.size());
    const auto i_dsetA = digisA->find(dsetB.id);
    if ( digisA->end() == i_dsetA ) { // B\A
      h_nDigisDiff->Fill(dsetB.size());
      h_nDigisRelDiff->Fill(1.);
    }
  }
}
