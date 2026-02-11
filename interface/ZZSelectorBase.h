#ifndef ZZSelectorBase_h
#define ZZSelectorBase_h

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>
#include <TSelector.h>
#include <TH1.h>
#include <TH2.h>
#include <exception>
#include <iostream>

// Headers needed by this particular selector
#include <vector>
#include "correction.h"
#include "Analysis/VVAnalysis/interface/ScaleFactor.h"
#include "Analysis/VVAnalysis/interface/SelectorBase.h"
#include "Analysis/VVAnalysis/interface/helpers.h"

class ZZSelectorBase : public SelectorBase {
public:
  std::unique_ptr<correction::CorrectionSet> pileupSF_;
  std::unique_ptr<correction::CorrectionSet> eIdSF_, eRecoSF_;
  std::unique_ptr<correction::CorrectionSet> mIdSF_;
  std::unique_ptr<correction::CorrectionSet> jetPUSF_;
  std::unique_ptr<correction::CorrectionSet> qqZZ_kfac_;
  std::string year;
  //ScaleFactor* mIsoSF_;

  //bool isVBS_;
  //MC variable to check for duplication(this is a flag to differentiate between channels)
  UInt_t run = 0;
  UInt_t lumi = 0;
  ULong64_t evt = 0;
  //Int_t duplicated=0;
  Float_t weight = 0;
  Float_t genWeight = 0;
  Float_t originalXWGTUP = 0;
  Float_t L1prefiringWeight = 0;
  Float_t L1prefiringWeightUp = 0;
  Float_t L1prefiringWeightDn = 0;
  Float_t nTruePU = 0;
  Float_t Z1Mass = 0;
  Float_t Z2Mass = 0;
  Float_t Z1Pt = 0;
  Float_t Z2Pt = 0;
  Float_t Z1Phi = 0;
  Float_t Z2Phi = 0;
  Float_t Z1Eta = 0;
  Float_t Z2Eta = 0;
  Float_t type1_pfMETEt = 0;
  Float_t type1_pfMETPhi = 0;
  Float_t l1GenPt = 0;
  Float_t l2GenPt = 0;
  Float_t l3GenPt = 0;
  Float_t l4GenPt = 0;

  Bool_t l1IsTight = false;
  Bool_t l2IsTight = false;
  Bool_t l3IsTight = false;
  Bool_t l4IsTight = false;
  Bool_t l1IsIso = false;
  Bool_t l2IsIso = false;
  Bool_t l3IsIso = false;
  Bool_t l4IsIso = false;
  Float_t l1Iso = 0;
  Float_t l2Iso = 0;
  Float_t l3Iso = 0;
  Float_t l4Iso = 0;

  Bool_t l1IsGap = false;
  Bool_t l2IsGap = false;
  Bool_t l3IsGap = false;
  Bool_t l4IsGap = false;

  Bool_t isUL_L1check = true;

  Float_t l1Pt = 0;
  Float_t l2Pt = 0;
  Float_t l3Pt = 0;
  Float_t l4Pt = 0;
  Float_t l1Energy = 0;
  Float_t l2Energy = 0;
  Float_t l3Energy = 0;
  Float_t l4Energy = 0;
  Float_t l1Eta = 0;
  Float_t l2Eta = 0;
  Float_t l3Eta = 0;
  Float_t l4Eta = 0;
  Float_t l1Phi = 0;
  Float_t l2Phi = 0;
  Float_t l3Phi = 0;
  Float_t l4Phi = 0;
  Float_t l1SIP3D = 0;
  Float_t l2SIP3D = 0;
  Float_t l3SIP3D = 0;
  Float_t l4SIP3D = 0;
  Int_t l1PdgId = 0;
  Int_t l2PdgId = 0;
  Int_t l3PdgId = 0;
  Int_t l4PdgId = 0;
  Float_t l1Mass = 0;
  Float_t l2Mass = 0;
  Float_t l3Mass = 0;
  Float_t l4Mass = 0;

  Float_t l1PVDXY = 0;
  Float_t l2PVDXY = 0;
  Float_t l3PVDXY = 0;
  Float_t l4PVDXY = 0;
  Float_t l1PVDZ = 0;
  Float_t l2PVDZ = 0;
  Float_t l3PVDZ = 0;
  Float_t l4PVDZ = 0;

  Float_t l3MtToMET = 0;

  TBranch* b_pdfWeights;
  TBranch* b_scaleWeights;
  //TBranch* b_duplicated;
  TBranch* b_genWeight;
  TBranch* b_originalXWGTUP;
  TBranch* b_L1prefiringWeight;
  TBranch* b_L1prefiringWeightUp;
  TBranch* b_L1prefiringWeightDn;
  TBranch* b_Z1Mass;
  TBranch* b_Z2Mass;
  TBranch* b_Z1Pt;
  TBranch* b_Z2Pt;
  TBranch* b_Z1Phi;
  TBranch* b_Z2Phi;
  TBranch* b_Z1Eta;
  TBranch* b_Z2Eta;
  TBranch* b_nTruePU;
  TBranch* b_type1_pfMETEt;
  TBranch* b_type1_pfMETPhi;
  TBranch* b_l1GenPt;
  TBranch* b_l2GenPt;
  TBranch* b_l3GenPt;
  TBranch* b_l4GenPt;

  TBranch* b_run;
  TBranch* b_lumi;
  TBranch* b_evt;

  TBranch* b_l1IsTight;
  TBranch* b_l2IsTight;
  TBranch* b_l3IsTight;
  TBranch* b_l4IsTight;
  TBranch* b_l1IsIso;
  TBranch* b_l2IsIso;
  TBranch* b_l3IsIso;
  TBranch* b_l4IsIso;
  TBranch* b_l1Iso;
  TBranch* b_l2Iso;
  TBranch* b_l3Iso;
  TBranch* b_l4Iso;

  TBranch* b_l1IsGap;
  TBranch* b_l2IsGap;
  TBranch* b_l3IsGap;
  TBranch* b_l4IsGap;

  TBranch* b_l1Pt;
  TBranch* b_l2Pt;
  TBranch* b_l3Pt;
  TBranch* b_l4Pt;
  TBranch* b_l1PVDZ;
  TBranch* b_l2PVDZ;
  TBranch* b_l3PVDZ;
  TBranch* b_l4PVDZ;
  TBranch* b_l1Energy;
  TBranch* b_l2Energy;
  TBranch* b_l3Energy;
  TBranch* b_l4Energy;
  TBranch* b_l1Eta;
  TBranch* b_l2Eta;
  TBranch* b_l3Eta;
  TBranch* b_l4Eta;
  TBranch* b_l1Phi;
  TBranch* b_l2Phi;
  TBranch* b_l3Phi;
  TBranch* b_l4Phi;
  TBranch* b_l1SIP3D;
  TBranch* b_l2SIP3D;
  TBranch* b_l3SIP3D;
  TBranch* b_l4SIP3D;
  TBranch* b_l1Mass;
  TBranch* b_l2Mass;
  TBranch* b_l3Mass;
  TBranch* b_l4Mass;
  TBranch* b_l1PdgId;
  TBranch* b_l2PdgId;
  TBranch* b_l3PdgId;
  TBranch* b_l4PdgId;
  TBranch* b_l3MtToMET;

  // Readers to access the data (delete the ones you do not need).
  virtual void SetScaleFactors() override;
  virtual void Init(TTree* tree) override;

  ClassDefOverride(ZZSelectorBase, 0);

protected:
  std::vector<std::string> nonprompt3l_ = {
      "tt-lep",
      "st-schan",
      "st-tchan-t",
      "st-tchan-tbar",
      "st-tw",
      "st-tbarw",
      "DYm50",
      "DYm50-1j",
      "DYm50-2j",
      "DYm50-3j",
      "DYm50-4j",
      "DYm50__LO",
  };

  bool isNonpromptEstimate_;
  bool isNonpromptMC_;
  bool isZgamma_;
  bool skipEvent_2e2m_ = false;
  const float FR_MAX_PT_ = 80;
  const float FR_MAX_ETA_ = 2.5;
  const float MuSF_MIN_PT_ = 3, MuSF_MAX_PT_ = 200, MuSF_MAX_ETA_ = 2.4;
  const float EleSF_MIN_PT_ = 7, EleRecoSF_MIN_PT_ = 10, EleSF_MAX_PT_ = 500;
  std::string EleRecoSF_Name_;
  virtual std::string GetNameFromFile() override;
  virtual void SetBranchesNanoAOD() override;
  virtual void SetBranchesUWVV() override;
  void LoadBranchesUWVV(Long64_t entry, std::pair<Systematic, std::string> variation) override;
  void LoadBranchesNanoAOD(Long64_t entry, std::pair<Systematic, std::string> variation) override;
  bool e1e2IsZ1();
  bool lep1IsTight();
  bool lep2IsTight();
  bool lep3IsTight();
  bool lep4IsTight();
  bool lep1IsIso();
  bool lep2IsIso();
  bool lep3IsIso();
  bool lep4IsIso();
  bool Z1PF();
  bool Z1FP();
  bool Z1FF();
  bool Z2PF();
  bool Z2FP();
  bool Z2FF();
  bool tightZ1Leptons();
  bool tightZ2Leptons();
};

#endif
