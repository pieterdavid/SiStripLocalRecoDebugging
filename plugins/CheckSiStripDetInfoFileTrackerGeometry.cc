#include "FWCore/Framework/interface/one/EDAnalyzer.h"
#include "CalibTracker/SiStripCommon/interface/SiStripDetInfoFileReader.h"
#include "Geometry/TrackerGeometryBuilder/interface/TrackerGeometry.h"
#include "Geometry/TrackerGeometryBuilder/interface/StripGeomDetUnit.h"
#include "Geometry/Records/interface/TrackerDigiGeometryRecord.h"
#include "FWCore/Framework/interface/MakerMacros.h"

namespace {

class CheckSiStripDetInfoFileTrackerGeometry : public edm::one::EDAnalyzer<>
{
public:
  explicit CheckSiStripDetInfoFileTrackerGeometry(const edm::ParameterSet& iPSet);

  void analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup) override;
private:
  SiStripDetInfoFileReader m_reader;
  edm::ESGetToken<TrackerGeometry, TrackerDigiGeometryRecord> m_tkGeomToken;
};

CheckSiStripDetInfoFileTrackerGeometry::CheckSiStripDetInfoFileTrackerGeometry(const edm::ParameterSet& iPSet)
  : m_reader(iPSet.getUntrackedParameter<edm::FileInPath>("filePath", edm::FileInPath{"CalibTracker/SiStripCommon/data/SiStripDetInfo.dat"}).fullPath())
{
  m_tkGeomToken = esConsumes<TrackerGeometry, TrackerDigiGeometryRecord>();
}

void CheckSiStripDetInfoFileTrackerGeometry::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
  const auto& tkGeom = iSetup.getData(m_tkGeomToken);
  std::size_t nStripDetGeom{0};
  for ( const auto det : tkGeom.detUnits() ) {
    const StripGeomDetUnit* stripDet = dynamic_cast<const StripGeomDetUnit*>(det);
    if ( stripDet != nullptr ) {
      ++nStripDetGeom;
    }
  }
  const auto fileDetIdList = m_reader.getAllDetIds();
  edm::LogInfo("CheckSiStripDetInfoFileTrackerGeometry") << "Number of DetIds from file: " << fileDetIdList.size() << "; from TrackerGeometry: " << nStripDetGeom;
}

}
DEFINE_FWK_MODULE(CheckSiStripDetInfoFileTrackerGeometry);
