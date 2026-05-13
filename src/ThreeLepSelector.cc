#include "Analysis/VVAnalysis/interface/ThreeLepSelector.h"

#include <TStyle.h>
#include <regex>
#include "TParameter.h"

#define Fill1D(NAME, VALUE_) HistFullFill(histMap1D_, NAME, variation.second, VALUE_, weight);
//#define Fill2D(NAME, VALUE1_, VALUE2_) HistFullFill(histMap2D_, NAME, variation.second, VALUE1_, VALUE2_, weight);
#define SetupPtEtaPhiM(PART, INDEX) PART##_pt[INDEX], PART##_eta[INDEX], PART##_phi[INDEX], PART##_mass[INDEX]

enum PID { PID_MUON = 13, PID_ELECTRON = 11, eBJet = 5 };
enum ElectronCBID { CBID_VETO = 1, CBID_LOOSE = 2, CBID_MEDIUM = 3, CBID_TIGHT = 4 };

typedef ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<double>> LorentzVector;

// This is very WZ specific and should really be improved or likely removed
std::string ThreeLepSelector::GetNameFromFile() {
  std::regex expr = std::regex("201[0-9]-[0-9][0-9]-[0-9][0-9]-(.*)-WZxsec2016");
  std::smatch matches;
  std::string fileName = fChain->GetTree()->GetDirectory()->GetFile()->GetName();

  std::regex_search(fileName, matches, expr);
  return std::string(matches.str(1));
}

void ThreeLepSelector::SetScaleFactors() {
  // calib = BTagCalibration("deepcsv", "data/btag_scales.csv");
  // btag_reader = BTagCalibrationReader(BTagEntry::OP_MEDIUM, "central");
  // btag_reader.load(calib, BTagEntry::FLAV_B, "comb");

  // pileupSF_ = (ScaleFactor *) GetInputList()->FindObject("pileupSF");
  // if (pileupSF_ == nullptr )
  //   std::cout << "missing Pileup SF" << std::endl;

  // eIdSF_ = (ScaleFactor *) GetInputList()->FindObject("electronTightIdSF");
  // if (eIdSF_ == nullptr )
  //   std::cout  << "missing Electron ID SF" << std::endl;

  // eGsfSF_ = (ScaleFactor *) GetInputList()->FindObject("electronGsfSF");
  // if (eGsfSF_ == nullptr )
  //   std::cout  << "missing Electron Gsf SF" << std::endl;

  // mIdSF_ = (ScaleFactor *) GetInputList()->FindObject("muonTightIdSF");
  // if (mIdSF_ == nullptr )
  // std::cout  << "missing Muon Id SF" << std::endl;

  //  mIsoSF_ = (ScaleFactor *) GetInputList()->FindObject("muonIsoSF");
  //  if (mIsoSF_ == nullptr )
  // std::cout  << "missing Muon Iso SF" << std::endl;
  //  Abort("Must pass muon Iso SF");

  // prefireEff_ = (TEfficiency*) GetInputList()->FindObject("prefireEfficiencyMap");
  // if (prefireEff_ == nullptr )
  //   Abort("Must pass prefiring efficiency map");
}

void ThreeLepSelector::Init(TTree* tree) {
  b.SetTree(tree);

  allChannels_ = {"mm", "ee", "em", "all", "lll"};

  // if(selection_ == TightWithLooseVeto) {
  hists1D_ = {"CutFlow",
              "ZMass",
              "ptl1",
              "etal1",
              "ptl2",
              "etal2",
              "SR",
              "bjetpt",
              "jetpt",
              "nbjet",
              "njet",
              "nleps",
              "CRW_nbjet",
              "CRW_njet",
              "CRZ_nbjet",
              "CRZ_njet",
              "Met",
              "HT",
              "weight"};
  //  hists2D_ = {"bJetvsJets"};
  // } else if(selection_ == FourTopPlots) {
  //  }

  SelectorBase::Init(tree);
}

void ThreeLepSelector::SetBranchesNanoAOD() {
  //  NECESSARY!!!!
  b.CleanUp();

  b.SetBranch("nElectron", nElectron);
  b.SetBranch("Electron_pt", Electron_pt);
  b.SetBranch("Electron_eta", Electron_eta);
  b.SetBranch("Electron_phi", Electron_phi);
  b.SetBranch("Electron_charge", Electron_charge);
  b.SetBranch("Electron_mass", Electron_mass);
  b.SetBranch("Electron_miniPFRelIso_all", Electron_miniPFRelIso_all);
  b.SetBranch("Electron_dxy", Electron_dxy);
  b.SetBranch("Electron_dz", Electron_dz);
  b.SetBranch("Electron_sip3d", Electron_sip3d);
  b.SetBranch("Electron_lostHits", Electron_lostHits);
  b.SetBranch("Electron_convVeto", Electron_convVeto);
  /*
  if(year_ == yr2018) {
    b.SetBranch("Electron_mvaFall17V2noIso",     Electron_MVA);
    b.SetBranch("Electron_cutBased",             Electron_cutBased);
  } else if(year_ == yr2017) {
    b.SetBranch("Electron_mvaFall17V1noIso",     Electron_MVA);
    b.SetBranch("Electron_cutBased_Fall17_V1",   Electron_cutBased);
  } else if(year_ == yr2016 || year_ == yrdefault) {
    b.SetBranch("Electron_mvaSpring16GP",        Electron_MVA);
    b.SetBranch("Electron_cutBased_Sum16",       Electron_cutBased);
  }
  */

  b.SetBranch("nMuon", nMuon);
  b.SetBranch("Muon_pt", Muon_pt);
  b.SetBranch("Muon_eta", Muon_eta);
  b.SetBranch("Muon_phi", Muon_phi);
  b.SetBranch("Muon_mass", Muon_mass);
  b.SetBranch("Muon_charge", Muon_charge);
  b.SetBranch("Muon_mediumId", Muon_mediumId);
  b.SetBranch("Muon_miniPFRelIso_all", Muon_miniPFRelIso_all);
  b.SetBranch("Muon_dxy", Muon_dxy);
  b.SetBranch("Muon_dz", Muon_dz);
  b.SetBranch("Muon_sip3d", Muon_sip3d);
  b.SetBranch("Muon_isGlobal", Muon_isGlobal);
  b.SetBranch("Muon_isPFcand", Muon_isPFcand);
  b.SetBranch("Muon_tightCharge", Muon_tightCharge);

  b.SetBranch("nJet", nJet);
  b.SetBranch("Jet_btagCSVV2", Jet_btagCSVV2);
  b.SetBranch("Jet_btagDeepB", Jet_btagDeepB);
  b.SetBranch("Jet_eta", Jet_eta);
  b.SetBranch("Jet_phi", Jet_phi);
  b.SetBranch("Jet_pt", Jet_pt);
  b.SetBranch("Jet_mass", Jet_mass);
  b.SetBranch("Jet_jetId", Jet_jetId);

  b.SetBranch("MET_pt", MET);
  b.SetBranch("MET_phi", type1_pfMETPhi);

  if (isMC_) {
    b.SetBranch("genWeight", genWeight);
    b.SetBranch("Pileup_nPU", numPU);
  }
}

void ThreeLepSelector::SetBranchesUWVV() { return; }

void ThreeLepSelector::LoadBranchesUWVV(Long64_t entry, std::pair<Systematic, std::string> variation) { return; }

/// Make to seperate fuctionality
void ThreeLepSelector::clearValues() {
  weight = 1;
  HT = 0;
  nJets = 0;
  nBJets = 0;
  passZVeto = true;
  goodLeptons.clear();
  looseMuons.clear();
  looseElectrons.clear();
  goodBJets.clear();
}

void ThreeLepSelector::LoadBranchesNanoAOD(Long64_t entry, std::pair<Systematic, std::string> variation) {
  clearValues();

  b.SetEntry(entry);

  if (nElectron > N_KEEP_MU_E_ || nMuon > N_KEEP_MU_E_) {
    std::string message = "Found more electrons or muons than max read number.\n    Found ";
    message += std::to_string(nElectron);
    message += " electrons.\n    Found ";
    message += std::to_string(nMuon);
    message += " Muons\n  --> Max read number was ";
    message += std::to_string(N_KEEP_MU_E_);
    message += "\nExiting because this can cause problems. Increase N_KEEP_MU_E_ to avoid this error.\n";
    throw std::domain_error(message);
  }

  /// basic setups
  setupElectrons();
  setupMuons();
  setupJets();
  setupChannel();

  // correct goodLeptons vector to order of SS leps first in order of pt
  if (goodLeptons.size() == 3) {
    /// Put same charge leps first
    if (goodLeptons[1].Charge() * goodLeptons[2].Charge() > 0) {
      std::swap(goodLeptons[0], goodLeptons[2]);
    } else if (goodLeptons[0].Charge() * goodLeptons[2].Charge() > 0) {
      std::swap(goodLeptons[1], goodLeptons[2]);
    }
    /// PT swap
    if (goodLeptons[0].Pt() < goodLeptons[1].Pt()) {
      std::swap(goodLeptons[0], goodLeptons[1]);
    }
  } else if (channel_ == em) {
    if (goodLeptons[0].Pt() < goodLeptons[1].Pt()) {
      std::swap(goodLeptons[0], goodLeptons[1]);
    }
  }

  if (isMC_) {
    ApplyScaleFactors();
  }

  passZVeto = true;
  return;
  /// zveto, commented out for now
  // if(goodLeptons.size() >= 2 && looseMuons.size() + looseElectrons.size() >= 3) {
  //   for(auto lep : goodLeptons) {
  //     if(lep.Id() == PID_MUON)
  // 	passZVeto = doesPassZVeto(lep, looseMuons);
  //     else
  // 	passZVeto = doesPassZVeto(lep, looseElectrons);
  //     if(!passZVeto) break;
  //   }
  // }
}

void ThreeLepSelector::setupMuons() {
  for (size_t i = 0; i < nMuon; ++i) {
    if (isGoodMuon(i)) {
      goodLeptons.push_back(GoodPart(SetupPtEtaPhiM(Muon, i)));
      goodLeptons.back().SetPdgId(PID_MUON * Muon_charge[i]);
      if (!passFullIso(goodLeptons.back().v, 0.76, 7.2)) {  // Extra Iso requirement
        goodLeptons.pop_back();
      } else {  // Add to Loose if pass tight
        looseMuons.push_back(goodLeptons.back());
        continue;
      }
    }
    if (isLooseMuon(i)) {
      looseMuons.push_back(GoodPart(SetupPtEtaPhiM(Muon, i)));
      looseMuons.back().SetPdgId(PID_MUON * Muon_charge[i]);
    }
  }
}

void ThreeLepSelector::setupElectrons() {
  for (size_t i = 0; i < nElectron; ++i) {
    if (isGoodElectron(i)) {
      goodLeptons.push_back(GoodPart(SetupPtEtaPhiM(Electron, i)));
      goodLeptons.back().SetPdgId(PID_ELECTRON * Electron_charge[i]);
      if (!passFullIso(goodLeptons.back().v, 0.8, 7.2)) {  // Extra Iso requirement
        goodLeptons.pop_back();
      } else {
        looseElectrons.push_back(goodLeptons.back());
        continue;
      }
    }
    if (isLooseElectron(i)) {
      looseElectrons.push_back(GoodPart(SetupPtEtaPhiM(Electron, i)));
      looseElectrons.back().SetPdgId(PID_ELECTRON * Electron_charge[i]);
    }
  }
}

void ThreeLepSelector::setupJets() {
  for (size_t i = 0; i < nJet; ++i) {
    if (goodLeptons.size() < 2)
      break;  // only try to find jets if have leptons
    /// jet
    if (isGoodJet(i)) {
      nJets++;
      HT += Jet_pt[i];
    }
    // bjet
    if (isGoodBJet(i)) {
      nBJets++;
      goodBJets.push_back(GoodPart(SetupPtEtaPhiM(Jet, i)));
    }
  }
}

void ThreeLepSelector::setupChannel() {
  if (goodLeptons.size() >= 3)
    channelName_ = "lll";
  else if (goodLeptons.size() != 2)
    channelName_ = "Unknown";
  else if (goodLeptons[0].Id() == PID_MUON && goodLeptons[1].Id() == PID_MUON)
    channelName_ = "mm";
  else if (goodLeptons[0].Id() == PID_ELECTRON && goodLeptons[1].Id() == PID_ELECTRON)
    channelName_ = "ee";
  else
    channelName_ = "em";

  channel_ = channelMap_[channelName_];
}

bool ThreeLepSelector::doesPassZVeto(GoodPart& lep, std::vector<GoodPart>& looseList) {
  for (auto lLep : looseList) {
    if ((lep.Charge() * lLep.Charge() < 0) && ((abs((lLep.v + lep.v).M() - 91.188) < 15) || ((lLep.v + lep.v).M() < 12))) {
      return false;
    }
  }
  return true;
}

void ThreeLepSelector::ApplyScaleFactors() {
  weight *= (genWeight > 0) ? 1.0 : -1.0;

  for (auto lep : goodLeptons) {
    if (lep.Id() == PID_MUON) {
      if (mIdSF_ != nullptr)
        weight *= mIdSF_->Evaluate2D(lep.Eta(), lep.Pt());
      if (mIdSF_ != nullptr)
        weight *= mIsoSF_->Evaluate2D(lep.Eta(), lep.Pt());
    } else {
      if (eIdSF_ != nullptr)
        weight *= eIdSF_->Evaluate2D(lep.Eta(), lep.Pt());
      if (eGsfSF_ != nullptr)
        weight *= eGsfSF_->Evaluate2D(lep.Eta(), lep.Pt());
    }
  }
  if (pileupSF_ != nullptr) {
    weight *= pileupSF_->Evaluate1D(numPU);
  }
  // for(auto jet : goodBJets) {
  //   weight *= btag_reader.eval_auto_bounds("central",  BTagEntry::FLAV_B,
  // 					   jet.Eta(), jet.Pt());
  // }

  return;
}

bool ThreeLepSelector::isGoodMuon(size_t index) {
  return ((Muon_pt[index] > 20) && (Muon_tightCharge[index] == 2) && (abs(Muon_eta[index]) < 2.4) && (Muon_mediumId[index]) &&
          (Muon_miniPFRelIso_all[index] < 0.16) && (Muon_dz[index] < 0.1) && (Muon_dxy[index] < 0.05) && (Muon_sip3d[index] < 4));
}

bool ThreeLepSelector::isGoodElectron(size_t index) {
  bool passId = false;

  if (selection_ == FourTopMVAEl || selection_ != FourTopCutBasedEl) {
    int caseIndex = 0;
    if (abs(Electron_eta[index]) < 0.8)
      caseIndex = 0;
    else if (abs(Electron_eta[index]) < 1.479)
      caseIndex = 1;
    else if (abs(Electron_eta[index]) < 2.5)
      caseIndex = 2;

    if (caseIndex == 0)
      passId = Electron_MVA[index] > std::max(0.52, 0.77 - 0.025 * (Electron_pt[index] - 15));
    else if (caseIndex == 1)
      passId = Electron_MVA[index] > std::max(0.11, 0.56 - 0.045 * (Electron_pt[index] - 15));
    else if (caseIndex == 2)
      passId = Electron_MVA[index] > std::max(-0.01, 0.48 - 0.049 * (Electron_pt[index] - 15));
  } else
    passId = (Electron_cutBased[index] == CBID_TIGHT);

  return ((Electron_pt[index] > 20) && (Electron_miniPFRelIso_all[index] < 0.12) && (passId) && (Electron_convVeto[index]) && (Electron_lostHits[index] == 0) &&
          (Electron_dz[index] < 0.1) && (Electron_dxy[index] < 0.05) && (Electron_sip3d[index] < 4));
}

bool ThreeLepSelector::isLooseMuon(size_t index) {
  return ((Muon_isGlobal[index]) && (Muon_isPFcand[index]) && (Muon_miniPFRelIso_all[index] < 0.4) && (Muon_dz[index] < 0.1) && (Muon_dxy[index] < 0.05));
}

bool ThreeLepSelector::isLooseElectron(size_t index) {
  bool passId = false;

  if (selection_ == FourTopMVAEl || selection_ != FourTopCutBasedEl) {
    int caseIndex = 0;
    //// PT Splitting
    if (Electron_pt[index] < 5)
      return false;
    else if (Electron_pt[index] < 10)
      caseIndex += 0;
    else if (Electron_pt[index] < 15)
      caseIndex += 1;
    else if (Electron_pt[index] < 25)
      caseIndex += 2;
    else
      caseIndex += 3;
    //// ETA Splitting
    if (abs(Electron_eta[index]) < 0.8)
      caseIndex += 0;
    else if (abs(Electron_eta[index]) < 1.479)
      caseIndex += 4;
    else if (abs(Electron_eta[index]) < 2.5)
      caseIndex += 8;
    /// MVA numbers. May generalize.
    if (caseIndex == 0)
      passId = Electron_MVA[index] > -0.46;
    else if (caseIndex == 1)
      passId = Electron_MVA[index] > -0.48;
    else if (caseIndex == 2)
      passId = Electron_MVA[index] > -0.48 - 0.037 * (Electron_pt[index] - 15);
    else if (caseIndex == 3)
      passId = Electron_MVA[index] > -0.85;
    else if (caseIndex == 4)
      passId = Electron_MVA[index] > -0.03;
    else if (caseIndex == 5)
      passId = Electron_MVA[index] > -0.67;
    else if (caseIndex == 6)
      passId = Electron_MVA[index] > -0.67 - 0.024 * (Electron_pt[index] - 15);
    else if (caseIndex == 7)
      passId = Electron_MVA[index] > -0.91;
    else if (caseIndex == 8)
      passId = Electron_MVA[index] > 0.06;
    else if (caseIndex == 9)
      passId = Electron_MVA[index] > -0.49;
    else if (caseIndex == 10)
      passId = Electron_MVA[index] > -0.49 - 0.034 * (Electron_pt[index] - 15);
    else if (caseIndex == 11)
      passId = Electron_MVA[index] > -0.83;
  } else {
    passId = (Electron_cutBased[index] >= CBID_LOOSE);
  }
  return ((passId) && (Electron_convVeto[index]) && (Electron_lostHits[index] <= 1) && (Electron_miniPFRelIso_all[index] < 0.4) && (Electron_dz[index] < 0.1) &&
          (Electron_dxy[index] < 0.05));
}

bool ThreeLepSelector::isGoodJet(size_t index) {
  return ((Jet_pt[index] > 40.0) && (abs(Jet_eta[index]) < 2.4) && (Jet_jetId[index] >= 1) && (doesNotOverlap(index)));
}

/// TODO: add toggle for different btag stuff
bool ThreeLepSelector::isGoodBJet(size_t index) {
  return ((Jet_pt[index] > 25.0) && (abs(Jet_eta[index]) < 2.4) && (Jet_jetId[index] >= 1) &&
          // (Jet_btagCSVV2[index] > 0.8484) &&
          (Jet_btagDeepB[index] > 0.6324) && (doesNotOverlap(index)));
}

bool ThreeLepSelector::passFullIso(LorentzVector& lep, int I2, int I3) {
  LorentzVector closeJet;
  double minDR = 10;
  for (size_t index = 0; index < nJet; ++index) {
    LorentzVector jet(SetupPtEtaPhiM(Jet, index));
    double dr = reco::deltaR(jet, lep);
    if (minDR > dr) {
      closeJet = jet;
      minDR = dr;
    }
  }

  if (lep.Pt() / closeJet.Pt() > I2)
    return true;

  auto diff = closeJet.Vect() - lep.Vect();
  auto cross = diff.Cross(lep.Vect());
  return (cross.Mag2() / diff.Mag2() > I3 * I3);
}

bool ThreeLepSelector::doesNotOverlap(size_t index) {
  LorentzVector tmp(SetupPtEtaPhiM(Jet, index));
  double dR = 0.4;
  for (auto lep : goodLeptons) {
    if (reco::deltaR(tmp, lep.v) < dR)
      return false;
  }
  return true;
}

void ThreeLepSelector::FillHistograms(Long64_t entry, std::pair<Systematic, std::string> variation) {
  int step = 0;
  Fill1D("CutFlow", 0);

  /// 2 good leptons
  if (goodLeptons.size() < 2)
    return;
  Fill1D("CutFlow", ++step);

  // first lep requirement
  if (goodLeptons[0].Pt() < 25)
    return;
  Fill1D("CutFlow", ++step);

  // same sign requirement
  if ((goodLeptons.size() == 2 && goodLeptons[0].Charge() * goodLeptons[1].Charge() < 0) ||
      (goodLeptons.size() == 3 && goodLeptons[0].Charge() * goodLeptons[2].Charge() > 0))
    return;
  Fill1D("CutFlow", ++step);

  // met cut
  if (MET < 50)
    return;
  Fill1D("CutFlow", ++step);

  // ht cut
  if (HT < 300)
    return;
  Fill1D("CutFlow", ++step);

  // jet cut
  if (nJets < 2)
    return;
  Fill1D("CutFlow", ++step);

  // bjet cut
  if (nBJets < 2)
    return;
  Fill1D("CutFlow", ++step);

  // // veto cut
  // if(!passZVeto) return;
  // Fill1D("CutFlow", ++step);
  Fill1D("SR", getSRBin());

  if (getSRBin() == -1) {
    return;
  } else if (getSRBin() == 0) {
    Fill1D("CRW_njet", nJets);
    Fill1D("CRW_nbjet", nBJets);
    return;
  } else if (getSRBin() == 9) {
    Fill1D("CRZ_njet", nJets);
    Fill1D("CRZ_nbjet", nBJets);
    return;
  }

  HistFullFill(histMap1D_, "weight", variation.second, abs(weight), 1);
  Fill1D("Met", MET);
  Fill1D("HT", HT);
  Fill1D("ptl1", goodLeptons[0].Pt());
  Fill1D("ptl2", goodLeptons[1].Pt());
  Fill1D("njet", nJets);
  Fill1D("nbjet", nBJets);
  //  Fill2D("bJetvsJets", nJets, nBJets);
  Fill1D("nleps", goodLeptons.size());

  for (size_t i = 0; i < nJet; ++i) {
    if (isGoodJet(i)) {
      Fill1D("jetpt", Jet_pt[i]);
    }
    if (isGoodBJet(i)) {
      Fill1D("bjetpt", Jet_pt[i]);
    }
  }
}

void ThreeLepSelector::SetupNewDirectory() {
  SelectorBase::SetupNewDirectory();

  InitializeHistogramsFromConfig();
}

int ThreeLepSelector::getSRBin() const {
  if (goodLeptons.size() == 2) {
    if (nBJets == 2) {
      if (!passZVeto)
        return -1;
      else if (nJets <= 5)
        return 0;  // WCR
      else if (nJets == 6)
        return 1;
      else if (nJets == 7)
        return 2;
      else if (nJets >= 8)
        return 3;
    } else if (nBJets == 3) {
      if (nJets == 5)
        return 4;
      else if (nJets == 6)
        return 4;
      else if (nJets >= 7)
        return 5;
    } else if (nBJets >= 4) {
      if (nJets >= 5)
        return 6;
    }
  } else {
    if (!passZVeto)
      return 9;  /// ZCR
    else if (nBJets == 2 && nJets >= 5)
      return 7;
    else if (nBJets >= 3 && nJets >= 4)
      return 8;
  }
  return -1;
}
