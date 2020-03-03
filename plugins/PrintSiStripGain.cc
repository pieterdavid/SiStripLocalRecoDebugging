#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/one/EDAnalyzer.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "CondFormats/SiStripObjects/interface/SiStripApvGain.h"
#include "CondFormats/DataRecord/interface/SiStripApvGainRcd.h"

#include "CalibFormats/SiStripObjects/interface/SiStripGain.h"
#include "CalibFormats/SiStripObjects/interface/SiStripQuality.h"
#include "CalibTracker/Records/interface/SiStripDependentRecords.h"

#include "CalibTracker/SiStripCommon/interface/SiStripDetInfoFileReader.h"

#include "Geometry/TrackerGeometryBuilder/interface/TrackerGeometry.h"
#include "Geometry/CommonTopologies/interface/StripTopology.h"
#include <TVector3.h>

class PrintSiStripGain : public edm::one::EDAnalyzer<> {
public:
  explicit PrintSiStripGain(const edm::ParameterSet&);
  ~PrintSiStripGain() override;
private:
  void analyze(const edm::Event&, const edm::EventSetup&) override;

  std::unique_ptr<SiStripDetInfoFileReader> m_reader;

  std::vector<uint32_t> m_dets;
};

PrintSiStripGain::PrintSiStripGain(const edm::ParameterSet& conf) {
  m_dets = conf.getParameter<std::vector<uint32_t>>("modules");
  m_reader = std::make_unique<SiStripDetInfoFileReader>(edm::FileInPath("CalibTracker/SiStripCommon/data/SiStripDetInfo.dat").fullPath());
}

PrintSiStripGain::~PrintSiStripGain() {}

namespace {
  std::pair<LocalPoint, LocalPoint> getStripEnds(float strip, const StripTopology& topo) {
    const auto lpMid = topo.localPosition(strip);
    const auto angle = topo.stripAngle(strip);
    const auto cosa = std::cos(angle);
    const auto sina = std::sin(angle);
    const auto dxy = LocalPoint::VectorType(.5*topo.stripLength()*sina, .5*topo.stripLength()*cosa, 0.);
    return std::make_pair(lpMid+dxy, lpMid-dxy);
  }
  std::pair<float,float> minmax(float tb, float bb, float te, float be) {
    float mn,mx;
    mn = mx = tb;
    // bb
    if ( bb < mn )
      mn = bb;
    else if ( bb > mx )
      mx = bb;
    // te
    if ( te < mn )
      mn = te;
    else if ( te > mx )
      mx = te;
    // be
    if ( be < mn )
      mn = be;
    else if ( be > mx )
      mx = be;
    return std::make_pair(mn, mx);
  }
}

void PrintSiStripGain::analyze(const edm::Event& event, const edm::EventSetup& eventSetup)
{
  edm::ESHandle<TrackerTopology> tTopo;
  eventSetup.get<TrackerTopologyRcd>().get(tTopo);
  edm::ESHandle<TrackerGeometry> tkGeom;
  eventSetup.get<TrackerDigiGeometryRecord>().get(tkGeom);

  edm::ESHandle<SiStripQuality> quality;
  eventSetup.get<SiStripQualityRcd>().get(quality);

  edm::ESHandle<SiStripGain> gain;
  eventSetup.get<SiStripGainRcd>().get(gain);
  edm::ESHandle<SiStripApvGain> tickmarkGain, particleGain;
  eventSetup.get<SiStripApvGainRcd>().get(tickmarkGain);
  eventSetup.get<SiStripApvGain2Rcd>().get(particleGain);

  for ( const auto det : m_dets ) {
    const auto nAPVs = m_reader->getNumberOfApvsAndStripLength(det).first;
    edm::LogWarning("PrintSiStripGain") << "Checking module " << det << ": " << tTopo->print(det);
    const auto gainRange = gain->getRange(det);
    const auto g1Range = tickmarkGain->getRange(det);
    const auto g2Range = particleGain->getRange(det);
    if ( quality->IsModuleBad(det) ) {
      edm::LogWarning("PrintSiStripGain") << "Module " << det << " is bad (from SiStripQuality)";
    } else {
      for ( std::size_t iAPV{0}; iAPV != nAPVs; ++iAPV ) {
        if ( quality->IsFiberBad(det, iAPV/2) ) {
          edm::LogWarning("PrintSiStripGain") << "Module " << det << " APV " << iAPV << " is bad (fiber #" << iAPV/2 << ")";
        } else if ( quality->IsApvBad(det, iAPV) ) {
          edm::LogWarning("PrintSiStripGain") << "Module " << det << " APV " << iAPV << " is bad";
        } else {
          edm::LogWarning("PrintSiStripGain") << "Gain values for module " << det << " APV#" << iAPV << ": "
            << "Gain=G1(" << SiStripApvGain::getApvGain(iAPV, g1Range) << ")*"
            << "G2(" << SiStripApvGain::getApvGain(iAPV, g2Range) << ")="
            << SiStripGain::getApvGain(iAPV, gainRange);
        }
      }
    }
  }
  // scan all dets for Gain>3
  for ( const DetId det : m_reader->getAllDetIds() ) {
    const auto nAPVs = m_reader->getNumberOfApvsAndStripLength(det).first;
    for ( std::size_t iAPV{0}; iAPV != nAPVs; ++iAPV ) {
      if ( ( ! quality->IsFiberBad(det, iAPV/2) ) && ( ! quality->IsApvBad(det, iAPV) ) ) {
        const auto gainRange = gain->getRange(det);
        const auto g1Range = tickmarkGain->getRange(det);
        const auto g2Range = particleGain->getRange(det);
        if ( SiStripGain::getApvGain(iAPV, gainRange) > 3. ) {
          const auto geomDet = tkGeom->idToDet(det);
          const auto& topo = static_cast<const StripTopology&>(geomDet->topology());
          // calculate eta and phi
          const auto lpBegin = getStripEnds(128.*iAPV, topo);
          const auto lpEnd   = getStripEnds(128.*(iAPV+1), topo);
          const auto gpTopBegin = geomDet->toGlobal(lpBegin.first);
          const auto gpBotBegin = geomDet->toGlobal(lpBegin.second);
          const auto gpTopEnd   = geomDet->toGlobal(lpEnd.first);
          const auto gpBotEnd   = geomDet->toGlobal(lpEnd.second);
          const auto etaRng = minmax(gpTopBegin.eta(), gpBotBegin.eta(), gpTopEnd.eta(), gpBotEnd.eta());
          const auto phiRng = minmax(gpTopBegin.phi(), gpBotBegin.phi(), gpTopEnd.phi(), gpBotEnd.phi());

          edm::LogWarning("PrintSiStripGain") << "Gain values for module " << det.rawId() << " APV#" << iAPV << ": "
            << "Gain=G1(" << SiStripApvGain::getApvGain(iAPV, g1Range) << ")*"
            << "G2(" << SiStripApvGain::getApvGain(iAPV, g2Range) << ")="
            << SiStripGain::getApvGain(iAPV, gainRange)
            << "\n" << tTopo->print(det)
            //<< "\n [loctopbegin=(x=" << lpBegin.first.x() << ",y=" << lpBegin.first.y() << ",z=" << lpBegin.first.z() << "), locbotbegin=(x=" << lpBegin.second.x() << ",y=" << lpBegin.second.y() << ",z=" << lpBegin.second.z() << "), pitch=" << topo.localPitch(LocalPoint(0.,0.,0.)) << "]"
            //<< "\n [loctopend=(x=" << lpEnd.first.x() << ",y=" << lpEnd.first.y() << ",z=" << lpEnd.first.z() << "), locbotend=(x=" << lpEnd.second.x() << ",y=" << lpEnd.second.y() << ",z=" << lpEnd.second.z() << "), pitch=" << topo.localPitch(LocalPoint(0.,0.,0.)) << "]"
            //<< "\n [topbegin=(r=" << gpTopBegin.perp() << ",phi=" << gpTopBegin.phi() << ",z=" << gpTopBegin.z() << ",eta=" << gpTopBegin.eta() << "), botbegin=(r=" << gpBotBegin.perp() << ",phi=" << gpBotBegin.phi() << ",z=" << gpBotBegin.z() << ",eta=" << gpBotBegin.eta() << ")]"
            //<< "\n [topend  =(r=" << gpTopEnd.perp() << ",phi=" << gpTopEnd.phi() << ",z=" << gpTopEnd.z() << ",eta=" << gpTopEnd.eta() << "), botend  =(r=" << gpBotEnd.perp() << ",phi=" << gpBotEnd.phi() << ",z=" << gpBotEnd.z() << ",eta=" << gpBotEnd.eta() << ")]"
            << " ETA=[" << etaRng.first << "," << etaRng.second << "], PHI=[" << phiRng.first << "," << phiRng.second << "]";
        }
      }
    }
  }
}

DEFINE_FWK_MODULE(PrintSiStripGain);
