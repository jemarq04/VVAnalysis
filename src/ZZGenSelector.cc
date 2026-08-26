#include "Analysis/VVAnalysis/interface/ZZGenSelector.h"
#include "TLorentzVector.h"
#include <boost/algorithm/string.hpp>

void ZZGenSelector::Init(TTree *tree)
{
    allChannels_ = {"ee", "mm", };
    hists1D_ = {
        "GenZ2lep2_Phi",
        "GenZ2lep2_Pt",
        "GenMass",
        "Pt",
        "nJets",
        "nJetCSVv2T",
        "Genyield",
        "GenZMass",
        "GenZ1Mass",
        "GenZ2Mass",
        "GenZZPt",
        "GenZZEta",
        "GenZ1Pt",
        "GenZ2Pt",
        "GenZPt",
        "GenZ1Phi",
        "GenZ2Phi",
        "GendPhiZ1Z2",
        "GenLepPt",
        "GenLepEta",
        "GenLep12Pt",
        "GenLep12Eta",
        "GenLep34Pt",
        "GenLep34Eta",
        "GenZ1lep1_Eta",
        "GenZ1lep1_Phi",
        "GenZ1lep1_Pt",
        "GenZ1lep2_Eta",
        "GenZ1lep2_Phi",
        "GenZ1lep2_Pt",
        "GenZ2lep1_Eta",
        "GenZ2lep1_Phi",
        "GenZ2lep1_Pt",
        "GenZ2lep2_Eta",
    };

    //hists2D_ = {"GenZ1Mass_GenZ2Mass"};
    SelectorBase::Init(tree);
}


void ZZGenSelector::LoadBranchesUWVV(Long64_t entry, std::pair<Systematic, std::string> variation) {
    Genweight = 1;
    b_Genl1Pt->GetEntry(entry);
    b_Genl2Pt->GetEntry(entry);
    b_Genl3Pt->GetEntry(entry);
    b_Genl1Eta->GetEntry(entry);
    b_Genl2Eta->GetEntry(entry);
    b_Genl3Eta->GetEntry(entry);
    b_Genl1Phi->GetEntry(entry);
    b_Genl2Phi->GetEntry(entry);
    b_Genl3Phi->GetEntry(entry);
    //std::cout<<"Is the ZZGenSelectorBase fine until here"<<std::endl;
    if (channel_ == eeee || channel_ == eemm || channel_ == mmee || channel_ == mmmm) {
      b_Genl4Pt->GetEntry(entry);
      b_Genl4Eta->GetEntry(entry);
      b_Genl4Phi->GetEntry(entry);
      b_GenZ2mass->GetEntry(entry);
      b_GenZ2pt->GetEntry(entry);
      b_GenZ2Phi->GetEntry(entry);
    }
    b_GenZ1mass->GetEntry(entry);
    b_GenZ1pt->GetEntry(entry);
    b_GenZ1Phi->GetEntry(entry);
    if(channel_ == mmee) {
      if(e1e2IsZ1())
        Genweight=0.0;
        //Makes Genweight 0 if Z1 is ee hence should not go in _mmee histos
    }
    else if(channel_ == eemm) {
      if(!(e1e2IsZ1()))
        Genweight=0.0;
        //Makes Genweight 0 if Z1 is mm hence should not go in _eemm
    }
    b_GenMass->GetEntry(entry);
    b_GenPt->GetEntry(entry);
    b_GenEta->GetEntry(entry);
    //std::cout<<"channel in LoadBranches function: "<<channel_<<std::endl;
    if(channel_ == eemm || channel_ == mmee){
      SetVariables(entry);
    }
    auto deltaPhiZZ = [](float phi1, float phi2) {
      float pi = TMath::Pi();
      float dphi = std::abs(phi1-phi2);
      if(dphi>pi)
          dphi = 2.0*pi - dphi;
      return dphi;
    };

    GendPhiZZ = deltaPhiZZ(GenZ1Phi,GenZ2Phi);
}

void ZZGenSelector::LoadBranchesNanoAOD(Long64_t entry, std::pair<Systematic, std::string> variation) {
    throw std::domain_error("NanoAOD ntuples not supported for ZZGenSelector!");
}

void ZZGenSelector::SetBranchesNanoAOD() {
    throw std::domain_error("NanoAOD ntuples not supported for ZZGenSelector!");
}

void ZZGenSelector::SetBranchesUWVV() {
    if (channel_ == eeee) {
        //std::cout<<"enum channel_: "<<channel_<<std::endl;
        fChain->SetBranchAddress("e1_e2_Mass", &GenZ1mass, &b_GenZ1mass);
        fChain->SetBranchAddress("e3_e4_Mass", &GenZ2mass, &b_GenZ2mass);
        fChain->SetBranchAddress("e1_e2_Pt", &GenZ1pt, &b_GenZ1pt);
        fChain->SetBranchAddress("e3_e4_Pt", &GenZ2pt, &b_GenZ2pt);
        fChain->SetBranchAddress("e1_e2_Phi", &GenZ1Phi, &b_GenZ1Phi);
        fChain->SetBranchAddress("e3_e4_Phi", &GenZ2Phi, &b_GenZ2Phi);
        fChain->SetBranchAddress("e1Pt", &Genl1Pt, &b_Genl1Pt);
        fChain->SetBranchAddress("e2Pt", &Genl2Pt, &b_Genl2Pt);
        fChain->SetBranchAddress("e3Pt", &Genl3Pt, &b_Genl3Pt);
        fChain->SetBranchAddress("e4Pt", &Genl4Pt, &b_Genl4Pt);
        fChain->SetBranchAddress("e1Eta", &Genl1Eta, &b_Genl1Eta);
        fChain->SetBranchAddress("e2Eta", &Genl2Eta, &b_Genl2Eta);
        fChain->SetBranchAddress("e3Eta", &Genl3Eta, &b_Genl3Eta);
        fChain->SetBranchAddress("e4Eta", &Genl4Eta, &b_Genl4Eta);
        fChain->SetBranchAddress("e1Phi", &Genl1Phi, &b_Genl1Phi);
        fChain->SetBranchAddress("e2Phi", &Genl2Phi, &b_Genl2Phi);
        fChain->SetBranchAddress("e3Phi", &Genl3Phi, &b_Genl3Phi);
        fChain->SetBranchAddress("e4Phi", &Genl4Phi, &b_Genl4Phi);
    }
    //Add 2e2mu channel also but it still needs to differentiate which one is Z1Mass and which one is Z2Mass leptons
    //This is done with a flag at the time of Process for each event on the fly
    else if (channel_ == eemm) {
        fChain->SetBranchAddress("e1_e2_Mass", &GenZ1mass, &b_GenZ1mass);
        fChain->SetBranchAddress("m1_m2_Mass", &GenZ2mass, &b_GenZ2mass);
        fChain->SetBranchAddress("e1_e2_Pt", &GenZ1pt, &b_GenZ1pt);
        fChain->SetBranchAddress("m1_m2_Pt", &GenZ2pt, &b_GenZ2pt);
        fChain->SetBranchAddress("e1_e2_Phi", &GenZ1Phi, &b_GenZ1Phi);
        fChain->SetBranchAddress("m1_m2_Phi", &GenZ2Phi, &b_GenZ2Phi);
        fChain->SetBranchAddress("e1Pt", &Genl1Pt, &b_Genl1Pt);
        fChain->SetBranchAddress("e2Pt", &Genl2Pt, &b_Genl2Pt);
        fChain->SetBranchAddress("m1Pt", &Genl3Pt, &b_Genl3Pt);
        fChain->SetBranchAddress("m2Pt", &Genl4Pt, &b_Genl4Pt);
        fChain->SetBranchAddress("e1Eta", &Genl1Eta, &b_Genl1Eta);
        fChain->SetBranchAddress("e2Eta", &Genl2Eta, &b_Genl2Eta);
        fChain->SetBranchAddress("m1Eta", &Genl3Eta, &b_Genl3Eta);
        fChain->SetBranchAddress("m2Eta", &Genl4Eta, &b_Genl4Eta);
        fChain->SetBranchAddress("e1Phi", &Genl1Phi, &b_Genl1Phi);
        fChain->SetBranchAddress("e2Phi", &Genl2Phi, &b_Genl2Phi);
        fChain->SetBranchAddress("m1Phi", &Genl3Phi, &b_Genl3Phi);
        fChain->SetBranchAddress("m2Phi", &Genl4Phi, &b_Genl4Phi);
    }
    else if (channel_ == mmee) {
        fChain->SetBranchAddress("e1_e2_Mass", &GenZ1mass, &b_GenZ1mass);
        fChain->SetBranchAddress("m1_m2_Mass", &GenZ2mass, &b_GenZ2mass);
        fChain->SetBranchAddress("e1_e2_Pt", &GenZ1pt, &b_GenZ1pt);
        fChain->SetBranchAddress("m1_m2_Pt", &GenZ2pt, &b_GenZ2pt);
        fChain->SetBranchAddress("e1_e2_Phi", &GenZ1Phi, &b_GenZ1Phi);
        fChain->SetBranchAddress("m1_m2_Phi", &GenZ2Phi, &b_GenZ2Phi);
        fChain->SetBranchAddress("e1Pt", &Genl1Pt, &b_Genl1Pt);
        fChain->SetBranchAddress("e2Pt", &Genl2Pt, &b_Genl2Pt);
        fChain->SetBranchAddress("m1Pt", &Genl3Pt, &b_Genl3Pt);
        fChain->SetBranchAddress("m2Pt", &Genl4Pt, &b_Genl4Pt);
        fChain->SetBranchAddress("e1Eta", &Genl1Eta, &b_Genl1Eta);
        fChain->SetBranchAddress("e2Eta", &Genl2Eta, &b_Genl2Eta);
        fChain->SetBranchAddress("m1Eta", &Genl3Eta, &b_Genl3Eta);
        fChain->SetBranchAddress("m2Eta", &Genl4Eta, &b_Genl4Eta);
        fChain->SetBranchAddress("e1Phi", &Genl1Phi, &b_Genl1Phi);
        fChain->SetBranchAddress("e2Phi", &Genl2Phi, &b_Genl2Phi);
        fChain->SetBranchAddress("m1Phi", &Genl3Phi, &b_Genl3Phi);
        fChain->SetBranchAddress("m2Phi", &Genl4Phi, &b_Genl4Phi);
    }
    else if (channel_ == mmmm) {
        fChain->SetBranchAddress("m1_m2_Mass", &GenZ1mass, &b_GenZ1mass);
        fChain->SetBranchAddress("m3_m4_Mass", &GenZ2mass, &b_GenZ2mass);
        fChain->SetBranchAddress("m1_m2_Pt", &GenZ1pt, &b_GenZ1pt);
        fChain->SetBranchAddress("m3_m4_Pt", &GenZ2pt, &b_GenZ2pt);
        fChain->SetBranchAddress("m1_m2_Phi", &GenZ1Phi, &b_GenZ1Phi);
        fChain->SetBranchAddress("m3_m4_Phi", &GenZ2Phi, &b_GenZ2Phi);
        fChain->SetBranchAddress("m1Pt", &Genl1Pt, &b_Genl1Pt);
        fChain->SetBranchAddress("m2Pt", &Genl2Pt, &b_Genl2Pt);
        fChain->SetBranchAddress("m3Pt", &Genl3Pt, &b_Genl3Pt);
        fChain->SetBranchAddress("m4Pt", &Genl4Pt, &b_Genl4Pt);
        fChain->SetBranchAddress("m1Eta", &Genl1Eta, &b_Genl1Eta);
        fChain->SetBranchAddress("m2Eta", &Genl2Eta, &b_Genl2Eta);
        fChain->SetBranchAddress("m3Eta", &Genl3Eta, &b_Genl3Eta);
        fChain->SetBranchAddress("m4Eta", &Genl4Eta, &b_Genl4Eta);
        fChain->SetBranchAddress("m1Phi", &Genl1Phi, &b_Genl1Phi);
        fChain->SetBranchAddress("m2Phi", &Genl2Phi, &b_Genl2Phi);
        fChain->SetBranchAddress("m3Phi", &Genl3Phi, &b_Genl3Phi);
        fChain->SetBranchAddress("m4Phi", &Genl4Phi, &b_Genl4Phi);
    }
    else
        throw std::invalid_argument("Invalid channel choice!");

    fChain->SetBranchAddress("Mass", &GenMass, &b_GenMass);
    fChain->SetBranchAddress("Pt", &GenPt, &b_GenPt);
    fChain->SetBranchAddress("Eta", &GenEta, &b_GenEta);
}

void ZZGenSelector::SetVariables(Long64_t entry) {
    if(!(e1e2IsZ1())){
      float tempMass = GenZ1mass;
      GenZ1mass = GenZ2mass;
      GenZ2mass = tempMass;
      float tempPt = GenZ1pt;
      GenZ1pt = GenZ2pt;
      GenZ2pt = tempPt;
      float templ1Pt = Genl1Pt;
      Genl1Pt = Genl3Pt;
      Genl3Pt = templ1Pt;
      float templ2Pt = Genl2Pt;
      Genl2Pt = Genl4Pt;
      Genl4Pt = templ2Pt;
      float templ1Eta = Genl1Eta;
      Genl1Eta = Genl3Eta;
      Genl3Eta = templ1Eta;
      float templ2Eta = Genl2Eta;
      Genl2Eta = Genl4Eta;
      Genl4Eta = templ2Eta;
      float templ1Phi = Genl1Phi;
      Genl1Phi = Genl3Phi;
      Genl3Phi = templ1Phi;
      float templ2Phi = Genl2Phi;
      Genl2Phi = Genl4Phi;
      Genl4Phi = templ2Phi;
    }
}
bool ZZGenSelector::ZZSelection() {
    if ((GenZ1mass > 60.0 && GenZ1mass < 120.0) && (GenZ2mass > 60.0 && GenZ2mass < 120.0))
        return true;
    else
        return false;
}
//We already require 4 < Z1,Z2 < 120  in the "Loose Skim"
bool ZZGenSelector::ZSelection() {
    if (GenZ1mass > 40.0 && GenZ2mass > 12.0)
        return true;
    else
        return false;
}
bool ZZGenSelector::Z4lSelection() {
    if (GenMass > 80.0 && GenMass < 100.0)
        return true;
    else
        return false;
}

bool ZZGenSelector::e1e2IsZ1(){
  return (std::abs(GenZ1mass-91.1876) < std::abs(GenZ2mass-91.1876));
}

void ZZGenSelector::FillHistograms(Long64_t entry, std::pair<Systematic, std::string> variation) {
    if (!ZZSelection())
        return;
    SafeHistFill(histMap1D_, getHistName("Genyield", variation.second), 1, Genweight);
    SafeHistFill(histMap1D_, getHistName("GenMass", variation.second), GenMass,Genweight);
    SafeHistFill(histMap1D_, getHistName("GenZMass", variation.second), GenZ1mass, Genweight);
    SafeHistFill(histMap1D_, getHistName("GenZMass", variation.second), GenZ2mass, Genweight);
    //Making LeptonPt and Eta plots
    SafeHistFill(histMap1D_, getHistName("GenLepPt", variation.second), Genl1Pt, Genweight);
    SafeHistFill(histMap1D_, getHistName("GenLepPt", variation.second), Genl2Pt, Genweight);
    SafeHistFill(histMap1D_, getHistName("GenLepPt", variation.second), Genl3Pt, Genweight);
    SafeHistFill(histMap1D_, getHistName("GenLepPt", variation.second), Genl4Pt, Genweight);
    SafeHistFill(histMap1D_, getHistName("GenLepEta", variation.second), Genl1Eta, Genweight);
    SafeHistFill(histMap1D_, getHistName("GenLepEta", variation.second), Genl2Eta, Genweight);
    SafeHistFill(histMap1D_, getHistName("GenLepEta", variation.second), Genl3Eta, Genweight);
    SafeHistFill(histMap1D_, getHistName("GenLepEta", variation.second), Genl4Eta, Genweight);
    // Summing 12,34 leptons
    SafeHistFill(histMap1D_, getHistName("GenLep12Pt", variation.second), Genl1Pt, Genweight);
    SafeHistFill(histMap1D_, getHistName("GenLep12Pt", variation.second), Genl2Pt, Genweight);
    SafeHistFill(histMap1D_, getHistName("GenLep34Pt", variation.second), Genl3Pt, Genweight);
    SafeHistFill(histMap1D_, getHistName("GenLep34Pt", variation.second), Genl4Pt, Genweight);
    SafeHistFill(histMap1D_, getHistName("GenLep12Eta", variation.second), Genl1Eta, Genweight);
    SafeHistFill(histMap1D_, getHistName("GenLep12Eta", variation.second), Genl2Eta, Genweight);
    SafeHistFill(histMap1D_, getHistName("GenLep34Eta", variation.second), Genl3Eta, Genweight);
    SafeHistFill(histMap1D_, getHistName("GenLep34Eta", variation.second), Genl4Eta, Genweight);
    SafeHistFill(histMap1D_, getHistName("GenZ1Mass", variation.second), GenZ1mass, Genweight);
    SafeHistFill(histMap1D_, getHistName("GenZ2Mass", variation.second), GenZ2mass, Genweight);
    SafeHistFill(histMap1D_, getHistName("GenZPt", variation.second), GenZ1pt, Genweight);
    SafeHistFill(histMap1D_, getHistName("GenZPt", variation.second), GenZ2pt, Genweight);
    SafeHistFill(histMap1D_, getHistName("GenZ1Pt", variation.second), GenZ1pt, Genweight);
    SafeHistFill(histMap1D_, getHistName("GenZ2Pt", variation.second), GenZ2pt, Genweight);
    SafeHistFill(histMap1D_, getHistName("GenZZPt", variation.second), GenPt, Genweight);
    SafeHistFill(histMap1D_, getHistName("GenZZEta", variation.second), GenEta, Genweight);
    SafeHistFill(histMap1D_, getHistName("GenZ1Phi", variation.second), GenZ1Phi, Genweight);
    SafeHistFill(histMap1D_, getHistName("GenZ2Phi", variation.second), GenZ2Phi, Genweight);
    SafeHistFill(histMap1D_, getHistName("GendPhiZ1Z2", variation.second), GendPhiZZ, Genweight);
    SafeHistFill(histMap1D_, getHistName("GenZ1lep1_Pt", variation.second), Genl1Pt, Genweight);
    SafeHistFill(histMap1D_, getHistName("GenZ1lep1_Eta", variation.second), Genl1Eta, Genweight);
    SafeHistFill(histMap1D_, getHistName("GenZ1lep1_Phi", variation.second), Genl1Phi, Genweight);
    SafeHistFill(histMap1D_, getHistName("GenZ1lep2_Pt", variation.second), Genl2Pt, Genweight);
    SafeHistFill(histMap1D_, getHistName("GenZ1lep2_Eta", variation.second), Genl2Eta, Genweight);
    SafeHistFill(histMap1D_, getHistName("GenZ1lep2_Phi", variation.second), Genl2Phi, Genweight);
    SafeHistFill(histMap1D_, getHistName("GenZ2lep1_Pt", variation.second), Genl3Pt, Genweight);
    SafeHistFill(histMap1D_, getHistName("GenZ2lep1_Eta", variation.second), Genl3Eta, Genweight);
    SafeHistFill(histMap1D_, getHistName("GenZ2lep1_Phi", variation.second), Genl3Phi, Genweight);
    SafeHistFill(histMap1D_, getHistName("GenZ2lep2_Pt", variation.second), Genl4Pt, Genweight);
    SafeHistFill(histMap1D_, getHistName("GenZ2lep2_Eta", variation.second), Genl4Eta, Genweight);
    SafeHistFill(histMap1D_, getHistName("GenZ2lep2_Phi", variation.second), Genl4Phi, Genweight);
    //2D Z1 vs Z2
    //SafeHistFill(hists2D_, getHistName("GenZ1Mass_GenZ2Mass", variation.second),GenZ1mass,GenZ2mass,Genweight);

}

void ZZGenSelector::SetupNewDirectory() {
    SelectorBase::SetupNewDirectory();

    InitializeHistogramsFromConfig();
}
