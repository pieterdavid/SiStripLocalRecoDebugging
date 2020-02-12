#!/usr/bin/env zsh
runs_2016Legacy=("260332" "271952" "274602" "275567" "279360" "279596" "282024" "283043" "283647")
for runNumber in $runs_2016Legacy; do
  cmsRun printSiStripGain.py globalTag=80X_dataRun2_2016LegacyRepro_v4 run=${runNumber} | grep -v '^%MSG' > log_2016Legacy_${runNumber}.txt
done

runs_2017EOY=("285368" "298430" "302322" "305040" "306054")
for runNumber in $runs_2017EOY; do
  cmsRun printSiStripGain.py globalTag=94X_dataRun2_ReReco_EOY17_v2 run=${runNumber} | grep -v '^%MSG' > log_2017EOY_${runNumber}.txt
done

runs_2018ABCrereco=("313120" "317244")
for runNumber in $runs_2018ABCrereco; do
  cmsRun printSiStripGain.py globalTag=102X_dataRun2_Sep2018Rereco_v1 run=${runNumber} | grep -v '^%MSG' > log_2018ABCRereco_${runNumber}.txt
done
runs_2018Dprompt=("317975" "320994" "322051" "324063")
for runNumber in $runs_2018Dprompt; do
  cmsRun printSiStripGain.py globalTag=102X_dataRun2_Prompt_v15 run=${runNumber} | grep -v '^%MSG' > log_2018DPrompt_${runNumber}.txt
done
