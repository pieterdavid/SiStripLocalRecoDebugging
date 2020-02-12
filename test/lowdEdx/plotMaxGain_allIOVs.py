#!/usr/bin/env python
import base64
import json
import subprocess
import os

def makePlot(plugin=None, db=None, dbTag=None, plot=None, begin=None, end=None, fileName=None):
    args = [
        "getPayloadData.py", "--plugin={0}".format(plugin), "--time_type=Run",
        "--db={0}".format(db), "--tag={0}".format(dbTag)
        ]
    args += [
        "--plot={0}".format(plot),
        "--iovs", '{{"start_iov": "{0}", "end_iov": "{1}"}}'.format(begin, end),
        "--suppress-output"
        ]
    out = subprocess.check_output(args)
    outP = json.loads(base64.b64decode(out))
    os.rename(outP["file"], fileName)

def getIOVsAndPayloads(db=None, dbTag=None, firstRun=None, lastRun=None):
    import subprocess
    out = subprocess.check_output(["conddb", "--noLimit", "--db={0}".format(db), "list", dbTag]).split("\n")[2:]
    iovs = [ (int(iovStart), plHash) for iovStart, date, time, plHash, obj in (ln.split() for ln in out if ln) if lastRun is None or int(iovStart) < lastRun ]
    if firstRun is not None:
        for i,(iS,plHash) in enumerate(iovs):
            if iS > firstRun:
                if i > 1:
                    iovs = iovs[i-1:]
                break
    return iovs

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Make gain payload plots using the payload inspector")
    parser.add_argument("--dbList", default="pro", help="Database to use, e.g. sqlite:mypayloads.db")
    parser.add_argument("--dbPI", default="frontier://PromptProd/CMS_CONDITIONS", help="Database to use, e.g. sqlite:mypayloads.db")
    parser.add_argument("--tag", default="SiStripApvGain", help="Tag inside the file that has the different payloads")
    parser.add_argument("--name", default="test", help="Unique part of the file names")
    parser.add_argument("--first", type=int, help="First run")
    parser.add_argument("--last", type=int, help="Last run")
    args = parser.parse_args()

    iovs = getIOVsAndPayloads(db=args.dbList, dbTag=args.tag, firstRun=args.first, lastRun=args.last)
    print("Found {0:d} IOVs for tag {1} from {2:d} to {3:d}".format(len(iovs), args.tag, args.first, args.last))
    for firstRun, plHash in iovs:
        print("Making plot for run {0:d} ({1})".format(firstRun, plHash))
        makePlot(plugin="pluginSiStripApvGain_PayloadInspector", db=args.dbPI, dbTag=args.tag, plot="plot_SiStripApvGainsMaximumTrackerMap",
                begin=firstRun, end=firstRun, fileName="{0}_{1:d}.png".format(args.name, firstRun))
