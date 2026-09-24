# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems import cmake, makefile
from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack_repo.builtin.build_systems.makefile import MakefilePackage

from spack.package import *


class Upp(CMakePackage, MakefilePackage):
    """
    The Unified Post Processor (UPP) software package is a software
    package designed to generate useful products from raw model
    output.
    """

    homepage = "https://github.com/NOAA-EMC/UPP"
    git = "https://github.com/NOAA-EMC/UPP.git"
    url = "https://github.com/NOAA-EMC/UPP/archive/refs/tags/upp_v10.0.10.tar.gz"

    maintainers("AlexanderRichert-NOAA", "edwardhartnett", "Hang-Lei-NOAA")

    license("LGPL-3.0-or-later")

    version("develop", branch="develop")
    version(
        "11.0.0",
        tag="upp_v11.0.0",
        commit="6b5c589c7650132c6f13a729a2853676a7b93bbb",
        submodules=True,
    )
    version("10.0.10", sha256="0c96a88d0e79b554d5fcee9401efcf4d6273da01d15e3413845274f73d70b66e")
    version(
        "10.0.9",
        tag="upp_v10.0.9",
        commit="a49af0549958def4744cb3903c7315476fe44530",
        submodules=True,
    )
    version(
        "10.0.8",
        tag="upp_v10.0.8",
        commit="ce989911a7a09a2e2a0e61b3acc87588b5b9fc26",
        submodules=True,
    )
    version("8.3.0", sha256="1c7960dfb62358954512a03fff709f6a3ab198c55b1106f34842e898ca5c4be8")
    version("8.2.0", sha256="38de2178dc79420f42aa3fb8b85796fc49d43d66f90e5276e47ab50c282627ac")

    build_system(conditional("cmake", when="@9:"), conditional("makefile", when="@:8"), default="cmake")

    variant("openmp", default=True, description="Use OpenMP threading")
    variant("postexec", default=True, description="Build NCEPpost executable")
    variant("wrf-io", default=False, description="Build with WRF-IO library")
    variant("docs", default=False, description="Build Doxygen documentation")

    depends_on("c", type="build")  # generated
    depends_on("fortran", type="build")  # generated

    depends_on("mpi")
    depends_on("netcdf-fortran")
    depends_on("bacio@2.4.1")
    depends_on("crtm")
    depends_on("g2")
    depends_on("g2tmpl")
    depends_on("ip")
    depends_on("w3emc")
    depends_on("gfsio", when="@:10.0.8")
    depends_on("wrf-io")

    depends_on("nemsio", when="+postexec")
    depends_on("sfcio", when="+postexec")
    depends_on("sigio", when="+postexec")
    depends_on("sp", when="+postexec")
    depends_on("w3nco", when="+postexec")
    depends_on("wrf-io", when="+wrf-io")
    depends_on("doxygen", when="+docs")

class CMakeBuilder(cmake.CMakeBuilder):
    def cmake_args(self):
        args = [
            self.define_from_variant("OPENMP", "openmp"),
            self.define_from_variant("BUILD_POSTEXEC", "postexec"),
            self.define_from_variant("BUILD_WITH_WRFIO", "wrf-io"),
            self.define_from_variant("ENABLE_DOCS", "docs"),
        ]

        return args

    def patch(self):
        if self.spec.satisfies("^[virtuals=fortran] intel-oneapi-compilers"):
            filter_file("Intel", "Intel|IntelLLVM", "CMakeLists.txt")
            filter_file("Intel", "Intel|IntelLLVM", "sorc/ncep_post.fd/CMakeLists.txt")
        if self.spec.satisfies("^g2@4:"):
            filter_file(r"find_package\(g2 REQUIRED\)", "find_package(g2c REQUIRED)\nfind_package(g2 REQUIRED)", "CMakeLists.txt")

class MakefileBuilder(makefile.MakefileBuilder):
    build_directory = "sorc/ncep_post.fd/"

    def patch(self):
        filter_file("^NETCDF_LDFLAGS", "#NETCDF_LDFLAGS", "sorc/ncep_post.fd/makefile_module")

    def setup_build_environment(self, env):
        def getlib(spec):
            prefix = spec.prefix
            libs = []
            for ufour in [True, False]:
                libname = "lib" + spec.name.replace("libpng", "png") + "_4"*ufour
                libs += find_libraries(libname, root=prefix, recursive=True, shared=True)
                libs += find_libraries(libname, root=prefix, recursive=True, shared=False)
            return libs[0]
        env.set("myFC", self.spec["mpi"].mpifc)
        if self.spec.satisfies("%oneapi") or self.spec.satisfies("%intel"):
            fcflags = "-O3 -convert big_endian -traceback -g -fp-model source -fpp -qopenmp"
        else:
            fcflags = "-O3"
        env.set("myFCFLAGS", fcflags)
        env.set("myCPP", spack_cc)
        env.set("myCPPFLAGS", "-P")
        env.set("SFCIO_INC4", self.spec["sfcio"].prefix.include_4)
        env.set("NEMSIO_INC", self.spec["nemsio"].prefix.include)
        env.set("BACIO_LIB4", getlib(self.spec["bacio"]))
        env.set("CRTM_INC", self.spec["crtm"].prefix.include)
        env.set("CRTM_LIB", getlib(self.spec["crtm"]))
        env.set("G2TMPL_INC", self.spec["g2tmpl"].prefix.include)
        env.set("G2TMPL_LIB", getlib(self.spec["g2tmpl"]))
        env.set("G2_INC4", self.spec["g2"].prefix.include_4)
        env.set("G2_LIB4", getlib(self.spec["g2"]))
        env.set("GFSIO_INC4", self.spec["gfsio"].prefix.include)
        env.set("GFSIO_LIB4", getlib(self.spec["gfsio"]))
        env.set("IP_INC4", self.spec["ip"].prefix.include_4)
        env.set("IP_LIB4", getlib(self.spec["ip"]))
        env.set("JASPER_LIB", getlib(self.spec["jasper"]))
        env.set("NEMSIO_LIB", getlib(self.spec["nemsio"]))
        nfconfig = which(join_path(self.spec["netcdf-fortran"].prefix.bin, "nf-config"), required=True)
        env.set("NETCDF_INC", nfconfig("--includedir", output=str))
        env.set("NETCDF_LDFLAGS", nfconfig("--flibs", output=str))
        env.set("PNG_LIB", getlib(self.spec["libpng"]))
        env.set("SFCIO_LIB4", getlib(self.spec["sfcio"]))
        env.set("SIGIO_INC4", self.spec["sigio"].prefix.include)
        env.set("SIGIO_LIB4", getlib(self.spec["sigio"]))
        env.set("SP_LIB4", getlib(self.spec["sp"]))
        env.set("W3EMC_INC4", self.spec["w3emc"].prefix.include_4)
        env.set("W3EMC_LIB4", getlib(self.spec["w3emc"]))
        env.set("W3NCO_LIB4", getlib(self.spec["w3nco"]))
        env.set("WRFIO_LIB", self.spec["wrf-io"].libs[0])
        env.set("Z_LIB", self.spec["zlib-api"].libs[0])

    def build(self, pkg, spec, prefix):
        with working_dir(self.build_directory):
            make("-f", "makefile_module", "-j1") # make-based build cannot build in parallel

    def install(self, pkg, spec, prefix):
        with working_dir(self.build_directory):
            mkdir(prefix.exec)
            copy("ncep_post", prefix.exec)
            symlink(prefix.exec, prefix.bin)
            copy_tree("include", prefix.include)
            mkdir(prefix.lib)
            copy("libnceppost.a", prefix.lib)
            copy_tree("../../jobs", prefix.jobs)
            copy_tree("../../scripts", prefix.scripts)
            copy_tree("../../ush", prefix.ush)
            copy_tree("../../parm", prefix.parm)
