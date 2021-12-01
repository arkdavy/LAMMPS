#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=3850
#SBATCH --time=24:00:00
#SBATCH --account=suXXX

# remove system-wide modules
module purge

ebversion='4.5.0'

# point the MODULEPATH to the local EB installation locations
export EASYBUILD_PREFIX=${HOME}/easybuild-$ebversion
export MODULEPATH=${EASYBUILD_PREFIX}/modules/Core

# load the local easybuild installation
module load EasyBuild/$ebversion

# install lammps with dependencies
eb $1 --robot --robot-path=`pwd`:$EB_ROBOT_PATH --rebuild 
