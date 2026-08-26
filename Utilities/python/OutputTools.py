import ROOT


def writeOutputListItem(item, directory):
    if item.ClassName() == "TList":
        d = directory.Get(item.GetName())
        if not d:
            d = directory.mkdir(item.GetName())
            ROOT.SetOwnership(d, False)
        for subItem in item:
            writeOutputListItem(subItem, d)
    elif hasattr(item, "Write"):
        directory.cd()
        item.Write()
    else:
        print("Couldn't write output item:")
        print(repr(item))
    directory.cd()


def getHistsInDic(output_list, varList, channels):
    histsChanDic = {}
    exist = False
    for chan in channels:
        if chan == "eemm":
            # Loop over the variables for which we want unfolded distributions
            histsDic = {}
            for var in varList:
                exist = False
                # Items are the histograms that the HistTools function saves in a composite list
                for item in output_list:
                    # print "MCsubItem:",subItem.GetName()
                    if "Gen" in var:
                        itemName = var + "_" + chan + "Gen"
                    else:
                        itemName = var + "_" + chan
                    if item.GetName() == itemName:
                        exist = True
                        hist = item.Clone()
                        # Find _mmee hist as well
                        if "Gen" in var:
                            h2 = output_list.FindObject(var + "_mmeeGen")
                        else:
                            h2 = output_list.FindObject(var + "_mmee")
                        hist.Add(h2)
                        hist.SetDirectory(0)
                if not exist:
                    raise ValueError("Histogram not found:%s" % itemName)
                histsDic[var] = hist
            histsChanDic[chan] = histsDic
        else:
            # Loop over the variables for which we want unfolded distributions
            histsDic = {}
            for var in varList:
                exist = False
                # print "var:",var
                # Items are the histograms that the HistTools function saves in a composite list
                for item in output_list:
                    # print "MCsubItem:",item.GetName()
                    if "Gen" in var:
                        itemName = var + "_" + chan + "Gen"
                    else:
                        itemName = var + "_" + chan
                    if item.GetName() == itemName:
                        exist = True
                        hist = item.Clone()
                        hist.SetDirectory(0)
                if not exist:
                    raise ValueError("Histogram not found:%s" % itemName)
                histsDic[var] = hist
            histsChanDic[chan] = histsDic
    return histsChanDic
