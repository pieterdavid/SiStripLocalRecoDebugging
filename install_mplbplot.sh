# no shebang, must be sourced

## based on Sebastien Brochet's install-tensorflow.sh script in cp3-llbb/HHTools)

## deduce source location from the script name
if [[ -z "${ZSH_NAME}" ]]; then
  thisscript="$(readlink -f ${BASH_SOURCE})"
else
  thisscript="$(readlink -f ${0})"
fi
pipinstall="$(dirname ${thisscript})/.python"

# Check if in CMSSW
if [ -z "$CMSSW_BASE" ]; then
  echo "You must use this package inside a CMSSW environment"
  return 1
fi
pymajmin=$(python -c 'import sys; print(".".join(str(num) for num in sys.version_info[:2]))')
if [[ "${pymajmin}" != "2.7" ]]; then
  echo "--> Only python 2.7 is supported"
  return 1
fi

# Check if it is already installed
scram tool info mplbplot > /dev/null 2> /dev/null
if [ $? -eq 0 ]; then
  echo "--> already installed (according to scram)"
  return 0
fi

# First, download and install pip, if needed
bk_pythonpath="${PYTHONPATH}"
python -m pip --version > /dev/null 2> /dev/null
if [ $? -ne 0 ]; then
  echo "--> No pip found, bootstrapping in ${pipinstall}"
  [ -d "${pipinstall}" ] || mkdir "${pipinstall}"
  if [ ! -f "${pipinstall}/bin/pip" ]; then
    wget -O "${pipinstall}/get-pip.py" "https://bootstrap.pypa.io/get-pip.py"
    python "${pipinstall}/get-pip.py" --prefix="${pipinstall}" --no-setuptools
  fi
  export PYTHONPATH="${pipinstall}/lib/python${pymajmin}/site-packages:${PYTHONPATH}"
fi

## install dependencies
installpath="${CMSSW_BASE}/install/mplbplot"
echo "--> Installing mplbplot"
python -m pip install --prefix="${installpath}" git+https://github.com/pieterdavid/mplbplot.git

# root_interface toolfile
toolfile="${installpath}/mplbplot.xml"
cat <<EOF_TOOLFILE >"${toolfile}"
<tool name="mplbplot" version="0.0.1">
  <info url="https://github.com/pieterdavid/mplbplot"/>
  <client>
    <environment name="MPLBPLOT_BASE" default="${installpath}"/>
    <runtime name="PYTHONPATH" value="\$MPLBPLOT_BASE/lib/python${pymajmin}/site-packages" type="path"/>
  </client>
</tool>
EOF_TOOLFILE

## cleanup
rm -rf "${pipinstall}"
export PYTHONPATH="${bk_pythonpath}"

echo "--> Updating environment"
scram setup "${toolfile}"
cmsenv

echo "--> mplbplot dependencies are installed"
