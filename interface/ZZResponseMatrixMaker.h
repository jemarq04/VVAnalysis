#ifndef ZZResponseMatrixMaker_h
#define ZZResponseMatrixMaker_h

#include "Analysis/VVAnalysis/interface/ZZSelector.h"

class ZZResponseMatrixMaker : public ZZSelector {
  TChain* GenTree_;

  // Values
  ULong64_t GenEvt;
  Float_t GenMass;
  Float_t GenZ1Mass;
  Float_t GenZ2Mass;

  Float_t Genl1Pt;
  Float_t Genl2Pt;
  Float_t Genl3Pt;
  Float_t Genl4Pt;
  Float_t Genl1Eta;
  Float_t Genl2Eta;
  Float_t Genl3Eta;
  Float_t Genl4Eta;
  Float_t Genl1Phi;
  Float_t Genl2Phi;
  Float_t Genl3Phi;
  Float_t Genl4Phi;
  Int_t Genl1PdgId;
  Int_t Genl2PdgId;
  Int_t Genl3PdgId;
  Int_t Genl4PdgId;

  // Branches
  TBranch* b_GenEvt;
  TBranch* b_GenMass;
  TBranch* b_GenZ1Mass;
  TBranch* b_GenZ2Mass;

  TBranch* b_Genl1Pt;
  TBranch* b_Genl2Pt;
  TBranch* b_Genl3Pt;
  TBranch* b_Genl4Pt;
  TBranch* b_Genl1Eta;
  TBranch* b_Genl2Eta;
  TBranch* b_Genl3Eta;
  TBranch* b_Genl4Eta;
  TBranch* b_Genl1Phi;
  TBranch* b_Genl2Phi;
  TBranch* b_Genl3Phi;
  TBranch* b_Genl4Phi;
  TBranch* b_Genl1PdgId;
  TBranch* b_Genl2PdgId;
  TBranch* b_Genl3PdgId;
  TBranch* b_Genl4PdgId;

  virtual void Init(TTree* tree) override;
  virtual void SlaveTerminate() override;
  ClassDefOverride(ZZResponseMatrixMaker, 0);

public:
  ~ZZResponseMatrixMaker();

private:
  void SetGenBranchesUWVV();
  void LoadGenBranchesUWVV(Long64_t entry);
  void FillHistograms(Long64_t entry, std::pair<Systematic, std::string> variation) override;

  Int_t numVolunteers_;
  std::map<Long64_t, ULong64_t> GenEvents_;
  std::map<Long64_t, bool> GenEventsMatched_;
  void StoreGenEvents();
  bool GetGenEvent(ULong64_t event);
};

#endif
