#ifndef ZZResponseMatrixMaker_h
#define ZZResponseMatrixMaker_h

#include "Analysis/VVAnalysis/interface/ZZSelector.h"

class ZZResponseMatrixMaker : public ZZSelector {
  TChain* genTree_;

  // Values
  ULong64_t genEvt;
  Float_t genMass;
  Float_t genZ1Mass;
  Float_t genZ2Mass;

  Float_t genl1Pt;
  Float_t genl2Pt;
  Float_t genl3Pt;
  Float_t genl4Pt;
  Float_t genl1Eta;
  Float_t genl2Eta;
  Float_t genl3Eta;
  Float_t genl4Eta;

  // Branches
  TBranch* b_genEvt;
  TBranch* b_genMass;
  TBranch* b_genZ1Mass;
  TBranch* b_genZ2Mass;

  TBranch* b_genl1Pt;
  TBranch* b_genl2Pt;
  TBranch* b_genl3Pt;
  TBranch* b_genl4Pt;
  TBranch* b_genl1Eta;
  TBranch* b_genl2Eta;
  TBranch* b_genl3Eta;
  TBranch* b_genl4Eta;

  // Histograms
  TH2D* MassResponseMatrix;
  TH2D* LepPt1ResponseMatrix;

  virtual void Init(TTree* tree) override;
  ClassDefOverride(ZZResponseMatrixMaker, 0);

public:
  ~ZZResponseMatrixMaker();

private:
  void SetGenBranchesUWVV();
  void LoadGenBranchesUWVV(Long64_t entry);
  void FillHistograms(Long64_t entry, std::pair<Systematic, std::string> variation) override;

  std::map<Long64_t, ULong64_t> genEvents_;
  void StoreGenEvents();
  bool GetGenEvent(ULong64_t event);
};

#endif
