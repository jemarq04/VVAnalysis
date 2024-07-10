#!/usr/bin/env python3
import ROOT
import glob
import datetime
from . import ConfigureJobs

def writeOutputListItem(item, directory):
    if item.ClassName() == "TList":
        d = directory.Get(item.GetName())
        if not d:
            d = directory.mkdir(item.GetName())
            ROOT.SetOwnership(d, False)
        for subItem in item:
            writeOutputListItem(subItem, d)
    elif hasattr(item, 'Write'):
        directory.cd()
        item.Write()
    else:
        print("Couldn't write output item:")
        print(repr(item))
    directory.cd()

def applySelector(filelist, selector_name, selection, 
        rootfile,
        analysis="WZxsec2016", channels=["eee", "eem", "emm", "mmm"], 
        extra_inputs = [],
        addsumweights=False, proof=False):
    path = ConfigureJobs.getManagerPath()
    for dataset in ConfigureJobs.getListOfFiles(filelist, path, selection):
        for chan in channels:
            select = getattr(ROOT, selector_name)()
            inputs = ROOT.TList()
            select.SetInputList(inputs)
            tchan = ROOT.TNamed("channel", chan)
            tname = ROOT.TNamed("name", dataset)
            inputs.Add(tname)
            inputs.Add(tchan)
            for inp in extra_inputs:
                inputs.Add(inp)
            ROOT.gROOT.cd()
            sumweights_hist = 0
            if proof:
                proof_path = "_".join([dataset, analysis, 
                    selection+("#/%s/ntuple" % chan)])
                ROOT.gProof.Process(proof_path, select, "")
                proof_meta_path = "_".join([dataset, analysis, 
                    selection+"#/metaInfo/metaInfo"])
                ## TODO proof draw command for meta tree
                #proof.DrawSelect(proof_path, "1>>sumweights", "")
            else: 
                chain = ROOT.TChain("%s/ntuple" % chan)
                meta_chain = ROOT.TChain("metaInfo/metaInfo")
                try:
                    file_path = ConfigureJobs.getInputFilesPath(dataset, 
                        path, selection, analysis)
                    print("File path is", file_path)
                    chain.Add(file_path)
                    chain.Process(select, "")
                    if "data" not in dataset and addsumweights and chan == "eee":
                        sumweights_hist = ROOT.TH1D("sumweights", "sumweights", 1,0,100)
                        meta_chain.Add(file_path)
                        print(file_path)
                        meta_chain.Draw("1>>sumweights", "summedWeights")
                        if sumweights_hist.Integral() <= 0:
                            raise ValueError("Sum of weights <= 0 found for file"
                                    "%s. Probably the file is empty." % dataset)
                        sumweights_hist.SetDirectory(0)
                except ValueError as e:
                    print(e)
                    if sumweights_hist:
                        sumweights_hist.Delete()
                    continue
            output_list = select.GetOutputList()
            if  sumweights_hist:
                dataset_list = output_list.FindObject(dataset)
                dataset_list.Add(sumweights_hist)
            for out in output_list:
                writeOutputListItem(out, rootfile)
                if out.ClassName() == "TList":
                    out.SetOwner()
                    ROOT.SetOwnership(out, False)
                    out.Delete()

