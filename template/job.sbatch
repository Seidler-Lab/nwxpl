#!/bin/csh -f
#SBATCH -N 1
#SBATCH --ntasks-per-node 36
#SBATCH -t 24:00:00
#SBATCH -A emsls51190
#SBATCH -o run.out
#SBATCH -e myjob.err
#SBATCH -J testjob
#SBATCH --export ALL
#SBATCH --mail-type=FAIL,END
#SBATCH --mail-user niri.govind@pnnl.gov

# Print out some information for refund purposes
############################################################################

echo "refund: UserID = niri"
echo "refund: SLURM Job ID = ${SLURM_JOBID}"
echo "refund: Number of nodes          = 2"
echo "refund: Number of cores per node = 36"
echo "refund: Number of cores          = 72"
echo "refund: Amount of time requested = 24:00"
echo "refund: Directory = ${PWD}"
echo " "
echo Processor list
echo " "
echo "${SLURM_JOB_NODELIST}"
echo " "

############################################################################

############################################################################
# Actually run the job
############################################################################

source /etc/profile.d/modules.csh
module purge
#setenv LD_LIBRARY_PATH /opt/rh/rh-python36/root/usr/lib64
module load intel/ips_20_u2
module load python/3.8.1
#module load impi/ips_18
#env. to get Intel MPI  and UCX information
setenv UCX_LOG_LEVEL WARN # [FATAL|ERROR|WARN|DIAG|INFO|DEBUG|TRACE
setenv I_MPI_DEBUG 1


setenv ARMCI_DEFAULT_SHMMAX 16384
setenv NWCHEM_BASIS_LIBRARY "/cluster/apps/nwchem/nwchem-7.0.1/src/basis/libraries/"
setenv NWCHEM_NWPW_LIBRARY "/cluster/apps/nwchem/nwchem-7.0.1/src/nwpw/libraryps/"
#this disables threaded in MKL since it is better to keep it to advanced users
setenv OMP_NUM_THREADS 1
setenv MKL_NUM_THREADS 1
setenv NWC_RANKS_PER_DEVICE 0
setenv ARMCI_OPENIB_DEVICE mlx5_0

setenv MPIRETURN 999
ldd  /tahoma/emsls51190/nwchem-exec/nwchem-7.0.2 
mpirun -n $SLURM_NPROCS  -ppn 36  /tahoma/emsls51190/nwchem-exec/nwchem-master input.nw
setenv MPIRETURN $?

############################################################################
# End of the job script
############################################################################

exit $MPIRETURN

