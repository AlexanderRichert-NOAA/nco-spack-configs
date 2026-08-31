# NIMBUS early access test stack

This repo provides a set of Spack configuration files for installing test stacks for NIMBUS early access. See the instructions below.

## Misc. notes
- The 'nco-core' environment contains a bunch of packages that ostensibly don't need to be distinguished by compiler (e.g., we don't need a separate copy of cmake for every compiler). Some of these packages are used by the nco-sci environments, which provide the main stack of scientific software dependencies.
- There are some commented-out packages in the spack.yaml's; these are ones that were in the spack-stack 'nco' template but that I didn't see in any prod {build,run}.ver's.
- xml-fortran = libxmlparse on WCOSS2.

## Setup instructions

All commands are run from this repository's root directory. The Spack repository will be cloned underneath it.

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
There's nothing magical about this commit, it's just a recent commit on spack develop branch that I've tested with.

### Initialize Spack (run on every shell session)

> [!IMPORTANT]
> Remember to run the `export` commands every time you initialize Spack.

```bash
export SPACK_DISABLE_LOCAL_CONFIG=true
. spack/share/spack/setup-env.sh
export SPACK_USER_CACHE_PATH=${SPACK_ROOT:?}/cache
```
> [!TIP]
> I suggest running `touch ~/.spack` to avoid accidentally populating that directory and inadvertently polluting later Spack configurations/builds.

### Install spack-helpers (run once)

Clone the `spack-helpers` repository to provide additional stack validation commands:
```bash
git clone https://github.com/NOAA-EMC/spack-helpers
```
The extension is already incorporated via common-config/config.yaml, so no further setup is needed (unless you want tab completions, in which case source `spack-helpers/source_me.sh`).

### Install the Spack bootstrap bundle (run once)

```bash
spack bootstrap now
```

## Install an environment

> [!IMPORTANT]
> The `nco-core` environment **must be installed first**, then `nco-sci*` environments, then add-on environments.

> [!IMPORTANT]
> The `external` paths in the `nco-sci*/spack.yaml` files that point to the `nco-core` installation **must be updated** to reflect the new installation path. I promise this is the only tedious part.

All commands are run from this repository's root directory. Currently the installed packages land under spack/opt/ and the modules go under each environment directory, but this can be easily customized.

### Set up and concretize an environment

To activate the nco-core environment:
```bash
spack env activate nco-core-gcc-11.5.0
spack concretize
```

### Validate the concretization

The `spack validate` commands below are provided by the `spack-helpers` extension.

#### Check for duplicate packages

As of commit `de4ab10baf0805b5dd07e490cd446e93498dee9b`, the expected duplicates are:
* `fms`
* `crtm`
* `crtm-fix`
* `py-cython`

```bash
spack validate check-duplicates
```

#### Check for packages built with GCC

Take inventory of packages in the `nco-sci*` environments that were built with GCC. As of commit `de4ab10baf0805b5dd07e490cd446e93498dee9b`, the only expected GCC-built package for the oneAPI environments is `bison`.
```bash
spack validate allow-pkgs-for-compiler gcc bison
```

Don't bother running this command in the nco-core-**gcc**-11.5.0 environment...

#### Check approved packages

There is currently no up-to-date list of NCO-approved packages. *If* an approved package list becomes available, run:
```bash
spack validate check-approved-pkgs --pkgs-from-file approved_packages.txt
```

### Do the build

Install the concretized environment:
```bash
spack install --only-concrete --jobs 20
```

### Generate module files

> [!NOTE]
> These steps are only required for add-on environments (but there's no harm in running them, either).
> `spack install` automatically generates module files for regular environments, **except for upstream packages used by add-on environments**.

The following commands apply the same configuration from `common-config/modules.yaml` that is used by `spack install`.
```bash
spack module lmod --name modules_flat refresh --upstream-modules
spack module lmod --name with_mpi_hierarchy refresh --upstream-modules
```
