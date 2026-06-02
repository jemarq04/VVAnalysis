files=(
  https://raw.githubusercontent.com/CJLST/ZZAnalysis/Run3/AnalysisStep/data/LeptonEffScaleFactors/SF2022eleID_preEE.root
  https://raw.githubusercontent.com/CJLST/ZZAnalysis/Run3/AnalysisStep/data/LeptonEffScaleFactors/SF2022eleID_postEE.root
  https://raw.githubusercontent.com/CJLST/ZZAnalysis/Run3/AnalysisStep/data/LeptonEffScaleFactors/SF2023eleID_preBPix.root
  https://raw.githubusercontent.com/CJLST/ZZAnalysis/Run3/AnalysisStep/data/LeptonEffScaleFactors/SF2023eleID_Gap_preBPix.root
  https://raw.githubusercontent.com/CJLST/ZZAnalysis/Run3/AnalysisStep/data/LeptonEffScaleFactors/SF2023eleID_postBPix.root
  https://raw.githubusercontent.com/CJLST/ZZAnalysis/Run3/AnalysisStep/data/LeptonEffScaleFactors/SF2023eleID_postBPix_Hole.root
  https://raw.githubusercontent.com/CJLST/ZZAnalysis/Run3/AnalysisStep/data/LeptonEffScaleFactors/SF2024eleID.root
  https://raw.githubusercontent.com/CJLST/ZZAnalysis/Run3/AnalysisStep/data/LeptonEffScaleFactors/SF2024eleID_Gap.root
  https://raw.githubusercontent.com/CJLST/ZZAnalysis/Run3/AnalysisStep/data/LeptonEffScaleFactors/final_HZZ_SF_Run3_2022_mupogsysts_newLoose_abseta3_fix_BCD_RMS.root
  https://raw.githubusercontent.com/CJLST/ZZAnalysis/Run3/AnalysisStep/data/LeptonEffScaleFactors/final_HZZ_SF_Run3_2022_mupogsysts_newLoose_abseta3_fix_EFG_RMS.root
  https://raw.githubusercontent.com/CJLST/ZZAnalysis/Run3/AnalysisStep/data/LeptonEffScaleFactors/final_HZZ_SF_2023C_RMS_mupogsysts.root
  https://raw.githubusercontent.com/CJLST/ZZAnalysis/Run3/AnalysisStep/data/LeptonEffScaleFactors/final_HZZ_SF_2023D_RMS_mupogsysts.root
  https://raw.githubusercontent.com/CJLST/ZZAnalysis/Run3/AnalysisStep/data/LeptonEffScaleFactors/HZZ_HZZ_SF_2024_RMS_mupogsystsC.root
)

for yr in 2022 2023 2024; do
  mkdir -p inputs/$yr
  for f in "${files[@]}"; do
    [[ ! ${f##*\/} = *$yr* ]] && continue
    curl --create-dirs --output-dir "inputs/$yr" -O $f
  done
done
