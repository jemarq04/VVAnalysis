#include "Analysis/VVAnalysis/interface/FakeRateSelector.h"
#include "Analysis/VVAnalysis/interface/WZSelector.h"
#include "Analysis/VVAnalysis/interface/WZSelectorBase.h"
#include "Analysis/VVAnalysis/interface/WZBackgroundSelector.h"
#include "Analysis/VVAnalysis/interface/ScaleFactor.h"
#include "Analysis/VVAnalysis/interface/disambiguateFinalStates.h"
#include "Analysis/VVAnalysis/interface/disambiguateFinalStatesZL.h"

namespace{
  namespace{
    FakeRateSelector pFakeRateSelector;
    WZSelectorBase pWZSelectorBase;
    WZSelector pWZSelector;
    WZBackgroundSelector pWZBackgroundSelector;
    ScaleFactor pScaleFactor;
    disambiguateFinalStates pDisambiguator;
    disambiguateFinalStates pDisambiguatorZL;
  }
}
