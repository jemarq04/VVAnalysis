#!/usr/bin/env python
import ROOT
from collections import OrderedDict
from . import ConfigureJobs
import os
import sys
from . import UserInput
import time

class CutString(object):
    def __init__(self):
        self.cuts = []
    def append(self, append):
        if self.cuts not in ["", None] and append not in ["", None]:
            self.cuts += append if isinstance(append, list) else [append]
    def contains(self, cut):
        return any(cut in x for x in self.cuts)
    def getString(self):
        return " && ".join(self.cuts)

def buildCutString(state, selections, analysis, trigger):
    cut_string = CutString()
    for selection in selections:
        selection_json = ConfigureJobs.getCutsJsonName(selection, analysis)
        cuts = UserInput.readInfo(selection_json)
        cut_string.append(cuts["Event"])
        cut_string.append(cuts["State"][state])
        if trigger != "":
            trigger_string = getTriggerCutString(trigger, analysis)
            if not cut_string.contains(trigger_string):
                cut_string.append(trigger_string)
        counts = dict((lep, state.count(lep)) for lep in state)
        current = dict((lep, 0) for lep in state)
        for lep in state:
            current[lep] += 1
            lep_name = ''.join([lep, "" if counts[lep] == 1 else str(current[lep])])
            for cut in cuts["Object"][lep]:
                cut_string.append(cut.format(object_name=lep_name))
    return cut_string
def setAliases(tree, state, aliases_json):
    aliases = UserInput.readInfo(aliases_json)
    for name, value in aliases["State"][state].items():
        tree.SetAlias(name, value)
    for name, value in aliases["Event"].items():
        tree.SetAlias(name, value)
def getTriggerCutString(trigger, analysis):
    triggers = UserInput.readInfo("Cuts/%s/triggers.json" % analysis)
    return triggers[trigger]
def applySelection(tree, state, selection, analysis, trigger):
    setAliases(tree, state, "Cuts/aliases.json")
    cut_string = buildCutString(state, analysis, selection, trigger)
    #tree.SetProof()
    listname = '_'.join(["list", state])
    num_passing = tree.Draw(">>" + listname, cut_string.getString(), "entrylist")
    #tlist = ROOT.gProof.GetOutputList().FindObject(listname) 
    tlist = ROOT.gDirectory.FindObject(listname);
    tree.SetEntryList(tlist)
