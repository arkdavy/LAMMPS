#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=3850
#SBATCH --time=24:00:00
#SBATCH --account=suXXX

# remove system-wide modules
module purge

# taken from Dugan's wiki, repeated here, valid for intel, MKL from 2019b
# https://bugzilla.csc.warwick.ac.uk/bugzilla/show_bug.cgi?id=15359
export EASYBUILD_OPTARCH="Intel:march=core-avx2; GCC:march=native"
export MKL_DEBUG_CPU_TYPE=5
export MKL_CBWR=COMPATIBLE

ebversion='4.5.0'

# point the MODULEPATH to the local EB installation locations
export EASYBUILD_PREFIX=${HOME}/easybuild-$ebversion
export MODULEPATH=${EASYBUILD_PREFIX}/modules/Core

# licensing server
export INTEL_LICENSE_FILE=

# for VTK compilation with intel, visit: https://gitlab.kitware.com/vtk/vtk/-/issues/17974
export DCMAKE_EXE_LINKER_FLAGS="-shared-intel"

# load the local easybuild installation
module load EasyBuild/$ebversion

# install SciPy separately, ignoring failing tests (check the easyconfig to see what test fail, or read the installation log)
eb SciPy-bundle-2019.10-iomkl-2019b.eb --robot --robot-path=`pwd`/easyconfigs:$EB_ROBOT_PATH --ignore-test-failure


# install lammps with dependencies
eb $1 --robot --robot-path=`pwd`/easyconfigs:$EB_ROBOT_PATH --include-easyblocks=`pwd`/../easyblocks/*.py --rebuild
