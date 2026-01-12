#include "Analysis/VVAnalysis/interface/ZGenSelector.h"
#include "DataFormats/Math/interface/LorentzVector.h"
#include <TStyle.h>
#include <regex>

void ZGenSelector::Init(TTree* tree) {
  allChannels_ = {"ee", "mm", "Unknown"};
  hists1D_ = {
      "CutFlow", "ZMass", "yZ",    "ptZ",   "ptl1",  "etal1", "phil1", "ptl2",  "etal2", "phil2", "ptj1",
      "ptj2",    "ptj3",  "etaj1", "etaj2", "etaj3", "phij1", "phij2", "phij3", "nJets", "MET",
  };
  nLeptons_ = 2;

  NanoGenSelectorBase::Init(tree);
}

void ZGenSelector::LoadBranchesNanoAOD(Long64_t entry, std::pair<Systematic, std::string> variation) {
  NanoGenSelectorBase::LoadBranchesNanoAOD(entry, variation);

  if (leptons.size() < 2) {
    channel_ = Unknown;
    channelName_ = "Unknown";
    return;
  }
  if (leptons.at(0).pdgId() + leptons.at(1).pdgId() == 0) {
    if (std::abs(leptons.at(0).pdgId()) == 11) {
      channel_ = ee;
      channelName_ = "ee";
    } else if (std::abs(leptons.at(0).pdgId()) == 13) {
      channel_ = mm;
      channelName_ = "mm";
    }
  } else {
    channel_ = Unknown;
    channelName_ = "Unknown";
  }
}

void ZGenSelector::SetComposite() {
  if (leptons.size() >= 2)
    zCand = leptons.at(0).polarP4() + leptons.at(1).polarP4();
}

void ZGenSelector::FillHistograms(Long64_t entry, std::pair<Systematic, std::string> variation) {
  int step = 0;
  SafeHistFill(histMap1D_, getHistName("CutFlow", variation.second), step++, weight);

  if (channel_ != mm && channel_ != ee)
    return;
  SafeHistFill(histMap1D_, getHistName("CutFlow", variation.second), step++, weight);

  auto lep1 = leptons.at(0);
  auto lep2 = leptons.at(1);
  if (std::abs(lep1.eta()) > 2.5 || std::abs(lep2.eta()) > 2.5)
    return;
  SafeHistFill(histMap1D_, getHistName("CutFlow", variation.second), step++, weight);

  if (lep1.pt() < 25. || lep2.pt() < 25.)
    return;
  SafeHistFill(histMap1D_, getHistName("CutFlow", variation.second), step++, weight);

  if (zCand.mass() < 60. || zCand.mass() > 120.)
    return;

  SafeHistFill(histMap1D_, getHistName("CutFlow", variation.second), step++, weight);
  SafeHistFill(histMap1D_, getHistName("ZMass", variation.second), zCand.mass(), weight);
  SafeHistFill(histMap1D_, getHistName("yZ", variation.second), zCand.Rapidity(), weight);
  SafeHistFill(histMap1D_, getHistName("ptZ", variation.second), zCand.pt(), weight);
  SafeHistFill(histMap1D_, getHistName("ptl1", variation.second), lep1.pt(), weight);
  SafeHistFill(histMap1D_, getHistName("etal1", variation.second), lep1.eta(), weight);
  SafeHistFill(histMap1D_, getHistName("phil1", variation.second), lep1.phi(), weight);
  SafeHistFill(histMap1D_, getHistName("ptl2", variation.second), lep2.pt(), weight);
  SafeHistFill(histMap1D_, getHistName("etal2", variation.second), lep2.eta(), weight);
  SafeHistFill(histMap1D_, getHistName("phil2", variation.second), lep2.phi(), weight);
  SafeHistFill(histMap1D_, getHistName("nJets", variation.second), jets.size(), weight);
  SafeHistFill(histMap1D_, getHistName("MET", variation.second), genMet.pt(), weight);
  for (size_t i = 1; i <= 3; i++) {
    if (jets.size() >= i) {
      const auto& jet = jets.at(i - 1);
      SafeHistFill(histMap1D_, getHistName("ptj" + std::to_string(i), variation.second), jet.pt(), weight);
      SafeHistFill(histMap1D_, getHistName("etaj" + std::to_string(i), variation.second), jet.eta(), weight);
      SafeHistFill(histMap1D_, getHistName("phij" + std::to_string(i), variation.second), jet.phi(), weight);
    }
  }
}
