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

  // Swap gen variables in the case that Z2 should be relabeled to Z1
  if ((channel_ == eemm || channel_ == mmee) && fabs(GenZ1Mass - 91.1876) < fabs(GenZ2Mass - 91.1876)) {
    std::swap(GenZ1Mass, GenZ2Mass);
    std::swap(Genl1Pt, Genl3Pt);
    std::swap(Genl2Pt, Genl4Pt);
    std::swap(Genl1Eta, Genl3Eta);
    std::swap(Genl2Eta, Genl4Eta);
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
  };
  Lepton leps[] = {{l1Pt, l1Eta}, {l2Pt, l2Eta}, {l3Pt, l3Eta}, {l4Pt, l4Eta}};
  Lepton genleps[] = {{Genl1Pt, Genl1Eta}, {Genl2Pt, Genl2Eta}, {Genl3Pt, Genl3Eta}, {Genl4Pt, Genl4Eta}};
  std::sort(leps, leps + 4, [](Lepton a, Lepton b) { return a.pt > b.pt; });
  std::sort(genleps, genleps + 4, [](Lepton a, Lepton b) { return a.pt > b.pt; });

  SafeHistFill(histMap2D_, getHistName("Mass_ResponseMatrix", variation.second), Mass, GenMass, weight);

  SafeHistFill(histMap2D_, getHistName("LepPt1_ResponseMatrix", variation.second), leps[0].pt, genleps[0].pt, weight);
  SafeHistFill(histMap2D_, getHistName("LepPt_ResponseMatrix", variation.second), leps[0].pt, genleps[0].pt, weight);
  SafeHistFill(histMap2D_, getHistName("LepPt_ResponseMatrix", variation.second), leps[1].pt, genleps[1].pt, weight);
  SafeHistFill(histMap2D_, getHistName("LepPt_ResponseMatrix", variation.second), leps[2].pt, genleps[2].pt, weight);
  SafeHistFill(histMap2D_, getHistName("LepPt_ResponseMatrix", variation.second), leps[3].pt, genleps[3].pt, weight);

  SafeHistFill(histMap2D_, getHistName("LepEta1_ResponseMatrix", variation.second), leps[0].eta, genleps[0].eta, weight);
  SafeHistFill(histMap2D_, getHistName("LepEta_ResponseMatrix", variation.second), leps[0].eta, genleps[0].eta, weight);
  SafeHistFill(histMap2D_, getHistName("LepEta_ResponseMatrix", variation.second), leps[1].eta, genleps[1].eta, weight);
  SafeHistFill(histMap2D_, getHistName("LepEta_ResponseMatrix", variation.second), leps[2].eta, genleps[2].eta, weight);
  SafeHistFill(histMap2D_, getHistName("LepEta_ResponseMatrix", variation.second), leps[3].eta, genleps[3].eta, weight);
}
