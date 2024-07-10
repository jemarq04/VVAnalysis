#!/usr/bin/env python3
import ROOT
import argparse
import os
from array import array

def addWeightsForState(original_file, state):
    tree = original_file.Get("%s/ntuple" % state)
    tree.SetBranchStatus("*", 0)
    if state == "eee":
        leps = ["e1", "e2", "e3"]
    elif state == "eem":
        leps = ["e1", "e2", "m"]
        mTightIso_weight = array('f', [0])
        mTightIso_branch = tree.Branch('mTightIsoSF', mTightIso_weight, 'mTightIsoSF/F') 
        tree.SetBranchStatus("mTightIsoSF", 1)
    elif state == "emm":
        leps = ["e", "m1", "m2"]
        m1TightIso_weight = array('f', [0])
        m1TightIso_branch = tree.Branch('m1TightIsoSF', m1TightIso_weight, 'm1TightIsoSF/F') 
        tree.SetBranchStatus("m1TightIsoSF", 1)
        m2TightIso_weight = array('f', [0])
        m2TightIso_branch = tree.Branch('m2TightIsoSF', m2TightIso_weight, 'm2TightIsoSF/F') 
        tree.SetBranchStatus("m2TightIsoSF", 1)
    elif state == "mmm":
        leps = ["m1", "m2", "m3"]
        m1TightIso_weight = array('f', [0])
        m1TightIso_branch = tree.Branch('m1TightIsoSF', m1TightIso_weight, 'm1TightIsoSF/F') 
        tree.SetBranchStatus("m1TightIsoSF", 1)
        m2TightIso_weight = array('f', [0])
        m2TightIso_branch = tree.Branch('m2TightIsoSF', m2TightIso_weight, 'm2TightIsoSF/F') 
        tree.SetBranchStatus("m2TightIsoSF", 1)
        m3TightIso_weight = array('f', [0])
        m3TightIso_branch = tree.Branch('m3TightIsoSF', m3TightIso_weight, 'm3TightIsoSF/F') 
        tree.SetBranchStatus("m3TightIsoSF", 1)
    else:
        print("That don't work :(")
        exit(1)
    pileup_weight = array('f', [0])
    pileup_branch = tree.Branch('pileupSF', pileup_weight, 'pileupSF/F') 
    tree.SetBranchStatus("pileupSF", 1)

    lepTightId_weights = [array('f', [0]), array('f', [0]), array('f', [0])]
    lepTightId_branches = []
    lepMediumId_weights = [array('f', [0]), array('f', [0]), array('f', [0])]
    lepMediumId_branches = []
    tree.SetBranchStatus("pileupSF", 1)
    tree.SetBranchStatus("nTruePU", 1)
    for i, lep in enumerate(leps):
        lepTightId_branches.append(tree.Branch('%sTightIDSF' % lep, lepTightId_weights[i], '%sTightIDSF/F' % lep)) 
        lepMediumId_branches.append(tree.Branch('%sMediumIDSF' % lep, lepMediumId_weights[i], '%sMediumIDSF/F' % lep)) 
        tree.SetBranchStatus("%sPt" % lep, 1)
        tree.SetBranchStatus("%sEta" % lep, 1)
        tree.SetBranchStatus("%sTightIDSF" % lep, 1)
        tree.SetBranchStatus("%sTightIDSF" % lep, 1)
    for entry in range(tree.GetEntries()):
        tree.GetEntry(entry)
        for i, lep in enumerate(leps):
            pt = getattr(tree, "%sPt" % lep)
            absEta = abs(getattr(tree, "%sEta" % lep))
            if "e" in lep:
                lepTightId_weights[i][0] = ROOT.electronTightIdSF(absEta, pt)
                lepMediumId_weights[i][0] = ROOT.electronMedIdSF(absEta, pt)
            else: 
                lepTightId_weights[i][0] = ROOT.muonTightIdSF(absEta, pt)
                lepMediumId_weights[i][0] = ROOT.muonMedIdSF(absEta, pt)
            lepTightId_branches[i].Fill()
            lepMediumId_branches[i].Fill()
        pileup_weight[0] = ROOT.pileupSF(tree.nTruePU)
        pileup_branch.Fill()
        if state == "eem":
            mTightIso_weight[0] = ROOT.muonTightIsoSF(
                abs(tree.mEta), tree.mPt)
            mTightIso_branch.Fill()
        elif state == "emm":
            m1TightIso_weight[0] = ROOT.muonTightIsoSF(
                abs(tree.m1Eta), tree.m1Pt)
            m1TightIso_branch.Fill()
            m2TightIso_weight[0] = ROOT.muonTightIsoSF(
                abs(tree.m2Eta), tree.m2Pt)
            m2TightIso_branch.Fill()
        elif state == "mmm":
            m1TightIso_weight[0] = ROOT.muonTightIsoSF(
                abs(tree.m1Eta), tree.m1Pt)
            m1TightIso_branch.Fill()
            m2TightIso_weight[0] = ROOT.muonTightIsoSF(
                abs(tree.m2Eta), tree.m2Pt)
            m2TightIso_branch.Fill()
            m3TightIso_weight[0] = ROOT.muonTightIsoSF(
                abs(tree.m3Eta), tree.m3Pt)
            m3TightIso_branch.Fill()
    tree.SetBranchStatus("*", 1)
    original_file.cd(state)
    tree.Write("", ROOT.TObject.kOverwrite)

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--input_file", required=True)
args = parser.parse_args()

file_path = os.path.dirname(os.path.realpath(__file__))
scalefac_path = "/".join([file_path, "../../ScaleFactors"])
ROOT.gROOT.LoadMacro("/".join([scalefac_path, "ScaleFactor.C+"]))
fScales = ROOT.TFile("/".join([scalefac_path, "scaleFactors.root"]))

pileupSF = fScales.Get('pileupSF')
muonTightIsoSF = fScales.Get('muonTightIsoSF')
muonTightIdSF = fScales.Get('muonTightIdSF')
muonMedIdSF = fScales.Get('muonMedIdSF')
electronTightIdSF = fScales.Get('electronTightIdSF')
electronMedIdSF = fScales.Get('electronMedIdSF')

pileupSF.RegisterGlobalFunction(1) #1D function
muonTightIsoSF.RegisterGlobalFunction(2) # 2D function
muonTightIdSF.RegisterGlobalFunction(2) # 2D function
muonMedIdSF.RegisterGlobalFunction(2) # 2D function
electronTightIdSF.RegisterGlobalFunction(2) # 2D function
electronMedIdSF.RegisterGlobalFunction(2) # 2D function

original_file = ROOT.TFile(args.input_file, "UPDATE")

states = ['eee', 'eem', 'emm', 'mmm']
for state in states:
    addWeightsForState(original_file, state)

