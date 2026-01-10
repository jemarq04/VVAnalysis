#ifndef FakeRateSelector_h
#define FakeRateSelector_h

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>
#include <TH1.h>
#include <TH2.h>
#include <exception>
#include <iostream>

// Headers needed by this particular selector
#include "Analysis/VVAnalysis/interface/ZZSelectorBase.h"
#include <vector>


class FakeRateSelector : public ZZSelectorBase {
public :
    TH2D* passingTightE2D_;
    TH1D* passingTightE1DPt_barrel_;
    TH1D* passingTightE1DPt_endcap_;
    TH1D* passingTightE1DEta_;
    TH2D* passingLooseE2D_;
    TH1D* passingLooseE1DPt_barrel_;
    TH1D* passingLooseE1DPt_endcap_;
    TH1D* passingLooseE1DEta_;
    TH2D* ratioE2D_;
    TH1D* ratioE1DPt_barrel_;
    TH1D* ratioE1DPt_endcap_;
    TH1D* ratioE1DEta_;

    TH2D* passingTightMu2D_;
    TH1D* passingTightMu1DPt_barrel_;
    TH1D* passingTightMu1DPt_endcap_;
    TH1D* passingTightMu1DEta_;
    TH2D* passingLooseMu2D_;
    TH1D* passingLooseMu1DPt_barrel_;
    TH1D* passingLooseMu1DPt_endcap_;
    TH1D* passingLooseMu1DEta_;
    TH2D* ratioMu2D_;
    TH1D* ratioMu1DPt_barrel_;
    TH1D* ratioMu1DPt_endcap_;
    TH1D* ratioMu1DEta_;
    TH2D* passingTight2D_;
    TH1D* passingTight1DPt_barrel_;
    TH1D* passingTight1DPt_endcap_;
    TH1D* passingTight1DEta_;
    TH2D* passingLoose2D_;
    TH1D* passingLoose1DPt_barrel_;
    TH1D* passingLoose1DPt_endcap_;
    TH1D* passingLoose1DEta_;
    TH2D* ratio2D_;
    TH1D* ratio1DPt_barrel_;
    TH1D* ratio1DPt_endcap_;
    TH1D* ratio1DEta_;

    virtual void    Init(TTree *tree) override;
    virtual void    SetupNewDirectory() override;
    //virtual void    FillHistograms(Long64_t entry, std::pair<Systematic, std::string> variation) override;
    ClassDefOverride(FakeRateSelector,0);

private:
    void    LoadBranchesUWVV(Long64_t entry, std::pair<Systematic, std::string> variation) override;


};

#endif
