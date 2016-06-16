// -*- C++ -*-
//
// Package:    UserCode/SiStripLocalRecoMonitoring
// Class:      SiStripCommonModeValuesPrinter
//
/**\class SiStripCommonModeValuesPrinter SiStripCommonModeValuesPrinter.cc UserCode/SiStripLocalRecoMonitoring/plugins/SiStripCommonModeValuesPrinter.cc

 Description: Read the common mode values produced by the SiStrip unpacker

 Implementation:
     Simple example & test
*/
//
// Original Author:  Pieter David
//         Created:  Fri, 27 May 2016 11:26:03 GMT
//
//

// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/one/EDAnalyzer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "FWCore/Framework/interface/ConsumesCollector.h"

#include "DataFormats/Common/interface/DetSetVector.h"
#include "DataFormats/SiStripDigi/interface/SiStripRawDigi.h"

//
// class declaration
//
class SiStripCommonModeValuesPrinter : public edm::one::EDAnalyzer<>  {
   public:
      explicit SiStripCommonModeValuesPrinter(const edm::ParameterSet&);
      ~SiStripCommonModeValuesPrinter();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void beginJob() override;
      virtual void analyze(const edm::Event&, const edm::EventSetup&) override;
      virtual void endJob() override;

      // ----------member data ---------------------------
      edm::EDGetTokenT<edm::DetSetVector<SiStripRawDigi>> m_cmDigiTok;
};

SiStripCommonModeValuesPrinter::SiStripCommonModeValuesPrinter(const edm::ParameterSet& iConfig)
{
  m_cmDigiTok = consumesCollector().consumes<edm::DetSetVector<SiStripRawDigi>>(
      iConfig.getUntrackedParameter<edm::InputTag>("CMDigis", edm::InputTag("siStripDigis", "CommonMode")));
}

SiStripCommonModeValuesPrinter::~SiStripCommonModeValuesPrinter()
{}

#include <iostream>

// ------------ method called for each event  ------------
void SiStripCommonModeValuesPrinter::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
  using namespace edm;
  using std::cout;
  using std::endl;

  Handle<DetSetVector<SiStripRawDigi>> cmDigis;
  iEvent.getByToken(m_cmDigiTok, cmDigis);

  cout << "SiStrip common modes: " << cmDigis->size() << " detsets" << endl;
  for ( const auto& ds : *cmDigis ) {
    cout << "  module " << std::hex << ds.detId() << std::dec << " : [ ";
    for ( const auto id : ds ) {
      cout << id.adc() << ", ";
    }
    cout << "]" << endl;
  }
}


// ------------ method called once each job just before starting event loop  ------------
void SiStripCommonModeValuesPrinter::beginJob()
{}

// ------------ method called once each job just after ending the event loop  ------------
void SiStripCommonModeValuesPrinter::endJob()
{}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
SiStripCommonModeValuesPrinter::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(SiStripCommonModeValuesPrinter);
