#### Run the following commands from the spack repo root directory

# Initialize Spack into shell (***remember to do the export's every time!!!***):
export SPACK_DISABLE_LOCAL_CONFIG=true
. share/spack/setup-env.sh
export SPACK_USER_CACHE_PATH=${SPACK_ROOT:?}/cache

#### One-time setup (nothing bad should happen if you re-run them though):
## Provide some extra stack validation commands:
git clone https://github.com/NOAA-EMC/spack-helpers
## Install Spack bootstrap bundle:
spack bootstrap now

#### Install an environment:
## IMPORTANT NOTES:
# - 'nco-core' env must be installed first, followed by nco-sci*, followed by any add-on's
# - The 'external' paths/hashes in the nco-sci* spack.yaml's that point to the nco-core installation will need to be updated based on the new installation path.
#
#
## Env set up/concretization.
# $ cd var/spack/environments/nco-core-gcc-11.5.0
# $ spack env activate .
# $ spack concretize
#
#
## Validate concretization. `spack validate` commands come from the spack-helpers extension.
#
## Check for duplicates; as of 05442a239a6508f1ce8a4b8cfc39a2ddffb9deb1, expected duplicates are fms, crtm, crtm-fix, py-cython:
# $ spack validate check-duplicates
#
## Take inventory of GCC-built packages in nco-sci* envs ('all' is a meaningless placeholder here);
## the only expected one as of 05442a239a6508f1ce8a4b8cfc39a2ddffb9deb1 is bison for oneapi:
# $ spack validate allow-pkgs-for-compiler gcc all
#
## Currently there is no up-to-date list of NCO-approved packages, but if someone creates one, then run:
# $ spack validate check-approved-pkgs --pkgs-from-file approved_packages.txt
#
#
## Installation.
# $ spack install --only-concrete --jobs 20
#
#
## Module files. These steps are only required for the add-on environments; `spack install` auto-generates module files, *except* the upstream packages for add-on environments.
## These commands apply the same configuration (common-config/modules.yaml) as what gets used in `spack install`.
# $ spack module lmod --name modules_flat refresh --upstream-modules
# $ spack module lmod --name with_mpi_hierarchy refresh --upstream-modules
