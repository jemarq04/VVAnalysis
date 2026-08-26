#ifndef NanoGenSelectorBase_h
#define NanoGenSelectorBase_h

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
#include "Analysis/VVAnalysis/interface/ScaleFactor.h"
#include "Analysis/VVAnalysis/interface/SelectorBase.h"
#include "DataFormats/HepMCCandidate/interface/GenParticle.h"
#include "Analysis/VVAnalysis/interface/helpers.h"

class NanoGenSelectorBase : public SelectorBase {
public :
    // Derived values
    reco::GenParticleCollection leptons;
    reco::GenParticleCollection neutrinos;
    std::vector<LorentzVector> jets;
    LorentzVector genMet;

    unsigned int nLeptons_ = 1;
    static const unsigned int N_KEEP_GEN_ = 150;
    static const unsigned int N_KEEP_JET_ = 30;
    float weight;
    // Values read from file
    Float_t genWeight;
    UInt_t nGenPart;
    Float_t GenPart_pt[N_KEEP_GEN_];
    Float_t GenPart_eta[N_KEEP_GEN_];
    Float_t GenPart_phi[N_KEEP_GEN_];
    Float_t GenPart_mass[N_KEEP_GEN_];
    Int_t GenPart_status[N_KEEP_GEN_];
    Int_t GenPart_pdgId[N_KEEP_GEN_];
    UInt_t nGenJet;
    Float_t GenJet_pt[N_KEEP_GEN_];
    Float_t GenJet_eta[N_KEEP_GEN_];
    Float_t GenJet_phi[N_KEEP_GEN_];
    Float_t GenJet_mass[N_KEEP_GEN_];
    Float_t GenMET_pt;
    Float_t GenMET_phi;

    TBranch* b_genWeight;
    TBranch* b_nGenPart;
    TBranch* b_GenPart_pt;
    TBranch* b_GenPart_eta;
    TBranch* b_GenPart_phi;
    TBranch* b_GenPart_mass;
    TBranch* b_GenPart_status;
    TBranch* b_GenPart_pdgId;
    TBranch* b_nGenJet;
    TBranch* b_GenJet_pt;
    TBranch* b_GenJet_eta;
    TBranch* b_GenJet_phi;
    TBranch* b_GenJet_mass;
    TBranch* b_GenJet_status;
    TBranch* b_GenMET_pt;
    TBranch* b_GenMET_phi;

    // Readers to access the data (delete the ones you do not need).
    virtual void    Init(TTree *tree) override;
    NanoGenSelectorBase(TTree * /*tree*/ =0) { }
    ~NanoGenSelectorBase() { }
    virtual void    SetupNewDirectory() override;

    ClassDefOverride(NanoGenSelectorBase,0);

protected:
    virtual void    SetBranchesNanoAOD() override;
    virtual void    FillHistograms(Long64_t entry, std::pair<Systematic, std::string> variation) override {}
    void LoadBranchesNanoAOD(Long64_t entry, std::pair<Systematic, std::string> variation) override;
    virtual void SetComposite() {}
    bool overlapsCollection(const LorentzVector& cand, reco::GenParticleCollection& collection, const float deltaRCut, size_t maxCompare);
};

#endif
