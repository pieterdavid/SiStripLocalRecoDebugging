#!/usr/bin/env zsh
firstruns_run2ultralegacy=("260332" "271952" "274602" "275567" "277194" "278820" "279360" "279596" "282024" "283043" "283647" "285368" "298430" "302322" "305040" "306054" "313120" "317244" "320824" "321475" "323790")
local logfile="log_Run2UL_combined.txt"
for runNumber in $firstruns_run2ultralegacy; do
  echo "\nChecking for values above 3 in G2 payload for run ${runNumber}" >> $logfile
  cmsRun printSiStripGain.py globalTag=106X_dataRun2_2017_2018_Candidate_2019_12_02_18_57_30 run=${runNumber} | grep -v '^%MSG' >> $logfile
done
