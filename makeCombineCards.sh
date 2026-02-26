echo 2022
python3 Utilities/scripts/setupZZCombineRun3.py -i HistFiles/Hists24Feb2026-ZZ4l2022.root -o CombineCards --rebin 100,200,250,300,350,400,500,600,800,1000 -c eeee,eemm,mmee,mmmm -a ZZ4l2022 2022

echo 2023
python3 Utilities/scripts/setupZZCombineRun3.py -i HistFiles/Hists25Feb2026-ZZ4l2023.root -o CombineCards --rebin 100,200,250,300,350,400,500,600,800,1000 -c eeee,eemm,mmee,mmmm -a ZZ4l2023 2023

echo 2024
python3 Utilities/scripts/setupZZCombineRun3.py -i HistFiles/Hists25Feb2026-ZZ4l2024.root -o CombineCards --rebin 100,200,250,300,350,400,500,600,800,1000 -c eeee,eemm,mmee,mmmm -a ZZ4l2024 2024
