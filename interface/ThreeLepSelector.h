#ifndef ThreeLepSelector_h
#define ThreeLepSelector_h

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>
#include <TSelector.h>
#include <TH1.h>
#include <TH2.h>
#include <TEfficiency.h>
#include <exception>
#include <iostream>

// Headers needed by this particular selector
#include <vector>
#include "Analysis/VVAnalysis/interface/ScaleFactor.h"
#include "Analysis/VVAnalysis/interface/SelectorBase.h"
#include "Analysis/VVAnalysis/interface/BranchManager.h"
#include "Analysis/VVAnalysis/interface/GoodParticle.h"
#include "CondFormats/BTauObjects/interface/BTagCalibration.h"
#include "CondTools/BTau/interface/BTagCalibrationReader.h"
typedef ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<double>> LorentzVector;

class ThreeLepSelector : public SelectorBase {
public:
  /*****************************************/
  /* ____  ____   ___  __  __   ___ __  __ */
  /* || )) || \\ // \\ ||\ ||  //   ||  || */
  /* ||=)  ||_// ||=|| ||\\|| ((    ||==|| */
  /* ||_)) || \\ || || || \||  \\__ ||  || */
  /*****************************************/

  ScaleFactor* pileupSF_;
  ScaleFactor* muonSF_;
  ScaleFactor* eIdSF_;
  ScaleFactor* eGsfSF_;
  ScaleFactor* mIdSF_;
  ScaleFactor* mIsoSF_;

  // Common variables
  Float_t genWeight;
  Float_t MET;
  Float_t type1_pfMETPhi;

  //NanoAOD variables
  static const unsigned int N_KEEP_MU_E_ = 15;
  static const unsigned int N_KEEP_JET_ = 35;

  UInt_t nElectron;
  Float_t Electron_pt[N_KEEP_MU_E_];
  Float_t Electron_eta[N_KEEP_MU_E_];
  Float_t Electron_phi[N_KEEP_MU_E_];
  Float_t Electron_mass[N_KEEP_MU_E_];
  Int_t Electron_cutBased[N_KEEP_MU_E_];
  Int_t Electron_charge[N_KEEP_MU_E_];
  Float_t Electron_MVA[N_KEEP_MU_E_];
  Float_t Electron_miniPFRelIso_all[N_KEEP_MU_E_];
  Float_t Electron_dxy[N_KEEP_MU_E_];
  Float_t Electron_dz[N_KEEP_MU_E_];
  Float_t Electron_sip3d[N_KEEP_MU_E_];
  Bool_t Electron_convVeto[N_KEEP_MU_E_];
  UChar_t Electron_lostHits[N_KEEP_MU_E_];

  UInt_t nMuon;
  Float_t Muon_pt[N_KEEP_MU_E_];
  Float_t Muon_eta[N_KEEP_MU_E_];
  Float_t Muon_phi[N_KEEP_MU_E_];
  Float_t Muon_mass[N_KEEP_MU_E_];
  Int_t Muon_charge[N_KEEP_MU_E_];
  Bool_t Muon_tightId[N_KEEP_MU_E_];
  Bool_t Muon_mediumId[N_KEEP_MU_E_];
  UChar_t Muon_tkIsoId[N_KEEP_MU_E_];
  Float_t Muon_pfRelIso04_all[N_KEEP_MU_E_];
  Float_t Muon_miniPFRelIso_all[N_KEEP_MU_E_];
  Float_t Muon_dxy[N_KEEP_MU_E_];
  Float_t Muon_dz[N_KEEP_MU_E_];
  Float_t Muon_sip3d[N_KEEP_MU_E_];
  Bool_t Muon_isGlobal[N_KEEP_MU_E_];
  Bool_t Muon_isPFcand[N_KEEP_MU_E_];
  Int_t Muon_tightCharge[N_KEEP_MU_E_];

  Int_t numPU;

  UInt_t nJet;
  Float_t Jet_btagCSVV2[N_KEEP_JET_];
  Float_t Jet_btagDeepB[N_KEEP_JET_];
  Float_t Jet_eta[N_KEEP_JET_];
  Float_t Jet_phi[N_KEEP_JET_];
  Float_t Jet_pt[N_KEEP_JET_];
  Float_t Jet_mass[N_KEEP_JET_];
  Float_t Jet_neHEF[N_KEEP_JET_];
  Float_t Jet_neEmEF[N_KEEP_JET_];
  Int_t Jet_nConstituents[N_KEEP_JET_];
  Float_t Jet_chHEF[N_KEEP_JET_];
  Float_t Jet_chEmEF[N_KEEP_JET_];
  Int_t Jet_jetId[N_KEEP_JET_];

  ClassDefOverride(ThreeLepSelector, 0);

  /*******************************************************/
  /* __ __  ___  ____  __  ___  ____  __     ____  __    */
  /* || || // \\ || \\ || // \\ || )) ||    ||    (( \   */
  /* \\ // ||=|| ||_// || ||=|| ||=)  ||    ||==   \\    */
  /*  \V/  || || || \\ || || || ||_)) ||__| ||___ \_))   */
  /*******************************************************/

  Float_t weight;
  BranchManager b;
  std::vector<GoodPart> goodLeptons;
  std::vector<GoodPart> looseMuons;
  std::vector<GoodPart> looseElectrons;
  std::vector<GoodPart> goodBJets;
  double HT;
  int nJets, nBJets;
  bool passZVeto;
  BTagCalibration calib;
  BTagCalibrationReader btag_reader;  // central sys type

  /************************************************************/
  /* _____ __ __ __  __   ___ ______ __   ___   __  __  __    */
  /* ||    || || ||\ ||  //   | || | ||  // \\  ||\ || (( \   */
  /* ||==  || || ||\\|| ((      ||   || ((   )) ||\\||  \\    */
  /* ||    \\_// || \||  \\__   ||   ||  \\_//  || \|| \_))   */
  /************************************************************/

  void setupMuons();
  void setupElectrons();
  void setupJets();
  void setupChannel();

  bool isGoodMuon(size_t);
  bool isLooseMuon(size_t);
  bool isGoodJet(size_t);
  bool isGoodBJet(size_t);
  bool isGoodElectron(size_t);
  bool isLooseElectron(size_t);
  bool isLooseMVAElectron(size_t);

  bool doesNotOverlap(size_t);
  bool passFullIso(LorentzVector&, int, int);
  bool doesPassZVeto(GoodPart&, std::vector<GoodPart>&);

  //// General Functions
  int getSRBin() const;
  void clearValues();
  void ApplyScaleFactors();

  // Overloaded or necesary functions
  void LoadBranchesNanoAOD(Long64_t entry, std::pair<Systematic, std::string> variation) override;
  void FillHistograms(Long64_t entry, std::pair<Systematic, std::string> variation) override;
  virtual void SetBranchesNanoAOD() override;
  virtual void SetupNewDirectory() override;
  virtual std::string GetNameFromFile() override;
  // Readers to access the data (delete the ones you do not need).
  virtual void SetScaleFactors() override;
  virtual void Init(TTree* tree) override;

  ///ignore
  void LoadBranchesUWVV(Long64_t entry, std::pair<Systematic, std::string> variation) override;
  virtual void SetBranchesUWVV() override;
};

#endif
