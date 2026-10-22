#include "Analysis/VVAnalysis/interface/ZZResponseMatrixMaker.h"

ZZResponseMatrixMaker::~ZZResponseMatrixMaker() {
  if (genTree_ != nullptr)
    delete genTree_;
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
  hists2D_ = {"Mass_ResponseMatrix", "LepPt1_ResponseMatrix", "LepEta1_ResponseMatrix"};
  systHists2D_ = {"Mass_ResponseMatrix", "LepPt1_ResponseMatrix", "LepEta1_ResponseMatrix"};
  ZZSelectorBase::Init(tree);

  // Create gen tree and set gen branches
  if (!isMC_)
    return;
  std::string genChannelName = channelName_ == "mmee" ? "eemm" : channelName_;
  if (genTree_ != nullptr)
    delete genTree_;
  genTree_ = new TChain((genChannelName + "Gen/ntuple").c_str(), (genChannelName + "Gen/ntuple").c_str());
  genTree_->Add(fChain->GetTree()->GetDirectory()->GetFile()->GetName());
  SetGenBranchesUWVV();
  StoreGenEvents();
}

void ZZResponseMatrixMaker::SetGenBranchesUWVV() {
  genTree_->SetBranchAddress("evt", &genEvt, &b_genEvt);
  genTree_->SetBranchAddress("Mass", &genMass, &b_genMass);
  if (channel_ == eeee) {
    genTree_->SetBranchAddress("e1_e2_Mass", &genZ1Mass, &b_genZ1Mass);
    genTree_->SetBranchAddress("e3_e4_Mass", &genZ2Mass, &b_genZ2Mass);
    genTree_->SetBranchAddress("e1Pt", &genl1Pt, &b_genl1Pt);
    genTree_->SetBranchAddress("e2Pt", &genl2Pt, &b_genl2Pt);
    genTree_->SetBranchAddress("e3Pt", &genl3Pt, &b_genl3Pt);
    genTree_->SetBranchAddress("e4Pt", &genl4Pt, &b_genl4Pt);
    genTree_->SetBranchAddress("e1Eta", &genl1Eta, &b_genl1Eta);
    genTree_->SetBranchAddress("e2Eta", &genl2Eta, &b_genl2Eta);
    genTree_->SetBranchAddress("e3Eta", &genl3Eta, &b_genl3Eta);
    genTree_->SetBranchAddress("e4Eta", &genl4Eta, &b_genl4Eta);
  } else if (channel_ == eemm || channel_ == mmee) {
    genTree_->SetBranchAddress("e1_e2_Mass", &genZ1Mass, &b_genZ1Mass);
    genTree_->SetBranchAddress("m1_m2_Mass", &genZ2Mass, &b_genZ2Mass);
    genTree_->SetBranchAddress("e1Pt", &genl1Pt, &b_genl1Pt);
    genTree_->SetBranchAddress("e2Pt", &genl2Pt, &b_genl2Pt);
    genTree_->SetBranchAddress("m1Pt", &genl3Pt, &b_genl3Pt);
    genTree_->SetBranchAddress("m2Pt", &genl4Pt, &b_genl4Pt);
    genTree_->SetBranchAddress("e1Eta", &genl1Eta, &b_genl1Eta);
    genTree_->SetBranchAddress("e2Eta", &genl2Eta, &b_genl2Eta);
    genTree_->SetBranchAddress("m1Eta", &genl3Eta, &b_genl3Eta);
    genTree_->SetBranchAddress("m2Eta", &genl4Eta, &b_genl4Eta);
  } else if (channel_ == mmmm) {
    genTree_->SetBranchAddress("m1_m2_Mass", &genZ1Mass, &b_genZ1Mass);
    genTree_->SetBranchAddress("m3_m4_Mass", &genZ2Mass, &b_genZ2Mass);
    genTree_->SetBranchAddress("m1Pt", &genl1Pt, &b_genl1Pt);
    genTree_->SetBranchAddress("m2Pt", &genl2Pt, &b_genl2Pt);
    genTree_->SetBranchAddress("m3Pt", &genl3Pt, &b_genl3Pt);
    genTree_->SetBranchAddress("m4Pt", &genl4Pt, &b_genl4Pt);
    genTree_->SetBranchAddress("m1Eta", &genl1Eta, &b_genl1Eta);
    genTree_->SetBranchAddress("m2Eta", &genl2Eta, &b_genl2Eta);
    genTree_->SetBranchAddress("m3Eta", &genl3Eta, &b_genl3Eta);
    genTree_->SetBranchAddress("m4Eta", &genl4Eta, &b_genl4Eta);
  }
}

void ZZResponseMatrixMaker::StoreGenEvents() {
  genEvents_.clear();

  Long64_t nentries = genTree_->GetEntries();
  for (Long64_t entry = 0; entry < nentries; entry++) {
    b_genEvt->GetEntry(entry);
    genEvents_[entry] = genEvt;
  }
}

bool ZZResponseMatrixMaker::GetGenEvent(ULong64_t event) {
  for (auto it : genEvents_) {
    if (it.second == event) {
      LoadGenBranchesUWVV(it.first);
      return true;
    }
  }
  return false;
}

void ZZResponseMatrixMaker::LoadGenBranchesUWVV(Long64_t entry) {
  b_genEvt->GetEntry(entry);
  b_genMass->GetEntry(entry);
  b_genZ1Mass->GetEntry(entry);
  b_genZ2Mass->GetEntry(entry);
  b_genl1Pt->GetEntry(entry);
  b_genl2Pt->GetEntry(entry);
  b_genl3Pt->GetEntry(entry);
  b_genl4Pt->GetEntry(entry);
  b_genl1Eta->GetEntry(entry);
  b_genl2Eta->GetEntry(entry);
  b_genl3Eta->GetEntry(entry);
  b_genl4Eta->GetEntry(entry);

  // Swap gen variables in the case that Z2 should be relabeled to Z1
  if ((channel_ == eemm || channel_ == mmee) && fabs(genZ1Mass - 91.1876) < fabs(genZ2Mass - 91.1876)) {
    std::swap(genZ1Mass, genZ2Mass);
    std::swap(genl1Pt, genl3Pt);
    std::swap(genl2Pt, genl4Pt);
    std::swap(genl1Eta, genl3Eta);
    std::swap(genl2Eta, genl4Eta);
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
  Lepton genleps[] = {{genl1Pt, genl1Eta}, {genl2Pt, genl2Eta}, {genl3Pt, genl3Eta}, {genl4Pt, genl4Eta}};
  std::sort(leps, leps + 4, [](Lepton a, Lepton b) { return a.pt > b.pt; });
  std::sort(genleps, genleps + 4, [](Lepton a, Lepton b) { return a.pt > b.pt; });

  SafeHistFill(histMap2D_, getHistName("Mass_ResponseMatrix", variation.second), Mass, genMass, weight);
  SafeHistFill(histMap2D_, getHistName("LepPt1_ResponseMatrix", variation.second), leps[0].pt, genleps[0].pt, weight);
  SafeHistFill(histMap2D_, getHistName("LepEta1_ResponseMatrix", variation.second), leps[0].eta, genleps[0].eta, weight);
}
