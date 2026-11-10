#include "Analysis/VVAnalysis/interface/ZZResponseMatrixMaker.h"

ZZResponseMatrixMaker::~ZZResponseMatrixMaker() {
  if (GenTree_ != nullptr)
    delete GenTree_;
}

void ZZResponseMatrixMaker::Init(TTree* tree) {
  fCutFormula = 0;
  systematics_ = {
      {electronRecoEffUp, "CMS_RecoEff_eUp"},
      {electronRecoEffDown, "CMS_RecoEff_eDown"},
      {electronEfficiencyUp, "CMS_eff_eUp"},
      {electronEfficiencyDown, "CMS_eff_eDown"},
      {muonEfficiencyUp, "CMS_eff_mUp"},
      {muonEfficiencyDown, "CMS_eff_mDown"},
      {pileupUp, "CMS_pileupUp"},
      {pileupDown, "CMS_pileupDown"},
  };
  hists2D_ = {"Mass_ResponseMatrix", "LepPt1_ResponseMatrix", "LepPt_ResponseMatrix", "LepEta_ResponseMatrix", "LepEta1_ResponseMatrix"};
  systHists2D_ = {"Mass_ResponseMatrix", "LepPt1_ResponseMatrix", "LepPt_ResponseMatrix", "LepEta_ResponseMatrix", "LepEta1_ResponseMatrix"};
  ZZSelectorBase::Init(tree);

  // Create gen tree and set gen branches
  if (!isMC_)
    return;
  std::string genChannelName = channelName_ == "mmee" ? "eemm" : channelName_;
  if (GenTree_ != nullptr)
    delete GenTree_;
  GenTree_ = new TChain((genChannelName + "Gen/ntuple").c_str(), (genChannelName + "Gen/ntuple").c_str());
  GenTree_->Add(fChain->GetTree()->GetDirectory()->GetFile()->GetName());
  SetGenBranchesUWVV();
  StoreGenEvents();
}

void ZZResponseMatrixMaker::SetGenBranchesUWVV() {
  GenTree_->SetBranchAddress("evt", &GenEvt, &b_GenEvt);
  GenTree_->SetBranchAddress("Mass", &GenMass, &b_GenMass);
  if (channel_ == eeee) {
    GenTree_->SetBranchAddress("e1_e2_Mass", &GenZ1Mass, &b_GenZ1Mass);
    GenTree_->SetBranchAddress("e3_e4_Mass", &GenZ2Mass, &b_GenZ2Mass);
    GenTree_->SetBranchAddress("e1Pt", &Genl1Pt, &b_Genl1Pt);
    GenTree_->SetBranchAddress("e2Pt", &Genl2Pt, &b_Genl2Pt);
    GenTree_->SetBranchAddress("e3Pt", &Genl3Pt, &b_Genl3Pt);
    GenTree_->SetBranchAddress("e4Pt", &Genl4Pt, &b_Genl4Pt);
    GenTree_->SetBranchAddress("e1Eta", &Genl1Eta, &b_Genl1Eta);
    GenTree_->SetBranchAddress("e2Eta", &Genl2Eta, &b_Genl2Eta);
    GenTree_->SetBranchAddress("e3Eta", &Genl3Eta, &b_Genl3Eta);
    GenTree_->SetBranchAddress("e4Eta", &Genl4Eta, &b_Genl4Eta);
    GenTree_->SetBranchAddress("e1Phi", &Genl1Phi, &b_Genl1Phi);
    GenTree_->SetBranchAddress("e2Phi", &Genl2Phi, &b_Genl2Phi);
    GenTree_->SetBranchAddress("e3Phi", &Genl3Phi, &b_Genl3Phi);
    GenTree_->SetBranchAddress("e4Phi", &Genl4Phi, &b_Genl4Phi);
    GenTree_->SetBranchAddress("e1PdgId", &Genl1PdgId, &b_Genl1PdgId);
    GenTree_->SetBranchAddress("e2PdgId", &Genl2PdgId, &b_Genl2PdgId);
    GenTree_->SetBranchAddress("e3PdgId", &Genl3PdgId, &b_Genl3PdgId);
    GenTree_->SetBranchAddress("e4PdgId", &Genl4PdgId, &b_Genl4PdgId);
  } else if (channel_ == eemm || channel_ == mmee) {
    GenTree_->SetBranchAddress("e1_e2_Mass", &GenZ1Mass, &b_GenZ1Mass);
    GenTree_->SetBranchAddress("m1_m2_Mass", &GenZ2Mass, &b_GenZ2Mass);
    GenTree_->SetBranchAddress("e1Pt", &Genl1Pt, &b_Genl1Pt);
    GenTree_->SetBranchAddress("e2Pt", &Genl2Pt, &b_Genl2Pt);
    GenTree_->SetBranchAddress("m1Pt", &Genl3Pt, &b_Genl3Pt);
    GenTree_->SetBranchAddress("m2Pt", &Genl4Pt, &b_Genl4Pt);
    GenTree_->SetBranchAddress("e1Eta", &Genl1Eta, &b_Genl1Eta);
    GenTree_->SetBranchAddress("e2Eta", &Genl2Eta, &b_Genl2Eta);
    GenTree_->SetBranchAddress("m1Eta", &Genl3Eta, &b_Genl3Eta);
    GenTree_->SetBranchAddress("m2Eta", &Genl4Eta, &b_Genl4Eta);
    GenTree_->SetBranchAddress("e1Phi", &Genl1Phi, &b_Genl1Phi);
    GenTree_->SetBranchAddress("e2Phi", &Genl2Phi, &b_Genl2Phi);
    GenTree_->SetBranchAddress("m1Phi", &Genl3Phi, &b_Genl3Phi);
    GenTree_->SetBranchAddress("m2Phi", &Genl4Phi, &b_Genl4Phi);
    GenTree_->SetBranchAddress("e1PdgId", &Genl1PdgId, &b_Genl1PdgId);
    GenTree_->SetBranchAddress("e2PdgId", &Genl2PdgId, &b_Genl2PdgId);
    GenTree_->SetBranchAddress("m1PdgId", &Genl3PdgId, &b_Genl3PdgId);
    GenTree_->SetBranchAddress("m2PdgId", &Genl4PdgId, &b_Genl4PdgId);
  } else if (channel_ == mmmm) {
    GenTree_->SetBranchAddress("m1_m2_Mass", &GenZ1Mass, &b_GenZ1Mass);
    GenTree_->SetBranchAddress("m3_m4_Mass", &GenZ2Mass, &b_GenZ2Mass);
    GenTree_->SetBranchAddress("m1Pt", &Genl1Pt, &b_Genl1Pt);
    GenTree_->SetBranchAddress("m2Pt", &Genl2Pt, &b_Genl2Pt);
    GenTree_->SetBranchAddress("m3Pt", &Genl3Pt, &b_Genl3Pt);
    GenTree_->SetBranchAddress("m4Pt", &Genl4Pt, &b_Genl4Pt);
    GenTree_->SetBranchAddress("m1Eta", &Genl1Eta, &b_Genl1Eta);
    GenTree_->SetBranchAddress("m2Eta", &Genl2Eta, &b_Genl2Eta);
    GenTree_->SetBranchAddress("m3Eta", &Genl3Eta, &b_Genl3Eta);
    GenTree_->SetBranchAddress("m4Eta", &Genl4Eta, &b_Genl4Eta);
    GenTree_->SetBranchAddress("m1Phi", &Genl1Phi, &b_Genl1Phi);
    GenTree_->SetBranchAddress("m2Phi", &Genl2Phi, &b_Genl2Phi);
    GenTree_->SetBranchAddress("m3Phi", &Genl3Phi, &b_Genl3Phi);
    GenTree_->SetBranchAddress("m4Phi", &Genl4Phi, &b_Genl4Phi);
    GenTree_->SetBranchAddress("m1PdgId", &Genl1PdgId, &b_Genl1PdgId);
    GenTree_->SetBranchAddress("m2PdgId", &Genl2PdgId, &b_Genl2PdgId);
    GenTree_->SetBranchAddress("m3PdgId", &Genl3PdgId, &b_Genl3PdgId);
    GenTree_->SetBranchAddress("m4PdgId", &Genl4PdgId, &b_Genl4PdgId);
  }
}

void ZZResponseMatrixMaker::StoreGenEvents() {
  GenEvents_.clear();

  Long64_t nentries = GenTree_->GetEntries();
  for (Long64_t entry = 0; entry < nentries; entry++) {
    b_GenEvt->GetEntry(entry);
    GenEvents_[entry] = GenEvt;
  }
}

bool ZZResponseMatrixMaker::GetGenEvent(ULong64_t event) {
  for (auto it : GenEvents_) {
    if (it.second == event) {
      LoadGenBranchesUWVV(it.first);
      return GenZ1Mass > 60 && GenZ1Mass < 120 && GenZ2Mass > 60 && GenZ2Mass < 120;
    }
  }
  return false;
}

void ZZResponseMatrixMaker::LoadGenBranchesUWVV(Long64_t entry) {
  b_GenEvt->GetEntry(entry);
  b_GenMass->GetEntry(entry);
  b_GenZ1Mass->GetEntry(entry);
  b_GenZ2Mass->GetEntry(entry);
  b_Genl1Pt->GetEntry(entry);
  b_Genl2Pt->GetEntry(entry);
  b_Genl3Pt->GetEntry(entry);
  b_Genl4Pt->GetEntry(entry);
  b_Genl1Eta->GetEntry(entry);
  b_Genl2Eta->GetEntry(entry);
  b_Genl3Eta->GetEntry(entry);
  b_Genl4Eta->GetEntry(entry);
  b_Genl1Phi->GetEntry(entry);
  b_Genl2Phi->GetEntry(entry);
  b_Genl3Phi->GetEntry(entry);
  b_Genl4Phi->GetEntry(entry);
  b_Genl1PdgId->GetEntry(entry);
  b_Genl2PdgId->GetEntry(entry);
  b_Genl3PdgId->GetEntry(entry);
  b_Genl4PdgId->GetEntry(entry);

  // Swap gen variables in the case that Z2 should be relabeled to Z1
  if ((channel_ == eemm || channel_ == mmee) && fabs(GenZ1Mass - 91.1876) < fabs(GenZ2Mass - 91.1876)) {
    std::swap(GenZ1Mass, GenZ2Mass);
    std::swap(Genl1Pt, Genl3Pt);
    std::swap(Genl2Pt, Genl4Pt);
    std::swap(Genl1Eta, Genl3Eta);
    std::swap(Genl2Eta, Genl4Eta);
    std::swap(Genl1Phi, Genl3Phi);
    std::swap(Genl2Phi, Genl4Phi);
    std::swap(Genl1PdgId, Genl3PdgId);
    std::swap(Genl2PdgId, Genl4PdgId);
  }
}

void ZZResponseMatrixMaker::FillHistograms(Long64_t entry, std::pair<Systematic, std::string> variation) {
  if ((channel_ == eemm || channel_ == mmee) && skipEvent_2e2m_)
    return;

  // Check for MC and gen match plus basic loose ZZ selections
  if (!isMC_ || !GetGenEvent(evt) || !HZZSIPSelection() || !PassesZZSelectionLoose())
    return;

  // Any "Full" histograms here (no Z mass cuts)

  // Final Z mass cuts
  if (!PassesZZSelection())
    return;

  // sort lepton pt
  struct Lepton {
    Float_t pt;
    Float_t eta;
    Float_t phi;
    Int_t pdgId;
  };
  Lepton leps[] = {{l1Pt, l1Eta, l1Phi, l1PdgId}, {l2Pt, l2Eta, l2Phi, l2PdgId}, {l3Pt, l3Eta, l3Phi, l3PdgId}, {l4Pt, l4Eta, l4Phi, l4PdgId}};
  Lepton genleps[] = {{Genl1Pt, Genl1Eta, Genl1Phi, Genl1PdgId},
                      {Genl2Pt, Genl2Eta, Genl2Phi, Genl2PdgId},
                      {Genl3Pt, Genl3Eta, Genl3Phi, Genl3PdgId},
                      {Genl4Pt, Genl4Eta, Genl4Phi, Genl4PdgId}};
  std::sort(leps, leps + 4, [](Lepton a, Lepton b) { return a.pt > b.pt; });
  std::sort(genleps, genleps + 4, [](Lepton a, Lepton b) { return a.pt > b.pt; });
  std::map<size_t, size_t> matches;

  {
    Float_t maxDPtRel = 1.;
    Float_t maxDeltaR = 0.3;
    typedef std::pair<size_t, size_t> MatchPair;

    // sorting algorithm from PhysObjectMatcher
    std::vector<MatchPair> matchPairs;  // container of matched pairs
    for (size_t iiLep = 0; iiLep < 4; iiLep++) {
      for (size_t iiGenLep = 0; iiGenLep < 4; iiGenLep++) {
        if (leps[iiLep].pdgId == genleps[iiGenLep].pdgId) {
          Float_t dPtRel = fabs(leps[iiLep].pt - genleps[iiGenLep].pt) / genleps[iiGenLep].pt;
          Float_t dR = deltaR(leps[iiLep].eta, leps[iiLep].phi, genleps[iiGenLep].eta, genleps[iiGenLep].phi);
          if (dPtRel < maxDPtRel && dR < maxDeltaR)
            matchPairs.push_back(std::make_pair(iiLep, iiGenLep));
        }
      }
    }

    // sort and resolve ambiguities
    std::vector<bool> locked(4, false);     // locks in target collection
    std::vector<bool> genlocked(4, false);  // locks in gen collection
    std::sort(matchPairs.begin(), matchPairs.end(), [&leps, &genleps](MatchPair p1, MatchPair p2) {
      return ZZSelector::deltaR(leps[p1.first].eta, leps[p1.first].phi, genleps[p1.second].eta, genleps[p1.second].phi) <
             ZZSelector::deltaR(leps[p2.first].eta, leps[p2.first].phi, genleps[p2.second].eta, genleps[p2.second].phi);
    });
    for (const auto& p : matchPairs) {
      if (locked[p.first] || genlocked[p.second])
        continue;
      matches[p.first] = p.second;
      locked[p.first] = true;
      genlocked[p.second] = true;
    }
  }

  SafeHistFill(histMap2D_, getHistName("Mass_ResponseMatrix", variation.second), Mass, GenMass, weight);

  SafeHistFill(histMap2D_, getHistName("LepPt1_ResponseMatrix", variation.second), leps[0].pt, genleps[0].pt, weight);
  SafeHistFill(histMap2D_, getHistName("LepPt_ResponseMatrix", variation.second), leps[0].pt, genleps[matches[0]].pt, weight);
  SafeHistFill(histMap2D_, getHistName("LepPt_ResponseMatrix", variation.second), leps[1].pt, genleps[matches[1]].pt, weight);
  SafeHistFill(histMap2D_, getHistName("LepPt_ResponseMatrix", variation.second), leps[2].pt, genleps[matches[2]].pt, weight);
  SafeHistFill(histMap2D_, getHistName("LepPt_ResponseMatrix", variation.second), leps[3].pt, genleps[matches[3]].pt, weight);

  SafeHistFill(histMap2D_, getHistName("LepEta1_ResponseMatrix", variation.second), leps[0].eta, genleps[0].eta, weight);
  SafeHistFill(histMap2D_, getHistName("LepEta_ResponseMatrix", variation.second), leps[0].eta, genleps[matches[0]].eta, weight);
  SafeHistFill(histMap2D_, getHistName("LepEta_ResponseMatrix", variation.second), leps[1].eta, genleps[matches[1]].eta, weight);
  SafeHistFill(histMap2D_, getHistName("LepEta_ResponseMatrix", variation.second), leps[2].eta, genleps[matches[2]].eta, weight);
  SafeHistFill(histMap2D_, getHistName("LepEta_ResponseMatrix", variation.second), leps[3].eta, genleps[matches[3]].eta, weight);

  SafeHistFill(histMap2D_, getHistName("LepPhi1_ResponseMatrix", variation.second), leps[0].phi, genleps[0].phi, weight);
  SafeHistFill(histMap2D_, getHistName("LepPhi_ResponseMatrix", variation.second), leps[0].phi, genleps[matches[0]].phi, weight);
  SafeHistFill(histMap2D_, getHistName("LepPhi_ResponseMatrix", variation.second), leps[1].phi, genleps[matches[1]].phi, weight);
  SafeHistFill(histMap2D_, getHistName("LepPhi_ResponseMatrix", variation.second), leps[2].phi, genleps[matches[2]].phi, weight);
  SafeHistFill(histMap2D_, getHistName("LepPhi_ResponseMatrix", variation.second), leps[3].phi, genleps[matches[3]].phi, weight);
}
