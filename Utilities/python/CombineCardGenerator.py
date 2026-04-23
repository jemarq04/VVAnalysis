import os
import json
import array
from typing import Union, Optional

import ROOT
from . import ConfigureJobs
from . import HistTools
from . import OutputTools


class Systematic:
    def __init__(self, name: str, shape: bool = False):
        self.name = name
        self.shape = shape

        self.systematics = {}

    def AddProcesses(self, values: dict):
        self.systematics.update(values)


class Process:
    def __init__(self, name: str, channels: list = None):
        if channels is None:
            channels = []
        self.name = name
        self.yields = dict.fromkeys(channels + ["all"], 0)

        self.variations = []

        self.members = []
        self.xsecs = []

    def AddVariations(self, name: str):
        if all(name + var not in self.variations for var in ["Up", "Down"]):
            self.variations += [name + var for var in ["Up", "Down"]]

    def LoadXSecs(self):
        self.xsecs = ConfigureJobs.getListOfFilesWithXSec(self.members)


class CombineCardGenerator:
    def __init__(
        self,
        analysis: str,
        fit_variable: str,
        hist_infile: Union[str, ROOT.TFile],
        sig_procs: list,
        bkg_procs: list,
        channels: Optional[list] = None,
        lumi: Optional[float] = None,
        auto_stats: Optional[float] = None,
        add_overflow: bool = False,
    ):
        if channels is None:
            channels = []
        self.analysis = analysis
        self.lumi = lumi

        self.channels = channels  # refer to eeee,eemm,mmee,mmmm (NOT Combine channels)
        self.all_channels = ["eeee", "eemm", "mmee", "mmmm"]

        self.hist_infile = self._GetFile(hist_infile)
        self.hist_data = {}
        self.fit_variable = fit_variable

        self.data = {"data": Process("data", self.all_channels)}
        self.sig_procs = {proc: Process(proc, self.all_channels) for proc in sig_procs}
        self.bkg_procs = {proc: Process(proc, self.all_channels) for proc in bkg_procs}
        # if "data" not in bkg_procs:
        #    self.bkg_procs.append(Process("data", channels))
        self.systematics = {ch: [] for ch in channels + ["all"]}

        self.longest_procname = 0
        for procname in list(self.sig_procs.keys()) + list(self.bkg_procs.keys()):
            if len(procname) > self.longest_procname:
                self.longest_procname = len(procname)

        self.auto_stats = auto_stats
        self.add_overflow = add_overflow

    def _GetFile(self, file: Union[str, ROOT.TFile]):
        if isinstance(file, str):
            return ROOT.TFile.Open(file)
        elif isinstance(file, ROOT.TFile):
            return file
        else:
            raise ValueError

    def AddSystematics(self, name: str, values: dict, channel: str = "all", shape: bool = False):
        """
        Adds systematics to the processes.

        Args:
            name (str):
                name of systematic (e.g. CMS_eff_e)
            values (dict(str: str)):
                values of the systematics for a given process name
                (e.g. {"ggZZ": "1.025", "VVV": "-"})
            channel (str):
                specifies the channel this systematic should apply to
                (default: all)
            shape (bool):
                marks this systematic as 'shape' type
                (default: False)
        """

        if not isinstance(values, dict):
            raise ValueError("expected dict, got %s" % type(values))

        for procname in list(self.sig_procs.keys()) + list(self.bkg_procs.keys()):
            if procname not in values:
                values[procname] = "-" if not shape else "0"

        syst = Systematic(name, shape)
        syst.AddProcesses(values)
        self.systematics[channel].append(syst)
        if channel == "all":
            for ch in self.channels:
                if all(name != syst.name for syst in self.systematics[ch]):
                    self.systematics[ch].append(syst)
        elif all(name != syst.name for syst in self.systematics["all"]):
            self.systematics["all"].append(syst)
        if shape:
            for procs in [self.sig_procs, self.bkg_procs]:
                for procname in procs:
                    if values[procname] != "-":
                        procs[procname].AddVariations(name)
            self.has_shape_type = True

    def _LoadHistInfo(self, rebin: Optional[list]):
        # Access plot groups
        manager_path = ConfigureJobs.getManagerPath()
        manager_name = ConfigureJobs.getManagerName()
        plot_groups = {}
        filename = "%s/%s/PlotGroups/%s.json" % (manager_path, manager_name, self.analysis)
        try:
            with open(filename) as json_file:
                plot_groups = json.load(json_file)
        except ValueError as err:
            raise ValueError(f"cannot find file {filename}. error was {err}") from err

        for procs in [self.sig_procs, self.bkg_procs, self.data]:
            for procname in procs:
                # Get plot group members
                if procname in plot_groups:
                    procs[procname].members += plot_groups[procname]["Members"]
                else:
                    print(f"process {procname} not found in {filename}")
                    continue

                # Get plot group xsecs
                procs[procname].LoadXSecs()

                # Get yields from ALL channels
                plotnames = ["_".join([self.fit_variable, chan]) for chan in self.all_channels]
                plotnames += [
                    "_".join([self.fit_variable, var, chan])
                    for var in procs[procname].variations
                    for chan in self.all_channels
                ]
                group = HistTools.makeCompositeHists(
                    self.hist_infile,
                    procname,
                    procs[procname].xsecs,
                    self.lumi,
                    hists=plotnames,
                    overflow=self.add_overflow,
                    rebin=array.array("d", rebin) if rebin is not None else None,
                )
                self.hist_data[procname] = group

                for chan in self.all_channels:
                    histname = "_".join([self.fit_variable, chan])
                    hist = group.FindObject(histname)
                    if "data" not in procname.lower():
                        HistTools.removeZeros(hist)

                    procs[procname].yields[chan] += round(hist.Integral(), 4)  # if hist.Integral() > 0 else 0.0001
                    procs[procname].yields["all"] += procs[procname].yields[chan]

    def _WriteHists(self, outdir: str):
        with ROOT.TFile.Open(f"{outdir}/{self.analysis}.root", "RECREATE") as hist_outfile:
            summed_hists = {"AllMC": ROOT.TList()}
            summed_hists["AllMC"].SetName("AllMC")
            for procs in [self.sig_procs, self.bkg_procs, self.data]:
                for procname in procs:
                    hists = self.hist_data[procname]
                    if procname not in summed_hists:
                        summed_hists[procname] = ROOT.TList()
                        summed_hists[procname].SetName(procname)
                    for h in hists:
                        if procname != "data":
                            sumhist = summed_hists["AllMC"].FindObject(h.GetName())
                            if sumhist:
                                sumhist.Add(h)
                            else:
                                summed_hists["AllMC"].Add(h.Clone())

                        histname = "_".join(h.GetName().split("_")[:-1])
                        sumhist = summed_hists[procname].FindObject(histname)
                        if sumhist:
                            sumhist.Add(h)
                        else:
                            summed_hists[procname].Add(h.Clone(histname))

                    OutputTools.writeOutputListItem(hists, hist_outfile)
                    hists.Delete()

            for procs in [self.sig_procs, self.bkg_procs, self.data]:
                for procname in procs:
                    hists = summed_hists[procname]
                    OutputTools.writeOutputListItem(hists, hist_outfile)
                    hists.Delete()

            hists = summed_hists["AllMC"]
            OutputTools.writeOutputListItem(hists, hist_outfile)
            hists.Delete()

    def GenerateCards(self, outdir: str, rebin: Optional[list]):
        if not os.path.isdir(outdir):
            raise ValueError("invalid directory: %s" % outdir)

        self._LoadHistInfo(rebin)
        self._WriteHists(outdir)

        # Print card for each requested channel
        for chan in ["all"] + self.channels:
            with open("%s/%s_%s.txt" % (outdir, self.analysis, chan), "w") as outfile:
                # Card header
                outfile.write(f"# With input file {self.hist_infile.GetName()}\n")
                outfile.write("imax 1  number of channels\n")
                outfile.write(
                    f"jmax {len(self.sig_procs) + len(self.bkg_procs) - 1:<2d} number of backgrounds plus signals minus 1\n"
                )
                outfile.write("kmax *  number of nuisance parameters (sources of systematical uncertainties)\n")
                outfile.write("------------\n\n")

                # Defining shape uncertainties
                fit_variable_name = self.fit_variable + (f"_{chan}" if chan != "all" else "")
                fit_variable_name_syst = f"{self.fit_variable}_$SYSTEMATIC" + (f"_{chan}" if chan != "all" else "")
                for procname, proc in self.sig_procs.items():
                    if proc.variations:
                        outfile.write(f"shapes {procname:<{self.longest_procname}} * {outdir}/{self.analysis}.root ")
                        outfile.write(
                            f"{procname + '/' + fit_variable_name:<{self.longest_procname + 1 + len(fit_variable_name)}}  "
                        )
                        outfile.write(f"{procname}/{fit_variable_name_syst}\n")
                for procname, proc in self.bkg_procs.items():
                    if proc.variations:
                        outfile.write(f"shapes {procname:<{self.longest_procname}} * {outdir}/{self.analysis}.root ")
                        outfile.write(
                            f"{procname + '/' + fit_variable_name:<{self.longest_procname + 1 + len(fit_variable_name)}}  "
                        )
                        outfile.write(f"{procname}/{fit_variable_name_syst}\n")
                if self.has_shape_type:
                    outfile.write("\n")
                outfile.write(
                    f"shapes {'data_obs':<{self.longest_procname}} * {outdir}/{self.analysis}.root data/{fit_variable_name}\n\n"
                )
                outfile.write("------------\n\n")
                outfile.write(f"bin         {chan}\n")
                outfile.write(f"observation {self.data['data'].yields[chan]}\n\n")
                outfile.write("------------\n\n")

                # Begin systematics table
                numcols = 2 + len(self.sig_procs) + len(self.bkg_procs)
                headers = []
                headers.append(["bin", ""] + [chan] * (numcols - 2))
                headers.append(["process", ""] + list(self.sig_procs.keys()) + list(self.bkg_procs.keys()))
                headers.append(
                    ["process", ""]
                    + [str(num) for num in range(1 - len(self.sig_procs), 1)]
                    + [str(num + 1) for num in range(len(self.bkg_procs))]
                )
                headers.append(
                    ["rate", ""]
                    + ["%.4f" % proc.yields[chan] for proc in self.sig_procs.values()]
                    + ["%.4f" % proc.yields[chan] for proc in self.bkg_procs.values()]
                )

                table = []
                for syst in self.systematics[chan]:
                    table.append(
                        [syst.name, "shape" if syst.shape else "lnN"]
                        + [syst.systematics[procname] for procname in self.sig_procs]
                        + [syst.systematics[procname] for procname in self.bkg_procs]
                    )

                longest_cells = [0] * numcols
                for row in headers + table:
                    for i in range(numcols):
                        if len(row[i]) > longest_cells[i]:
                            longest_cells[i] = len(row[i])
                longest_cells[0] += 5

                # Print table
                for row in headers:
                    for i in range(numcols):
                        outfile.write(f"{row[i]:<{longest_cells[i]}}    ")
                    outfile.write("\n")
                outfile.write(f"{'-' * (sum(longest_cells) + 4 * len(longest_cells))}\n\n")
                for row in table:
                    for i in range(numcols):
                        outfile.write(f"{row[i]:<{longest_cells[i]}}    ")
                    outfile.write("\n")

                if self.auto_stats is not None:
                    outfile.write(f"\n* autoMCStats {self.auto_stats}\n")

    def __del__(self):
        if self.hist_infile:
            self.hist_infile.Close()
