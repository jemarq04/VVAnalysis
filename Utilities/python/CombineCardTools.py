import logging
from . import ConfigureJobs
from . import HistTools
from . import OutputTools
from prettytable import PrettyTable
import os
import ROOT

class CombineCardTools(object):
    def __init__(self):
        self.fitVariable = ""
        self.fitVariableAppend = {}
        self.processes = []
        self.yields = {}
        self.histData = {}
        self.crossSectionMap = {}
        self.outputFile = ""
        self.templateName = ""
        self.channels = []
        self.variations = {}
        self.rebin = None
        self.isMC = True
        self.isUnrolledFit = False
        self.lumi = 1
        self.outputFolder = "."
        self.theoryVariations = {}

    def setPlotGroups(self, xsecMap):
        self.crossSectionMap = xsecMap

    def setRebin(self, rebin):
        self.rebin = rebin

    def setCrosSectionMap(self, xsecMap):
        self.crossSectionMap = xsecMap

    # Map of plot groups and members (individual processes)
    def setProcesses(self, processes):
        self.processes = processes

    def setFitVariableAppend(self, process, append):
        self.fitVariableAppend[process] = append

    def setFitVariable(self, variable):
        self.fitVariable = variable

    def setVariations(self, variations, exclude=[]):
        if not self.processes:
            raise ValueError("No processes defined, can't set variations")
        for process in list(self.processes.keys()):
            if process in exclude:
                self.setVariationsByProcess(process, [])
                continue
            self.setVariationsByProcess(process, variations)

    def getVariations(self):
        return self.variations

    def getVariationsForProcess(self, process):
        if process not in list(self.variations.keys()):
            raise ValueError("Variations not defined for process %s" % process)
        return self.variations[process]

    def setVariationsByProcess(self, process, variations):
        if "Up" not in variations and "Down" not in variations:
            variations = [x+y for x in variations for y in ["Up", "Down"]]
        self.variations[process] = variations

    def weightHistName(self, channel, process):
        fitVariable = self.getFitVariable(process)
        variable = fitVariable.replace("unrolled", "2D") if self.isUnrolledFit else fitVariable
        return "_".join([variable, "lheWeights", channel])

    def setLumi(self, lumi):
        self.lumi = lumi

    def setOutputFolder(self, outputFolder):
        self.outputFolder = outputFolder
        if not os.path.isdir(outputFolder):
            os.makedirs(outputFolder)

    def addTheoryVar(self, processName, varName, entries, central=0, exclude=[]):
        if "scale" not in varName.lower() and "pdf" not in varName.lower():
            raise ValueError("Invalid theory uncertainty %s. Must be type 'scale' or 'pdf'" % varName)
        name = "scale" if "scale" in varName.lower() else "pdf"

        if not processName in self.theoryVariations:
            self.theoryVariations[processName] = {}

        self.theoryVariations[processName].update({ name : {
                "entries" : entries,
                "central" : central,
                "exclude" : exclude,
                "combine" : "envelope" if name == "scale" else ("hessian" if "hessian" in varName else "mc"),
            }
        })

    def getRootFile(self, rtfile, mode=None):
        if type(rtfile) == str:
            if mode:
                return ROOT.TFile.Open(rtfile, mode)
            else:
                return ROOT.TFile.Open(rtfile)
        return rtfile

    def setTemplateFileName(self, templateName):
        self.templateName = templateName

    def setOutputFile(self, outputFile):
        #self.outputFile = self.getRootFile("/".join([self.outputFolder, outputFile]), "RECREATE")
        self.outputFile = self.getRootFile(outputFile, "RECREATE")

    def setInputFile(self, inputFile):
        self.inputFile = self.getRootFile(inputFile)

    def setChannels(self, channels):
        self.channels = channels
        for chan in self.channels + ["all"]:
            self.yields[chan] = {}

    def processHists(self, processName):
        return self.histData[processName] 

    def getFitVariable(self, process):
        if process not in self.fitVariableAppend:
            return self.fitVariable 
        return "_".join([self.fitVariable, self.fitVariableAppend[process]])

    def combineChannels(self, group, central=True):
        variations = self.variations[group.GetName()][:]
        fitVariable = self.getFitVariable(group.GetName())
        if central:
            variations.append("")
        for var in variations:
            # TODO: Remove these two replace statements, it's WZ/ZZ specific
            name = fitVariable if var == "" else "_".join([fitVariable, var])
            hist_name = name + "_" + self.channels[0]
            hist = group.FindObject(hist_name)
            if not hist:
                logging.warning("Failed to find hist %s in group %s. Skipping" % (hist_name, group.GetName()))
                continue
            hist = hist.Clone(name)
            ROOT.SetOwnership(hist, False)
            group.Add(hist) 
            for chan in self.channels[1:]:
                chan_hist = group.FindObject(name + "_" + chan)
                hist.Add(chan_hist)

    def listOfHistsByProcess(self, processName):
        if self.fitVariable == "":
            raise ValueError("Must declare fit variable before defining plots")
        fitVariable = self.getFitVariable(processName)
        plots = ["_".join([fitVariable, chan]) for chan in self.channels]
        variations = self.getVariationsForProcess(processName)
        plots += ["_".join([fitVariable, var, c]) for var in variations for c in self.channels]
        if processName in list(self.theoryVariations.keys()):
            plots += [self.weightHistName(c, processName) for c in self.channels]
        return plots

    # processName needs to match a PlotGroup 
    def loadHistsForProcess(self, processName, scaleNorm=1):
        plotsToRead = self.listOfHistsByProcess(processName)

        group = HistTools.makeCompositeHists(self.inputFile, processName, 
                    {proc : self.crossSectionMap[proc] for proc in self.processes[processName]}, 
                    self.lumi, plotsToRead, rebin=self.rebin, overflow=False)

        fitVariable = self.getFitVariable(processName)
        #TODO:Make optional
        processedHists = []
        for chan in self.channels:
            histName = "_".join([fitVariable, chan]) if chan != "all" else fitVariable
            hist = group.FindObject(histName)
            #TODO: Make optional
            if "data" not in processName.lower():
                HistTools.removeZeros(hist)
            HistTools.addOverflow(hist)
            processedHists.append(histName)
            self.yields[chan].update({processName : round(hist.Integral(), 4) if hist.Integral() > 0 else 0.0001})

            if chan == self.channels[0]:
                self.yields["all"][processName] = self.yields[chan][processName]
            else:
                self.yields["all"][processName] += self.yields[chan][processName]

            if processName in self.theoryVariations:
                weightHist = group.FindObject(self.weightHistName(chan, processName))
                if not weightHist:
                    logging.warning("Failed to find %s. Skipping" % self.weightHistName(chan, processName))
                    continue
                theoryVars = self.theoryVariations[processName]
                scaleHists = HistTools.getScaleHists(weightHist, processName, self.rebin, 
                        entries=theoryVars['scale']['entries'], central=theoryVars['scale']['central'])
                pdfFunction = getattr(HistTools, "get%sPDFVariationHists" % ("Hessian" if "hessian" in theoryVars['pdf']['combine'] else "MC"))
                pdfHists = pdfFunction(weightHist, theoryVars['pdf']['entries'], processName, 
                        self.rebin, central=theoryVars['pdf']['central'])
                group.extend(scaleHists+pdfHists)
        #TODO: You may want to combine channels before removing zeros
        self.combineChannels(group)
        #TODO: Make optional
        list(map(HistTools.addOverflow, [x for x in group if (x.GetName() not in processedHists)]))
        if "data" not in group.GetName().lower():
            list(map(HistTools.removeZeros, [x for x in group if (x.GetName() not in processedHists)]))
        self.histData[processName] = group

    # It's best to call this function for process, otherwise you can end up
    # storing many large histograms in memory
    def writeProcessHistsToOutput(self, processName):
        if processName not in list(self.histData.keys()) or not self.histData[processName]:
            raise ValueError("Hists for process %s not found" % processName)
        processHists = self.histData[processName]
        OutputTools.writeOutputListItem(processHists, self.outputFile)
        processHists.Delete()
        
    def writeCards(self, chan, nuisances, year="", extraArgs={}):
        chan_dict = self.yields[chan].copy()
        chan_dict.update(extraArgs)
        chan_dict["nuisances"] = nuisances
        chan_dict["fit_variable"] = self.fitVariable
        chan_dict["output_file"] = self.outputFile.GetName()
        outputCard = self.templateName.split("/")[-1].format(channel=chan, year=year) 
        outputCard = outputCard.replace("template", "")
        outputCard = outputCard.replace("__", "_")
        ConfigureJobs.fillTemplatedFile(self.templateName.format(channel=chan, year=year),
            "/".join([self.outputFolder, outputCard]),
            chan_dict
        )

