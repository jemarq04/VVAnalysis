#include "Analysis/VVAnalysis/interface/ZZSelector.h"
#include "TLorentzVector.h"
#include <boost/algorithm/string.hpp>
#include <utility>

void ZZSelector::Init(TTree* tree) {
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

  // This would be set true inside ZZBackground Selector
  // isNonPrompt_ = false;

  systHists_ = {"yield",       "Mass",       "MassFull",     "nJets",        "nJets_central", "jetPt[1]",     "jetPt[0]",
                "jetEta[0]",   "jetEta[1]",  "absjetEta[0]", "absjetEta[1]", "Mass0j",        "Mass1j",       "Mass2j",
                "Mass3j",      "Mass34j",    "Mass4j",       "Mass0jFull",   "Mass1jFull",    "Mass2jFull",   "Mass3jFull",
                "Mass34jFull", "Mass4jFull", "CosTheta1",    "CosTheta2",    "CosThetaStar",  "RapidityDiff", "dPhiOSll"};
  // hists1D_ = {
  //      "yield", "backgroundControlYield","nTruePU","nvtx","ZMass","Z1Mass","Z2Mass","ZZPt",
  //      "Z1Pt","Z2Pt","Z1Phi","Z2Phi","dPhiZ1Z2","ZPt","LepPt","LepEta",
  //      "Z1lep1_Eta","Z1lep1_Phi","Z1lep1_Pt","Z1lep1_PdgId","Z1lep2_Eta",
  //      "Z1lep2_Phi","Z1lep2_Pt","Z1lep2_PdgId","Z2lep1_Eta","Z2lep1_Phi","Z2lep1_Pt","Z2lep1_PdgId",
  //      "Z2lep2_Eta","Z2lep2_Phi","Z2lep2_Pt","Z2lep2_PdgId","Mass","nJets",
  // };

  hists1D_ = {"yield",        "Z1Mass",    "Z2Mass",       "ZMass",        "Z1MassFull", "Z2MassFull", "ZMassFull",   "EleZMass",      "MuZMass",
              "LepPt",        "ElePt",     "MuPt",         "LepPt1",       "LepPt2",     "LepPt3",     "LepPt4",      "Z1LepPt",       "Z2LepPt",
              "LepEta",       "EleEta",    "MuEta",        "Mass",         "ZZPt",       "ZPt",        "nJets",       "nJets_central", "MassFull",
              "CosTheta1",    "CosTheta2", "CosThetaStar", "RapidityDiff", "dPhiOSll",   "Mass0j",     "Mass1j",      "Mass2j",        "Mass3j",
              "Mass34j",      "Mass4j",    "Mass0jFull",   "Mass1jFull",   "Mass2jFull", "Mass3jFull", "Mass34jFull", "Mass4jFull",    "jetEta[0]",
              "absjetEta[0]", "jetEta[1]", "absjetEta[1]", "jetPt[0]",     "jetPt[1]"};

  jetTest2D_ = {};  // also defined in hists1D_ to pass checks in InitializeHistogramsFromConfig()
  jethists1D_ = {"Mass",         "MassFull",     "nJets",      "nJets_central", "jetPt[1]",   "jetPt[0]",   "jetEta[0]",   "jetEta[1]",
                 "absjetEta[0]", "absjetEta[1]", "mjj",        "dEtajj",        "Mass0j",     "Mass1j",     "Mass2j",      "Mass3j",
                 "Mass34j",      "Mass4j",       "Mass0jFull", "Mass1jFull",    "Mass2jFull", "Mass3jFull", "Mass34jFull", "Mass4jFull"};

  weighthists1D_ = {"yield",        "Z1Mass",    "Z2Mass",       "ZMass",        "Z1MassFull", "Z2MassFull", "ZMassFull",   "EleZMass",      "MuZMass",
                    "LepPt",        "ElePt",     "MuPt",         "LepPt1",       "LepPt2",     "LepPt3",     "LepPt4",      "Z1LepPt",       "Z2LepPt",
                    "LepEta",       "EleEta",    "MuEta",        "Mass",         "ZZPt",       "ZPt",        "nJets",       "nJets_central", "MassFull",
                    "CosTheta1",    "CosTheta2", "CosThetaStar", "RapidityDiff", "dPhiOSll",   "Mass0j",     "Mass1j",      "Mass2j",        "Mass3j",
                    "Mass34j",      "Mass4j",    "Mass0jFull",   "Mass1jFull",   "Mass2jFull", "Mass3jFull", "Mass34jFull", "Mass4jFull",    "jetEta[0]",
                    "absjetEta[0]", "jetEta[1]", "absjetEta[1]", "jetPt[0]",     "jetPt[1]"};
  ZZSelectorBase::Init(tree);
  // fCutFormula = new TTreeFormula("CutFormula", fOption, fChain);
  // fCutFormula->SetQuickLoad(kTRUE);
  // if (!fCutFormula->GetNdim())
  //{
  //   delete fCutFormula;
  //   fCutFormula = 0;
  // }
  fCutFormula = 0;  // turn off trigger cut test
}

void ZZSelector::SetBranchesUWVV() {
  ZZSelectorBase::SetBranchesUWVV();
  if (isMC_) {
    weight_info_ = GetLheWeightInfo();
    if (weight_info_ > 0) {
      fChain->SetBranchAddress("scaleWeights", &scaleWeights, &b_scaleWeights);
      if (weight_info_ == 4) {
        fChain->SetBranchAddress("scaleWeightIDs", &scaleWeightIDs, &b_scaleWeightIDs);
        b_scaleWeightIDs->GetEntry(0);
        for (size_t i = 0; i < scaleWeightIDs->size(); i++) {
          SafeHistFill(histMap1D_, getHistName("scaleWeightIDs", ""), i, scaleWeightIDs->at(i));
        }
      }
    }
    if ((weight_info_ == 2 || weight_info_ == 3) && doSystematics_ && !isNonPrompt_)
      fChain->SetBranchAddress("pdfWeights", &pdfWeights, &b_pdfWeights);
    //if (weight_info_ > 0) std::cout << "NOTE: Weight info stored!" << std::endl;
    //else std::cout << "NOTE: Weight info not stored!" << std::endl;
  }
  fChain->SetBranchAddress("Mass", &Mass, &b_Mass);
  fChain->SetBranchAddress("Pt", &Pt, &b_Pt);
  fChain->SetBranchAddress("Eta", &Eta, &b_Eta);

  fChain->SetBranchAddress("jetPt", &jetPt, &b_jetPt);

  fChain->SetBranchAddress("jetPUID", &jetPUID, &b_jetPUID);
  if (isMC_) {
    applyPUSF_ = false;
    if (applyPUSF_ || applyPUSFNtp_) {
      try {  // catching doesn't seem to work. Crash directly in either here or getentry()
        fChain->SetBranchAddress("isGenJetMatched", &isGenJetMatched, &b_isGenJetMatched);
        fChain->SetBranchAddress("jetPUSFmulfac", &jetPUSFmulfac, &b_jetPUSFmulfac);
      } catch (...) {
        applyPUSF_ = false;
        std::cout << "Cannot set address; PU SF is not applied for this sample" << std::endl;
      }
    }
    fChain->SetBranchAddress("jetPt_jesUp", &jetPt_jesUp, &b_jetPt_jesUp);
    fChain->SetBranchAddress("jetPt_jesDown", &jetPt_jesDown, &b_jetPt_jesDown);
    fChain->SetBranchAddress("jetPt_jerUp", &jetPt_jerUp, &b_jetPt_jerUp);
    fChain->SetBranchAddress("jetPt_jerDown", &jetPt_jerDown, &b_jetPt_jerDown);
  }

  fChain->SetBranchAddress("jetPhi", &jetPhi, &b_jetPhi);

  fChain->SetBranchAddress("jetEta", &jetEta, &b_jetEta);
  if (isMC_) {
    fChain->SetBranchAddress("jetEta_jesUp", &jetEta_jesUp, &b_jetEta_jesUp);
    fChain->SetBranchAddress("jetEta_jesDown", &jetEta_jesDown, &b_jetEta_jesDown);
    fChain->SetBranchAddress("jetEta_jerUp", &jetEta_jerUp, &b_jetEta_jerUp);
    fChain->SetBranchAddress("jetEta_jerDown", &jetEta_jerDown, &b_jetEta_jerDown);
  }

  fChain->SetBranchAddress("mjj", &mjj, &b_mjj);
  if (isMC_) {
    fChain->SetBranchAddress("mjj_jesUp", &mjj_jesUp, &b_mjj_jesUp);
    fChain->SetBranchAddress("mjj_jesDown", &mjj_jesDown, &b_mjj_jesDown);
    fChain->SetBranchAddress("mjj_jerUp", &mjj_jerUp, &b_mjj_jerUp);
    fChain->SetBranchAddress("mjj_jerDown", &mjj_jerDown, &b_mjj_jerDown);
  }

  fChain->SetBranchAddress("nJets", &nJets, &b_nJets);
  if (isMC_) {
    fChain->SetBranchAddress("nJets_jesUp", &nJets_jesUp, &b_nJets_jesUp);
    fChain->SetBranchAddress("nJets_jesDown", &nJets_jesDown, &b_nJets_jesDown);
    fChain->SetBranchAddress("nJets_jerUp", &nJets_jerUp, &b_nJets_jerUp);
    fChain->SetBranchAddress("nJets_jerDown", &nJets_jerDown, &b_nJets_jerDown);
  }
}

unsigned int ZZSelector::GetLheWeightInfo() {
  std::vector<std::string> noLheWeights = {"ggZZ2e2mu",
                                           "ggZZ4e",
                                           "ggZZ4m",
                                           "ggZZ4t",
                                           "ggZZ2e2tau",
                                           "ggZZ2mu2tau",
                                           "zz4l-sherpa",
                                           "ZZJJTo2e2mu-EWK-phantom",
                                           "ZZJJTo4e-EWK-phantom",
                                           "ZZJJTo4mu-EWK-phantom"};
  std::vector<std::string> scaleWeightsAndIDs = {"pp_eemm-cHWB_massless",
                                                 "pp_eemm-cHG_massless",
                                                 "pp_eemm-cll1_massless",
                                                 "pp_eemm-ceu_massless",
                                                 "pp_eemm-ced_massless",
                                                 "pp_eemm-cee_massless",
                                                 "pp_eemm-cll_massless",
                                                 "pp_eemmj-cHG_massless",
                                                 "gg_eemm-cHG_massless"};
  std::vector<std::string> scaleAndPdfWeights = {"wz3lnu-powheg", "wz3lnu-mg5amcnlo", "ZZZ", "WZZ", "WWZ", "zz4l-powheg", "zz4l-amcatnlo", "ZZJJTo4L-EWK"};
  std::vector<std::string> allLheWeights = {
      //"wzjj-aqgcft", "wzjj-aqgcfm", "wzjj-aqgcfs",
      //"wz-atgc_pt0-200", "wz-atgc_pt200-300",
      //"wz-atgc_pt300"
  };

  if (isaTGC_)
    return 0;

  for (std::string other : noLheWeights)
    if (name_.rfind(other, 0) == 0)
      return 0;
  for (std::string other : scaleAndPdfWeights)
    if (name_.rfind(other, 0) == 0)
      return 2;
  for (std::string other : allLheWeights)
    if (name_.rfind(other, 0) == 0)
      return 3;
  for (std::string other : scaleWeightsAndIDs)
    if (name_.rfind(other, 0) == 0)
      return 4;

  if (isUL_L1check)
    return 0;
  return 1;
}

bool ZZSelector::CheckQQZZ() {
  std::vector<std::string> samples = {"zz4l-powheg", "zz4l-amcatnlo", "qqZZSpec", "zz4l-powheg_postEE", "zz4l-amcatnlo_postEE", "qqZZSpec_postEE"};
  return std::find(samples.begin(), samples.end(), name_) != samples.end();
}

void ZZSelector::LoadBranchesUWVV(Long64_t entry, std::pair<Systematic, std::string> variation) {
  ZZSelectorBase::LoadBranchesUWVV(entry, variation);
  if ((channel_ == eemm || channel_ == mmee) && skipEvent_2e2m_)
    return;

  passCurrentTrig = (fCutFormula && fCutFormula->EvalInstance() > 0.);

  // Event branches
  b_Mass->GetEntry(entry);
  b_Pt->GetEntry(entry);
  b_Eta->GetEntry(entry);

  // Jet branches
  b_jetPhi->GetEntry(entry);
  b_mjj->GetEntry(entry);
  b_jetPt->GetEntry(entry);
  b_jetPUID->GetEntry(entry);
  b_jetEta->GetEntry(entry);
  b_nJets->GetEntry(entry);

  // Jet systematics and PUSF
  if (isMC_) {
    b_mjj_jesUp->GetEntry(entry);
    b_mjj_jesDown->GetEntry(entry);
    b_mjj_jerUp->GetEntry(entry);
    b_mjj_jerDown->GetEntry(entry);
    b_jetPt_jesUp->GetEntry(entry);
    b_jetPt_jesDown->GetEntry(entry);
    b_jetPt_jerUp->GetEntry(entry);
    b_jetPt_jerDown->GetEntry(entry);
    b_jetEta_jesUp->GetEntry(entry);
    b_jetEta_jesDown->GetEntry(entry);
    b_jetEta_jerUp->GetEntry(entry);
    b_jetEta_jerDown->GetEntry(entry);
    b_nJets_jesUp->GetEntry(entry);
    b_nJets_jesDown->GetEntry(entry);
    b_nJets_jerUp->GetEntry(entry);
    b_nJets_jerDown->GetEntry(entry);
    if (applyPUSF_ || applyPUSFNtp_) {
      try {  // catching doesn't seem to work. Crash directly somewhere for sample without isGenJetMatched.
        b_isGenJetMatched->GetEntry(entry);
        b_jetPUSFmulfac->GetEntry(entry);
      } catch (...) {
        applyPUSF_ = false;
        std::cout << "PU SF is not applied for this sample" << std::endl;
      }
    }
  }

  // Apply scale factors
  if (isMC_)
    ApplyScaleFactors();

  // Jet gen matching
  if (isMC_) {
    bool applyjetMatch = false;
    if (applyjetMatch) {
      // apply gen jet matching for remaining processing if MC. For data, should apply PU id at ntuplization step but can also apply here
      if (jetPt->size() == jetEta->size() && jetPt->size() == jetPUID->size() && jetPUID->size() == isGenJetMatched->size()) {
        auto jetit = jetPt->begin();
        auto jetait = jetEta->begin();
        auto jPUIDit = jetPUID->begin();
        auto jmatchit = isGenJetMatched->begin();

        while (jetit != jetPt->end()) {
          if (*jmatchit < 1) {
            jetit = jetPt->erase(jetit);
            jetait = jetEta->erase(jetait);
            jPUIDit = jetPUID->erase(jPUIDit);
            jmatchit = isGenJetMatched->erase(jmatchit);
            // std::cout<<"A jet is removed by PU id"<<std::endl;
          } else {
            ++jetit;
            ++jetait;
            ++jPUIDit;
            ++jmatchit;
          }
        }
      } else {
        std::cout << "Something Wrong jetPt vs jetEta, jetPUID, isGenJetMatched size" << jetPt->size() << " " << jetEta->size();
        std::cout << " " << jetPUID->size() << std::endl;  //<< " " << isGenJetMatched->size() << std::endl;
      }
    }
  }

  if (variation.first == Central) {
    // Get LHE weights
    if (isMC_ && !isNonPrompt_ && weight_info_ > 0) {
      b_scaleWeights->GetEntry(entry);
      lheWeights = *scaleWeights;
      //std::cout << "NOTE: LHE Weights found = " << lheWeights.size() << std::endl;

      if (doSystematics_) {
        if (weight_info_ == 2) {
          b_pdfWeights->GetEntry(entry);
          // Only keep NNPDF weights
          lheWeights.insert(lheWeights.end(), pdfWeights->begin(), pdfWeights->begin() + std::min(static_cast<size_t>(103), pdfWeights->size()));
        } else if (weight_info_ == 3) {
          b_pdfWeights->GetEntry(entry);
          lheWeights.insert(lheWeights.end(), pdfWeights->begin(), pdfWeights->end());
        }
      }
    }
  } else if (isMC_)  // Systematic uncertainties and creating shiftUp and shiftDown histograms
    ShiftEfficiencies(variation.first);

  // Determine Z1 and Z2 for 2e2mu channels
  if (channel_ == eemm || channel_ == mmee)
    if (TightZZLeptons())
      SetVariables(entry);

  // Calculate extra variables for analysis
  auto deltaPhiZZ = [](float phi1, float phi2) {
    float pi = TMath::Pi();
    float dphi = fabs(phi1 - phi2);
    if (dphi > pi)
      dphi = 2.0 * pi - dphi;
    return dphi;
  };
  auto deltaEtajj = [](std::vector<float>* jEta) {
    if (jEta->size() < 2)
      return -1.;
    double etaDiff = jEta->at(0) - jEta->at(1);
    return std::abs(etaDiff);
  };

  auto deltaRZZ = [](float eta1, float eta2, float dPhi) {
    float dEta = eta1 - eta2;
    return std::sqrt(dPhi * dPhi + dEta * dEta);
  };

  dEtajj = deltaEtajj(jetEta);
  dPhiZZ = deltaPhiZZ(Z1Phi, Z2Phi);
  dRZZ = deltaRZZ(Z1Eta, Z2Eta, dPhiZZ);

  auto polCosTheta = [](const TLorentzVector& zzp4, const TLorentzVector& zp4_input, const TLorentzVector& lp4_input) {
    TLorentzVector zp4 = zp4_input;
    TLorentzVector lp4 = lp4_input;

    lp4.Boost(-zp4.BoostVector());
    zp4.Boost(-zzp4.BoostVector());

    return lp4.Vect().Dot(zp4.Vect()) / (lp4.Vect().Mag() * zp4.Vect().Mag());
  };
  auto polCosThetaStar = [](const TLorentzVector& zzp4, const TLorentzVector& zp4_input) {
    TLorentzVector zp4 = zp4_input;

    zp4.Boost(-zzp4.BoostVector());

    return zp4.Vect().Dot(zzp4.Vect()) / (zp4.Vect().Mag() * zzp4.Vect().Mag());
  };

  /*
  using FourVec = ROOT::Math::PtEtaPhiEVector;
  auto polCosTheta_new = [](const FourVec& zzp4_input, const FourVec& zp4_input, const FourVec& lp4_input) {
    FourVec zp4 = zp4_input;
    FourVec lp4 = lp4_input;

    ROOT::Math::VectorUtil::boost(lp4, -zp4_input.BoostToCM());   // Boost lepton to Z rest frame
    ROOT::Math::VectorUtil::boost(zp4, -zzp4_input.BoostToCM());  // Boost Z to ZZ rest frame

    return lp4.Vect().Dot(zp4.Vect()) / std::sqrt(lp4.Vect().Mag2() * zp4.Vect().Mag2());
  };
  auto polCosThetaStar_new = [](const FourVec& zzp4_input, const FourVec& zp4_input) {
    FourVec zp4 = zp4_input;

    ROOT::Math::VectorUtil::boost(zp4, -zzp4_input.BoostToCM());  // Boost Z to ZZ rest frame

    return zp4.Vect().Dot(zzp4_input.Vect()) / std::sqrt(zp4.Vect().Mag2() * zzp4_input.Vect().Mag2());
  };
  */

  TLorentzVector lp1p4, lp2p4;
  //FourVec lp1p4_new, lp2p4_new;
  if (l1PdgId > 0) {
    lp1p4.SetPtEtaPhiE(l1Pt, l1Eta, l1Phi, l1Energy);
    //lp1p4_new = FourVec(l1Pt, l1Eta, l1Phi, l1Energy);
  } else {
    lp1p4.SetPtEtaPhiE(l2Pt, l2Eta, l2Phi, l2Energy);
    //lp1p4_new = FourVec(l2Pt, l2Eta, l2Phi, l2Energy);
  }
  if (l3PdgId > 0) {
    lp2p4.SetPtEtaPhiE(l3Pt, l3Eta, l3Phi, l3Energy);
    //lp2p4_new = FourVec(l3Pt, l3Eta, l3Phi, l3Energy);
  } else {
    lp2p4.SetPtEtaPhiE(l4Pt, l4Eta, l4Phi, l4Energy);
    //lp2p4_new = FourVec(l4Pt, l4Eta, l4Phi, l4Energy);
  }
  TLorentzVector z1p4, z2p4, zzp4;
  z1p4.SetPtEtaPhiM(Z1Pt, Z1Eta, Z1Phi, Z1Mass);
  z2p4.SetPtEtaPhiM(Z2Pt, Z2Eta, Z2Phi, Z2Mass);
  zzp4 = z1p4 + z2p4;
  //FourVec z1p4_new(Z1Pt, Z1Eta, Z1Phi, Z1Mass);
  //FourVec z2p4_new(Z2Pt, Z2Eta, Z2Phi, Z2Mass);
  //FourVec zzp4_new = z1p4_new + z2p4_new;

  CosTheta1 = polCosTheta(zzp4, z1p4, lp1p4);
  CosTheta2 = polCosTheta(zzp4, z2p4, lp2p4);
  CosThetaStar = polCosThetaStar(zzp4, z1p4);

  RapidityDiff = std::abs(z1p4.Rapidity() - z2p4.Rapidity());

  // delta phi between positron and muon
  if (channel_ == eemm) {
    if (l1PdgId > 0) {  //l1 is positron
      if (l3PdgId < 0)
        dPhiOSll = deltaPhiZZ(l1Phi, l3Phi);
      else
        dPhiOSll = deltaPhiZZ(l1Phi, l4Phi);
    } else {  //l2 is positron
      if (l3PdgId < 0)
        dPhiOSll = deltaPhiZZ(l2Phi, l3Phi);
      else
        dPhiOSll = deltaPhiZZ(l2Phi, l4Phi);
    }
  } else if (channel_ == mmee) {
    if (l3PdgId > 0) {  //l3 is positron
      if (l1PdgId < 0)
        dPhiOSll = deltaPhiZZ(l3Phi, l1Phi);
      else
        dPhiOSll = deltaPhiZZ(l3Phi, l2Phi);
    } else {  //l4 is positron
      if (l1PdgId < 0)
        dPhiOSll = deltaPhiZZ(l4Phi, l1Phi);
      else
        dPhiOSll = deltaPhiZZ(l4Phi, l2Phi);
    }
  } else {
    dPhiOSll = -99;
  }
}

void ZZSelector::ApplyScaleFactors() {
  if (CheckQQZZ() && qqZZ_kfac_ != nullptr) {
    if (channel_ == eeee || channel_ == mmmm)
      weight *= qqZZ_kfac_->at("qqZZ4l_NLO_NNLO")->evaluate({Mass});
    else
      weight *= qqZZ_kfac_->at("qqZZ2l2l_NLO_NNLO")->evaluate({Mass});
  }

  if (applyPUSFNtp_)
    weight *= jetPUSFmulfac;

  if (applyPUSF_) {
    for (std::size_t ind = 0; ind < jetPt->size(); ind++) {
      // only used real jets for applying SF
      if (isGenJetMatched->at(ind) < 1)
        continue;

      if (jetPt->at(ind) < 50) {
        float jetPUSF = jetPUSF_->at("PUJetID_eff")->evaluate({jetEta->at(ind), jetPt->at(ind), "nom", "T"});
        float jeffPU = jetPUSF_->at("PUJetID_eff")->evaluate({jetEta->at(ind), jetPt->at(ind), "MCEff", "T"});
        float mulfac = 1.;

        // doesn't pass PU id
        if (jetPUID->at(ind) < 7)
          mulfac = (1. - jetPUSF * jeffPU) / (1. - jeffPU);
        else
          mulfac = jetPUSF;

        weight *= mulfac;
      }
    }
  }

  // In order to get around the Overflow issue, set the Pt, not ideal.
  // std::cout<<"weight before SF: "<<weight<<std::endl;
  if (channel_ == eeee) {
    float pt_e1 = l1Pt < EleSF_MAX_PT_ ? l1Pt : EleSF_MAX_PT_ - 0.01;
    float pt_e2 = l2Pt < EleSF_MAX_PT_ ? l2Pt : EleSF_MAX_PT_ - 0.01;
    float pt_e3 = l3Pt < EleSF_MAX_PT_ ? l3Pt : EleSF_MAX_PT_ - 0.01;
    float pt_e4 = l4Pt < EleSF_MAX_PT_ ? l4Pt : EleSF_MAX_PT_ - 0.01;
    if (eIdSF_ != nullptr) {
      if (pt_e1 > EleSF_MIN_PT_) {
        if (year == "2023D" && (l1Eta < 0 && l1Eta > -1.5 && l1Phi < -0.8 && l1Phi > -1.2))
          weight *= eIdSF_->at("2023D_Hole")->evaluate({l1Eta, pt_e1, "nominal"});
        else
          weight *= eIdSF_->at(year.c_str())->evaluate({l1Eta, pt_e1, "nominal"});
      }
      if (pt_e2 > EleSF_MIN_PT_) {
        if (year == "2023D" && (l2Eta < 0 && l2Eta > -1.5 && l2Phi < -0.8 && l2Phi > -1.2))
          weight *= eIdSF_->at("2023D_Hole")->evaluate({l2Eta, pt_e2, "nominal"});
        else
          weight *= eIdSF_->at(year.c_str())->evaluate({l2Eta, pt_e2, "nominal"});
      }
      if (pt_e3 > EleSF_MIN_PT_) {
        if (year == "2023D" && (l3Eta < 0 && l3Eta > -1.5 && l3Phi < -0.8 && l3Phi > -1.2))
          weight *= eIdSF_->at("2023D_Hole")->evaluate({l3Eta, pt_e3, "nominal"});
        else
          weight *= eIdSF_->at(year.c_str())->evaluate({l3Eta, pt_e3, "nominal"});
      }
      if (pt_e4 > EleSF_MIN_PT_) {
        if (year == "2023D" && (l4Eta < 0 && l4Eta > -1.5 && l4Phi < -0.8 && l4Phi > -1.2))
          weight *= eIdSF_->at("2023D_Hole")->evaluate({l4Eta, pt_e4, "nominal"});
        else
          weight *= eIdSF_->at(year.c_str())->evaluate({l4Eta, pt_e4, "nominal"});
      }
    }
    if (eRecoSF_ != nullptr) {
      const auto recoref = (*eRecoSF_->begin()).second;
      if (pt_e1 > EleRecoSF_MIN_PT_) {
        if (EleRecoSF_Name_.rfind("2023", 0) != std::string::npos)
          weight *= recoref->evaluate({EleRecoSF_Name_.c_str(), "sf", GetEleRecoSFName(pt_e1), l1Eta, pt_e1, l1Phi});
        else if (EleRecoSF_Name_ != "2025Prompt" || GetEleRecoSFName(pt_e1) != "RecoBelow20")
          weight *= recoref->evaluate({EleRecoSF_Name_.c_str(), "sf", GetEleRecoSFName(pt_e1), l1Eta, pt_e1});
      }
      if (pt_e2 > EleRecoSF_MIN_PT_) {
        if (EleRecoSF_Name_.rfind("2023", 0) != std::string::npos)
          weight *= recoref->evaluate({EleRecoSF_Name_.c_str(), "sf", GetEleRecoSFName(pt_e2), l2Eta, pt_e2, l2Phi});
        else if (EleRecoSF_Name_ != "2025Prompt" || GetEleRecoSFName(pt_e2) != "RecoBelow20")
          weight *= recoref->evaluate({EleRecoSF_Name_.c_str(), "sf", GetEleRecoSFName(pt_e2), l2Eta, pt_e2});
      }
      if (pt_e3 > EleRecoSF_MIN_PT_) {
        if (EleRecoSF_Name_.rfind("2023", 0) != std::string::npos)
          weight *= recoref->evaluate({EleRecoSF_Name_.c_str(), "sf", GetEleRecoSFName(pt_e3), l3Eta, pt_e3, l3Phi});
        else if (EleRecoSF_Name_ != "2025Prompt" || GetEleRecoSFName(pt_e3) != "RecoBelow20")
          weight *= recoref->evaluate({EleRecoSF_Name_.c_str(), "sf", GetEleRecoSFName(pt_e3), l3Eta, pt_e3});
      }
      if (pt_e4 > EleRecoSF_MIN_PT_) {
        if (EleRecoSF_Name_.rfind("2023", 0) != std::string::npos)
          weight *= recoref->evaluate({EleRecoSF_Name_.c_str(), "sf", GetEleRecoSFName(pt_e4), l4Eta, pt_e4, l4Phi});
        else if (EleRecoSF_Name_ != "2025Prompt" || GetEleRecoSFName(pt_e4) != "RecoBelow20")
          weight *= recoref->evaluate({EleRecoSF_Name_.c_str(), "sf", GetEleRecoSFName(pt_e4), l4Eta, pt_e4});
      }
    }
  } else if (channel_ == eemm || channel_ == mmee) {
    float pt_e1 = l1Pt < EleSF_MAX_PT_ ? l1Pt : EleSF_MAX_PT_ - 0.01;
    float pt_e2 = l2Pt < EleSF_MAX_PT_ ? l2Pt : EleSF_MAX_PT_ - 0.01;
    float pt_m3 = l3Pt < MuSF_MAX_PT_ ? l3Pt : MuSF_MAX_PT_ - 0.01;
    float pt_m4 = l4Pt < MuSF_MAX_PT_ ? l4Pt : MuSF_MAX_PT_ - 0.01;
    if (eIdSF_ != nullptr) {
      if (pt_e1 > EleSF_MIN_PT_) {
        if (year == "2023D" && (l1Eta < 0 && l1Eta > -1.5 && l1Phi < -0.8 && l1Phi > -1.2))
          weight *= eIdSF_->at("2023D_Hole")->evaluate({l1Eta, pt_e1, "nominal"});
        else if (EleRecoSF_Name_ != "2025Prompt" || GetEleRecoSFName(pt_e1) != "RecoBelow20")
          weight *= eIdSF_->at(year.c_str())->evaluate({l1Eta, pt_e1, "nominal"});
      }
      if (pt_e2 > EleSF_MIN_PT_) {
        if (year == "2023D" && (l2Eta < 0 && l2Eta > -1.5 && l2Phi < -0.8 && l2Phi > -1.2))
          weight *= eIdSF_->at("2023D_Hole")->evaluate({l2Eta, pt_e2, "nominal"});
        else if (EleRecoSF_Name_ != "2025Prompt" || GetEleRecoSFName(pt_e2) != "RecoBelow20")
          weight *= eIdSF_->at(year.c_str())->evaluate({l2Eta, pt_e2, "nominal"});
      }
    }
    if (eRecoSF_ != nullptr) {
      const auto recoref = (*eRecoSF_->begin()).second;
      if (pt_e1 > EleRecoSF_MIN_PT_) {
        if (EleRecoSF_Name_.rfind("2023", 0) != std::string::npos)
          weight *= recoref->evaluate({EleRecoSF_Name_.c_str(), "sf", GetEleRecoSFName(pt_e1), l1Eta, pt_e1, l1Phi});
        else if (EleRecoSF_Name_ != "2025Prompt" || GetEleRecoSFName(pt_e1) != "RecoBelow20")
          weight *= recoref->evaluate({EleRecoSF_Name_.c_str(), "sf", GetEleRecoSFName(pt_e1), l1Eta, pt_e1});
      }
      if (pt_e2 > EleRecoSF_MIN_PT_) {
        if (EleRecoSF_Name_.rfind("2023", 0) != std::string::npos)
          weight *= recoref->evaluate({EleRecoSF_Name_.c_str(), "sf", GetEleRecoSFName(pt_e2), l2Eta, pt_e2, l2Phi});
        else if (EleRecoSF_Name_ != "2025Prompt" || GetEleRecoSFName(pt_e2) != "RecoBelow20")
          weight *= recoref->evaluate({EleRecoSF_Name_.c_str(), "sf", GetEleRecoSFName(pt_e2), l2Eta, pt_e2});
      }
    }
    if (mIdSF_ != nullptr) {
      if (pt_m3 > MuSF_MIN_PT_)
        weight *= mIdSF_->at(year.c_str())->evaluate({l3Eta, pt_m3, "nominal"});
      if (pt_m4 > MuSF_MIN_PT_)
        weight *= mIdSF_->at(year.c_str())->evaluate({l4Eta, pt_m4, "nominal"});
    }
  } else {
    float pt_m1 = l1Pt < MuSF_MAX_PT_ ? l1Pt : MuSF_MAX_PT_ - 0.01;
    float pt_m2 = l2Pt < MuSF_MAX_PT_ ? l2Pt : MuSF_MAX_PT_ - 0.01;
    float pt_m3 = l3Pt < MuSF_MAX_PT_ ? l3Pt : MuSF_MAX_PT_ - 0.01;
    float pt_m4 = l4Pt < MuSF_MAX_PT_ ? l4Pt : MuSF_MAX_PT_ - 0.01;
    if (mIdSF_ != nullptr) {
      if (pt_m1 > MuSF_MIN_PT_)
        weight *= mIdSF_->at(year.c_str())->evaluate({l1Eta, pt_m1, "nominal"});
      if (pt_m2 > MuSF_MIN_PT_)
        weight *= mIdSF_->at(year.c_str())->evaluate({l2Eta, pt_m2, "nominal"});
      if (pt_m3 > MuSF_MIN_PT_)
        weight *= mIdSF_->at(year.c_str())->evaluate({l3Eta, pt_m3, "nominal"});
      if (pt_m4 > MuSF_MIN_PT_)
        weight *= mIdSF_->at(year.c_str())->evaluate({l4Eta, pt_m4, "nominal"});
    }
  }
  if (pileupSF_ != nullptr)
    weight *= (*pileupSF_->begin()).second->evaluate({nTruePU, "nominal"});
}

void ZZSelector::SetVariables(Long64_t entry) {
  // By default, e1e2 is Z1. if that's not true, swap Z candidate entries
  if (!(e1e2IsZ1())) {
    std::swap(Z1Mass, Z2Mass);
    std::swap(Z1Pt, Z2Pt);
    std::swap(Z1Eta, Z2Eta);
    std::swap(Z1Phi, Z2Phi);
    std::swap(l1IsTight, l3IsTight);
    std::swap(l2IsTight, l4IsTight);
    std::swap(l1IsIso, l3IsIso);
    std::swap(l2IsIso, l4IsIso);
    std::swap(l1Iso, l3Iso);
    std::swap(l2Iso, l4Iso);
    std::swap(l1IsGap, l3IsGap);
    std::swap(l2IsGap, l4IsGap);
    std::swap(l1Pt, l3Pt);
    std::swap(l2Pt, l4Pt);
    std::swap(l1Eta, l3Eta);
    std::swap(l2Eta, l4Eta);
    std::swap(l1Phi, l3Phi);
    std::swap(l2Phi, l4Phi);
    std::swap(l1Energy, l3Energy);
    std::swap(l2Energy, l4Energy);
    std::swap(l1Mass, l3Mass);
    std::swap(l2Mass, l4Mass);
    std::swap(l1PVDXY, l3PVDXY);
    std::swap(l2PVDXY, l4PVDXY);
    std::swap(l1PVDZ, l3PVDZ);
    std::swap(l2PVDZ, l4PVDZ);
    std::swap(l1SIP3D, l3SIP3D);
    std::swap(l2SIP3D, l4SIP3D);
    std::swap(l1PdgId, l3PdgId);
    std::swap(l2PdgId, l4PdgId);
  }
}

void ZZSelector::ShiftEfficiencies(Systematic variation) {
  std::string shift =
      (variation == electronEfficiencyDown || variation == electronRecoEffDown || variation == muonEfficiencyDown || variation == pileupDown) ? "down" : "up";

  if (pileupSF_ != nullptr && (variation == pileupUp || variation == pileupDown))
    weight *= (*pileupSF_->begin()).second->evaluate({nTruePU, shift}) / (*pileupSF_->begin()).second->evaluate({nTruePU, "nominal"});
  else if (channel_ == eeee) {
    float pt_e1 = l1Pt < EleSF_MAX_PT_ ? l1Pt : EleSF_MAX_PT_ - 0.01;
    float pt_e2 = l2Pt < EleSF_MAX_PT_ ? l2Pt : EleSF_MAX_PT_ - 0.01;
    float pt_e3 = l3Pt < EleSF_MAX_PT_ ? l3Pt : EleSF_MAX_PT_ - 0.01;
    float pt_e4 = l4Pt < EleSF_MAX_PT_ ? l4Pt : EleSF_MAX_PT_ - 0.01;
    if (variation == electronRecoEffUp || variation == electronRecoEffDown) {
      if (eRecoSF_ != nullptr) {
        // Applying Electron Reco SFs Up/Down for ElectronRecoSyst
        const auto recoref = (*eRecoSF_->begin()).second;
        if (pt_e1 > EleRecoSF_MIN_PT_) {
          if (EleRecoSF_Name_.rfind("2023", 0) != std::string::npos)
            weight *= recoref->evaluate({EleRecoSF_Name_.c_str(), (shift == "up") ? "sfup" : "sfdown", GetEleRecoSFName(pt_e1), l1Eta, pt_e1, l1Phi}) /
                      recoref->evaluate({EleRecoSF_Name_.c_str(), "sf", GetEleRecoSFName(pt_e1), l1Eta, pt_e1, l1Phi});
          else if (EleRecoSF_Name_ != "2025Prompt" || GetEleRecoSFName(pt_e1) != "RecoBelow20")
            weight *= recoref->evaluate({EleRecoSF_Name_.c_str(), (shift == "up") ? "sfup" : "sfdown", GetEleRecoSFName(pt_e1), l1Eta, pt_e1}) /
                      recoref->evaluate({EleRecoSF_Name_.c_str(), "sf", GetEleRecoSFName(pt_e1), l1Eta, pt_e1});
        }
        if (pt_e2 > EleRecoSF_MIN_PT_) {
          if (EleRecoSF_Name_.rfind("2023", 0) != std::string::npos)
            weight *= recoref->evaluate({EleRecoSF_Name_.c_str(), (shift == "up") ? "sfup" : "sfdown", GetEleRecoSFName(pt_e2), l2Eta, pt_e2, l2Phi}) /
                      recoref->evaluate({EleRecoSF_Name_.c_str(), "sf", GetEleRecoSFName(pt_e2), l2Eta, pt_e2, l2Phi});
          else if (EleRecoSF_Name_ != "2025Prompt" || GetEleRecoSFName(pt_e2) != "RecoBelow20")
            weight *= recoref->evaluate({EleRecoSF_Name_.c_str(), (shift == "up") ? "sfup" : "sfdown", GetEleRecoSFName(pt_e2), l2Eta, pt_e2}) /
                      recoref->evaluate({EleRecoSF_Name_.c_str(), "sf", GetEleRecoSFName(pt_e2), l2Eta, pt_e2});
        }
        if (pt_e3 > EleRecoSF_MIN_PT_) {
          if (EleRecoSF_Name_.rfind("2023", 0) != std::string::npos)
            weight *= recoref->evaluate({EleRecoSF_Name_.c_str(), (shift == "up") ? "sfup" : "sfdown", GetEleRecoSFName(pt_e3), l3Eta, pt_e3, l3Phi}) /
                      recoref->evaluate({EleRecoSF_Name_.c_str(), "sf", GetEleRecoSFName(pt_e3), l3Eta, pt_e3, l3Phi});
          else if (EleRecoSF_Name_ != "2025Prompt" || GetEleRecoSFName(pt_e3) != "RecoBelow20")
            weight *= recoref->evaluate({EleRecoSF_Name_.c_str(), (shift == "up") ? "sfup" : "sfdown", GetEleRecoSFName(pt_e3), l3Eta, pt_e3}) /
                      recoref->evaluate({EleRecoSF_Name_.c_str(), "sf", GetEleRecoSFName(pt_e3), l3Eta, pt_e3});
        }
        if (pt_e4 > EleRecoSF_MIN_PT_) {
          if (EleRecoSF_Name_.rfind("2023", 0) != std::string::npos)
            weight *= recoref->evaluate({EleRecoSF_Name_.c_str(), (shift == "up") ? "sfup" : "sfdown", GetEleRecoSFName(pt_e4), l4Eta, pt_e4, l4Phi}) /
                      recoref->evaluate({EleRecoSF_Name_.c_str(), "sf", GetEleRecoSFName(pt_e4), l4Eta, pt_e4, l4Phi});
          else if (EleRecoSF_Name_ != "2025Prompt" || GetEleRecoSFName(pt_e4) != "RecoBelow20")
            weight *= recoref->evaluate({EleRecoSF_Name_.c_str(), (shift == "up") ? "sfup" : "sfdown", GetEleRecoSFName(pt_e4), l4Eta, pt_e4}) /
                      recoref->evaluate({EleRecoSF_Name_.c_str(), "sf", GetEleRecoSFName(pt_e4), l4Eta, pt_e4});
        }
      }
    }
    // Applying Electron ID SFs Up/Down for ElectronIDEffSyst
    else if (variation == electronEfficiencyUp || variation == electronEfficiencyDown) {
      if (eIdSF_ != nullptr) {
        if (pt_e1 > EleSF_MIN_PT_) {
          if (year == "2023D" && (l1Eta < 0 && l1Eta > -1.5 && l1Phi < -0.8 && l1Phi > -1.2))
            weight *= eIdSF_->at("2023D_Hole")->evaluate({l1Eta, pt_e1, shift}) / eIdSF_->at("2023D_Hole")->evaluate({l1Eta, pt_e1, "nominal"});
          else
            weight *= eIdSF_->at(year.c_str())->evaluate({l1Eta, pt_e1, shift}) / eIdSF_->at(year.c_str())->evaluate({l1Eta, pt_e1, "nominal"});
        }
        if (pt_e2 > EleSF_MIN_PT_) {
          if (year == "2023D" && (l2Eta < 0 && l2Eta > -1.5 && l2Phi < -0.8 && l2Phi > -1.2))
            weight *= eIdSF_->at("2023D_Hole")->evaluate({l2Eta, pt_e2, shift}) / eIdSF_->at("2023D_Hole")->evaluate({l2Eta, pt_e2, "nominal"});
          else
            weight *= eIdSF_->at(year.c_str())->evaluate({l2Eta, pt_e2, shift}) / eIdSF_->at(year.c_str())->evaluate({l2Eta, pt_e2, "nominal"});
        }
        if (pt_e3 > EleSF_MIN_PT_) {
          if (year == "2023D" && (l3Eta < 0 && l3Eta > -1.5 && l3Phi < -0.8 && l3Phi > -1.2))
            weight *= eIdSF_->at("2023D_Hole")->evaluate({l3Eta, pt_e3, shift}) / eIdSF_->at("2023D_Hole")->evaluate({l3Eta, pt_e3, "nominal"});
          else
            weight *= eIdSF_->at(year.c_str())->evaluate({l3Eta, pt_e3, shift}) / eIdSF_->at(year.c_str())->evaluate({l3Eta, pt_e3, "nominal"});
        }
        if (pt_e4 > EleSF_MIN_PT_) {
          if (year == "2023D" && (l4Eta < 0 && l4Eta > -1.5 && l4Phi < -0.8 && l4Phi > -1.2))
            weight *= eIdSF_->at("2023D_Hole")->evaluate({l4Eta, pt_e4, shift}) / eIdSF_->at("2023D_Hole")->evaluate({l4Eta, pt_e4, "nominal"});
          else
            weight *= eIdSF_->at(year.c_str())->evaluate({l4Eta, pt_e4, shift}) / eIdSF_->at(year.c_str())->evaluate({l4Eta, pt_e4, "nominal"});
        }
      }
    }
  } else if (channel_ == eemm || channel_ == mmee) {
    // In order to get around the Overflow issue, set the Pt, not ideal.
    float pt_e1 = l1Pt < EleSF_MAX_PT_ ? l1Pt : EleSF_MAX_PT_ - 0.01;
    float pt_e2 = l2Pt < EleSF_MAX_PT_ ? l2Pt : EleSF_MAX_PT_ - 0.01;
    float pt_m3 = l3Pt < MuSF_MAX_PT_ ? l3Pt : MuSF_MAX_PT_ - 0.01;
    float pt_m4 = l4Pt < MuSF_MAX_PT_ ? l4Pt : MuSF_MAX_PT_ - 0.01;
    if (variation == electronRecoEffUp || variation == electronRecoEffDown) {
      if (eRecoSF_ != nullptr) {
        // Applying Electron Reco SFs Up/Down for ElectronRecoEffSyst
        const auto recoref = (*eRecoSF_->begin()).second;
        if (pt_e1 > EleRecoSF_MIN_PT_) {
          if (EleRecoSF_Name_.rfind("2023", 0) != std::string::npos)
            weight *= recoref->evaluate({EleRecoSF_Name_.c_str(), (shift == "up") ? "sfup" : "sfdown", GetEleRecoSFName(pt_e1), l1Eta, pt_e1, l1Phi}) /
                      recoref->evaluate({EleRecoSF_Name_.c_str(), "sf", GetEleRecoSFName(pt_e1), l1Eta, pt_e1, l1Phi});
          else if (EleRecoSF_Name_ != "2025Prompt" || GetEleRecoSFName(pt_e1) != "RecoBelow20")
            weight *= recoref->evaluate({EleRecoSF_Name_.c_str(), (shift == "up") ? "sfup" : "sfdown", GetEleRecoSFName(pt_e1), l1Eta, pt_e1}) /
                      recoref->evaluate({EleRecoSF_Name_.c_str(), "sf", GetEleRecoSFName(pt_e1), l1Eta, pt_e1});
        }
        if (pt_e2 > EleRecoSF_MIN_PT_) {
          if (EleRecoSF_Name_.rfind("2023", 0) != std::string::npos)
            weight *= recoref->evaluate({EleRecoSF_Name_.c_str(), (shift == "up") ? "sfup" : "sfdown", GetEleRecoSFName(pt_e2), l2Eta, pt_e2, l2Phi}) /
                      recoref->evaluate({EleRecoSF_Name_.c_str(), "sf", GetEleRecoSFName(pt_e2), l2Eta, pt_e2, l2Phi});
          else if (EleRecoSF_Name_ != "2025Prompt" || GetEleRecoSFName(pt_e2) != "RecoBelow20")
            weight *= recoref->evaluate({EleRecoSF_Name_.c_str(), (shift == "up") ? "sfup" : "sfdown", GetEleRecoSFName(pt_e2), l2Eta, pt_e2}) /
                      recoref->evaluate({EleRecoSF_Name_.c_str(), "sf", GetEleRecoSFName(pt_e2), l2Eta, pt_e2});
        }
      }
    }
    // Applying Electron ID SFs Up/Down for ElectronIDEffSyst
    else if (variation == electronEfficiencyUp || variation == electronEfficiencyDown) {
      if (eIdSF_ != nullptr) {
        if (pt_e1 > EleSF_MIN_PT_) {
          if (year == "2023D" && (l1Eta < 0 && l1Eta > -1.5 && l1Phi < -0.8 && l1Phi > -1.2))
            weight *= eIdSF_->at("2023D_Hole")->evaluate({l1Eta, pt_e1, shift}) / eIdSF_->at("2023D_Hole")->evaluate({l1Eta, pt_e1, "nominal"});
          else
            weight *= eIdSF_->at(year.c_str())->evaluate({l1Eta, pt_e1, shift}) / eIdSF_->at(year.c_str())->evaluate({l1Eta, pt_e1, "nominal"});
        }
        if (pt_e2 > EleSF_MIN_PT_) {
          if (year == "2023D" && (l2Eta < 0 && l2Eta > -1.5 && l2Phi < -0.8 && l2Phi > -1.2))
            weight *= eIdSF_->at("2023D_Hole")->evaluate({l2Eta, pt_e2, shift}) / eIdSF_->at("2023D_Hole")->evaluate({l2Eta, pt_e2, "nominal"});
          else
            weight *= eIdSF_->at(year.c_str())->evaluate({l2Eta, pt_e2, shift}) / eIdSF_->at(year.c_str())->evaluate({l2Eta, pt_e2, "nominal"});
        }
      }
    } else if (variation == muonEfficiencyUp || variation == muonEfficiencyDown) {
      if (mIdSF_ != nullptr) {
        if (pt_m3 > MuSF_MIN_PT_)
          weight *= mIdSF_->at(year.c_str())->evaluate({l3Eta, pt_m3, shift}) / mIdSF_->at(year.c_str())->evaluate({l3Eta, pt_m3, "nominal"});
        if (pt_m4 > MuSF_MIN_PT_)
          weight *= mIdSF_->at(year.c_str())->evaluate({l4Eta, pt_m4, shift}) / mIdSF_->at(year.c_str())->evaluate({l4Eta, pt_m4, "nominal"});
      }
    }
  } else if (channel_ == mmmm && (variation == muonEfficiencyUp || variation == muonEfficiencyDown)) {
    float pt_m1 = l1Pt < MuSF_MAX_PT_ ? l1Pt : MuSF_MAX_PT_ - 0.01;
    float pt_m2 = l2Pt < MuSF_MAX_PT_ ? l2Pt : MuSF_MAX_PT_ - 0.01;
    float pt_m3 = l3Pt < MuSF_MAX_PT_ ? l3Pt : MuSF_MAX_PT_ - 0.01;
    float pt_m4 = l4Pt < MuSF_MAX_PT_ ? l4Pt : MuSF_MAX_PT_ - 0.01;
    if (mIdSF_ != nullptr) {
      if (pt_m1 > MuSF_MIN_PT_)
        weight *= mIdSF_->at(year.c_str())->evaluate({l1Eta, pt_m1, shift}) / mIdSF_->at(year.c_str())->evaluate({l1Eta, pt_m1, "nominal"});
      if (pt_m2 > MuSF_MIN_PT_)
        weight *= mIdSF_->at(year.c_str())->evaluate({l2Eta, pt_m2, shift}) / mIdSF_->at(year.c_str())->evaluate({l2Eta, pt_m2, "nominal"});
      if (pt_m3 > MuSF_MIN_PT_)
        weight *= mIdSF_->at(year.c_str())->evaluate({l3Eta, pt_m3, shift}) / mIdSF_->at(year.c_str())->evaluate({l3Eta, pt_m3, "nominal"});
      if (pt_m4 > MuSF_MIN_PT_)
        weight *= mIdSF_->at(year.c_str())->evaluate({l4Eta, pt_m4, shift}) / mIdSF_->at(year.c_str())->evaluate({l4Eta, pt_m4, "nominal"});
    }
  }
}

bool ZZSelector::PassesZZjjSelection() { return (jetPt->size() == jetEta->size() && jetPt->size() >= 2 && mjj >= 100); }

bool ZZSelector::Passes4eExtraCut() {
  float lpt_arraySort[] = {l1Pt, l2Pt, l3Pt, l4Pt};
  std::sort(lpt_arraySort, lpt_arraySort + 4, std::greater<float>());

  if (channel_ == eeee)
    return lpt_arraySort[0] > 23 && lpt_arraySort[1] > 12;
  else
    return true;
}

bool ZZSelector::Passes2e2mExtraCut(Long64_t entry) {
  if (channel_ == eeee || channel_ == mmmm)
    return true;

  float ept_arraySort[2];
  if (std::abs(l1PdgId) == 11) {
    ept_arraySort[0] = l1Pt;
    ept_arraySort[1] = l2Pt;
  } else {
    ept_arraySort[0] = l3Pt;
    ept_arraySort[1] = l4Pt;
  }
  std::sort(ept_arraySort, ept_arraySort + 2, std::greater<float>());

  return ept_arraySort[0] > 23 && ept_arraySort[1] > 12;
}

bool ZZSelector::PassesZZSelection(bool nonPrompt) {
  // This nonPrompt boolean is for ZZBackgroundSelector
  // When running ZZBackgroundSelector, FillHistograms should run just with ZZSelection, we cannot require TightZZLeptons by definition
  if (nonPrompt)
    return ZZSelection();
  else
    return ZZSelection() && TightZZLeptons();
}

bool ZZSelector::PassesZZSelectionLoose(bool nonPrompt) {
  // This nonPrompt boolean is for ZZBackgroundSelector
  // When running ZZBackgroundSelector, FillHistograms should run just with ZZSelection, we cannot require TightZZLeptons by definition
  if (nonPrompt)
    return true;
  else
    return TightZZLeptons();
}

bool ZZSelector::PassesZZSelectionTight(bool nonPrompt) {
  if (nonPrompt)
    return ZZSelectionTight();
  else
    return ZZSelectionTight() && TightZZLeptons();
}

bool ZZSelector::PassesHZZSelection(bool nonPrompt) {
  if (nonPrompt)
    return ZSelection();
  else
    return ZSelection() && TightZZLeptons();
}
bool ZZSelector::TightZZLeptons() { return tightZ1Leptons() && tightZ2Leptons(); }
bool ZZSelector::ZZSelection() { return (Z1Mass > 60.0 && Z1Mass < 120.0) && (Z2Mass > 60.0 && Z2Mass < 120.0); }
bool ZZSelector::ZZSelectionTight() { return (Z1Mass > 81.1876 && Z1Mass < 101.1876) && (Z2Mass > 81.1876 && Z2Mass < 101.1876); }

// We already require 4 < Z1,Z2 < 120  in the "Loose Skim"
bool ZZSelector::ZSelection() { return Z1Mass > 40.0 && Z2Mass > 12.0; }
bool ZZSelector::Z4lSelection() { return Mass > 80.0 && Mass < 100.0; }

std::string ZZSelector::GetEleRecoSFName(Float_t ele_pt) {
  std::string name;
  if (ele_pt < 20)
    name = "RecoBelow20";
  else if (ele_pt < 75)
    name = "Reco20to75";
  else
    name = "RecoAbove75";
  return name;
}

void ZZSelector::FillHistograms(Long64_t entry, std::pair<Systematic, std::string> variation) {
  if ((channel_ == eemm || channel_ == mmee) && skipEvent_2e2m_)
    return;
  //weight = 1; //NOTE: unweighted
  //if (entry == 0 && variation.first == Central)
  //  std::cout << fChain->GetTree()->GetDirectory()->GetFile()->GetName() << std::endl;

  // require TightZZLeptons for prompt
  if (!PassesZZSelectionLoose(isNonPrompt_))
    return;

  //Apply extra 23/12 GeV cut to 4e channel
  //if (!Passes4eExtraCut()) return;

  //Apply extra 23/12 GeV cut to electrons in 2e2m channel
  //if (!Passes2e2mExtraCut(entry)) return;

  //if (!passCurrentTrig) return;

  //Begin filling ntuple
  //Fill variables for full mass range
  // (before ZZ mass cut)
  int nJets_tmp = jetPt->size();
  float jpt0_tmp = -9999;
  float jeta0_tmp = -9999;
  float jpt1_tmp = -9999;
  float jeta1_tmp = -9999;

  //mjj and dEtajj has default values already (but dEtajj=-1 is small although unphysical... unlike -9999), but need to assign values for temporary jetPt[1] and jetEta[1]
  if (nJets_tmp >= 1) {
    jpt0_tmp = jetPt->at(0);
    jeta0_tmp = jetEta->at(0);
    if (nJets_tmp >= 2) {
      jpt1_tmp = jetPt->at(1);
      jeta1_tmp = jetEta->at(1);
    }
  }

  bool writeNtpFullRange = false;
  if (writeNtp_ && writeNtpFullRange) {
    SafeSetBranch(ftntp_, getBranchName("weight", variation.second), &weight);
    SafeSetBranch(ftntp_, getBranchName("Mass", variation.second), &Mass);
    SafeSetBranch(ftntp_, getBranchName("nJets", variation.second), &nJets_tmp);
    SafeSetBranch(ftntp_, getBranchName("jetPt0", variation.second), &jpt0_tmp);
    SafeSetBranch(ftntp_, getBranchName("jetEta0", variation.second), &jeta0_tmp);

    SafeSetBranch(ftntp_, getBranchName("run", variation.second), &run);
    SafeSetBranch(ftntp_, getBranchName("lumi", variation.second), &lumi);
    SafeSetBranch(ftntp_, getBranchName("evt", variation.second), &evt);

    SafeSetBranch(ftntp_, getBranchName("jetPt1", variation.second), &jpt1_tmp);
    SafeSetBranch(ftntp_, getBranchName("jetEta1", variation.second), &jeta1_tmp);

    SafeSetBranch(ftntp_, getBranchName("mjj", variation.second), &mjj);
    SafeSetBranch(ftntp_, getBranchName("dEtajj", variation.second), &dEtajj);

    if (isMC_) {
      SafeSetBranch(ftntp_, getBranchName("genWeight", variation.second), &genWeight);
      SafeSetBranch(ftntp_, getBranchName("L1prefiringWeight", variation.second), &L1prefiringWeight);
      SafeSetBranch(ftntp_, getBranchName("L1prefiringWeightUp", variation.second), &L1prefiringWeightUp);
      SafeSetBranch(ftntp_, getBranchName("L1prefiringWeightDn", variation.second), &L1prefiringWeightDn);
    }
    ftntp_->Fill();
  }

  SafeHistFill(histMap1D_, getHistName("ZMassFull", variation.second), Z1Mass, weight);
  SafeHistFill(histMap1D_, getHistName("ZMassFull", variation.second), Z2Mass, weight);
  SafeHistFill(histMap1D_, getHistName("Z1MassFull", variation.second), Z1Mass, weight);
  SafeHistFill(histMap1D_, getHistName("Z2MassFull", variation.second), Z2Mass, weight);
  if (isMC_) {
    float lheweight;
    for (size_t i = 0; i < lheWeights.size(); i++) {
      lheweight = lheWeights[i] / lheWeights[0] * weight;
      SafeHistFill(weighthistMap1D_, getHistName("ZMassFull", variation.second), Z1Mass, i, lheweight);
      SafeHistFill(weighthistMap1D_, getHistName("ZMassFull", variation.second), Z2Mass, i, lheweight);
      SafeHistFill(weighthistMap1D_, getHistName("Z1MassFull", variation.second), Z1Mass, i, lheweight);
      SafeHistFill(weighthistMap1D_, getHistName("Z2MassFull", variation.second), Z2Mass, i, lheweight);
    }
  }

  std::vector<std::vector<float>*> vjetEta = {jetEta_jesUp, jetEta_jesDown, jetEta_jerUp, jetEta_jerDown};
  std::vector<std::vector<float>*> vjetPt = {jetPt_jesUp, jetPt_jesDown, jetPt_jerUp, jetPt_jerDown};
  std::vector<unsigned int> vnJets = {nJets_jesUp, nJets_jesDown, nJets_jerUp, nJets_jerDown};
  std::vector<float> vmjj = {mjj_jesUp, mjj_jesDown, mjj_jerUp, mjj_jerDown};

  if ((variation.first == Central || (doaTGC_ && isaTGC_)) && isMC_) {
    // Do jet systematics JES and JER
    if (isMC_) {
      float lheweight;
      for (size_t i = 0; i < vjetEta.size(); i++) {  // No actual syst for full m4l but just for consistency
        SafeHistFill(jethistMap1D_, getHistName("MassFull", variation.second), Mass, i, weight);

        if (vnJets[i] == 0) {
          SafeHistFill(jethistMap1D_, getHistName("Mass0jFull", variation.second), Mass, i, weight);
        } else if (vnJets[i] == 1) {
          SafeHistFill(jethistMap1D_, getHistName("Mass1jFull", variation.second), Mass, i, weight);
        } else if (vnJets[i] == 2) {
          SafeHistFill(jethistMap1D_, getHistName("Mass2jFull", variation.second), Mass, i, weight);
        } else {
          if (vnJets[i] == 3) {
            SafeHistFill(jethistMap1D_, getHistName("Mass3jFull", variation.second), Mass, i, weight);
          }
          if (vnJets[i] >= 3) {
            SafeHistFill(jethistMap1D_, getHistName("Mass34jFull", variation.second), Mass, i, weight);
          }
          if (vnJets[i] >= 4) {
            SafeHistFill(jethistMap1D_, getHistName("Mass4jFull", variation.second), Mass, i, weight);
          }
        }
      }

      // LHE weighted
      for (size_t i = 0; i < lheWeights.size(); i++) {
        if (jetPt->size() != jetEta->size())
          break;
        lheweight = lheWeights[i] / lheWeights[0] * weight;
        SafeHistFill(weighthistMap1D_, getHistName("MassFull", variation.second), Mass, i, lheweight);

        if (jetPt->size() == 0) {
          SafeHistFill(weighthistMap1D_, getHistName("Mass0jFull", variation.second), Mass, i, lheweight);
        } else if (jetPt->size() == 1) {
          SafeHistFill(weighthistMap1D_, getHistName("Mass1jFull", variation.second), Mass, i, lheweight);
        } else if (jetPt->size() == 2) {
          SafeHistFill(weighthistMap1D_, getHistName("Mass2jFull", variation.second), Mass, i, lheweight);
        } else {
          if (jetPt->size() == 3) {
            SafeHistFill(weighthistMap1D_, getHistName("Mass3jFull", variation.second), Mass, i, lheweight);
          }
          if (jetPt->size() >= 3) {
            SafeHistFill(weighthistMap1D_, getHistName("Mass34jFull", variation.second), Mass, i, lheweight);
          }
          if (jetPt->size() >= 4) {
            SafeHistFill(weighthistMap1D_, getHistName("Mass4jFull", variation.second), Mass, i, lheweight);
          }
        }
      }
    }
  }

  if (jetPt->size() == jetEta->size()) {
    SafeHistFill(histMap1D_, getHistName("MassFull", variation.second), Mass, weight);

    if (jetPt->size() == 0) {
      SafeHistFill(histMap1D_, getHistName("Mass0jFull", variation.second), Mass, weight);
    } else if (jetPt->size() == 1) {
      SafeHistFill(histMap1D_, getHistName("Mass1jFull", variation.second), Mass, weight);
    } else if (jetPt->size() == 2) {
      SafeHistFill(histMap1D_, getHistName("Mass2jFull", variation.second), Mass, weight);
    } else {
      if (jetPt->size() == 3) {
        SafeHistFill(histMap1D_, getHistName("Mass3jFull", variation.second), Mass, weight);
      }
      if (jetPt->size() >= 3) {
        SafeHistFill(histMap1D_, getHistName("Mass34jFull", variation.second), Mass, weight);
      }
      if (jetPt->size() >= 4) {
        SafeHistFill(histMap1D_, getHistName("Mass4jFull", variation.second), Mass, weight);
      }
    }
  }
  //End filling ntuple

  // sort lepton pt
  float lpt_array[] = {l1Pt, l2Pt, l3Pt, l4Pt};
  std::sort(lpt_array, lpt_array + 4, std::greater<float>());
  float l1PtTmp = lpt_array[0];
  float l2PtTmp = lpt_array[1];
  float l3PtTmp = lpt_array[2];
  float l4PtTmp = lpt_array[3];

  //float e1PtTmp = 0.;
  //float e2PtTmp = 0.;
  if (channel_ == eemm || channel_ == mmee) {
    float lpt_arraySort[2] = {0};
    if (std::abs(l1PdgId) == 11) {
      lpt_arraySort[0] = l1Pt;
      lpt_arraySort[1] = l2Pt;
    } else {
      lpt_arraySort[0] = l3Pt;
      lpt_arraySort[1] = l4Pt;
    }
    std::sort(lpt_arraySort, lpt_arraySort + 2, std::greater<float>());
    //e1PtTmp = lpt_arraySort[0];
    //e2PtTmp = lpt_arraySort[1];
  }

  //finish sorting lepton pt

  if (80 < Mass && Mass < 110) {
    //SafeHistFill(histMap1D_, getHistName("PassTriggerFull", variation.second), 1, weight);

    //SafeHistFill(histMap1D_, getHistName("LepPtFull", variation.second), l1Pt, weight);
    //SafeHistFill(histMap1D_, getHistName("LepPtFull", variation.second), l2Pt, weight);
    //SafeHistFill(histMap1D_, getHistName("LepPtFull", variation.second), l3Pt, weight);
    //SafeHistFill(histMap1D_, getHistName("LepPtFull", variation.second), l4Pt, weight);
    //SafeHistFill(histMap1D_, getHistName("LepPt1Full", variation.second), l1PtTmp, weight);
    //SafeHistFill(histMap1D_, getHistName("LepPt2Full", variation.second), l2PtTmp, weight);
    //SafeHistFill(histMap1D_, getHistName("LepPt3Full", variation.second), l3PtTmp, weight);
    //SafeHistFill(histMap1D_, getHistName("LepPt4Full", variation.second), l4PtTmp, weight);
    //SafeHistFill(histMap1D_, getHistName("e1PtSortedFull", variation.second), e1PtTmp, weight);
    //SafeHistFill(histMap1D_, getHistName("e2PtSortedFull", variation.second), e2PtTmp, weight);
  }

  // eta for all jets in full mass range
  for (unsigned int ind = 0; ind < jetPt->size(); ind++) {
    //SafeHistFill(histMap1D_, getHistName("jetEtaAllj", variation.second), jetEta->at(ind), weight);
    //SafeHistFill(histMap1D_, getHistName("absjetEtaAllj", variation.second), std::abs(jetEta->at(ind)), weight);

    if (jetPt->at(ind) > 50) {
      //SafeHistFill(histMap1D_, getHistName("jetEtaAllj50", variation.second), jetEta->at(ind), weight);
      //SafeHistFill(histMap1D_, getHistName("absjetEtaAllj50", variation.second), std::abs(jetEta->at(ind)), weight);
    }
  }

  if (Mass < 180) {
    for (unsigned int ind = 0; ind < jetPt->size(); ind++) {
      //SafeHistFill(histMap1D_, getHistName("jetEtaAllj_180", variation.second), jetEta->at(ind), weight);
      //SafeHistFill(histMap1D_, getHistName("absjetEtaAllj_180", variation.second), std::abs(jetEta->at(ind)), weight);

      if (jetPt->at(ind) > 50) {
        //SafeHistFill(histMap1D_, getHistName("jetEtaAllj50_180", variation.second), jetEta->at(ind), weight);
        //SafeHistFill(histMap1D_, getHistName("absjetEtaAllj50_180", variation.second), std::abs(jetEta->at(ind)), weight);
      }
    }
  }
  // bool noBlind = true;
  // Applying the ZZ Selection here
  // std::cout<<"Is fillHistograms working?"<<std::endl;
  // std::cout<<"isNonPrompt_ in FillHistograms:"<<isNonPrompt_<<std::endl;

  // Require ZZ mass between 60,120
  if (!PassesZZSelection(isNonPrompt_))
    return;

  for (unsigned int ind = 0; ind < jetPt->size(); ind++) {
    //SafeHistFill(histMap1D_, getHistName("jetEtaAllj_120", variation.second), jetEta->at(ind), weight);
    //SafeHistFill(histMap1D_, getHistName("absjetEtaAllj_120", variation.second), std::abs(jetEta->at(ind)), weight);

    if (jetPt->at(ind) > 50) {
      //SafeHistFill(histMap1D_, getHistName("jetEtaAllj50_120", variation.second), jetEta->at(ind), weight);
      //SafeHistFill(histMap1D_, getHistName("absjetEtaAllj50_120", variation.second), std::abs(jetEta->at(ind)), weight);
    }
  }

  if ((variation.first == Central || (doaTGC_ && isaTGC_)) && isMC_) {
    // Do jet systematics JES and JER
    if (isMC_) {
      float lheweight;
      for (size_t i = 0; i < vjetEta.size(); i++) {
        SafeHistFill(jethistMap1D_, getHistName("nJets", variation.second), vnJets[i], i, weight);

        if (vnJets[i] > 0) {
          SafeHistFill(jethistMap1D_, getHistName("jetPt[0]", variation.second), vjetPt[i]->at(0), i, weight);
          SafeHistFill(jethistMap1D_, getHistName("jetEta[0]", variation.second), vjetEta[i]->at(0), i, weight);
          SafeHistFill(jethistMap1D_, getHistName("absjetEta[0]", variation.second), std::abs(vjetEta[i]->at(0)), i, weight);

          if (vnJets[i] > 1) {
            SafeHistFill(jethistMap1D_, getHistName("jetPt[1]", variation.second), vjetPt[i]->at(1), i, weight);
            SafeHistFill(jethistMap1D_, getHistName("jetEta[1]", variation.second), vjetEta[i]->at(1), i, weight);
            SafeHistFill(jethistMap1D_, getHistName("absjetEta[1]", variation.second), std::abs(vjetEta[i]->at(1)), i, weight);

            //SafeHistFill(jethistMap1D_, getHistName("dEtajj", variation.second), std::abs(vjetEta[i]->at(0) - vjetEta[i]->at(1)), i, weight);
            //SafeHistFill(jethistMap1D_, getHistName("mjj", variation.second), vmjj[i], i, weight);
          }
        }

        // No actual syst for full m4l but just for consistency
        SafeHistFill(jethistMap1D_, getHistName("Mass", variation.second), Mass, i, weight);

        if (vnJets[i] == 0) {
          SafeHistFill(jethistMap1D_, getHistName("Mass0j", variation.second), Mass, i, weight);
        } else if (vnJets[i] == 1) {
          SafeHistFill(jethistMap1D_, getHistName("Mass1j", variation.second), Mass, i, weight);
        } else if (vnJets[i] == 2) {
          SafeHistFill(jethistMap1D_, getHistName("Mass2j", variation.second), Mass, i, weight);
        } else {
          if (vnJets[i] == 3) {
            SafeHistFill(jethistMap1D_, getHistName("Mass3j", variation.second), Mass, i, weight);
          }
          if (vnJets[i] >= 3) {
            SafeHistFill(jethistMap1D_, getHistName("Mass34j", variation.second), Mass, i, weight);
          }
          if (vnJets[i] >= 4) {
            SafeHistFill(jethistMap1D_, getHistName("Mass4j", variation.second), Mass, i, weight);
          }
        }
      }  // loop over syst indices

      // Jet plots with LHE weights
      for (size_t i = 0; i < lheWeights.size(); i++)  // expect 0 to 111 currently
      {
        if (jetPt->size() != jetEta->size())
          break;
        lheweight = lheWeights[i] / lheWeights[0] * weight;
        SafeHistFill(weighthistMap1D_, getHistName("nJets", variation.second), jetPt->size(), i, lheweight);

        if (jetPt->size() > 0) {
          SafeHistFill(weighthistMap1D_, getHistName("jetPt[0]", variation.second), jetPt->at(0), i, lheweight);
          SafeHistFill(weighthistMap1D_, getHistName("jetEta[0]", variation.second), jetEta->at(0), i, lheweight);
          SafeHistFill(weighthistMap1D_, getHistName("absjetEta[0]", variation.second), std::abs(jetEta->at(0)), i, lheweight);
          if (jetPt->size() > 1) {
            SafeHistFill(weighthistMap1D_, getHistName("jetPt[1]", variation.second), jetPt->at(1), i, lheweight);
            SafeHistFill(weighthistMap1D_, getHistName("jetEta[1]", variation.second), jetEta->at(1), i, lheweight);
            SafeHistFill(weighthistMap1D_, getHistName("absjetEta[1]", variation.second), std::abs(jetEta->at(1)), i, lheweight);

            //SafeHistFill(weighthistMap1D_, getHistName("dEtajj", variation.second), dEtajj, i, lheweight);
            //SafeHistFill(weighthistMap1D_, getHistName("mjj", variation.second), mjj, i, lheweight);
          }
        }

        if (jetPt->size() == 0) {
          SafeHistFill(weighthistMap1D_, getHistName("Mass0j", variation.second), Mass, i, lheweight);
        } else if (jetPt->size() == 1) {
          SafeHistFill(weighthistMap1D_, getHistName("Mass1j", variation.second), Mass, i, lheweight);
        } else if (jetPt->size() == 2) {
          SafeHistFill(weighthistMap1D_, getHistName("Mass2j", variation.second), Mass, i, lheweight);
        } else {
          if (jetPt->size() == 3) {
            SafeHistFill(weighthistMap1D_, getHistName("Mass3j", variation.second), Mass, i, lheweight);
          }
          if (jetPt->size() >= 3) {
            SafeHistFill(weighthistMap1D_, getHistName("Mass34j", variation.second), Mass, i, lheweight);
          }
          if (jetPt->size() >= 4) {
            SafeHistFill(weighthistMap1D_, getHistName("Mass4j", variation.second), Mass, i, lheweight);
          }
        }
      }
    }
  }
  // std::cout<<"isNonPrompt_ in FillHistograms after ZZSelection:"<<isNonPrompt_<<std::endl;
  // std::cout<<run<<":"<<lumi<<":"<<evt<<std::endl;
  // std::cout << "variation.second: "<<variation.second;

  //Begin filling ntuple
  //=====================A place where the on-shell selections have been applied and we fill the ntuple====================================================

  if (writeNtp_ && !writeNtpFullRange) {
    SafeSetBranch(ftntp_, getBranchName("weight", variation.second), &weight);
    SafeSetBranch(ftntp_, getBranchName("Mass", variation.second), &Mass);
    SafeSetBranch(ftntp_, getBranchName("nJets", variation.second), &nJets_tmp);
    SafeSetBranch(ftntp_, getBranchName("jetPt0", variation.second), &jpt0_tmp);
    SafeSetBranch(ftntp_, getBranchName("jetEta0", variation.second), &jeta0_tmp);

    SafeSetBranch(ftntp_, getBranchName("run", variation.second), &run);
    SafeSetBranch(ftntp_, getBranchName("lumi", variation.second), &lumi);
    SafeSetBranch(ftntp_, getBranchName("evt", variation.second), &evt);

    SafeSetBranch(ftntp_, getBranchName("jetPt1", variation.second), &jpt1_tmp);
    SafeSetBranch(ftntp_, getBranchName("jetEta1", variation.second), &jeta1_tmp);

    SafeSetBranch(ftntp_, getBranchName("mjj", variation.second), &mjj);
    SafeSetBranch(ftntp_, getBranchName("dEtajj", variation.second), &dEtajj);

    if (isMC_) {
      SafeSetBranch(ftntp_, getBranchName("genWeight", variation.second), &genWeight);
      SafeSetBranch(ftntp_, getBranchName("L1prefiringWeight", variation.second), &L1prefiringWeight);
      SafeSetBranch(ftntp_, getBranchName("L1prefiringWeightUp", variation.second), &L1prefiringWeightUp);
      SafeSetBranch(ftntp_, getBranchName("L1prefiringWeightDn", variation.second), &L1prefiringWeightDn);
    }
    ftntp_->Fill();
  }
  //End filling ntuple

  // Plot with LHE weights
  if (isMC_) {
    float lheweight;
    for (size_t i = 0; i < lheWeights.size(); i++) {
      lheweight = lheWeights[i] / lheWeights[0] * weight;
      if (80 < Mass && Mass < 110) {
        //TODO: counter-intuitive? 'Full' referred to plots before Mass selection above. this is tighter?
        //SafeHistFill(weighthistMap1D_, getHistName("LepPt1Full", variation.second), l1PtTmp, i, lheweight);
        //SafeHistFill(weighthistMap1D_, getHistName("LepPt2Full", variation.second), l2PtTmp, i, lheweight);
        //SafeHistFill(weighthistMap1D_, getHistName("LepPt3Full", variation.second), l3PtTmp, i, lheweight);
        //SafeHistFill(weighthistMap1D_, getHistName("LepPt4Full", variation.second), l4PtTmp, i, lheweight);
        //SafeHistFill(weighthistMap1D_, getHistName("LepPtFull", variation.second), l1Pt, i, lheweight);
        //SafeHistFill(weighthistMap1D_, getHistName("LepPtFull", variation.second), l2Pt, i, lheweight);
        //SafeHistFill(weighthistMap1D_, getHistName("LepPtFull", variation.second), l3Pt, i, lheweight);
        //SafeHistFill(weighthistMap1D_, getHistName("LepPtFull", variation.second), l4Pt, i, lheweight);
        //SafeHistFill(weighthistMap1D_, getHistName("e1PtSortedFull", variation.second), e1PtTmp, i, lheweight);
        //SafeHistFill(weighthistMap1D_, getHistName("e2PtSortedFull", variation.second), e2PtTmp, i, lheweight);
      }
      if (channel_ == eeee) {
        SafeHistFill(weighthistMap1D_, getHistName("ElePt", variation.second), l1Pt, i, lheweight);
        SafeHistFill(weighthistMap1D_, getHistName("ElePt", variation.second), l2Pt, i, lheweight);
        SafeHistFill(weighthistMap1D_, getHistName("ElePt", variation.second), l3Pt, i, lheweight);
        SafeHistFill(weighthistMap1D_, getHistName("ElePt", variation.second), l4Pt, i, lheweight);
        SafeHistFill(weighthistMap1D_, getHistName("EleEta", variation.second), l1Eta, i, lheweight);
        SafeHistFill(weighthistMap1D_, getHistName("EleEta", variation.second), l2Eta, i, lheweight);
        SafeHistFill(weighthistMap1D_, getHistName("EleEta", variation.second), l3Eta, i, lheweight);
        SafeHistFill(weighthistMap1D_, getHistName("EleEta", variation.second), l4Eta, i, lheweight);
        SafeHistFill(weighthistMap1D_, getHistName("EleZMass", variation.second), Z1Mass, i, lheweight);
        SafeHistFill(weighthistMap1D_, getHistName("EleZMass", variation.second), Z2Mass, i, lheweight);
      } else if (channel_ == eemm) {
        SafeHistFill(weighthistMap1D_, getHistName("ElePt", variation.second), l1Pt, i, lheweight);
        SafeHistFill(weighthistMap1D_, getHistName("ElePt", variation.second), l2Pt, i, lheweight);
        SafeHistFill(weighthistMap1D_, getHistName("MuPt", variation.second), l3Pt, i, lheweight);
        SafeHistFill(weighthistMap1D_, getHistName("MuPt", variation.second), l4Pt, i, lheweight);
        SafeHistFill(weighthistMap1D_, getHistName("EleEta", variation.second), l1Eta, i, lheweight);
        SafeHistFill(weighthistMap1D_, getHistName("EleEta", variation.second), l2Eta, i, lheweight);
        SafeHistFill(weighthistMap1D_, getHistName("MuEta", variation.second), l3Eta, i, lheweight);
        SafeHistFill(weighthistMap1D_, getHistName("MuEta", variation.second), l4Eta, i, lheweight);
        SafeHistFill(weighthistMap1D_, getHistName("EleZMass", variation.second), Z1Mass, i, lheweight);
        SafeHistFill(weighthistMap1D_, getHistName("MuZMass", variation.second), Z2Mass, i, lheweight);
      } else if (channel_ == mmee) {
        SafeHistFill(weighthistMap1D_, getHistName("MuPt", variation.second), l1Pt, i, lheweight);
        SafeHistFill(weighthistMap1D_, getHistName("MuPt", variation.second), l2Pt, i, lheweight);
        SafeHistFill(weighthistMap1D_, getHistName("ElePt", variation.second), l3Pt, i, lheweight);
        SafeHistFill(weighthistMap1D_, getHistName("ElePt", variation.second), l4Pt, i, lheweight);
        SafeHistFill(weighthistMap1D_, getHistName("MuEta", variation.second), l1Eta, i, lheweight);
        SafeHistFill(weighthistMap1D_, getHistName("MuEta", variation.second), l2Eta, i, lheweight);
        SafeHistFill(weighthistMap1D_, getHistName("EleEta", variation.second), l3Eta, i, lheweight);
        SafeHistFill(weighthistMap1D_, getHistName("EleEta", variation.second), l4Eta, i, lheweight);
        SafeHistFill(weighthistMap1D_, getHistName("MuZMass", variation.second), Z1Mass, i, lheweight);
        SafeHistFill(weighthistMap1D_, getHistName("EleZMass", variation.second), Z2Mass, i, lheweight);
      } else {
        SafeHistFill(weighthistMap1D_, getHistName("MuPt", variation.second), l1Pt, i, lheweight);
        SafeHistFill(weighthistMap1D_, getHistName("MuPt", variation.second), l2Pt, i, lheweight);
        SafeHistFill(weighthistMap1D_, getHistName("MuPt", variation.second), l3Pt, i, lheweight);
        SafeHistFill(weighthistMap1D_, getHistName("MuPt", variation.second), l4Pt, i, lheweight);
        SafeHistFill(weighthistMap1D_, getHistName("MuEta", variation.second), l1Eta, i, lheweight);
        SafeHistFill(weighthistMap1D_, getHistName("MuEta", variation.second), l2Eta, i, lheweight);
        SafeHistFill(weighthistMap1D_, getHistName("MuEta", variation.second), l3Eta, i, lheweight);
        SafeHistFill(weighthistMap1D_, getHistName("MuEta", variation.second), l4Eta, i, lheweight);
        SafeHistFill(weighthistMap1D_, getHistName("MuZMass", variation.second), Z1Mass, i, lheweight);
        SafeHistFill(weighthistMap1D_, getHistName("MuZMass", variation.second), Z2Mass, i, lheweight);
      }

      SafeHistFill(weighthistMap1D_, getHistName("yield", variation.second), 1, i, lheweight);
      SafeHistFill(weighthistMap1D_, getHistName("Mass", variation.second), Mass, i, lheweight);
      //TODO: Full?
      SafeHistFill(weighthistMap1D_, getHistName("MassFull", variation.second), Mass, i, lheweight);
      SafeHistFill(weighthistMap1D_, getHistName("ZZPt", variation.second), Pt, i, lheweight);
      //SafeHistFill(weighthistMap1D_, getHistName("ZZEta", variation.second), Eta, i, lheweight);
      SafeHistFill(weighthistMap1D_, getHistName("ZPt", variation.second), Z1Pt, i, lheweight);
      SafeHistFill(weighthistMap1D_, getHistName("ZPt", variation.second), Z2Pt, i, lheweight);
      SafeHistFill(weighthistMap1D_, getHistName("Z1Mass", variation.second), Z1Mass, i, lheweight);
      SafeHistFill(weighthistMap1D_, getHistName("Z2Mass", variation.second), Z2Mass, i, lheweight);
      SafeHistFill(weighthistMap1D_, getHistName("ZMass", variation.second), Z1Mass, i, lheweight);
      SafeHistFill(weighthistMap1D_, getHistName("ZMass", variation.second), Z2Mass, i, lheweight);
      SafeHistFill(weighthistMap1D_, getHistName("Lep1Eta", variation.second), l1Eta, i, lheweight);
      SafeHistFill(weighthistMap1D_, getHistName("Lep2Eta", variation.second), l2Eta, i, lheweight);
      SafeHistFill(weighthistMap1D_, getHistName("Lep3Eta", variation.second), l3Eta, i, lheweight);
      SafeHistFill(weighthistMap1D_, getHistName("Lep4Eta", variation.second), l4Eta, i, lheweight);
      SafeHistFill(weighthistMap1D_, getHistName("LepEta", variation.second), l1Eta, i, lheweight);
      SafeHistFill(weighthistMap1D_, getHistName("LepEta", variation.second), l2Eta, i, lheweight);
      SafeHistFill(weighthistMap1D_, getHistName("LepEta", variation.second), l3Eta, i, lheweight);
      SafeHistFill(weighthistMap1D_, getHistName("LepEta", variation.second), l4Eta, i, lheweight);
      //SafeHistFill(weighthistMap1D_, getHistName("Lep1Energy", variation.second), l1Energy, i, lheweight);
      //SafeHistFill(weighthistMap1D_, getHistName("Lep2Energy", variation.second), l2Energy, i, lheweight);
      //SafeHistFill(weighthistMap1D_, getHistName("Lep3Energy", variation.second), l3Energy, i, lheweight);
      //SafeHistFill(weighthistMap1D_, getHistName("Lep4Energy", variation.second), l4Energy, i, lheweight);
      SafeHistFill(weighthistMap1D_, getHistName("LepPt", variation.second), l1Pt, i, lheweight);
      SafeHistFill(weighthistMap1D_, getHistName("LepPt", variation.second), l2Pt, i, lheweight);
      SafeHistFill(weighthistMap1D_, getHistName("LepPt", variation.second), l3Pt, i, lheweight);
      SafeHistFill(weighthistMap1D_, getHistName("LepPt", variation.second), l4Pt, i, lheweight);
      SafeHistFill(weighthistMap1D_, getHistName("Z1LepPt", variation.second), l1Pt, i, lheweight);
      SafeHistFill(weighthistMap1D_, getHistName("Z1LepPt", variation.second), l2Pt, i, lheweight);
      SafeHistFill(weighthistMap1D_, getHistName("Z2LepPt", variation.second), l3Pt, i, lheweight);
      SafeHistFill(weighthistMap1D_, getHistName("Z2LepPt", variation.second), l4Pt, i, lheweight);
      //SafeHistFill(weighthistMap1D_, getHistName("e1PtSorted", variation.second), e1PtTmp, i, lheweight);
      //SafeHistFill(weighthistMap1D_, getHistName("e2PtSorted", variation.second), e2PtTmp, i, lheweight);
      //SafeHistFill(weighthistMap1D_, getHistName("dPhiZ1Z2", variation.second), dPhiZZ, i, lheweight);
      //SafeHistFill(weighthistMap1D_, getHistName("dRZ1Z2", variation.second), dRZZ, i, lheweight);
      //SafeHistFill(weighthistMap1D_, getHistName("SIP3D", variation.second), l1SIP3D, i, lheweight);
      //SafeHistFill(weighthistMap1D_, getHistName("SIP3D", variation.second), l2SIP3D, i, lheweight);
      //SafeHistFill(weighthistMap1D_, getHistName("SIP3D", variation.second), l3SIP3D, i, lheweight);
      //SafeHistFill(weighthistMap1D_, getHistName("SIP3D", variation.second), l4SIP3D, i, lheweight);
      //SafeHistFill(weighthistMap1D_, getHistName("PVDZ", variation.second), l1PVDZ, i, lheweight);
      //SafeHistFill(weighthistMap1D_, getHistName("PVDZ", variation.second), l2PVDZ, i, lheweight);
      //SafeHistFill(weighthistMap1D_, getHistName("PVDZ", variation.second), l3PVDZ, i, lheweight);
      //SafeHistFill(weighthistMap1D_, getHistName("PVDZ", variation.second), l4PVDZ, i, lheweight);
      //SafeHistFill(weighthistMap1D_, getHistName("deltaPVDZ_sameZ", variation.second), std::abs(l1PVDZ - l2PVDZ), i, lheweight);
      //SafeHistFill(weighthistMap1D_, getHistName("deltaPVDZ_sameZ", variation.second), std::abs(l3PVDZ - l4PVDZ), i, lheweight);
      //SafeHistFill(weighthistMap1D_, getHistName("deltaPVDZ_diffZ", variation.second), std::abs(l1PVDZ - l3PVDZ), i, lheweight);
      //SafeHistFill(weighthistMap1D_, getHistName("deltaPVDZ_diffZ", variation.second), std::abs(l2PVDZ - l4PVDZ), i, lheweight);
      //SafeHistFill(weighthistMap1D_, getHistName("deltaPVDZ_diffZ", variation.second), std::abs(l1PVDZ - l4PVDZ), i, lheweight);
      //SafeHistFill(weighthistMap1D_, getHistName("deltaPVDZ_diffZ", variation.second), std::abs(l2PVDZ - l3PVDZ), i, lheweight);
      //SafeHistFill(weighthistMap1D_, getHistName("Lep1Iso", variation.second), l1Iso, i, lheweight);
      //SafeHistFill(weighthistMap1D_, getHistName("Lep2Iso", variation.second), l2Iso, i, lheweight);
      //SafeHistFill(weighthistMap1D_, getHistName("Lep3Iso", variation.second), l3Iso, i, lheweight);
      //SafeHistFill(weighthistMap1D_, getHistName("Lep4Iso", variation.second), l4Iso, i, lheweight);
      //SafeHistFill(weighthistMap1D_, getHistName("LepIso", variation.second), l1Iso, i, lheweight);
      //SafeHistFill(weighthistMap1D_, getHistName("LepIso", variation.second), l2Iso, i, lheweight);
      //SafeHistFill(weighthistMap1D_, getHistName("LepIso", variation.second), l3Iso, i, lheweight);
      //SafeHistFill(weighthistMap1D_, getHistName("LepIso", variation.second), l4Iso, i, lheweight);

      SafeHistFill(weighthistMap1D_, getHistName("CosTheta1", variation.second), CosTheta1, i, lheweight);
      SafeHistFill(weighthistMap1D_, getHistName("CosTheta2", variation.second), CosTheta2, i, lheweight);
      SafeHistFill(weighthistMap1D_, getHistName("CosThetaStar", variation.second), CosThetaStar, i, lheweight);
      SafeHistFill(weighthistMap1D_, getHistName("RapidityDiff", variation.second), RapidityDiff, i, lheweight);
      if (channel_ == eemm || channel_ == mmee) {
        SafeHistFill(weighthistMap1D_, getHistName("dPhiOSll", variation.second), dPhiOSll, i, lheweight);
      }
    }
  }

  SafeHistFill(histMap1D_, getHistName("yield", variation.second), 1, weight);
  SafeHistFill(histMap1D_, getHistName("Mass", variation.second), Mass, weight);
  //SafeHistFill(histMap1D_, getHistName("PVDZ", variation.second), l1PVDZ, weight);
  //SafeHistFill(histMap1D_, getHistName("PVDZ", variation.second), l2PVDZ, weight);
  //SafeHistFill(histMap1D_, getHistName("PVDZ", variation.second), l3PVDZ, weight);
  //SafeHistFill(histMap1D_, getHistName("PVDZ", variation.second), l4PVDZ, weight);
  //SafeHistFill(histMap1D_, getHistName("deltaPVDZ_sameZ", variation.second), std::abs(l1PVDZ - l2PVDZ), weight);
  //SafeHistFill(histMap1D_, getHistName("deltaPVDZ_sameZ", variation.second), std::abs(l3PVDZ - l4PVDZ), weight);
  //SafeHistFill(histMap1D_, getHistName("deltaPVDZ_diffZ", variation.second), std::abs(l1PVDZ - l3PVDZ), weight);
  //SafeHistFill(histMap1D_, getHistName("deltaPVDZ_diffZ", variation.second), std::abs(l2PVDZ - l4PVDZ), weight);
  //SafeHistFill(histMap1D_, getHistName("deltaPVDZ_diffZ", variation.second), std::abs(l1PVDZ - l4PVDZ), weight);
  //SafeHistFill(histMap1D_, getHistName("deltaPVDZ_diffZ", variation.second), std::abs(l2PVDZ - l3PVDZ), weight);

  if (channel_ == eeee) {
    SafeHistFill(histMap1D_, getHistName("ElePt", variation.second), l1Pt, weight);
    SafeHistFill(histMap1D_, getHistName("ElePt", variation.second), l2Pt, weight);
    SafeHistFill(histMap1D_, getHistName("ElePt", variation.second), l3Pt, weight);
    SafeHistFill(histMap1D_, getHistName("ElePt", variation.second), l4Pt, weight);
    SafeHistFill(histMap1D_, getHistName("EleEta", variation.second), l1Eta, weight);
    SafeHistFill(histMap1D_, getHistName("EleEta", variation.second), l2Eta, weight);
    SafeHistFill(histMap1D_, getHistName("EleEta", variation.second), l3Eta, weight);
    SafeHistFill(histMap1D_, getHistName("EleEta", variation.second), l4Eta, weight);
    SafeHistFill(histMap1D_, getHistName("EleZMass", variation.second), Z1Mass, weight);
    SafeHistFill(histMap1D_, getHistName("EleZMass", variation.second), Z2Mass, weight);
  } else if (channel_ == eemm) {
    SafeHistFill(histMap1D_, getHistName("ElePt", variation.second), l1Pt, weight);
    SafeHistFill(histMap1D_, getHistName("ElePt", variation.second), l2Pt, weight);
    SafeHistFill(histMap1D_, getHistName("MuPt", variation.second), l3Pt, weight);
    SafeHistFill(histMap1D_, getHistName("MuPt", variation.second), l4Pt, weight);
    SafeHistFill(histMap1D_, getHistName("EleEta", variation.second), l1Eta, weight);
    SafeHistFill(histMap1D_, getHistName("EleEta", variation.second), l2Eta, weight);
    SafeHistFill(histMap1D_, getHistName("MuEta", variation.second), l3Eta, weight);
    SafeHistFill(histMap1D_, getHistName("MuEta", variation.second), l4Eta, weight);
    SafeHistFill(histMap1D_, getHistName("EleZMass", variation.second), Z1Mass, weight);
    SafeHistFill(histMap1D_, getHistName("MuZMass", variation.second), Z2Mass, weight);
  } else if (channel_ == mmee) {
    SafeHistFill(histMap1D_, getHistName("MuPt", variation.second), l1Pt, weight);
    SafeHistFill(histMap1D_, getHistName("MuPt", variation.second), l2Pt, weight);
    SafeHistFill(histMap1D_, getHistName("ElePt", variation.second), l3Pt, weight);
    SafeHistFill(histMap1D_, getHistName("ElePt", variation.second), l4Pt, weight);
    SafeHistFill(histMap1D_, getHistName("MuEta", variation.second), l1Eta, weight);
    SafeHistFill(histMap1D_, getHistName("MuEta", variation.second), l2Eta, weight);
    SafeHistFill(histMap1D_, getHistName("EleEta", variation.second), l3Eta, weight);
    SafeHistFill(histMap1D_, getHistName("EleEta", variation.second), l4Eta, weight);
    SafeHistFill(histMap1D_, getHistName("MuZMass", variation.second), Z1Mass, weight);
    SafeHistFill(histMap1D_, getHistName("EleZMass", variation.second), Z2Mass, weight);
  } else {
    SafeHistFill(histMap1D_, getHistName("MuPt", variation.second), l1Pt, weight);
    SafeHistFill(histMap1D_, getHistName("MuPt", variation.second), l2Pt, weight);
    SafeHistFill(histMap1D_, getHistName("MuPt", variation.second), l3Pt, weight);
    SafeHistFill(histMap1D_, getHistName("MuPt", variation.second), l4Pt, weight);
    SafeHistFill(histMap1D_, getHistName("MuEta", variation.second), l1Eta, weight);
    SafeHistFill(histMap1D_, getHistName("MuEta", variation.second), l2Eta, weight);
    SafeHistFill(histMap1D_, getHistName("MuEta", variation.second), l3Eta, weight);
    SafeHistFill(histMap1D_, getHistName("MuEta", variation.second), l4Eta, weight);
    SafeHistFill(histMap1D_, getHistName("MuZMass", variation.second), Z1Mass, weight);
    SafeHistFill(histMap1D_, getHistName("MuZMass", variation.second), Z2Mass, weight);
  }

  SafeHistFill(histMap1D_, getHistName("Z1Mass", variation.second), Z1Mass, weight);
  SafeHistFill(histMap1D_, getHistName("Z2Mass", variation.second), Z2Mass, weight);
  SafeHistFill(histMap1D_, getHistName("ZMass", variation.second), Z1Mass, weight);
  SafeHistFill(histMap1D_, getHistName("ZMass", variation.second), Z2Mass, weight);
  SafeHistFill(histMap1D_, getHistName("ZPt", variation.second), Z1Pt, weight);
  SafeHistFill(histMap1D_, getHistName("ZPt", variation.second), Z2Pt, weight);
  //SafeHistFill(histMap1D_, getHistName("dPhiZ1Z2", variation.second), dPhiZZ, weight);
  //SafeHistFill(histMap1D_, getHistName("dRZ1Z2", variation.second), dRZZ, weight);
  SafeHistFill(histMap1D_, getHistName("ZZPt", variation.second), Pt, weight);
  //SafeHistFill(histMap1D_, getHistName("ZZEta", variation.second), Eta, weight);
  SafeHistFill(histMap1D_, getHistName("CosTheta1", variation.second), CosTheta1, weight);
  SafeHistFill(histMap1D_, getHistName("CosTheta2", variation.second), CosTheta2, weight);
  SafeHistFill(histMap1D_, getHistName("CosThetaStar", variation.second), CosThetaStar, weight);
  SafeHistFill(histMap1D_, getHistName("RapidityDiff", variation.second), RapidityDiff, weight);
  if (channel_ == eemm || channel_ == mmee) {
    SafeHistFill(histMap1D_, getHistName("dPhiOSll", variation.second), dPhiOSll, weight);
  }
  //SafeHistFill(histMap1D_, getHistName("Lep1Iso", variation.second), l1Iso, weight);
  //SafeHistFill(histMap1D_, getHistName("Lep2Iso", variation.second), l2Iso, weight);
  //SafeHistFill(histMap1D_, getHistName("Lep3Iso", variation.second), l3Iso, weight);
  //SafeHistFill(histMap1D_, getHistName("Lep4Iso", variation.second), l4Iso, weight);
  //SafeHistFill(histMap1D_, getHistName("LepIso", variation.second), l1Iso, weight);
  //SafeHistFill(histMap1D_, getHistName("LepIso", variation.second), l2Iso, weight);
  //SafeHistFill(histMap1D_, getHistName("LepIso", variation.second), l3Iso, weight);
  //SafeHistFill(histMap1D_, getHistName("LepIso", variation.second), l4Iso, weight);

  //SafeHistFill(histMap1D_, getHistName("SIP3D", variation.second), l1SIP3D, weight);
  //SafeHistFill(histMap1D_, getHistName("SIP3D", variation.second), l2SIP3D, weight);
  //SafeHistFill(histMap1D_, getHistName("SIP3D", variation.second), l3SIP3D, weight);
  //SafeHistFill(histMap1D_, getHistName("SIP3D", variation.second), l4SIP3D, weight);

  // Making LeptonPt and Eta plots
  //SafeHistFill(histMap1D_, getHistName("Lep1Energy", variation.second), l1Energy, weight);
  //SafeHistFill(histMap1D_, getHistName("Lep2Energy", variation.second), l2Energy, weight);
  //SafeHistFill(histMap1D_, getHistName("Lep3Energy", variation.second), l3Energy, weight);
  //SafeHistFill(histMap1D_, getHistName("Lep4Energy", variation.second), l4Energy, weight);
  SafeHistFill(histMap1D_, getHistName("LepPt", variation.second), l1Pt, weight);
  SafeHistFill(histMap1D_, getHistName("LepPt", variation.second), l2Pt, weight);
  SafeHistFill(histMap1D_, getHistName("LepPt", variation.second), l3Pt, weight);
  SafeHistFill(histMap1D_, getHistName("LepPt", variation.second), l4Pt, weight);
  SafeHistFill(histMap1D_, getHistName("LepPt1", variation.second), l1PtTmp, weight);
  SafeHistFill(histMap1D_, getHistName("LepPt2", variation.second), l2PtTmp, weight);
  SafeHistFill(histMap1D_, getHistName("LepPt3", variation.second), l3PtTmp, weight);
  SafeHistFill(histMap1D_, getHistName("LepPt4", variation.second), l4PtTmp, weight);
  SafeHistFill(histMap1D_, getHistName("Z1LepPt", variation.second), l1Pt, weight);
  SafeHistFill(histMap1D_, getHistName("Z1LepPt", variation.second), l2Pt, weight);
  SafeHistFill(histMap1D_, getHistName("Z2LepPt", variation.second), l3Pt, weight);
  SafeHistFill(histMap1D_, getHistName("Z2LepPt", variation.second), l4Pt, weight);
  //SafeHistFill(histMap1D_, getHistName("e1PtSorted", variation.second), e1PtTmp, weight);
  //SafeHistFill(histMap1D_, getHistName("e2PtSorted", variation.second), e2PtTmp, weight);
  SafeHistFill(histMap1D_, getHistName("Lep1Eta", variation.second), l1Eta, weight);
  SafeHistFill(histMap1D_, getHistName("Lep2Eta", variation.second), l2Eta, weight);
  SafeHistFill(histMap1D_, getHistName("Lep3Eta", variation.second), l3Eta, weight);
  SafeHistFill(histMap1D_, getHistName("Lep4Eta", variation.second), l4Eta, weight);
  SafeHistFill(histMap1D_, getHistName("LepEta", variation.second), l1Eta, weight);
  SafeHistFill(histMap1D_, getHistName("LepEta", variation.second), l2Eta, weight);
  SafeHistFill(histMap1D_, getHistName("LepEta", variation.second), l3Eta, weight);
  SafeHistFill(histMap1D_, getHistName("LepEta", variation.second), l4Eta, weight);

  // Jet plots
  if (jetPt->size() == jetEta->size()) {
    int central_nJets = 0;
    for (unsigned int cind = 0; cind < jetPt->size(); cind++)
      if (std::abs(jetEta->at(cind)) < 2.4)
        central_nJets++;

    SafeHistFill(histMap1D_, getHistName("nJets", variation.second), jetPt->size(), weight);
    SafeHistFill(histMap1D_, getHistName("nJets_central", variation.second), central_nJets, weight);

    if (jetPt->size() == 0) {
      SafeHistFill(histMap1D_, getHistName("Mass0j", variation.second), Mass, weight);
    } else if (jetPt->size() == 1) {
      SafeHistFill(histMap1D_, getHistName("Mass1j", variation.second), Mass, weight);
    } else if (jetPt->size() == 2) {
      SafeHistFill(histMap1D_, getHistName("Mass2j", variation.second), Mass, weight);
    } else {
      if (jetPt->size() == 3) {
        SafeHistFill(histMap1D_, getHistName("Mass3j", variation.second), Mass, weight);
      }
      if (jetPt->size() >= 3) {
        SafeHistFill(histMap1D_, getHistName("Mass34j", variation.second), Mass, weight);
      }
      if (jetPt->size() >= 4) {
        SafeHistFill(histMap1D_, getHistName("Mass4j", variation.second), Mass, weight);
      }
    }

    if (jetPt->size() > 0) {
      SafeHistFill(histMap1D_, getHistName("jetPt[0]", variation.second), jetPt->at(0), weight);
      SafeHistFill(histMap1D_, getHistName("jetEta[0]", variation.second), jetEta->at(0), weight);
      SafeHistFill(histMap1D_, getHistName("absjetEta[0]", variation.second), std::abs(jetEta->at(0)), weight);
      //SafeHistFill(histMap1D_, getHistName("jetPhi[0]", variation.second), jetPhi->at(0), weight);

      for (unsigned int ind = 0; ind < jetPt->size(); ind++) {
        //SafeHistFill(histMap1D_, getHistName("jetEtaAllj", variation.second), jetEta->at(ind), weight);
        //SafeHistFill(histMap1D_, getHistName("absjetEtaAllj", variation.second), std::abs(jetEta->at(ind)), weight);
      }

      if (jetPt->size() == 1) {
        //SafeHistFill(histMap1D_, getHistName("jetPtN1", variation.second), jetPt->at(0), weight);
        //SafeHistFill(histMap1D_, getHistName("absjetEtaN1", variation.second), std::abs(jetEta->at(0)), weight);
        //SafeHistFill(jetTestMap2D_, getHistName("jetPtN1", variation.second), jetPt->at(0), std::abs(jetEta->at(0)), weight);
        if (jetPt->at(0) < 100) {
          //SafeHistFill(histMap1D_, getHistName("absjetEtaN1_100", variation.second), std::abs(jetEta->at(0)), weight);
        }
      }
    }
    if (jetPt->size() > 1) {
      SafeHistFill(histMap1D_, getHistName("jetPt[1]", variation.second), jetPt->at(1), weight);
      SafeHistFill(histMap1D_, getHistName("jetEta[1]", variation.second), jetEta->at(1), weight);
      SafeHistFill(histMap1D_, getHistName("absjetEta[1]", variation.second), std::abs(jetEta->at(1)), weight);
      //SafeHistFill(histMap1D_, getHistName("jetPhi[1]", variation.second), jetPhi->at(1), weight);
      //SafeHistFill(histMap1D_, getHistName("dEtajj", variation.second), dEtajj, weight);
      //SafeHistFill(histMap1D_, getHistName("mjj", variation.second), mjj, weight);

      if (jetPt->size() == 2) {
        //SafeHistFill(histMap1D_, getHistName("jetEta[01]", variation.second), jetEta->at(0), weight);
        //SafeHistFill(histMap1D_, getHistName("jetEta[01]", variation.second), jetEta->at(1), weight);
        // pt vs eta for 2-jet event lowest pt jet
        //SafeHistFill(jetTestMap2D_, getHistName("jetPtN2", variation.second), jetPt->at(1), std::abs(jetEta->at(1)), weight);
      }
      //SafeHistFill(histMap1D_, getHistName("jetPt[01]", variation.second), jetPt->at(0), weight);
      //SafeHistFill(histMap1D_, getHistName("jetPt[01]", variation.second), jetPt->at(1), weight);
    }

    if (jetPt->size() > 2) {
      //SafeHistFill(histMap1D_, getHistName("jetPt[2]", variation.second), jetPt->at(2), weight);
      //SafeHistFill(histMap1D_, getHistName("jetEta[2]", variation.second), jetEta->at(2), weight);
      //SafeHistFill(histMap1D_, getHistName("jetPhi[2]", variation.second), jetPhi->at(2), weight);

      // pt vs eta for 3-jet event lowest pt jet
      if (jetPt->size() == 3) {
        //SafeHistFill(jetTestMap2D_, getHistName("jetPtN3", variation.second), jetPt->at(2), std::abs(jetEta->at(2)), weight);
      }
    }
  }

  if (isMC_) {
    // std::cout<<run<<":"<<lumi<<":"<<evt<<std::endl;
    // std::cout<<"UpdatedSF:"<<weight<<std::endl;
  }

  //SafeHistFill(histMap1D_, getHistName("Mass", variation.second), Mass,weight);
  //SafeHistFill(histMap1D_, getHistName("dEtajj", variation.second), dEtajj, weight);

  // Summing 12,34 leptons
  //SafeHistFill(histMap1D_, getHistName("Z1Mass", variation.second), Z1Mass, weight);
  //SafeHistFill(histMap1D_, getHistName("Z2Mass", variation.second), Z2Mass, weight);
  //SafeHistFill(histMap1D_, getHistName("Z1Pt", variation.second), Z1Pt, weight);
  //SafeHistFill(histMap1D_, getHistName("Z2Pt", variation.second), Z2Pt, weight);
  //SafeHistFill(histMap1D_, getHistName("Z1Phi", variation.second), Z1Phi, weight);
  //SafeHistFill(histMap1D_, getHistName("Z2Phi", variation.second), Z2Phi, weight);
  //SafeHistFill(histMap1D_, getHistName("Z1lep1_Pt", variation.second), l1Pt, weight);
  //SafeHistFill(histMap1D_, getHistName("Z1lep1_Eta", variation.second), l1Eta, weight);
  //SafeHistFill(histMap1D_, getHistName("Z1lep1_Phi", variation.second), l1Phi, weight);
  //SafeHistFill(histMap1D_, getHistName("Z1lep1_PdgId", variation.second), l1PdgId, weight);
  //SafeHistFill(histMap1D_, getHistName("Z1lep2_Pt", variation.second), l2Pt, weight);
  //SafeHistFill(histMap1D_, getHistName("Z1lep2_Eta", variation.second), l2Eta, weight);
  //SafeHistFill(histMap1D_, getHistName("Z1lep2_Phi", variation.second), l2Phi, weight);
  //SafeHistFill(histMap1D_, getHistName("Z1lep2_PdgId", variation.second), l2PdgId, weight);
  //SafeHistFill(histMap1D_, getHistName("Z2lep1_Pt", variation.second), l3Pt, weight);
  //SafeHistFill(histMap1D_, getHistName("Z2lep1_Eta", variation.second), l3Eta, weight);
  //SafeHistFill(histMap1D_, getHistName("Z2lep1_Phi", variation.second), l3Phi, weight);
  //SafeHistFill(histMap1D_, getHistName("Z2lep1_PdgId", variation.second), l3PdgId, weight);
  //SafeHistFill(histMap1D_, getHistName("Z2lep2_Pt", variation.second), l4Pt, weight);
  //SafeHistFill(histMap1D_, getHistName("Z2lep2_Eta", variation.second), l4Eta, weight);
  //SafeHistFill(histMap1D_, getHistName("Z2lep2_Phi", variation.second), l4Phi, weight);
  //SafeHistFill(histMap1D_, getHistName("Z2lep2_PdgId", variation.second), l4PdgId, weight);
  //SafeHistFill(hists2D_, getHistName("Z1lep1_Z1lep2_Pt",variation.second),l1Pt,l2Pt,weight);
  //SafeHistFill(hists2D_, getHistName("Z1lep1_Z1lep2_Eta",variation.second),l1Eta,l2Eta,weight);
  //SafeHistFill(hists2D_, getHistName("Z1lep1_Z1lep2_Phi",variation.second),l1Phi,l2Phi,weight);
  //SafeHistFill(hists2D_, getHistName("Z2lep1_Z2lep2_Pt",variation.second),l3Pt,l4Pt,weight);
  //SafeHistFill(hists2D_, getHistName("Z2lep1_Z2lep2_Eta",variation.second),l3Eta,l4Eta,weight);
  //SafeHistFill(hists2D_, getHistName("Z2lep1_Z2lep2_Phi",variation.second),l3Phi,l4Phi,weight);
  ////2D Z1 vs Z2
  //SafeHistFill(hists2D_, getHistName("Z1Mass_Z2Mass",variation.second),Z1Mass,Z2Mass,weight);

  // if (histMap1D_[getHistName("nvtx", variation.second)] != nullptr) {
  //     b_nvtx->GetEntry(entry);
  //     histMap1D_[getHistName("nvtx", variation.second)]->Fill(nvtx, weight);
  // }
  // if (isMC_)
  //SafeHistFill(histMap1D_, getHistName("nTruePU", variation.second), nTruePU, weight);
}

void ZZSelector::SetupNewDirectory() {
  SelectorBase::SetupNewDirectory();
  isaTGC_ = name_.find("atgc") != std::string::npos;
  // std::cout<<"selection in ZZSelector: "<<selection_<<std::endl;
  applyFullSelection_ = (selection_ == ZZselection);
  // std::cout<<applyFullSelection_<<std::endl;
  InitializeHistogramsFromConfig();
  // std::cout<<"Do Histos get initialized"<<std::endl;
}
