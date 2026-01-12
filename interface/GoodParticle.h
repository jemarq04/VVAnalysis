#ifndef _GOOD_PARTICLE_H_
#define _GOOD_PARTICLE_H_

#include "helpers.h"
// Wrapper for lepton objects so to ignore problems with
// accessing data if particle is muon vs electron

struct GoodPart {
  LorentzVector v;
  int pdgId;

  GoodPart(double pt, double eta, double phi, double m) : v(pt, eta, phi, m) {}

  void SetPdgId(int pdg) { pdgId = pdg; }

  double Pt() { return v.Pt(); }
  double Eta() { return v.Eta(); }
  double Phi() { return v.Phi(); }

  int Charge() { return pdgId; }
  int Id() { return std::abs(pdgId); }
};

#endif
