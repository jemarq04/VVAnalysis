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

  virtual void Init(TTree* tree) override;
  ClassDefOverride(ZZResponseMatrixMaker, 0);

public:
  ~ZZResponseMatrixMaker();

private:
  void SetGenBranchesUWVV();
  void LoadGenBranchesUWVV(Long64_t entry);
  void FillHistograms(Long64_t entry, std::pair<Systematic, std::string> variation) override;

  std::map<Long64_t, ULong64_t> GenEvents_;
  void StoreGenEvents();
  bool GetGenEvent(ULong64_t event);
};

#endif
