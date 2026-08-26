#include <string>
#include <sstream>

#include <algorithm>
#include <iterator>

#define SSTR( x ) static_cast< std::ostringstream & >( \
        ( std::ostringstream() << std::dec << x ) ).str()

#include <TError.h>
#include <TMath.h>
#include <TCanvas.h>
#include <TRandom3.h>
#include <TFitter.h>
#include <TF1.h>
#include <TStyle.h>
#include <TVector.h>
#include <TGraph.h>
#include <TFile.h>
#include <TLegend.h>
#include <TProfile.h>
//#include "RooUnfoldResponse.h"
#include "TUnfoldDensity.h"

// #define VERBOSE_LCURVE_SCAN

using namespace std;


TRandom *rnd=0;

TH2 *gHistInvEMatrix;

TVirtualFitter *gFitter=0;

void divideByBinWidth(TH1* hist) {
  for(Int_t i=1; i<=hist->GetNbinsX(); i++) {
     hist->SetBinContent(i,hist->GetBinContent(i)/hist->GetBinWidth(i));
     hist->SetBinError(i,hist->GetBinError(i)/hist->GetBinWidth(i));
  }
}
void normalize(TH1* hist) {
  hist->Scale(1./hist->Integral());
}

int testUnfold0Toys(TString input = "nominal", int nToys = 100)
{
  gErrorIgnoreLevel = kError;

  // switch on histogram errors
  TH1::SetDefaultSumw2();

  // show fit result
  gStyle->SetOptFit(1111);

  gSystem->Load("RooUnfold/libRooUnfold");
  // Viridis palette reversed + white
  //stops = array('d', [0.0, 0.05, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0000])
  //red   = array('d', [26./255., 51./255.,  43./255.,  33./255.,  28./255.,  35./255.,  74./255., 144./255., 246./255., 1., 1.])
  //std::reverse(std::begin(arr), std::end(arr));
  //green = array('d', [9./255., 24./255.,  55./255.,  87./255., 118./255., 150./255., 180./255., 200./255., 222./255., 1., 1.])
  //blue  = array('d', [30./255., 96./255., 112./255., 114./255., 112./255., 101./255.,  72./255.,  35./255.,   0./255., 1., 1.])
  //ROOT.TColor.CreateGradientColorTable(11, stops, red[::-1], green[::-1], blue[::-1], 255)

  const Int_t Number = 11;
  Double_t Red[Number]    = { 26./255., 51./255.,  43./255.,  33./255.,  28./255.,  35./255.,  74./255., 144./255., 246./255., 1., 1. };
  std::reverse(std::begin(Red), std::end(Red));
  Double_t Green[Number]  = { 9./255., 24./255.,  55./255.,  87./255., 118./255., 150./255., 180./255., 200./255., 222./255., 1., 1. };
  std::reverse(std::begin(Green), std::end(Green));
  Double_t Blue[Number]   = { 30./255., 96./255., 112./255., 114./255., 112./255., 101./255.,  72./255.,  35./255.,   0./255., 1., 1. };
  std::reverse(std::begin(Blue), std::end(Blue));
  Double_t Length[Number] = { 0.0, 0.05, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0 };
  TColor::CreateGradientColorTable(Number,Length,Red,Green,Blue, 255);

  //============================================
  // generate MC distribution
  //
  TFile file("PowResponseMatrix-16Mar2020-ZZ4l2016_drz1z2.root", "READ");

  TH2D *histMdetGenMC = (TH2D*) file.Get(input);
  TH1D *histMgenMC = histMdetGenMC->ProjectionX();
  //histMgenMC->Scale(1./histMgenMC->Integral());
  TH1D *histMdetMC = histMdetGenMC->ProjectionY();
  //histMdetMC->Scale(1./histMdetMC->Integral());
  TH1D* histMdetMCsig = histMdetGenMC->ProjectionY("histMdetNonGenMC", 1, -1);
  TH2D* histMdetGenMCSig = (TH2D*) histMdetGenMC->Clone("histMdetGenMCSig");

  std::cout<<"GenIntegral: "<<histMgenMC->Integral(0,10)<<std::endl;
  std::cout<<"RecoIntegral: "<<histMdetMC->Integral(0,10)<<std::endl;
  bool reg = false;
  if (reg) input = input + "_reg";

  input = input + "_drz1z2";

  double lumi = 1; // fb^{-1}
  double dataMCSF = lumi;
  histMgenMC->Scale(dataMCSF);
  histMdetMC->Scale(dataMCSF);
  histMdetMCsig->Scale(dataMCSF);

  double integral = histMdetGenMC->Integral(0,-1,0,-1);
  std::cout << "integral: " << integral << std::endl;
  //double nExpectedEvents = integral*lumi*832.;
  double nExpectedEvents = integral*lumi*100;
  std::vector<double> wheel = { 0. };
  for (int i = 0; i < histMdetGenMC->GetNcells()+1; ++i) {
    //std::cout << wheel.back() << std::endl;
    wheel.push_back(wheel.back() + histMdetGenMC->GetBinContent(i));
  }

  //histMdetGenMC->Scale(1./histMdetGenMC->Integral());
  //histMdetGenMC->Scale(1000000.);

  //Set non-reco bins to 0
  //for (int i = 0; i < histMdetGenMCSig->GetNbinsX()+2; ++i) histMdetGenMCSig->SetBinContent(i, 0, 0.);
  //Set non-gen bins to 0
  //for (int i = 0; i < histMdetGenMCSig->GetNbinsY()+2; ++i) histMdetGenMCSig->SetBinContent(0, i, 0.);
  //Set non-reco non-gen bin to 0
  //histMdetGenMC->SetBinContent(0, 0, 36500000.);

  RooUnfoldResponse* response = new RooUnfoldResponse(histMdetMC,histMgenMC,histMdetGenMCSig);


  TRandom3 random(1);

  TH2F* hPull = new TH2F("pull", "pull;bin;pull", histMgenMC->GetNbinsX(), 0.5, histMgenMC->GetNbinsX()+0.5, 50, -5, 5);
  TProfile* hUnc = new TProfile("unc", "Relative uncertainty;bin;Relative uncertainty", histMgenMC->GetNbinsX(), 0.5, histMgenMC->GetNbinsX()+0.5);
  TProfile* hBias = new TProfile("bias", "Relative bias;bin;Relative bias", histMgenMC->GetNbinsX(), 0.5, histMgenMC->GetNbinsX()+0.5);
  std::vector<std::vector<double> > pseudoresults;

  TFile outfile("toys/"+input+"_toys.root", "RECREATE");

  for (int t = 0; t < nToys; ++t) {
    if(t%int(nToys/100)==0) std::cout << "toy number " << t << "/" << nToys << std::endl;
    //============================================
    // generate toy distribution
    //
    TH2D* histMdetGenToy = (TH2D*) histMdetGenMC->Clone("histMdetGenToy");
    histMdetGenToy->Scale(dataMCSF);
    histMdetGenToy->Reset();

    int drawn = 0;
    while (drawn < nExpectedEvents) {
      double pick = random.Uniform(integral);
      //std::cout << pick << ":";
      auto low = std::lower_bound(wheel.begin(), wheel.end(), pick);
      int position = low - wheel.begin() - 1;
      //std::cout << position << " ";
      //int position = -1;
      //for (unsigned int i = 0; i < wheel.size(); ++i) {
      //  if (pick < wheel[i]) break;
      //  ++position;
      //}
      //std::cout << position << " ";
      histMdetGenToy->SetBinContent(position, histMdetGenToy->GetBinContent(position) + 1);
      ++drawn;
    }
    for (int i = 0; i < histMdetGenToy->GetNcells()+2; ++i) {
      histMdetGenToy->SetBinError(i, sqrt(histMdetGenToy->GetBinContent(i)));
    }
    //histMdetGenToy->FillRandom(histMdetGenMC, nExpectedEvents);

    TH1D *histMdetData = histMdetGenToy->ProjectionY("histMdetData");
    TH1D *histMgenToy = histMdetGenToy->ProjectionX("histMgenToy");

    //double dataMCSF = 36500.; //histMdetData->Integral()/histMdetMC->Integral();
    //dataMCSF = histMdetData->Integral()/histMdetMC->Integral()*100;
    //dataMCSF = 100000.;

    //if (not DATA) {
    //  histMdetData->Scale(dataMCSF*832.); // For MC test
    //}
    //histMdetData->Scale(100.);
    //histMdetData->SetBinContent(0, 0.);

    //for (int i = 0; i < histMdetData->GetNbinsX()+2; ++i) cout << histMdetData->GetBinContent(i) << " +/- " << histMdetData->GetBinError(i) << endl;

    //for (int i = 0; i < histMdetNonGenMC->GetNbinsX()+2; ++i) cout << histMdetNonGenMC->GetBinContent(i)*dataMCSF << endl;

    // backgrounds
    TH1D *histMdetDataBGSubtracted = (TH1D*) histMdetData->Clone();

    TH1D *histMdetNonGenMCbkg = histMdetGenMC->ProjectionY("histMdetNonGenMCbkg", 0, 0);
    TH1D *histMdetNonGenMCall = histMdetGenMC->ProjectionY("histMdetNonGenMCall");
    //double SF = histMdetDataBGSubtracted->Integral(1, -1) * histMdetNonGenMCall->Integral(1,-1);
    //std::cout << "SF=" << SF << std::endl;
    //histMdetDataBGSubtracted->Add(histMdetNonGenMCbkg, -SF*832.);
    //*
    for (int i = 0; i < histMdetDataBGSubtracted->GetNbinsX()+2; ++i) {
      double sf = histMdetNonGenMCbkg->GetBinContent(i) / histMdetNonGenMCall->GetBinContent(i);
      histMdetDataBGSubtracted->SetBinContent(i, (1.-sf)*histMdetDataBGSubtracted->GetBinContent(i));
      if (std::isnan(histMdetDataBGSubtracted->GetBinContent(i)))
        histMdetDataBGSubtracted->SetBinContent(i, 0);
      histMdetDataBGSubtracted->SetBinError(i, (1.-sf)*histMdetDataBGSubtracted->GetBinError(i));
      if (std::isnan(histMdetDataBGSubtracted->GetBinError(i)))
        histMdetDataBGSubtracted->SetBinError(i, 0);

    }
    //*/
    /*
    for (auto background : backgrounds) {
      TFile bkgfile(basepath+background.first, "READ");
      TH2D *histMdetGenMCbkg = (TH2D*) bkgfile.Get(observable+"_"+flavor+"_responsematrix");
      TH1D *histMdetNonGenMCbkg = histMdetGenMCbkg->ProjectionY("histMdetNonGenMCbkg_"+background.first, 0, 0);
      histMdetDataBGSubtracted->Add(histMdetNonGenMCbkg, -dataMCSF);
    }
    //*/
    //for (int i = 0; i < histMdetDataBGSubtracted->GetNbinsX()+2; ++i) {
    //  std::cout << histMdetDataBGSubtracted->GetBinContent(i) << " +/- " << histMdetDataBGSubtracted->GetBinError(i) << std::endl;
    //}



    //histMdetData->SetBinContent(0, 1000000.);


    //=========================================================================
    // set up the unfolding
    // define migration matrix
    //TUnfold::ERegMode regMode = TUnfold::kRegModeCurvature;
    //TUnfold::EConstraint constraint = TUnfold::kEConstraintArea;
    //TUnfoldDensity::EDensityMode densityFlags=TUnfoldDensity::kDensityModeBinWidth;
    //
    //TUnfoldDensity unfold(histMdetGenMCSig,TUnfold::kHistMapOutputHoriz,regMode,constraint,densityFlags);
    RooUnfoldInvert unfold(response,histMdetDataBGSubtracted);
    // define input and bias scame
    // do not use the bias, because MC peak may be at the wrong place
    // watch out for error codes returned by the SetInput method
    // errors larger or equal 10000 are fatal:
    // the data points specified as input are not sufficient to constrain the
    // unfolding process/
   // if(unfold.SetInput(histMdetDataBGSubtracted)>=10000) {
   //   std::cout<<"Unfolding result may be wrong\n";
   // }

   // //========================================================================
   // // the unfolding is done here
   // //
   // // scan L curve and find best point
   //
   // double opt_tau = 0;
   // if (reg && histMdetGenMCSig->GetNbinsX() > 2) {
   //   Int_t nScan=100;
   //   Double_t tauMin=1e-10;
   //   Double_t tauMax=1e-3;
   //   unfold.ScanLcurve(nScan, tauMin, tauMax, 0);
   //   opt_tau = unfold.GetTau();
   // }

    //==========================================================================
    // retreive results into histograms

    //unfold.DoUnfold(0.);
    //unfold.DoUnfold(opt_tau);

    outfile.cd();
    //TH1 *histMunfold=unfold.GetOutput((std::string("Unfolded_")+std::to_string(t)).c_str());
    TH1D* histMunfold= (TH1D*) unfold.Hreco();
    histMunfold->Write();

    for (int i = 1; i < histMunfold->GetNbinsX()+1; ++i) {
      double pull = (histMunfold->GetBinContent(i) - histMgenToy->GetBinContent(i)) / histMunfold->GetBinError(i); // sqrt(pow(histMunfold->GetBinError(i), 2) + pow(histMgenToy->GetBinError(i), 2));
      //std::cout << histMgenMC->GetBinContent(i) << std::endl;
      hPull->Fill(i, pull);
      double relUnc = histMunfold->GetBinError(i) / histMunfold->GetBinContent(i);
      hUnc->Fill(i, relUnc);
      double relBias = (histMunfold->GetBinContent(i) - histMgenToy->GetBinContent(i)) / histMgenToy->GetBinContent(i);
      hBias->Fill(i, relBias);
    }

    std::vector<double> pseudoresult;
    double integral = 0.;
    for (int i = 1; i < histMunfold->GetNbinsX()+1; ++i) {
      pseudoresult.push_back(histMunfold->GetBinContent(i));
      integral += histMunfold->GetBinContent(i);
    }
    for (int i = 0; i < histMunfold->GetNbinsX(); ++i) {
      pseudoresult[i] = pseudoresult[i]/integral;
    }
    pseudoresults.push_back(pseudoresult);
  }


  //=====================================================================
  // plot some histograms
  TCanvas output("output","output",500,500);
  output.cd();

  hPull->FitSlicesY();
  TH1D *pull_1 = (TH1D*) gDirectory->Get("pull_1");
  pull_1->GetYaxis()->SetRangeUser(-1.,1.);
  pull_1->Fit("pol0");

  output.SaveAs("toys/"+input+"_pull_mean.pdf");
  output.SaveAs("toys/"+input+"_pull_mean.png");
  output.SaveAs("toys/"+input+"_pull_mean.root");

  TH1D *pull_2 = (TH1D*) gDirectory->Get("pull_2");
  pull_2->GetYaxis()->SetRangeUser(0.,2.);
  pull_2->Fit("pol0");

  output.SaveAs("toys/"+input+"_pull_width.pdf");
  output.SaveAs("toys/"+input+"_pull_width.png");
  output.SaveAs("toys/"+input+"_pull_width.root");

  for (int i = 0; i < pull_1->GetNbinsX()+2; ++i) {
    pull_1->SetBinError(i, pull_2->GetBinContent(i));
  }

  hPull->Draw("colz");
  pull_1->SetLineColor(kWhite);
  pull_1->SetMarkerColor(kWhite);
  pull_1->SetLineWidth(4);
  pull_1->Draw("e1,same");

  output.SaveAs("toys/"+input+"_pull.pdf");
  output.SaveAs("toys/"+input+"_pull.png");
  output.SaveAs("toys/"+input+"_pull.root");

  output.SetLeftMargin(0.15);
  hUnc->Draw("");
  output.SaveAs("toys/"+input+"_relUncertainty.pdf");
  output.SaveAs("toys/"+input+"_relUncertainty.png");
  output.SaveAs("toys/"+input+"_relUncertainty.root");

  hBias->Draw("");
  output.SaveAs("toys/"+input+"_relBias.pdf");
  output.SaveAs("toys/"+input+"_relBias.png");
  output.SaveAs("toys/"+input+"_relBias.root");

  /*
  vector<vector<double>> pseudoresults_T;
  for (unsigned int i = 0; i < pseudoresults[0].size(); i++) {
    std::vector<double> column;
    for (unsigned int j = 0; j < pseudoresults.size(); j++) {
      column.push_back(pseudoresults[j][i]);
    }
    pseudoresults_T.push_back(column);
  }
  vector<vector<double>> cov = compute_covariance_matrix(pseudoresults_T);
  */

  return 0;
}
