#!/usr/bin/env zsh

echo "---> Testing VR packing on 5 events"
for vrMode in "16" "8BOTBOT" "8TOPBOT" "10"; do
  cmsRun test/testPacker_fromVR.py "testVR=${vrMode}" nEvents=5
  grep -A2 SiStripRawDigiDiff "detailedInfo.log" | grep --color=never "Found" | uniq -c
done

echo "---> Testing ZS(lite) packing on 5 events"
for zsMode in "8" "8BOTBOT" "8TOPBOT" "10" "lite8" "lite8BOTBOT" "lite8TOPBOT" "lite10"; do
  cmsRun test/testPacker_fromVR.py "testZS=${zsMode}" nEvents=5
  grep -A2 SiStripDigiDiff "detailedInfo.log" | grep --color=never "Found"
done
