#include "Analysis/VVAnalysis/interface/WZSelectorBase.h"
#include <TStyle.h>

void WZSelectorBase::Begin(TTree * /*tree*/) { TString option = GetOption(); }

void WZSelectorBase::SlaveBegin(TTree * /*tree*/) {}
void WZSelectorBase::Init(TTree *tree) {
  if (!tree)
    return;
  fChain = tree;

  TString option = GetOption();

  if (GetInputList() != nullptr) {
    TNamed *name = (TNamed *)GetInputList()->FindObject("name");
    TNamed *chan = (TNamed *)GetInputList()->FindObject("channel");
    TNamed *selection = (TNamed *)GetInputList()->FindObject("selection");
    if (name != nullptr) {
      name_ = name->GetTitle();
    }
    if (chan != nullptr) {
      channelName_ = chan->GetTitle();
    }
    if (selection != nullptr) {
      selectionName_ = selection->GetTitle();
    }
  }
  std::cout << "Processing " << name_ << std::endl;

  isMC_ = false;
  if (name_.find("data") == std::string::npos) {
    isMC_ = true;
    fChain->SetBranchAddress("genWeight", &genWeight, &b_genWeight);
  } else {
    fChain->SetBranchAddress("Flag_duplicateMuonsPass", &Flag_duplicateMuonsPass, &b_Flag_duplicateMuonsPass);
    fChain->SetBranchAddress("Flag_badMuonsPass", &Flag_badMuonsPass, &b_Flag_badMuonsPass);
  }

  currentHistDir_ = dynamic_cast<TList *>(fOutput->FindObject(name_.c_str()));
  if (currentHistDir_ == nullptr) {
    currentHistDir_ = new TList();
    currentHistDir_->SetName(name_.c_str());
    fOutput->Add(currentHistDir_);
    // Watch for something that I hope never happens,
    size_t existingObjectPtrsSize = allObjects_.size();
    SetupNewDirectory();
    if (existingObjectPtrsSize > 0 && allObjects_.size() != existingObjectPtrsSize) {
      Abort(Form(
          "WZSelectorBase: Size of allObjects has changed!: %lu to %lu", existingObjectPtrsSize, allObjects_.size()));
    }
  }
  UpdateDirectory();

  if (channelName_ == "eee") {
    channel_ = eee;
    fChain->SetBranchAddress("e1IsCBVIDTight", &l1IsTight, &b_l1IsTight);
    fChain->SetBranchAddress("e2IsCBVIDTight", &l2IsTight, &b_l2IsTight);
    fChain->SetBranchAddress("e3IsCBVIDTight", &l3IsTight, &b_l3IsTight);
  } else if (channelName_ == "eem") {
    channel_ = eem;
    fChain->SetBranchAddress("e1IsCBVIDTight", &l1IsTight, &b_l1IsTight);
    fChain->SetBranchAddress("e2IsCBVIDTight", &l2IsTight, &b_l2IsTight);
    fChain->SetBranchAddress("mIsWZTight", &l3IsTight, &b_l3IsTight);
  } else if (channelName_ == "emm") {
    channel_ = emm;
    fChain->SetBranchAddress("eIsCBVIDTight", &l3IsTight, &b_l3IsTight);
    fChain->SetBranchAddress("m1IsWZTight", &l1IsTight, &b_l1IsTight);
    fChain->SetBranchAddress("m2IsWZTight", &l2IsTight, &b_l2IsTight);
  } else if (channelName_ == "mmm") {
    channel_ = mmm;
    fChain->SetBranchAddress("m1IsWZTight", &l1IsTight, &b_l1IsTight);
    fChain->SetBranchAddress("m2IsWZTight", &l2IsTight, &b_l2IsTight);
    fChain->SetBranchAddress("m3IsWZTight", &l3IsTight, &b_l3IsTight);
  } else
    throw std::invalid_argument("Invalid channel choice!");

  if (selectionName_ == "tightleptons" || selectionName_ == "Wselection")
    selection_ = tightleptons;
  else if (selectionName_ == "VBSselection")
    selection_ = VBSselection;
  else if (selectionName_ == "VBSselection_Tight") {
    selection_ = VBSselection_Tight;
  } else {
    std::cerr << "INFO: Selection set to default value: TightLeptons" << std::endl;
    selection_ = tightleptons;
  }
  isVBS_ = (selection_ == VBSselection || selection_ == VBSselection_Tight);

  fChain->SetBranchAddress("nCBVIDTightElec", &nCBVIDTightElec, &b_nCBVIDTightElec);
  fChain->SetBranchAddress("nWZTightMuon", &nWZTightMuon, &b_nWZTightMuon);
  fChain->SetBranchAddress("nWZTightMuon", &nWZTightMuon, &b_nWZTightMuon);
  fChain->SetBranchAddress(
      "Flag_BadChargedCandidateFilterPass", &Flag_BadChargedCandidateFilterPass, &b_Flag_BadChargedCandidateFilterPass);
  fChain->SetBranchAddress("Flag_BadPFMuonFilterPass", &Flag_BadPFMuonFilterPass, &b_Flag_BadPFMuonFilterPass);
  fChain->SetBranchAddress("Flag_HBHENoiseFilterPass", &Flag_HBHENoiseFilterPass, &b_Flag_HBHENoiseFilterPass);
  fChain->SetBranchAddress("Flag_HBHENoiseIsoFilterPass", &Flag_HBHENoiseIsoFilterPass, &b_Flag_HBHENoiseIsoFilterPass);
  fChain->SetBranchAddress("Flag_EcalDeadCellTriggerPrimitiveFilterPass",
                           &Flag_EcalDeadCellTriggerPrimitiveFilterPass,
                           &b_Flag_EcalDeadCellTriggerPrimitiveFilterPass);
  fChain->SetBranchAddress("Flag_goodVerticesPass", &Flag_goodVerticesPass, &b_Flag_goodVerticesPass);
  fChain->SetBranchAddress("Flag_eeBadScFilterPass", &Flag_eeBadScFilterPass, &b_Flag_eeBadScFilterPass);
  fChain->SetBranchAddress(
      "Flag_globalTightHalo2016FilterPass", &Flag_globalTightHalo2016FilterPass, &b_Flag_globalTightHalo2016FilterPass);
}

Bool_t WZSelectorBase::Notify() { return kTRUE; }

Bool_t WZSelectorBase::Process(Long64_t entry) {
  genWeight = 1;
  if (isMC_)
    b_genWeight->GetEntry(entry);
  else {
    b_Flag_duplicateMuonsPass->GetEntry(entry);
    b_Flag_badMuonsPass->GetEntry(entry);
  }
  b_l1IsTight->GetEntry(entry);
  b_l2IsTight->GetEntry(entry);
  b_l3IsTight->GetEntry(entry);
  b_nCBVIDTightElec->GetEntry(entry);
  b_nWZTightMuon->GetEntry(entry);
  b_Flag_BadPFMuonFilterPass->GetEntry(entry);
  b_Flag_BadChargedCandidateFilterPass->GetEntry(entry);
  b_Flag_HBHENoiseFilterPass->GetEntry(entry);
  b_Flag_HBHENoiseIsoFilterPass->GetEntry(entry);
  b_Flag_EcalDeadCellTriggerPrimitiveFilterPass->GetEntry(entry);
  b_Flag_goodVerticesPass->GetEntry(entry);
  b_Flag_eeBadScFilterPass->GetEntry(entry);
  b_Flag_globalTightHalo2016FilterPass->GetEntry(entry);

  passesLeptonVeto = nWZTightMuon + nCBVIDTightElec <= 3;

  return kTRUE;
}

// Meant to be a wrapper for the tight ID just in case it changes
// To be a function of multiple variables
bool WZSelectorBase::zlep1IsTight() { return l1IsTight; }

bool WZSelectorBase::zlep2IsTight() { return l2IsTight; }

bool WZSelectorBase::tightZLeptons() { return zlep1IsTight() && zlep2IsTight(); }

bool WZSelectorBase::lepton3IsTight() { return l3IsTight; }

void WZSelectorBase::Terminate() {}

void WZSelectorBase::SlaveTerminate() {}
void WZSelectorBase::UpdateDirectory() {
  for (TNamed **objPtrPtr : allObjects_) {
    if (*objPtrPtr == nullptr)
      Abort("WZSelectorBase: Call to UpdateObject but existing pointer is null");
    *objPtrPtr = (TNamed *)currentHistDir_->FindObject((*objPtrPtr)->GetName());
    if (*objPtrPtr == nullptr)
      Abort("WZSelectorBase: Call to UpdateObject but current directory has no instance");
  }
}

void WZSelectorBase::SetupNewDirectory() {}
