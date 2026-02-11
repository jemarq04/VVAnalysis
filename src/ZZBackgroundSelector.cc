#include "Analysis/VVAnalysis/interface/ZZBackgroundSelector.h"
#include "TLorentzVector.h"
#include <TStyle.h>

void ZZBackgroundSelector::SlaveBegin(TTree* /*tree*/) {
  //systematics_ = {
  //    {jetEnergyScaleUp, "CMS_scale_jUp"},
  //    {jetEnergyScaleDown, "CMS_scale_jDown"},
  //    {jetEnergyResolutionUp, "CMS_res_jUp"},
  //    {jetEnergyResolutionDown, "CMS_res_jDown"},
  //};
  //isNonpromptEstimate_ = true;
  //doaQGC_ = false;

  ZZSelector::SlaveBegin(0);
  fakeRate_allE_ = (ScaleFactor*)GetInputList()->FindObject("fakeRate_allE");
  if (fakeRate_allE_ == nullptr)
    Abort("Must pass electron fake rate to input list!");
  fakeRate_allMu_ = (ScaleFactor*)GetInputList()->FindObject("fakeRate_allMu");
  if (fakeRate_allMu_ == nullptr)
    Abort("Must pass muon fake rate to input list!");
}
void ZZBackgroundSelector::Init(TTree* tree) {
  isNonPrompt_ = true;
  ZZSelector::Init(tree);
  systematics_ = {};
}

void ZZBackgroundSelector::SetupNewDirectory() {
  ZZSelector::SetupNewDirectory();

  // Insure that hist ranges are exactly the same as ZZSelector, just change name
  for (const auto&& obj : *currentHistDir_) {
    std::string name = obj->GetName();
    TNamed* named = dynamic_cast<TNamed*>(obj);
    named->SetName(name.insert(name.length() - 4, "Fakes_").c_str());
  }
  AddObject<TH1D>(MassHistPPPF_, ("Mass_PPPF_" + channelName_).c_str(), "Mass; m_{4l} [GeV]; Events;", 40, 70, 870);
  AddObject<TH1D>(MassHistPPFF_, ("Mass_PPFF_" + channelName_).c_str(), "Mass; m_{4l} [GeV]; Events;", 40, 70, 870);
  AddObject<TH1D>(
      Z1MassHistPPPF_, ("Z1Mass_PPPF_" + channelName_).c_str(), "Z1Mass; m_{Z_{1}} [GeV]; Events;", 60, 0, 120);
  AddObject<TH1D>(
      Z1MassHistPPFF_, ("Z1Mass_PPFF_" + channelName_).c_str(), "Z1Mass; m_{Z_{1}} [GeV]; Events;", 60, 0, 120);
  AddObject<TH1D>(
      Z2MassHistPPPF_, ("Z2Mass_PPPF_" + channelName_).c_str(), "Z2Mass; m_{Z_{2}} [GeV]; Events;", 60, 0, 120);
  AddObject<TH1D>(
      Z2MassHistPPFF_, ("Z2Mass_PPFF_" + channelName_).c_str(), "Z2Mass; m_{Z_{2}} [GeV]; Events;", 60, 0, 120);

  AddObject<TH1D>(
      MassFullHistPPPF_, ("MassFull_PPPF_" + channelName_).c_str(), "Mass; m_{4l} [GeV]; Events;", 40, 70, 870);
  AddObject<TH1D>(
      MassFullHistPPFF_, ("MassFull_PPFF_" + channelName_).c_str(), "Mass; m_{4l} [GeV]; Events;", 40, 70, 870);
  AddObject<TH1D>(
      Z1MassFullHistPPPF_, ("Z1MassFull_PPPF_" + channelName_).c_str(), "Z1Mass; m_{Z_{1}} [GeV]; Events;", 60, 0, 120);
  AddObject<TH1D>(
      Z1MassFullHistPPFF_, ("Z1MassFull_PPFF_" + channelName_).c_str(), "Z1Mass; m_{Z_{1}} [GeV]; Events;", 60, 0, 120);
  AddObject<TH1D>(
      Z2MassFullHistPPPF_, ("Z2MassFull_PPPF_" + channelName_).c_str(), "Z2Mass; m_{Z_{2}} [GeV]; Events;", 60, 0, 120);
  AddObject<TH1D>(
      Z2MassFullHistPPFF_, ("Z2MassFull_PPFF_" + channelName_).c_str(), "Z2Mass; m_{Z_{2}} [GeV]; Events;", 60, 0, 120);

  AddObject<TH1D>(
      WeightsHistmmee_, ("Weights_mmee_" + channelName_).c_str(), "Weight; Event Weight; Events;", 10, -5, 5);
  AddObject<TH1D>(
      WeightsHisteemm_, ("Weights_eemm_" + channelName_).c_str(), "Weight; Event Weight; Events;", 100, -5, 5);
}
float ZZBackgroundSelector::getEventWeight(Long64_t entry) {
  float evtwgt = 0;

  if (channel_ == mmee && (e1e2IsZ1()))
    WeightsHistmmee_->Fill(1, weight);

  if (channel_ == eemm && !(e1e2IsZ1()))
    WeightsHisteemm_->Fill(1, weight);

  //if (channel_ == eeee || channel_ == mmmm){
  //}
  //in eemm the e1e2IsZ1 function already sets the correct Z1,Z2 leptons and even the IDs from LoadBranches
  //So only need to take care which is l3 and l4
  // if (channel_ == eemm || channel_ == mmee){
  //   if(Z2FP()){
  //     float templ3Pt = l3Pt;
  //     l3Pt = l4Pt;
  //     l4Pt = templ3Pt;
  //     float templ3Eta = l3Eta;
  //     l3Eta = l4Eta;
  //     l4Eta = templ3Eta;
  //   }
  // }
  //std::cout<<"Weight in Bkg Seletor getEventWeight function: "<<weight<<std::endl;
  if (IsPPPFRegion()) {
    if (ZZSelection()) {
      //std::cout<<"Weight in PPPF: "<<weight<<std::endl;
      Z1MassHistPPPF_->Fill(Z1Mass, weight);
      Z2MassHistPPPF_->Fill(Z2Mass, weight);
      MassHistPPPF_->Fill(Mass, weight);
    }
    Z1MassFullHistPPPF_->Fill(Z1Mass, weight);
    Z2MassFullHistPPPF_->Fill(Z2Mass, weight);
    MassFullHistPPPF_->Fill(Mass, weight);

    evtwgt = (getl4FakeRate(entry) * weight);
    //WeightsHistPPPF_->Fill(1,evtwgt);
  }
  if (IsPPFFRegion()) {
    if (ZZSelection()) {
      //std::cout<<"Weight in PPFF: "<<weight<<std::endl;
      Z1MassHistPPFF_->Fill(Z1Mass, weight);
      Z2MassHistPPFF_->Fill(Z2Mass, weight);
      MassHistPPFF_->Fill(Mass, weight);
    }
    Z1MassFullHistPPFF_->Fill(Z1Mass, weight);
    Z2MassFullHistPPFF_->Fill(Z2Mass, weight);
    MassFullHistPPFF_->Fill(Mass, weight);

    evtwgt = ((-1 * getl3FakeRate(entry) * getl4FakeRate(entry)) * weight);
    //evtwgt = ((getl3FakeRate(entry)*getl4FakeRate(entry))*weight);
    //WeightsHistPPFF_->Fill(1,evtwgt);
  }
  //std::cout<<"eventWeight after Fake Rate: "<<evtwgt<<std::endl;
  return evtwgt;
}

void ZZBackgroundSelector::LoadBranchesUWVV(Long64_t entry, std::pair<Systematic, std::string> variation) {
  ZZSelector::LoadBranchesUWVV(entry, variation);
  SetZ1Z2Masses();
  //turn off ZZSelection otherwise it will cause problem in full mass range m4l plots
  //if (!ZZSelection()){
  //  return;}

  //std::cout<<"isNonPrompt_ from ZZSelector: "<<isNonPrompt_<<std::endl;
  //isNonPrompt_ = true;
  //std::cout<<"isNonPrompt_ from ZZBackgroundSelector: "<<isNonPrompt_<<std::endl;
  //We don't want systematics to run for data-driven nonPrompt Estimate so save time and space
  //systematics_ = {};
  //doSystematics_ = false;
  weight = getEventWeight(entry);
  //std::cout<<"eventWeight in loadBranchesUWVV: "<<weight<<std::endl;
}
float ZZBackgroundSelector::getl3FakeRate(Long64_t entry) {
  float pt_fillval = l3Pt < FR_MAX_PT_ ? l3Pt : FR_MAX_PT_ - 0.01;
  float fr = 1;
  if (channel_ == eeee || (channel_ == mmee && !(e1e2IsZ1()))) {
    fr = fakeRate_allE_->Evaluate2D(pt_fillval, std::abs(l3Eta));
    //fr = 0.03;//avg e fake rate
    //std::cout<<"channel: "<<channel_<<std::endl;
    //std::cout<<"l3 E Fake Rate: "<<fr<<std::endl;
  } else if (channel_ == mmmm || (channel_ == eemm && (e1e2IsZ1()))) {
    fr = fakeRate_allMu_->Evaluate2D(pt_fillval, std::abs(l3Eta));
    //fr = 0.1;//avg mu fake rate
    //std::cout<<"channel: "<<channel_<<std::endl;
    //std::cout<<"l3 Mu Fake Rate: "<<fr<<std::endl;
  } else {
    fr = 0.;
  }
  return fr / (1 - fr);
}

float ZZBackgroundSelector::getl4FakeRate(Long64_t entry) {
  float pt_fillval = l4Pt < FR_MAX_PT_ ? l4Pt : FR_MAX_PT_ - 0.01;
  float fr = 1;
  if (channel_ == eeee || (channel_ == mmee && !(e1e2IsZ1()))) {
    fr = fakeRate_allE_->Evaluate2D(pt_fillval, std::abs(l4Eta));
    //fr = 0.03;//avg e fake rate
    //std::cout<<"channel: "<<channel_<<std::endl;
    //std::cout<<"l4 E Fake Rate: "<<fr<<std::endl;
  } else if (channel_ == mmmm || (channel_ == eemm && (e1e2IsZ1()))) {
    fr = fakeRate_allMu_->Evaluate2D(pt_fillval, std::abs(l4Eta));
    //fr = 0.1;//avg mu fake rate
    //std::cout<<"channel: "<<channel_<<std::endl;
    //std::cout<<"l4 Mu Fake Rate: "<<fr<<std::endl;
  } else {
    fr = 0.;
  }
  return fr / (1 - fr);
}
//Remember that we only build Z1 (Real Z) out of OS-SF tight leptons
bool ZZBackgroundSelector::IsPPPFRegion() {
  return ((tightZ1Leptons() && (Z2PF() || Z2FP())) || (tightZ2Leptons() && (Z1PF() || Z1FP())));
}
//Remember that we only build Z1 (Real Z) out of OS-SF tight leptons
bool ZZBackgroundSelector::IsPPFFRegion() {
  if (channel_ == eeee || channel_ == mmmm)
    return ((tightZ1Leptons() && Z2FF()) || (tightZ2Leptons() && Z1FF()) || (Z1FP() && Z2PF()) || (Z1PF() && Z2FP()) ||
            (Z1PF() && Z2PF()) || (Z1FP() && Z2FP()));
  else
    return ((tightZ1Leptons() && Z2FF()) || (tightZ2Leptons() && Z1FF()));
}
//Remember that we only build Z1 (Real Z) out of OS-SF tight leptons
//This is only for 4e,4mu channels as eemm/mmee channels is already taken care of by SetVariables function which gets
//called in LoadBranches() from ZZSelector. The SetVariables function should work in CRs, SR equally. We only need
//SetZ1Z2Masses function for 4e/4mu in CRs.
void ZZBackgroundSelector::SetZ1Z2Masses() {
  TLorentzVector lepton1;
  lepton1.SetPtEtaPhiM(l1Pt, l1Eta, l1Phi, l1Mass);
  TLorentzVector lepton2;
  lepton2.SetPtEtaPhiM(l2Pt, l2Eta, l2Phi, l2Mass);
  TLorentzVector lepton3;
  lepton3.SetPtEtaPhiM(l3Pt, l3Eta, l3Phi, l3Mass);
  TLorentzVector lepton4;
  lepton4.SetPtEtaPhiM(l4Pt, l4Eta, l4Phi, l4Mass);
  if (tightZ1Leptons() && !tightZ2Leptons()) {
    Z1Mass = (lepton1 + lepton2).M();
    Z2Mass = (lepton3 + lepton4).M();
    Z1Pt = (lepton1 + lepton2).Pt();
    Z2Pt = (lepton3 + lepton4).Pt();
    //In Z2 what is l3 and l4 can change the fake rate a little bit.
    if (Z2FP()) {
      float templ3Pt = l3Pt;
      l3Pt = l4Pt;
      l4Pt = templ3Pt;
      float templ3Eta = l3Eta;
      l3Eta = l4Eta;
      l4Eta = templ3Eta;
    }
  } else if (tightZ2Leptons() && !tightZ1Leptons()) {
    Z1Mass = (lepton3 + lepton4).M();
    Z2Mass = (lepton1 + lepton2).M();
    Z1Pt = (lepton3 + lepton4).Pt();
    Z2Pt = (lepton1 + lepton2).Pt();
    //Fakes are l1,l2 from skims, reverse them
    float templ1Pt = l1Pt;
    l1Pt = l3Pt;
    l3Pt = templ1Pt;
    float templ2Pt = l2Pt;
    l2Pt = l4Pt;
    l4Pt = templ2Pt;
    float templ1Eta = l1Eta;
    l1Eta = l3Eta;
    l3Eta = templ1Eta;
    float templ2Eta = l2Eta;
    l2Eta = l4Eta;
    l4Eta = templ2Eta;
    //Now we have two fakes identified by l3Pt, l4Pt and l3Eta, l4Eta
    //Further special condition between l3,l4 which one to use for l4fake rate in PPPF region, their IDs still are labeled l1IsTight,l2IsTight
    if (Z1FP()) {
      float templ3Pt = l3Pt;
      l3Pt = l4Pt;
      l4Pt = templ3Pt;
      float templ3Eta = l3Eta;
      l3Eta = l4Eta;
      l4Eta = templ3Eta;
    }
  }
  //The last two conditions only matter for TTJets fakes (very small amount)
  else if (Z1FP() && Z2PF()) {
    //Make sure I am not making a Z in eemm with an e and mu!
    if ((channel_ == eeee || channel_ == mmmm) && l1PdgId * l4PdgId < 0) {
      Z1Mass = (lepton2 + lepton3).M();
      Z2Mass = (lepton1 + lepton4).M();
      Z1Pt = (lepton2 + lepton3).Pt();
      Z2Pt = (lepton1 + lepton4).Pt();
      //Here the two fakes are l1,l4 and we only need to relabel l1 -> l3
      float templ1Pt = l1Pt;
      l1Pt = l3Pt;
      l3Pt = templ1Pt;
      float templ1Eta = l1Eta;
      l1Eta = l3Eta;
      l3Eta = templ1Eta;
    }
  } else if (Z1PF() && Z2FP()) {
    //Make sure I am not making a Z in eemm with an e and mu!
    if ((channel_ == eeee || channel_ == mmmm) && l1PdgId * l4PdgId < 0) {
      Z1Mass = (lepton1 + lepton4).M();
      Z2Mass = (lepton2 + lepton3).M();
      Z1Pt = (lepton1 + lepton4).Pt();
      Z2Pt = (lepton2 + lepton3).Pt();
      //Here the two fakes are l2,l3 and we only need to relabel l2 -> l4 since this only matters in PPFF region so l3,l4 are interchangeable
      float templ2Pt = l2Pt;
      l2Pt = l4Pt;
      l4Pt = templ2Pt;
      float templ2Eta = l2Eta;
      l2Eta = l4Eta;
      l4Eta = templ2Eta;
    }
  } else if (Z1PF() && Z2PF()) {
    if ((channel_ == eeee || channel_ == mmmm) && l1PdgId * l3PdgId < 0) {
      //std::cout<<"Z1PF() && Z2PF()) loop enter "<<std::endl;
      Z1Mass = (lepton1 + lepton3).M();
      Z2Mass = (lepton2 + lepton4).M();
      Z1Pt = (lepton1 + lepton3).Pt();
      Z2Pt = (lepton2 + lepton4).Pt();
      //Here the two fakes are l2,l4 and we only need to relabel l2 -> l3
      float templ2Pt = l2Pt;
      l2Pt = l3Pt;
      l3Pt = templ2Pt;
      float templ2Eta = l2Eta;
      l2Eta = l3Eta;
      l3Eta = templ2Eta;
    }
  } else if (Z1FP() && Z2FP()) {
    if ((channel_ == eeee || channel_ == mmmm) && l1PdgId * l3PdgId < 0) {
      //std::cout<<"Z1FP() && Z2FP()) loop enter "<<std::endl;
      Z1Mass = (lepton2 + lepton4).M();
      Z2Mass = (lepton1 + lepton3).M();
      Z1Pt = (lepton2 + lepton4).Pt();
      Z2Pt = (lepton1 + lepton3).Pt();
      //Here the two fakes are l1,l3 and we only need to relabel l1 -> l4
      float templ1Pt = l1Pt;
      l1Pt = l4Pt;
      l4Pt = templ1Pt;
      float templ1Eta = l1Eta;
      l1Eta = l4Eta;
      l4Eta = templ1Eta;
    }
  }
}
