# Install NIMBUS test stack

## Notes
- There are some commented-out packages in the spack.yaml's; these are ones I wasn't sure whether to including based on looking at prod {build,run}.ver's.
- xml-fortran = libxmlparse on WCOSS2.

## Usage instructions

### Clone this repo (run once)
```bash
git clone https://github.com/AlexanderRichert-NOAA/nco-spack-configs
cd nco-spack-configs
```

### Clone Spack (run once)
```bash
git clone https://github.com/spack/spack
pushd spack ; git checkout 062d8100b92504ac3248650aab73ef016e7620f6 ; popd
```

### Initialize Spack (run every time)

> [!IMPORTANT]
> Remember to run the `export` commands every time you initialize Spack.

```bash
export SPACK_DISABLE_LOCAL_CONFIG=true
. share/spack/setup-env.sh
export SPACK_USER_CACHE_PATH=${SPACK_ROOT:?}/cache
```

## Install spack-helpers (run once)

Clone the `spack-helpers` repository to provide additional stack validation commands:
```bash
git clone https://github.com/NOAA-EMC/spack-helpers
```
The repo is already pointed to in common-config/config.yaml.

## Install the Spack bootstrap bundle (run once)

```bash
spack bootstrap now
```

## Install an Environment

> [!IMPORTANT]
> The `nco-core` environment **must be installed first**, then `nco-sci*` environments, then add-on environments.
> Also, the `external` paths in the `nco-sci*` `spack.yaml` files that point to the `nco-core` installation **must be updated** to reflect the new installation path. I promise this is the only tedious part.

## Set up and concretize an environment

For example:
```bash
cd var/spack/environments/nco-core-gcc-11.5.0
spack env activate .
spack concretize
```

## Validate the concretization

The `spack validate` commands below are provided by the `spack-helpers` extension.

#### Check for duplicate packages

As of commit `05442a239a6508f1ce8a4b8cfc39a2ddffb9deb1`, the expected duplicates are:

* `fms`
* `crtm`
* `crtm-fix`
* `py-cython`

```bash
spack validate check-duplicates
```

#### Check for packages built with GCC

Take inventory of packages in the `nco-sci*` environments that were built with GCC. As of commit `05442a239a6508f1ce8a4b8cfc39a2ddffb9deb1`, the only expected GCC-built package for the oneAPI environments is `bison`.
```bash
spack validate allow-pkgs-for-compiler gcc bison
```

#### Check approved packages

There is currently no up-to-date list of NCO-approved packages. *If* an approved package list becomes available, run:
```bash
spack validate check-approved-pkgs --pkgs-from-file approved_packages.txt
```

## Installation

Install the concretized environment:
```bash
spack install --only-concrete --jobs 20
```

## Generate module files

> [!NOTE]
> These steps are only required for add-on environments (but there's no harm in running them, either).
> `spack install` automatically generates module files for regular environments, **except for upstream packages used by add-on environments**.

The following commands apply the same configuration from `common-config/modules.yaml` that is used by `spack install`.
```bash
spack module lmod --name modules_flat refresh --upstream-modules
spack module lmod --name with_mpi_hierarchy refresh --upstream-modules
```
