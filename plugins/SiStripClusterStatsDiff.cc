#include "FWCore/Framework/interface/stream/EDAnalyzer.h"
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Utilities/interface/InputTag.h"

#include "DataFormats/Common/interface/DetSetVector.h"
#include "DataFormats/Common/interface/DetSetVectorNew.h"
#include "DataFormats/SiStripCluster/interface/SiStripCluster.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

class SiStripClusterStatsDiff : public edm::stream::EDAnalyzer<>
{
public:
  SiStripClusterStatsDiff(const edm::ParameterSet& conf);
  void analyze(const edm::Event& evt, const edm::EventSetup& eSetup) override;
private:
  edm::EDGetTokenT<edmNew::DetSetVector<SiStripCluster>> m_digiAtoken;
  edm::EDGetTokenT<edmNew::DetSetVector<SiStripCluster>> m_digiBtoken;
  TH1F* h_nClusA, * h_nClusB, * h_nClusDiff, * h_nClusRelDiff;
};

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(SiStripClusterStatsDiff);

#include "DataFormats/Common/interface/Handle.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"

SiStripClusterStatsDiff::SiStripClusterStatsDiff(const edm::ParameterSet& conf)
{
  const auto inTagA = conf.getParameter<edm::InputTag>("A");
  m_digiAtoken = consumes<edmNew::DetSetVector<SiStripCluster>>(inTagA);
  const auto inTagB = conf.getParameter<edm::InputTag>("B");
  m_digiBtoken = consumes<edmNew::DetSetVector<SiStripCluster>>(inTagB);
  edm::LogInfo("SiStripClusterStatsDiff") << "Loading digis from (A) " << inTagA << " and (B) " << inTagB;
  edm::Service<TFileService> fs;
  h_nClusA = fs->make<TH1F>("nClusA", ("nClus per module in collection "+inTagA.encode()).c_str(), 100, 0., 100.);
  h_nClusB = fs->make<TH1F>("nClusB", ("nClus per module in collection "+inTagB.encode()).c_str(), 100, 0., 100.);
  h_nClusDiff = fs->make<TH1F>("nClusDiff", ("Differences in nClus per module between the collections "+inTagA.encode()+" and "+inTagB.encode()).c_str(), 40, -20., 20.);
  h_nClusRelDiff = fs->make<TH1F>("nClusRelDiff", ("Relative ifferences in nClus per module between the collections "+inTagA.encode()+" and "+inTagB.encode()+" (B-A)").c_str(), 100, -.05, .05);
}

void SiStripClusterStatsDiff::analyze(const edm::Event& evt, const edm::EventSetup& eSetup)
{
  edm::Handle<edmNew::DetSetVector<SiStripCluster>> digisA;
  evt.getByToken(m_digiAtoken, digisA);
  edm::Handle<edmNew::DetSetVector<SiStripCluster>> digisB;
  evt.getByToken(m_digiBtoken, digisB);
  for ( const auto& dsetA : *digisA ) {
    const auto i_dsetB = digisB->find(dsetA.id());
    h_nClusA->Fill(dsetA.size());
    if ( digisB->end() != i_dsetB ) { // A and B: compare
      const auto& dsetB = *i_dsetB;
      h_nClusDiff->Fill(dsetB.size()-dsetA.size());
      h_nClusRelDiff->Fill(.5*(dsetB.size()-dsetA.size())/(dsetB.size()+dsetA.size()));
    } else { // A\B
      h_nClusDiff->Fill(-dsetA.size());
      h_nClusRelDiff->Fill(-1.);
    }
  }
  for ( const auto& dsetB : *digisB ) {
    h_nClusB->Fill(dsetB.size());
    const auto i_dsetA = digisA->find(dsetB.id());
    if ( digisA->end() == i_dsetA ) { // B\A
      h_nClusDiff->Fill(dsetB.size());
      h_nClusRelDiff->Fill(1.);
    }
  }
}
