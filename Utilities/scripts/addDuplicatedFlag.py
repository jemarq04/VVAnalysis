#!/usr/bin/env python3
import ROOT
import argparse
import os
from array import array

def eventsbyChannel(setList):
    #print "Number of not deduplicated events in all datasets", len(events)
    print("Number of events in eeee ntuple", len(setList[0]))
    print("Number of events in eemm ntuple", len(setList[1]))
    print("Number of events in mmmm ntuple", len(setList[2]))

def getEventScore(original_file):
    states = ['eeee', 'eemm','mmmm']
    #events is a list of the three sets event_%state
    events=[]
    events_eeee = set()
    events_eemm = set()
    events_mmmm = set()
    #events_score is a list of the following dictionaries
    events_score=[]
    event_score_eeee={}
    event_score_eemm={}
    event_score_mmmm={}
    for state in states:
        tree = original_file.Get("%s/ntuple" % state)
        if state.count('e') > 2:
            for i in tree:
                score=[]
                mass_discriminant=abs(i.e1_e2_Mass-91.1876)
                Z2PtSum = (i.e3Pt + i.e4Pt)
                score.append(mass_discriminant)
                score.append(Z2PtSum)
                events_eeee.add('{0}:{1}:{2}'.format(i.run,i.lumi,i.evt))
                event_score_eeee.update({'{0}:{1}:{2}'.format(i.run,i.lumi,i.evt) :score})
        elif state.count('m') > 2:
            for i in tree:
                score=[]
                mass_discriminant=abs(i.m1_m2_Mass-91.1876)
                Z2PtSum = (i.m3Pt + i.m4Pt)
                score.append(mass_discriminant)
                score.append(Z2PtSum)
                events_mmmm.add('{0}:{1}:{2}'.format(i.run,i.lumi,i.evt))
                event_score_mmmm.update({'{0}:{1}:{2}'.format(i.run,i.lumi,i.evt) :score})
        else:
            for i in tree:
                score=[]
                if(abs(i.e1_e2_Mass-91.1876) < abs(i.m1_m2_Mass-91.1876)):
                    mass_discriminant=abs(i.e1_e2_Mass-91.1876)
                    Z2PtSum = (i.m1Pt + i.m2Pt)
                else: 
                    mass_discriminant=abs(i.m1_m2_Mass-91.1876)
                    Z2PtSum = (i.e1Pt + i.e2Pt)
                score.append(mass_discriminant)
                score.append(Z2PtSum)
                events_eemm.add('{0}:{1}:{2}'.format(i.run,i.lumi,i.evt))
                event_score_eemm.update({'{0}:{1}:{2}'.format(i.run,i.lumi,i.evt) :score})
    #append here to preserve the order where 0th element -> eeee, 1st element -> eemm, 2nd element -> mmmmm
    events.append(events_eeee)
    events.append(events_eemm)
    events.append(events_mmmm)
    events_score.append(event_score_eeee)
    events_score.append(event_score_eemm)
    events_score.append(event_score_mmmm)
    return events,events_score

def getSetIntersections(setList):
    SetIntersectionList=[]
    ab = set.intersection(setList[0],setList[1])
    bc = set.intersection(setList[1],setList[2]) 
    ac = set.intersection(setList[0],setList[2])
    SetIntersectionList.append(ab)
    SetIntersectionList.append(bc)
    SetIntersectionList.append(ac)
    return SetIntersectionList

#flagduplicates function calls a list of dictionaries events_score, events(list of sets to be modified) and SetIntersectionList
def flagduplicates(IntersectionList,dictList):
    eeee_flag=[] 
    eemm_flag=[]
    mmmm_flag=[]
    FlaggedEventsList=[]
    eeee_eemm = IntersectionList[0]
    eemm_mmmm = IntersectionList[1]
    event_score_eeee = dictList[0]
    event_score_eemm = dictList[1]
    event_score_mmmm = dictList[2]
    if(len(eeee_eemm) > 0):
        #use i as the key to get the "score" list in the relevant dictionaries
        #mass_discriminant = score[0], Z2PtSum = score[1]
        for i in eeee_eemm:
            #print i
            #print "event_score_eee[massdiscriminant]: ", event_score_eeee[i][0]
            #print "event_score_eeee[Z2PtSum]: ", event_score_eeee[i][1]
            #print "event_score_eemm[massdiscriminant]: ", event_score_eemm[i][0]
            #print "event_score_eemm[Z2PtSum]: ", event_score_eemm[i][1]
            if((event_score_eeee[i][0] < event_score_eemm[i][0]) or ((event_score_eeee[i][0] == event_score_eemm[i][0]) and (event_score_eeee[i][1] > event_score_eemm[i][1]))):
                eemm_flag.append(i)
            else:
                eeee_flag.append(i) 
    if(len(eemm_mmmm) > 0):
        #use i as the key to get the "score" list in the relevant dictionaries
        #mass_discriminant = score[0], Z2PtSum = score[1]
        for i in eemm_mmmm:
            if((event_score_eemm[i][0] < event_score_mmmm[i][0]) or ((event_score_eemm[i][0] == event_score_mmmm[i][0]) and (event_score_eemm[i][1] > event_score_mmmm[i][1]))):
                mmmm_flag.append(i)
            else:
                eemm_flag.append(i)
    FlaggedEventsList.append(eeee_flag)
    FlaggedEventsList.append(eemm_flag)
    FlaggedEventsList.append(mmmm_flag)
    return FlaggedEventsList

#Takes original_file as input to get the tree for each state
#Also takes "FlaggedEvents" List of lists for each final state. This list is a result of flagduplicates function
#For now, looping over the tree a second time seems to be the only option
#If an event is in a channel where it shouldn't be, its flagged "duplicated=1" otherwise this flag is always zero
def addDuplicationFlag(original_file,state,FlaggedEvents):
    tree = original_file.Get("%s/ntuple" % state)
    tree.SetBranchStatus("*", 0)
    Flag = array('i',[0])
    Flag_branch = tree.Branch('duplicated', Flag, 'duplicated/I')
    tree.SetBranchStatus("duplicated",1)
    #print "No.of events flagged from eeee: ",len(FlaggedEventList[0])
    #print FlaggedEventList[0]
    if (state == "eeee" and len(FlaggedEvents[0])>0):
        tree.SetBranchStatus("run",1)
        tree.SetBranchStatus("lumi",1)
        tree.SetBranchStatus("evt",1)
        for i in tree:
            eventString='{0}:{1}:{2}'.format(i.run,i.lumi,i.evt)
            if eventString in FlaggedEvents[0]:
                #print eventString
                Flag[0]=1
                Flag_branch.Fill()
            else:
                Flag[0]=0
                Flag_branch.Fill()
    #print "No.of events flagged from eemm: ",len(FlaggedEventList[1])
    #print FlaggedEventList[1]
    if (state == "eemm" and len(FlaggedEvents[1])>0):
        tree.SetBranchStatus("run",1)
        tree.SetBranchStatus("lumi",1)
        tree.SetBranchStatus("evt",1)
        for i in tree:
            eventString='{0}:{1}:{2}'.format(i.run,i.lumi,i.evt)
            if eventString in FlaggedEvents[1]:
                Flag[0]=1
                Flag_branch.Fill()
            else:
                Flag[0]=0
                Flag_branch.Fill()
    #print "No.of events flagged from mmmm: ",len(FlaggedEventList[2])
    #print FlaggedEventList[2]
    if (state == "mmmm" and len(FlaggedEvents[2])>0):
        tree.SetBranchStatus("run",1)
        tree.SetBranchStatus("lumi",1)
        tree.SetBranchStatus("evt",1)
        for i in tree:
            eventString='{0}:{1}:{2}'.format(i.run,i.lumi,i.evt)
            if eventString in FlaggedEvents[2]:
                Flag[0]=1
                Flag_branch.Fill()
            else:
                Flag[0]=0
                Flag_branch.Fill()
    tree.SetBranchStatus("*", 1)
    original_file.cd(state)
    tree.Write("", ROOT.TObject.kOverwrite)


parser= argparse.ArgumentParser()
parser.add_argument("-f", "--input_file", required=True)
args = parser.parse_args()


original_file = ROOT.TFile(args.input_file, "UPDATE")

events,events_score = getEventScore(original_file)
#eeee_eemm,eemm_mmmm,eeee_mmmm => SetIntersectionList[0],[1],[2] respectively
IntersectionList = getSetIntersections(events) 
eventsbyChannel(events)
print("No.of events in eeee_eemm intersection: ",len(IntersectionList[0]))
print("No.of events in eemm_mmmm intersection: ",len(IntersectionList[1]))
print("No.of events in eeee_mmmm intersection: ",len(IntersectionList[2]))
#Apply flagduplicates function
#FinalEventList is a list of 3 sets containining unique events corresponding to the three states
FlaggedEventList = flagduplicates(IntersectionList,events_score)
print("No.of events flagged from eeee: ",len(FlaggedEventList[0]))
print(FlaggedEventList[0])
print("No.of events flagged from eemm: ",len(FlaggedEventList[1]))
#print FlaggedEventList[1]
print("No.of events flagged from mmmm: ",len(FlaggedEventList[2]))
print(FlaggedEventList[2])

states = ['eeee', 'eemm','mmmm']
for state in states:
    addDuplicationFlag(original_file, state,FlaggedEventList)
