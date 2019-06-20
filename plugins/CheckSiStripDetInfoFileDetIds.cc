#include "FWCore/Framework/interface/one/EDAnalyzer.h"
#include "CalibTracker/SiStripCommon/interface/SiStripDetInfoFileReader.h"
#include "Geometry/TrackerNumberingBuilder/interface/utils.h"
#include "Geometry/Records/interface/IdealGeometryRecord.h"
#include "Geometry/TrackerNumberingBuilder/interface/GeometricDet.h"
#include "DataFormats/TrackerCommon/interface/SiStripEnums.h"
#include "FWCore/Framework/interface/MakerMacros.h"

namespace {

class CheckSiStripDetInfoFileDetIds : public edm::one::EDAnalyzer<>
{
public:
  explicit CheckSiStripDetInfoFileDetIds(const edm::ParameterSet& iPSet);

  void analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup) override;
private:
  SiStripDetInfoFileReader m_reader;
  edm::ESGetToken<GeometricDet, IdealGeometryRecord> m_geomDetToken;
};

CheckSiStripDetInfoFileDetIds::CheckSiStripDetInfoFileDetIds(const edm::ParameterSet& iPSet)
  : m_reader(iPSet.getUntrackedParameter<edm::FileInPath>("filePath", edm::FileInPath{"CalibTracker/SiStripCommon/data/SiStripDetInfo.dat"}).fullPath())
{
  m_geomDetToken = esConsumes<GeometricDet, IdealGeometryRecord>();
}

void CheckSiStripDetInfoFileDetIds::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
  const auto& geomDet = iSetup.getData(m_geomDetToken);
  const auto geomDetIdList = getSiStripDetIds(geomDet);
  const auto fileDetIdList = m_reader.getAllDetIds();
  edm::LogInfo("CheckSiStripDetInfoFileDetIds") << "Number of DetIds from file: " << fileDetIdList.size() << "; from GeometricDet: " << geomDetIdList.size();
  const auto nToCheckEqual = std::min(fileDetIdList.size(), geomDetIdList.size());
  for ( std::size_t i{0}; i < nToCheckEqual; ++i ) {
    if ( fileDetIdList[i] != geomDetIdList[i] ) {
      edm::LogInfo("CheckSiStripDetInfoFileDetIds") << "DetId#" << i << " is different: " << fileDetIdList[i] << " , " << geomDetIdList[i];
    }
  }
}

}
DEFINE_FWK_MODULE(CheckSiStripDetInfoFileDetIds);
