// -*- C++ -*-
//
// Package:    UserCode/SiStripClustersPrinter
// Class:      SiStripClustersPrinter
// 
/**\class SiStripClustersPrinter SiStripClustersPrinter.cc UserCode/SiStripClustersPrinter/plugins/SiStripClustersPrinter.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Alessia Saggio
//         Created:  Thu, 16 Jun 2016 10:13:36 GMT
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
#include "DataFormats/Common/interface/DetSetVectorNew.h"
#include "DataFormats/SiStripCluster/interface/SiStripCluster.h"

//
// class declaration
//

// If the analyzer does not use TFileService, please remove
// the template argument to the base class so the class inherits
// from  edm::one::EDAnalyzer<> and also remove the line from
// constructor "usesResource("TFileService");"
// This will improve performance in multithreaded jobs.

class SiStripClustersPrinter : public edm::one::EDAnalyzer<edm::one::SharedResources>  {

    public:
      explicit SiStripClustersPrinter(const edm::ParameterSet&);
      ~SiStripClustersPrinter();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);


   private:
      virtual void beginJob() override;
      virtual void analyze(const edm::Event&, const edm::EventSetup&) override;
      virtual void endJob() override;

      // ----------member data ---------------------------
edm::EDGetTokenT<edmNew::DetSetVector<SiStripCluster>> m_clustersToken;

};

//
// constants, enums and typedefs
//

//
// static data member definitions
//

//
// constructors and destructor
//
SiStripClustersPrinter::SiStripClustersPrinter(const edm::ParameterSet& iConfig)

{
   //now do what ever initialization is needed
   usesResource("TFileService");
   m_clustersToken = consumes<edmNew::DetSetVector<SiStripCluster>>(edm::InputTag("siStripClusters"));
}


SiStripClustersPrinter::~SiStripClustersPrinter()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//
#include <iostream>
// ------------ method called for each event  ------------
void
SiStripClustersPrinter::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   using namespace edm;


#ifdef THIS_IS_AN_EVENT_EXAMPLE
   Handle<ExampleData> pIn;
   iEvent.getByLabel("example",pIn);
#endif
   
#ifdef THIS_IS_AN_EVENTSETUP_EXAMPLE
   ESHandle<SetupData> pSetup;
   iSetup.get<SetupRecord>().get(pSetup);
#endif

edm::Handle<edmNew::DetSetVector<SiStripCluster>> clusters;
iEvent.getByToken(m_clustersToken, clusters);
std::cout << "number of clusters: " << clusters->size() << std::endl;
}


// ------------ method called once each job just before starting event loop  ------------
void 
SiStripClustersPrinter::beginJob()
{}

// ------------ method called once each job just after ending the event loop  ------------
void 
SiStripClustersPrinter::endJob() 
{}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
SiStripClustersPrinter::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(SiStripClustersPrinter);
