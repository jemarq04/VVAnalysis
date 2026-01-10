#include "Analysis/VVAnalysis/interface/FakeRateSelector.h"
#include <TStyle.h>

void FakeRateSelector::LoadBranchesUWVV(Long64_t entry, std::pair<Systematic, std::string> variation) {
  ZZSelectorBase::LoadBranchesUWVV(entry, variation);
  //In HZZ AN it says: |M_inv(l1,l2)- MZ| < 7 GeV, to reduce the contribution from photon (asymmetric) conversions populating low masses.
  if (Z1Mass > 98.1876 || Z1Mass < 84.1876)
    return;
  if (type1_pfMETEt > 25)
    return;
  if (l3MtToMET > 30)
    return;
  if (!tightZ1Leptons())
    return;

  float pt_fillval = l3Pt;
  float eta_fillval = std::abs(l3Eta);
  //std::cout<<"Is it filling?"<<std::endl;
  //std::cout<<pt_fillval<<std::endl;
  float loose_weight = weight;
  //if (channel_ == eee || channel_ == emm) {
  //    loose_weight /= eIdSF_->Evaluate2D(std::abs(l3Eta), l3Pt);
  //}
  //else if (channel_ == eem || channel_ == mmm) {
  //    loose_weight /= mIsoSF_->Evaluate2D(std::abs(l3Eta), l3Pt);
  //}
  //Electron barrel up to |eta| = 1.479
  if((channel_ == eee) || (channel_ == emm)){
    if(eta_fillval < 1.479)
      passingLooseE1DPt_barrel_->Fill(pt_fillval, loose_weight);
    else
      passingLooseE1DPt_endcap_->Fill(pt_fillval, loose_weight);

    passingLooseE2D_->Fill(pt_fillval, eta_fillval, loose_weight);
    passingLooseE1DEta_->Fill(eta_fillval, loose_weight);
  }
  //Muon barrel up to |eta| = 1.2
  else if (channel_ == eem || channel_ == mmm) {
    if(eta_fillval < 1.2)
      passingLooseMu1DPt_barrel_->Fill(pt_fillval, loose_weight);
    else
      passingLooseMu1DPt_endcap_->Fill(pt_fillval, loose_weight);

    passingLooseMu2D_->Fill(pt_fillval, eta_fillval, loose_weight);
    passingLooseMu1DEta_->Fill(eta_fillval, loose_weight);
  }
  if (lep3IsTight()) {
    if((channel_ == eee) || (channel_ == emm)){
      if(eta_fillval < 1.479)
        passingTightE1DPt_barrel_->Fill(pt_fillval, loose_weight);
      else
        passingTightE1DPt_endcap_->Fill(pt_fillval, loose_weight);

      passingTightE2D_->Fill(pt_fillval, eta_fillval, weight);
      passingTightE1DEta_->Fill(eta_fillval, weight);
    }
    //Muon barrel up to |eta| = 1.2
    else if (channel_ == eem || channel_ == mmm) {
      if(eta_fillval < 1.2)
        passingTightMu1DPt_barrel_->Fill(pt_fillval, loose_weight);
      else
        passingTightMu1DPt_endcap_->Fill(pt_fillval, loose_weight);

      passingTightMu2D_->Fill(pt_fillval, eta_fillval, weight);
      passingTightMu1DEta_->Fill(eta_fillval, weight);
    }
  }
}

void FakeRateSelector::Init(TTree *tree)
{
  //systematics_ = {{Central,""}};
  ZZSelectorBase::Init(tree);
}

void FakeRateSelector::SetupNewDirectory()
{
  ZZSelectorBase::SetupNewDirectory();

  const int MuPtbins = 6;
  double Mu_Pt_bins[MuPtbins+1] = {5,10,20,30,40,50,80};

  const int ElePtbins = 6;
  double Ele_Pt_bins[ElePtbins+1] = {5,10,20,30,40,50,80};
  //For electron fakes

  const int nEleEtabins=4;
  double Ele_eta_bins[nEleEtabins+1] = {0.,0.7395,1.479,2.0,2.5};

  //For muons fakes

  const int nMuEtabins=2;
  double Mu_eta_bins[nMuEtabins+1] = {0.,1.2,2.4};

  AddObject<TH2D>(passingTightE2D_, ("passingTightE2D_"+channelName_).c_str(), "|#eta|; p_{T} [GeV]", ElePtbins, Ele_Pt_bins, nEleEtabins,Ele_eta_bins);
  AddObject<TH1D>(passingTightE1DEta_, ("passingTightE1DEta_"+channelName_).c_str(), "Tight leptons; |#eta|", nEleEtabins,Ele_eta_bins);
  AddObject<TH2D>(passingLooseE2D_, ("passingLooseE2D_"+channelName_).c_str(), "|#eta|; p_{T} [GeV]", ElePtbins, Ele_Pt_bins, nEleEtabins,Ele_eta_bins);
  AddObject<TH1D>(passingLooseE1DEta_, ("passingLooseE1DEta_"+channelName_).c_str(), "Loose leptons; |#eta|", nEleEtabins,Ele_eta_bins);
  AddObject<TH1D>(passingTightE1DPt_barrel_, ("passingTightE1DPt_barrel_"+channelName_).c_str(), "Tight leptons; p_{T} [GeV]", ElePtbins, Ele_Pt_bins);
  AddObject<TH1D>(passingTightE1DPt_endcap_, ("passingTightE1DPt_endcap_"+channelName_).c_str(), "Tight leptons; p_{T} [GeV]", ElePtbins, Ele_Pt_bins);
  AddObject<TH1D>(passingLooseE1DPt_barrel_, ("passingLooseE1DPt_barrel_"+channelName_).c_str(), "Loose leptons; p_{T} [GeV]", ElePtbins, Ele_Pt_bins);
  AddObject<TH1D>(passingLooseE1DPt_endcap_, ("passingLooseE1DPt_endcap_"+channelName_).c_str(), "Loose leptons; p_{T} [GeV]", ElePtbins, Ele_Pt_bins);

  AddObject<TH2D>(passingTightMu2D_, ("passingTightMu2D_"+channelName_).c_str(), "|#eta|; p_{T} [GeV]", MuPtbins, Mu_Pt_bins, nMuEtabins,Mu_eta_bins);
  AddObject<TH1D>(passingTightMu1DEta_, ("passingTightMu1DEta_"+channelName_).c_str(), "Tight leptons; |#eta|", nMuEtabins,Mu_eta_bins);
  AddObject<TH2D>(passingLooseMu2D_, ("passingLooseMu2D_"+channelName_).c_str(), "|#eta|; p_{T} [GeV]", MuPtbins, Mu_Pt_bins, nMuEtabins,Mu_eta_bins);
  AddObject<TH1D>(passingLooseMu1DEta_, ("passingLooseMu1DEta_"+channelName_).c_str(), "Loose leptons; |#eta|", nMuEtabins,Mu_eta_bins);
  AddObject<TH1D>(passingTightMu1DPt_barrel_, ("passingTightMu1DPt_barrel_"+channelName_).c_str(), "Tight leptons; p_{T} [GeV]", MuPtbins, Mu_Pt_bins);
  AddObject<TH1D>(passingTightMu1DPt_endcap_, ("passingTightMu1DPt_endcap_"+channelName_).c_str(), "Tight leptons; p_{T} [GeV]", MuPtbins, Mu_Pt_bins);
  AddObject<TH1D>(passingLooseMu1DPt_barrel_, ("passingLooseMu1DPt_barrel_"+channelName_).c_str(), "Loose leptons; p_{T} [GeV]", MuPtbins, Mu_Pt_bins);
  AddObject<TH1D>(passingLooseMu1DPt_endcap_, ("passingLooseMu1DPt_endcap_"+channelName_).c_str(), "Loose leptons; p_{T} [GeV]", MuPtbins, Mu_Pt_bins);
}
