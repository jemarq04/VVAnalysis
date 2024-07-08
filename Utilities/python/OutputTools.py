import ROOT

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
