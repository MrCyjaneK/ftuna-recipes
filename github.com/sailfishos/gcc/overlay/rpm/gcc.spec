# Combined gcc / cross-armv*-gcc) specfile
Name: gcc-go
# Keep Name on top !

%if "%{?bootstrap}" == ""
%define bootstrap 0
%else
%if "%{bootstrap}" != "0" && "%{bootstrap}" != "1" && "%{bootstrap}" != "2"
%{error:Bootstrap parameter should me one of: 0, 1, 2}
%endif
%endif

%ifarch aarch64 x86_64
%define _libdir /usr/lib64
%define _lib lib64
%endif

%global isl_version 0.24

# crossbuild / accelerator section
# \/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
%define crossbuild 0
%if 0
# this is the ix86 -> arm cross compiler (cross-armv*-gcc)
#
# We set requires/provides by hand and disable post-build-checks.
# Captain Trunk: Sledge, you cannot disarm that nuclear bomb!
# Sledge Hammer: Trust me, I know what I'm doing. 
AutoReqProv: 0
AutoReq: false
#!BuildIgnore: rpmlint-Moblin
#!BuildIgnore: rpmlint-mini
#!BuildIgnore: post-build-checks
# cross platform
%if %(echo %{crossarch} | grep -q "^arm" && echo 1 || echo 0)
%define cross_gcc_target_platform %{crossarch}-%{_vendor}-linux-gnueabi
%else
%define cross_gcc_target_platform %{crossarch}-%{_vendor}-linux-gnu
%endif
# gcc_target_platform holds the host (executing the compiler)
# cross_gcc_target_platform holds the target (for which the compiler is producing binaries)
# prefix for cross compiler
%define _prefix /opt/cross
%global debug_package %{nil}
%if %{bootstrap} == 0
%define __strip %{_prefix}/bin/%{cross_gcc_target_platform}-strip
%else
# strip of 'foreign arch' symbols fails
%define __strip /bin/true
%endif
# sysroot for cross-compiler
%define crosssysroot %{_prefix}/%{cross_gcc_target_platform}/sys-root
# flag
%define crossbuild 1
# macros in buildrequires is hard to expand for the scheduler (e.g. crossarch) which would make this easier.
%if %{bootstrap} == 2
%define cross_deps cross-%{crossarch}-glibc-headers cross-%{crossarch}-libxcrypt-devel cross-%{crossarch}-kernel-headers cross-%{crossarch}-binutils
%endif
%if %{bootstrap} == 0
%define cross_deps cross-%{crossarch}-glibc cross-%{crossarch}-glibc-devel cross-%{crossarch}-libxcrypt cross-%{crossarch}-libxcrypt-devel cross-%{crossarch}-glibc-headers cross-%{crossarch}-kernel-headers cross-%{crossarch}-binutils
%endif
%if %{bootstrap} == 1
%define cross_deps cross-%{crossarch}-kernel-headers cross-%{crossarch}-binutils
%endif

BuildRequires: %{cross_deps}

# Fixme: find way to make this without listing every package
%if "%{crossarch}" == "armv7hl"
%define crossextraconfig --with-float=hard --with-fpu=neon --with-arch=armv7-a --with-mode=thumb
%endif
%if "%{crossarch}" == "i486"
%define crossextraconfig --disable-libstdcxx-pch --with-arch=i686 --with-fpmatch=sse --with-gnu-as=/opt/cross/bin/i486-meego-linux-gnu-as --with-gnu-ld=/opt/cross/bin/i486-meego-linux-gnu-ld --with-as=/opt/cross/bin/i486-meego-linux-gnu-as --with-ld=/opt/cross/bin/i486-meego-linux-gnu-ld
%endif
%if "%{crossarch}" == "x86_64"
%define crossextraconfig --disable-libstdcxx-pch
%endif
%if "%{crossarch}" == "aarch64"
%define crossextraconfig --with-arch=armv8-a
%endif

# single target atm.
ExclusiveArch: %ix86 x86_64
#
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
# end crossbuild / accelerator section
%endif

%global gcc_version 13.5.0
%global gcc_release 2
%global _unpackaged_files_terminate_build 0
%global _performance_build 1
%global build_ada 0
%global build_objc 0
%global build_go 1
%global build_d 0
%global include_gappletviewer 0
%global multilib_64_archs %{nil}
%ifarch x86_64
%global multilib_32_arch i686
%endif
%global build_64bit_multilib 0
%ifarch %{ix86} x86_64 ia64 ppc64le
%global build_libquadmath 1
%else
%global build_libquadmath 0
%endif
%ifarch %{ix86} x86_64 ppc ppc64 ppc64le ppc64p7 s390 s390x %{arm} aarch64
%global build_libasan 1
%else
%global build_libasan 0
%endif
%ifarch x86_64 aarch64
%global build_libhwasan 1
%else
%global build_libhwasan 0
%endif
%ifarch x86_64 ppc64 ppc64le aarch64 s390x
%global build_libtsan 1
%else
%global build_libtsan 0
%endif
%ifarch x86_64 ppc64 ppc64le aarch64 s390x
%global build_liblsan 1
%else
%global build_liblsan 0
%endif
%ifarch %{ix86} x86_64 ppc ppc64 ppc64le ppc64p7 s390 s390x %{arm} aarch64
%global build_libubsan 1
%else
%global build_libubsan 0
%endif
%ifarch %{ix86} x86_64 ppc ppc64 ppc64le ppc64p7 s390 s390x %{arm} aarch64 %{mips} riscv64
%global build_libatomic 1
%else
%global build_libatomic 0
%endif
%ifarch %{ix86} x86_64 %{arm} alpha ppc ppc64 ppc64le ppc64p7 s390 s390x aarch64
%global build_libitm 1
%else
%global build_libitm 0
%endif
#GCC Graphite needs isl
%global build_isl 1
%global build_libstdcxx_doc 0
%ifarch %{ix86} x86_64 ppc ppc64 ppc64le ppc64p7 s390 s390x %{arm} aarch64 %{mips}
%global attr_ifunc 1
%else
%global attr_ifunc 0
%endif

Summary: Go frontend for GCC
Version: 13.5.0
%if %{bootstrap}
Release: 0.%{bootstrap}.%{gcc_release}
%else
Release: %{gcc_release}
%endif
License: GPLv3+ and GPLv3+ with exceptions and GPLv2+ with exceptions and LGPLv2+ and BSD
URL: https://github.com/sailfishos/gcc
Source0: %{name}-%{version}.tar.bz2

BuildRequires: binutils >= 2.31
BuildRequires: glibc-static
BuildRequires: zlib-devel, gettext,  bison, flex
BuildRequires: mpc-devel
BuildRequires: glibc-devel >= 2.4.90-13
BuildRequires: elfutils-devel >= 0.147
BuildRequires: libstdc++-devel
BuildRequires: libgomp
BuildRequires: libxcrypt-devel
BuildRequires: libzstd-devel

%if %{build_libstdcxx_doc}
BuildRequires: doxygen
BuildRequires: graphviz
%endif

BuildRequires: net-tools
BuildRequires: procps
Requires: libgo = %{version}-%{release}
Requires: libgo-devel = %{version}-%{release}
Provides: gccgo = %{version}-%{release}
AutoReq: true

#We need -gnueabi indicator for ARM
%ifnarch %{arm} aarch64
%global _gnu %{nil}
%endif
%global gcc_target_platform %{_target_platform}

%description
gccgo and the Go runtime library from GCC %{gcc_version}.

%package -n libgo
Summary: Go runtime
Autoreq: true

%description -n libgo
This package contains Go shared library which is needed to run
Go dynamically linked programs.

%package -n libgo-devel
Summary: Go development libraries
Requires: libgo = %{version}-%{release}
Autoreq: true

%description -n libgo-devel
This package includes libraries and support files for compiling
Go programs.

%package -n libgo-static
Summary: Static Go libraries
Requires: libgo = %{version}-%{release}
Requires: gcc

%description -n libgo-static
This package contains static Go libraries.

%prep
%setup -q -n %{name}-%{version}/upstream

# sfosbuild places only Source0 in SOURCES. isl and the patches are in
# the packaging tree, beside the upstream submodule.
rpmroot=%{_builddir}/%{name}-%{version}/rpm
tar xfj $rpmroot/isl-0.24.tar.bz2
for p in \
	gcc13-hack.patch \
	gcc13-sparc-config-detection.patch \
	gcc13-libgomp-omp_h-multilib.patch \
	gcc13-libtool-no-rpath.patch \
	gcc13-isl-dl.patch \
	gcc13-isl-dl2.patch \
	gcc13-libstdc++-docs.patch \
	gcc13-no-add-needed.patch \
	gcc13-Wno-format-security.patch \
	gcc13-rh1574936.patch \
	gcc13-d-shared-libphobos.patch \
	gcc13-reproducible-builds.patch \
	gcc13-reproducible-builds-buildid-for-checksum.patch \
	isl-rh2155127.patch \
	gcc13-fortran-fdec-duplicates.patch
do
	patch -p0 < $rpmroot/$p
done
touch -r isl-0.24/m4/ax_prog_cxx_for_build.m4 isl-0.24/m4/ax_prog_cc_for_build.m4

echo 'Sailfish OS gcc %{gcc_version}-%{gcc_release}' > gcc/DEV-PHASE

cp -a libstdc++-v3/config/cpu/i{4,3}86/atomicity.h

./contrib/gcc_update --touch

LC_ALL=C sed -i -e 's/\xa0/ /' gcc/doc/options.texi

%build

rm -fr obj-%{gcc_target_platform}
mkdir obj-%{gcc_target_platform}
cd obj-%{gcc_target_platform}

%if %{build_isl}
mkdir isl-build isl-install
%ifarch s390 s390x
ISL_FLAG_PIC=-fPIC
%else
ISL_FLAG_PIC=-fpic
%endif
cd isl-build
../../isl-%{isl_version}/configure --disable-shared \
  CC=/usr/bin/gcc CXX=/usr/bin/g++ \
  CFLAGS="${CFLAGS:-%optflags} $ISL_FLAG_PIC" --prefix=`cd ..; pwd`/isl-install
make %{?_smp_mflags}
make %{?_smp_mflags} install
cd ..
%endif

CC=gcc
OPT_FLAGS="%{optflags}"
OPT_FLAGS=`echo $OPT_FLAGS|sed -e 's/-Wp,-U_FORTIFY_SOURCE,-D_FORTIFY_SOURCE=[123]//g'`
OPT_FLAGS=`echo $OPT_FLAGS|sed -e 's/\(-Wp,\)\?-D_FORTIFY_SOURCE=[123]//g'`
OPT_FLAGS=`echo $OPT_FLAGS|sed -e 's/\(-Wp,\)\?-U_FORTIFY_SOURCE//g'`
OPT_FLAGS=`echo $OPT_FLAGS|sed -e 's/-m64//g;s/-m32//g;s/-m31//g'`
OPT_FLAGS=`echo $OPT_FLAGS|sed -e 's/-fno-omit-frame-pointer//g;s/-mbackchain//g;s/-mno-omit-leaf-frame-pointer//g'`
OPT_FLAGS=`echo $OPT_FLAGS|sed -e 's/-Werror=format-security/-Wformat-security/g'`
%ifarch %{ix86}
OPT_FLAGS=`echo $OPT_FLAGS|sed -e 's/-march=i.86//g'`
%endif
OPT_FLAGS=`echo "$OPT_FLAGS" | sed -e 's/[[:blank:]]\+/ /g'`
case "$OPT_FLAGS" in
  *-fasynchronous-unwind-tables*)
    sed -i -e 's/-fno-exceptions /-fno-exceptions -fno-asynchronous-unwind-tables /' \
      ../libgcc/Makefile.in
    ;;
esac

%ifarch %arm aarch64

%define ARM_EXTRA_CONFIGURE ""
# for armv7hl reset the gcc specs
%ifarch armv7hl
%define ARM_EXTRA_CONFIGURE --with-float=hard --with-fpu=neon --with-mode=thumb --with-arch=armv7-a
%endif
# aarch64
%ifarch aarch64
%define ARM_EXTRA_CONFIGURE --with-arch=armv8-a
%endif
%endif

%if %{build_go}
enablelgo=,go
%else
enablelgo=
%endif

%if %{crossbuild}
# cross build
export PATH=/opt/cross/bin:$PATH
# strip all after -march . no arch specific options in cross-compiler build .
# -march=core2 -mssse3 -mtune=atom -mfpmath=sse -fasynchronous-unwi
export OPT_FLAGS=`echo "$OPT_FLAGS" | sed -e "s#\-march=.*##g" | sed -e 's#\-mtune=.*##g`
%endif

CC="$CC" CFLAGS="$OPT_FLAGS" CXXFLAGS="`echo $OPT_FLAGS | sed 's/ -Wall / /g'`" XCFLAGS="$OPT_FLAGS" TCFLAGS="$OPT_FLAGS" \
	GCJFLAGS="$OPT_FLAGS" \
	../configure --prefix=%{_prefix} --mandir=%{_mandir} \
%if !%{crossbuild}
%if ! 0%{?qemu_user_space_build}
	--enable-bootstrap \
%else
	--disable-bootstrap \
%endif
%else
	--disable-bootstrap \
%endif
	--with-bugurl=https://github.com/sailfishos/ \
	--enable-plugin --enable-initfini-array \
%if %{build_isl}
	--with-isl=`pwd`/isl-install \
%else
	--without-isl \
%endif
%if %{crossbuild}
	--host=%{gcc_target_platform} \
	--target=%{cross_gcc_target_platform} \
	--with-sysroot=%{crosssysroot} \
	--disable-multilib \
%else
%ifarch %{arm} aarch64
	%ARM_EXTRA_CONFIGURE \
	--disable-sjlj-exceptions \
	--enable-gold \
	--with-plugin-ld=gold \
%endif
%ifarch aarch64 x86_64
	--libdir=/usr/lib64 \
%endif
%ifarch %{ix86} x86_64
	--with-tune=generic \
%endif
%ifarch i586
	--with-arch=core2 --with-tune=atom --with-fpmath=sse \
%endif
%ifarch i486
	--with-arch=i686 --with-fpmath=sse \
%endif
%ifarch x86_64
	--disable-libstdcxx-pch \
%endif
%ifarch riscv64
	--with-arch=rv64gc --with-abi=lp64d --with-multilib-list=lp64d \
%endif
%endif
%if %{build_64bit_multilib}
	--enable-targets=all \
	--enable-multilib \
%else
	--disable-multilib \
%endif
	--enable-checking=release \
	--disable-fixed-point \
	--with-system-zlib --enable-__cxa_atexit --disable-libunwind-exceptions \
	--enable-libstdcxx-backtrace --with-libstdcxx-zoneinfo=%{_datadir}/zoneinfo \
	--enable-gnu-unique-object \
	--enable-lto \
	--enable-linker-build-id \
	--disable-libmpx \
%if %{bootstrap} == 0
	--enable-languages=c,c++,lto${enablelgo} \
	--enable-threads=posix \
	--enable-shared \
%endif
%if %{bootstrap} == 1
	--enable-languages=c \
	--without-headers \
	--with-newlib \
	--disable-decimal-float \
	--disable-fixed-point \
	--disable-threads \
	--disable-shared \
	--disable-libssp \
	--disable-libgomp \
	--disable-libquadmath \
%endif
%if %{bootstrap} == 2
	--enable-languages=c \
	--with-sysroot=%{crosssysroot} \
	--disable-libssp \
	--disable-libgomp \
	--disable-libquadmath \
%endif
	--disable-libgcj \
	--disable-libcilkrts \
%if %{attr_ifunc}
	--enable-gnu-indirect-function \
%endif
%if %{crossbuild}
	%{crossextraconfig} \
%endif
	--build=%{gcc_target_platform} || ( cat config.log ; exit 1 )

GCJFLAGS="$OPT_FLAGS" make %{?_smp_mflags} BOOT_CFLAGS="$OPT_FLAGS"

# Make generated man pages even if Pod::Man is not new enough
perl -pi -e 's/head3/head2/' ../contrib/texi2pod.pl
for i in ../gcc/doc/*.texi; do
  cp -a $i $i.orig; sed 's/ftable/table/' $i.orig > $i
done
make %{?_smp_mflags} -C gcc generated-manpages
for i in ../gcc/doc/*.texi; do mv -f $i.orig $i; done

# Make generated doxygen pages.
%if %{build_libstdcxx_doc}
cd %{gcc_target_platform}/libstdc++-v3
make doc-html-doxygen
make doc-man-doxygen
cd ../..
%endif

# Clean any old compressed docs
if [ -d rpm.doc ]; then
  find rpm.doc -name "*.bz2" -delete
fi

# Copy various doc files here and there
cd ..
mkdir -p rpm.doc/gfortran rpm.doc/objc rpm.doc/gdc rpm.doc/libphobos
mkdir -p rpm.doc/go rpm.doc/libgo rpm.doc/libquadmath rpm.doc/libitm
mkdir -p rpm.doc/changelogs/{gcc/cp,gcc/ada,gcc/jit,libstdc++-v3,libobjc,libgomp,libcc1,libatomic,libsanitizer}

for i in {gcc,gcc/cp,gcc/ada,gcc/jit,libstdc++-v3,libobjc,libgomp,libcc1,libatomic,libsanitizer}/ChangeLog*; do
	cp -p $i rpm.doc/changelogs/$i
done

%if %{build_objc}
(cd libobjc; for i in README*; do
	cp -p $i ../rpm.doc/objc/$i.libobjc
done)
%endif
%if %{build_d}
(cd gcc/d; for i in ChangeLog*; do
	cp -p $i ../../rpm.doc/gdc/$i.gdc
done)
(cd libphobos; for i in ChangeLog*; do
	cp -p $i ../rpm.doc/libphobos/$i.libphobos
done
cp -a src/LICENSE*.txt libdruntime/LICENSE.txt ../rpm.doc/libphobos/)
%endif
%if %{build_libquadmath}
(cd libquadmath; for i in ChangeLog* COPYING.LIB; do
	cp -p $i ../rpm.doc/libquadmath/$i.libquadmath
done)
%endif
%if %{build_libitm}
(cd libitm; for i in ChangeLog*; do
	cp -p $i ../rpm.doc/libitm/$i.libitm
done)
%endif
%if %{build_go}
(cd gcc/go; for i in README* ChangeLog*; do
	cp -p $i ../../rpm.doc/go/$i
done)
(cd libgo; for i in LICENSE* PATENTS* README; do
	cp -p $i ../rpm.doc/libgo/$i.libgo
done)
%endif

rm -f rpm.doc/changelogs/gcc/ChangeLog.[1-9]
find rpm.doc -name \*ChangeLog\* | xargs bzip2 -9

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}

# RISC-V ABI wants to install everything in /lib64/lp64d or /usr/lib64/lp64d.
# Make these be symlinks to /lib64 or /usr/lib64 respectively. See:
# https://lists.fedoraproject.org/archives/list/devel@lists.fedoraproject.org/thread/DRHT5YTPK4WWVGL3GIN5BF2IKX2ODHZ3/
%ifarch riscv64
for d in %{buildroot}%{_libdir} %{buildroot}/%{_lib} \
	  %{buildroot}%{_datadir}/gdb/auto-load/%{_prefix}/%{_lib} \
	  %{buildroot}%{_prefix}/include/c++/%{gcc_version}/%{gcc_target_platform}/%{_lib}; do
  mkdir -p $d
  (cd $d && ln -sf . lp64d)
done
%endif

cd obj-%{gcc_target_platform}

%if !%{crossbuild}
# native
TARGET_PLATFORM=%{gcc_target_platform}

# There are some MP bugs in libstdc++ Makefiles
make %{?_smp_mflags} -C %{gcc_target_platform}/libstdc++-v3
%else
# cross build
export PATH=/opt/cross/bin:$PATH
# strip all after -march . no arch specific options in cross-compiler build .
# -march=core2 -mssse3 -mtune=atom -mfpmath=sse -fasynchronous-unwi
export OPT_FLAGS=`echo "$OPT_FLAGS" | sed -e "s#\-march=.*##g"`
echo "$OPT_FLAGS"
TARGET_PLATFORM=%{cross_gcc_target_platform}
# There are some MP bugs in libstdc++ Makefiles
make %{?_smp_mflags} -C %{cross_gcc_target_platform}/libstdc++-v3
%endif

make %{?_smp_mflags} prefix=%{buildroot}%{_prefix} mandir=%{buildroot}%{_mandir} libdir=%{buildroot}%{_libdir} \
  install

%if !%{crossbuild}
# native
# \/\/\/
FULLPATH=%{buildroot}%{_prefix}/%{_lib}/gcc/%{gcc_target_platform}/%{gcc_version}
FULLEPATH=%{buildroot}%{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_version}

mkdir -p $FULLPATH
mkdir -p $FULLEPATH

ln -sf gcc %{buildroot}%{_prefix}/bin/cc
mkdir -p %{buildroot}/%{_lib}
ln -sf ..%{_prefix}/bin/cpp %{buildroot}/%{_lib}/cpp

%if %{build_go}
mv %{buildroot}%{_prefix}/bin/go{,.gcc}
mv %{buildroot}%{_prefix}/bin/gofmt{,.gcc}
%endif

cxxconfig="`find %{gcc_target_platform}/libstdc++-v3/include -name c++config.h`"
for i in `find %{gcc_target_platform}/[36]*/libstdc++-v3/include -name c++config.h 2>/dev/null`; do
  if ! diff -up $cxxconfig $i; then
    cat > %{buildroot}%{_prefix}/include/c++/%{gcc_version}/%{gcc_target_platform}/bits/c++config.h <<EOF
#ifndef _CPP_CPPCONFIG_WRAPPER
#define _CPP_CPPCONFIG_WRAPPER 1
#include <bits/wordsize.h>
#if __WORDSIZE == 32
%ifarch %{multilib_64_archs}
`cat $(find %{gcc_target_platform}/32/libstdc++-v3/include -name c++config.h)`
%else
`cat $(find %{gcc_target_platform}/libstdc++-v3/include -name c++config.h)`
%endif
#else
%ifarch %{multilib_64_archs}
`cat $(find %{gcc_target_platform}/libstdc++-v3/include -name c++config.h)`
%else
`cat $(find %{gcc_target_platform}/64/libstdc++-v3/include -name c++config.h)`
%endif
#endif
#endif
EOF
    break
  fi
done

for f in `find %{buildroot}%{_prefix}/include/c++/%{gcc_version}/%{gcc_target_platform}/ -name c++config.h`; do
  for i in 1 2 4 8; do
    sed -i -e 's/#define _GLIBCXX_ATOMIC_BUILTINS_'$i' 1/#ifdef __GCC_HAVE_SYNC_COMPARE_AND_SWAP_'$i'\
&\
#endif/' $f
  done
done

# Nuke bits/*.h.gch dirs
# 1) there is no bits/*.h header installed, so when gch file can't be
#    used, compilation fails
# 2) sometimes it is hard to match the exact options used for building
#    libstdc++-v3 or they aren't desirable
# 3) there are multilib issues, conflicts etc. with this
# 4) it is huge
# People can always precompile on their own whatever they want, but
# shipping this for everybody is unnecessary.
rm -rf %{buildroot}%{_prefix}/include/c++/%{gcc_version}/%{gcc_target_platform}/bits/*.h.gch

%if %{build_libstdcxx_doc}
libstdcxx_doc_builddir=%{gcc_target_platform}/libstdc++-v3/doc/doxygen
mkdir -p ../rpm.doc/libstdc++-v3
cp -r -p ../libstdc++-v3/doc/html ../rpm.doc/libstdc++-v3/html
cp -r -p $libstdcxx_doc_builddir/html ../rpm.doc/libstdc++-v3/html/api
mkdir -p %{buildroot}%{_mandir}/man3
cp -r -p $libstdcxx_doc_builddir/man/man3/* %{buildroot}%{_mandir}/man3/
find ../rpm.doc/libstdc++-v3 -name \*~ | xargs rm
%endif

#Debug
#set -x
#find %{buildroot}%{_prefix}/

FULLLSUBDIR=
%ifarch sparcv9 ppc
FULLLSUBDIR=lib32
%endif
%ifarch sparc64 ppc64 ppc64p7
FULLLSUBDIR=lib64
%endif
if [ -n "$FULLLSUBDIR" ]; then
  FULLLPATH=$FULLPATH/$FULLLSUBDIR
  mkdir -p $FULLLPATH
else
  FULLLPATH=$FULLPATH
fi

find %{buildroot} -name \*.la | xargs rm -f
%if %{build_d}
mv %{buildroot}%{_prefix}/%{_lib}/libgphobos.spec $FULLPATH/
%endif
%if %{build_libitm}
mv %{buildroot}%{_prefix}/%{_lib}/libitm.spec $FULLPATH/
%endif
%if %{build_libasan}
mv %{buildroot}%{_prefix}/%{_lib}/libsanitizer.spec $FULLPATH/
%endif

mkdir -p %{buildroot}/%{_lib}

mv -f %{buildroot}%{_prefix}/%{_lib}/libgcc_s.so.1 %{buildroot}/%{_lib}/libgcc_s-%{gcc_version}.so.1
chmod 755 %{buildroot}/%{_lib}/libgcc_s-%{gcc_version}.so.1
ln -sf libgcc_s-%{gcc_version}.so.1 %{buildroot}/%{_lib}/libgcc_s.so.1

%ifarch %{ix86} x86_64 ppc ppc64 ppc64p7 ppc64le %{arm} aarch64 riscv64
rm -f $FULLPATH/libgcc_s.so
echo '/* GNU ld script
   Use the shared library, but some functions are only in
   the static library, so try that secondarily.  */
OUTPUT_FORMAT('`gcc -Wl,--print-output-format -nostdlib -r -o /dev/null`')
GROUP ( /%{_lib}/libgcc_s.so.1 libgcc.a )' > $FULLPATH/libgcc_s.so
%else
ln -sf /%{_lib}/libgcc_s.so.1 $FULLPATH/libgcc_s.so
%endif
%ifarch sparcv9 ppc
%ifarch ppc
rm -f $FULLPATH/64/libgcc_s.so
echo '/* GNU ld script
   Use the shared library, but some functions are only in
   the static library, so try that secondarily.  */
OUTPUT_FORMAT('`gcc -m64 -Wl,--print-output-format -nostdlib -r -o /dev/null`')
GROUP ( /lib64/libgcc_s.so.1 libgcc.a )' > $FULLPATH/64/libgcc_s.so
%else
ln -sf /lib64/libgcc_s.so.1 $FULLPATH/64/libgcc_s.so
%endif
%endif
%ifarch %{multilib_64_archs}
%ifarch x86_64 ppc64 ppc64p7
rm -f $FULLPATH/64/libgcc_s.so
echo '/* GNU ld script
   Use the shared library, but some functions are only in
   the static library, so try that secondarily.  */
OUTPUT_FORMAT('`gcc -m32 -Wl,--print-output-format -nostdlib -r -o /dev/null`')
GROUP ( /%{_lib}/libgcc_s.so.1 libgcc.a )' > $FULLPATH/32/libgcc_s.so
%else
ln -sf /lib/libgcc_s.so.1 $FULLPATH/32/libgcc_s.so
%endif
%endif

mv -f %{buildroot}%{_prefix}/%{_lib}/libgomp.spec $FULLPATH/

mkdir -p %{buildroot}%{_prefix}/libexec/getconf
if gcc/xgcc -B gcc/ -E -P -dD -xc /dev/null | grep '__LONG_MAX__.*\(2147483647\|0x7fffffff\($\|[LU]\)\)'; then
  ln -sf POSIX_V6_ILP32_OFF32 %{buildroot}%{_prefix}/libexec/getconf/default
else
  ln -sf POSIX_V6_LP64_OFF64 %{buildroot}%{_prefix}/libexec/getconf/default
fi

mkdir -p %{buildroot}%{_datadir}/gdb/auto-load/%{_prefix}/%{_lib}
mv -f %{buildroot}%{_prefix}/%{_lib}/libstdc++*gdb.py* \
      %{buildroot}%{_datadir}/gdb/auto-load/%{_prefix}/%{_lib}/

pushd $FULLPATH
if [ "%{_lib}" = "lib" ]; then
%if %{build_objc}
ln -sf ../../../libobjc.so.4 libobjc.so
%endif
ln -sf ../../../libstdc++.so.6.*[0-9] libstdc++.so
ln -sf ../../../libgomp.so.1.* libgomp.so
%if %{build_go}
ln -sf ../../../libgo.so.22.* libgo.so
%endif
%if %{build_libquadmath}
ln -sf ../../../libquadmath.so.0.* libquadmath.so
%endif
%if %{build_d}
ln -sf ../../../libgdruntime.so.4.* libgdruntime.so
ln -sf ../../../libgphobos.so.4.* libgphobos.so
%endif
%if %{build_libitm}
ln -sf ../../../libitm.so.1.* libitm.so
%endif
%if %{build_libatomic}
ln -sf ../../../libatomic.so.1.* libatomic.so
%endif
%if %{build_libasan}
ln -sf ../../../libasan.so.8.* libasan.so
mv ../../../libasan_preinit.o libasan_preinit.o
%endif
%if %{build_libubsan}
ln -sf ../../../libubsan.so.1.* libubsan.so
%endif
else
%if %{build_objc}
ln -sf ../../../../%{_lib}/libobjc.so.4 libobjc.so
%endif
ln -sf ../../../../%{_lib}/libstdc++.so.6.*[0-9] libstdc++.so
ln -sf ../../../../%{_lib}/libgomp.so.1.* libgomp.so
%if %{build_go}
ln -sf ../../../../%{_lib}/libgo.so.22.* libgo.so
%endif
%if %{build_libquadmath}
ln -sf ../../../../%{_lib}/libquadmath.so.0.* libquadmath.so
%endif
%if %{build_d}
ln -sf ../../../../%{_lib}/libgdruntime.so.4.* libgdruntime.so
ln -sf ../../../../%{_lib}/libgphobos.so.4.* libgphobos.so
%endif
%if %{build_libitm}
ln -sf ../../../../%{_lib}/libitm.so.1.* libitm.so
%endif
%if %{build_libatomic}
ln -sf ../../../../%{_lib}/libatomic.so.1.* libatomic.so
%endif
%if %{build_libasan}
ln -sf ../../../../%{_lib}/libasan.so.8.* libasan.so
mv ../../../../%{_lib}/libasan_preinit.o libasan_preinit.o
%endif
%if %{build_libubsan}
ln -sf ../../../../%{_lib}/libubsan.so.1.* libubsan.so
%endif
%if %{build_go}
ln -sf ../../../../%{_lib}/libgo.so.22.* libgo.so
%endif
%if %{build_libtsan}
rm -f libtsan.so
echo 'INPUT ( %{_prefix}/%{_lib}/'`echo ../../../../%{_lib}/libtsan.so.2.* | sed 's,^.*libt,libt,'`' )' > libtsan.so
mv ../../../../%{_lib}/libtsan_preinit.o libtsan_preinit.o
%endif
%if %{build_libhwasan}
rm -f libhwasan.so
echo 'INPUT ( %{_prefix}/%{_lib}/'`echo ../../../../%{_lib}/libhwasan.so.0.* | sed 's,^.*libh,libh,'`' )' > libhwasan.so
mv ../../../../%{_lib}/libhwasan_preinit.o libhwasan_preinit.o
%endif
%if %{build_liblsan}
rm -f liblsan.so
echo 'INPUT ( %{_prefix}/%{_lib}/'`echo ../../../../%{_lib}/liblsan.so.0.* | sed 's,^.*libl,libl,'`' )' > liblsan.so
mv ../../../../%{_lib}/liblsan_preinit.o liblsan_preinit.o
%endif
fi
mv -f %{buildroot}%{_prefix}/%{_lib}/libstdc++.*a $FULLLPATH/
mv -f %{buildroot}%{_prefix}/%{_lib}/libstdc++fs.*a $FULLLPATH/
mv -f %{buildroot}%{_prefix}/%{_lib}/libstdc++exp.*a $FULLLPATH/
mv -f %{buildroot}%{_prefix}/%{_lib}/libstdc++_libbacktrace.*a $FULLLPATH/
mv -f %{buildroot}%{_prefix}/%{_lib}/libsupc++.*a $FULLLPATH/
%if %{build_objc}
mv -f %{buildroot}%{_prefix}/%{_lib}/libobjc.*a .
%endif
mv -f %{buildroot}%{_prefix}/%{_lib}/libgomp.*a .
%if %{build_libquadmath}
mv -f %{buildroot}%{_prefix}/%{_lib}/libquadmath.*a $FULLLPATH/
%endif
%if %{build_d}
mv -f %{buildroot}%{_prefix}/%{_lib}/libgdruntime.*a $FULLLPATH/
mv -f %{buildroot}%{_prefix}/%{_lib}/libgphobos.*a $FULLLPATH/
%endif
%if %{build_libitm}
mv -f %{buildroot}%{_prefix}/%{_lib}/libitm.*a $FULLLPATH/
%endif
%if %{build_libatomic}
mv -f %{buildroot}%{_prefix}/%{_lib}/libatomic.*a $FULLLPATH/
%endif
%if %{build_libasan}
mv -f %{buildroot}%{_prefix}/%{_lib}/libasan.*a $FULLLPATH/
%endif
%if %{build_libubsan}
mv -f %{buildroot}%{_prefix}/%{_lib}/libubsan.*a $FULLLPATH/
%endif
%if %{build_libtsan}
mv -f %{buildroot}%{_prefix}/%{_lib}/libtsan.*a $FULLPATH/
%endif
%if %{build_libhwasan}
mv -f %{buildroot}%{_prefix}/%{_lib}/libhwasan.*a $FULLPATH/
%endif
%if %{build_liblsan}
mv -f %{buildroot}%{_prefix}/%{_lib}/liblsan.*a $FULLPATH/
%endif
%if %{build_go}
mv -f %{buildroot}%{_prefix}/%{_lib}/libgo.*a $FULLLPATH/
mv -f %{buildroot}%{_prefix}/%{_lib}/libgobegin.*a $FULLLPATH/
mv -f %{buildroot}%{_prefix}/%{_lib}/libgolibbegin.*a $FULLLPATH/
%endif


%ifarch %{multilib_64_archs}
mkdir -p 32
ln -sf ../../../../libobjc.so.4 32/libobjc.so
ln -sf ../`echo ../../../../lib64/libstdc++.so.6.* | sed s~/../lib64/~/~` 32/libstdc++.so
ln -sf ../`echo ../../../../lib64/libgomp.so.1.* | sed s~/../lib64/~/~` 32/libgomp.so
%if %{build_libquadmath}
rm -f libquadmath.so
echo 'INPUT ( %{_prefix}/lib64/'`echo ../../../../lib64/libquadmath.so.0.* | sed 's,^.*libq,libq,'`' )' > libquadmath.so
echo 'INPUT ( %{_prefix}/lib/'`echo ../../../../lib64/libquadmath.so.0.* | sed 's,^.*libq,libq,'`' )' > 32/libquadmath.so
%endif
mv -f %{buildroot}%{_prefix}/lib/libsupc++.*a 32/
%if %{build_objc}
mv -f %{buildroot}%{_prefix}/lib/libobjc.*a 32/
%endif
mv -f %{buildroot}%{_prefix}/lib/libgomp.*a 32/
ln -sf ../../../%{multilib_32_arch}-%{_vendor}-%{_target_os}/%{gcc_version}/libstdc++.a 32/libstdc++.a
%if %{build_libquadmath}
ln -sf ../../../%{multilib_32_arch}-%{_vendor}-%{_target_os}/%{gcc_version}/libquadmath.a 32/libquadmath.a
%endif
%if %{build_go}
ln -sf ../../../%{multilib_32_arch}-%{_vendor}-%{_target_os}/%{gcc_version}/libgo.a 32/libgo.a
ln -sf ../../../%{multilib_32_arch}-%{_vendor}-%{_target_os}/%{gcc_version}/libgobegin.a 32/libgobegin.a
ln -sf ../../../%{multilib_32_arch}-%{_vendor}-%{_target_os}/%{gcc_version}/libgolibbegin.a 32/libgolibbegin.a
%endif
%endif

# If we are building a debug package then copy all of the static archives
# into the debug directory to keep them as unstripped copies.
%if 0%{?_enable_debug_packages}
for d in . $FULLLSUBDIR; do
  mkdir -p $RPM_BUILD_ROOT%{_prefix}/%{_lib}/debug%{_prefix}/%{_lib}/gcc/%{gcc_target_platform}/%{gcc_version}/$d
  for f in `find $d -maxdepth 1 -a \
		\( -name libasan.a -o -name libatomic.a \
		-o -name libcaf_single.a \
		-o -name libgcc.a -o -name libgcc_eh.a \
		-o -name libgcov.a \
		-o -name libgo.a -o -name libgobegin.a \
		-o -name libgolibbegin.a -o -name libgomp.a \
		-o -name libitm.a -o -name liblsan.a \
		-o -name libobjc.a -o -name libgdruntime.a -o -name libgphobos.a \
		-o -name libm2\*.a -o -name libquadmath.a -o -name libstdc++.a \
		-o -name libstdc++fs.a -o -name libstdc++exp.a \
		-o -name libstdc++_libbacktrace.a -o -name libsupc++.a \
		-o -name libtsan.a -o -name libubsan.a \) -a -type f`; do
    cp -a $f $RPM_BUILD_ROOT%{_prefix}/%{_lib}/debug%{_prefix}/%{_lib}/gcc/%{gcc_target_platform}/%{gcc_version}/$d/
  done
done
%endif

# Strip debug info from Fortran/ObjC/Java/Go static libraries
strip -g `find . \( -name libobjc.a -o -name libgomp.a \
		    -o -name libgcc.a -o -name libgcov.a -o -name libquadmath.a -o -name libgo.a \) -a -type f`
popd
chmod 755 %{buildroot}%{_prefix}/%{_lib}/libgomp.so.1.*
chmod 755 %{buildroot}%{_prefix}/%{_lib}/libcc1.so.0.*
%if %{build_libquadmath}
chmod 755 %{buildroot}%{_prefix}/%{_lib}/libquadmath.so.0.*
%endif
%if %{build_d}
chmod 755 %{buildroot}%{_prefix}/%{_lib}/libgdruntime.so.4.*
chmod 755 %{buildroot}%{_prefix}/%{_lib}/libgphobos.so.4.*
%endif
%if %{build_libitm}
chmod 755 %{buildroot}%{_prefix}/%{_lib}/libitm.so.1.*
%endif
%if %{build_libatomic}
chmod 755 %{buildroot}%{_prefix}/%{_lib}/libatomic.so.1.*
%endif
%if %{build_libasan}
chmod 755 %{buildroot}%{_prefix}/%{_lib}/libasan.so.8.*
%endif
%if %{build_libubsan}
chmod 755 %{buildroot}%{_prefix}/%{_lib}/libubsan.so.1.*
%endif
%if %{build_libtsan}
chmod 755 %{buildroot}%{_prefix}/%{_lib}/libtsan.so.2.*
%endif
%if %{build_libhwasan}
chmod 755 %{buildroot}%{_prefix}/%{_lib}/libhwasan.so.0.*
%endif
%if %{build_liblsan}
chmod 755 %{buildroot}%{_prefix}/%{_lib}/liblsan.so.0.*
%endif
%if %{build_objc}
chmod 755 %{buildroot}%{_prefix}/%{_lib}/libobjc.so.4.*
%endif

%if %{build_ada}
chmod 755 %{buildroot}%{_prefix}/%{_lib}/libgnarl*so*
chmod 755 %{buildroot}%{_prefix}/%{_lib}/libgnat*so*
%endif

for h in `find $FULLPATH/include -name \*.h`; do
  if grep -q 'It has been auto-edited by fixincludes from' $h; then
    rh=`grep -A2 'It has been auto-edited by fixincludes from' $h | tail -1 | sed 's|^.*"\(.*\)".*$|\1|'`
    diff -up $rh $h || :
    rm -f $h
  fi
done

cat > %{buildroot}%{_prefix}/bin/c89 <<"EOF"
#!/bin/sh
fl="-std=c89"
for opt; do
  case "$opt" in
    -ansi|-std=c89|-std=iso9899:1990) fl="";;
    -std=*) echo "`basename $0` called with non ANSI/ISO C option $opt" >&2
	    exit 1;;
  esac
done
exec gcc $fl ${1+"$@"}
EOF
cat > %{buildroot}%{_prefix}/bin/c99 <<"EOF"
#!/bin/sh
fl="-std=c99"
for opt; do
  case "$opt" in
    -std=c99|-std=iso9899:1999) fl="";;
    -std=*) echo "`basename $0` called with non ISO C99 option $opt" >&2
	    exit 1;;
  esac
done
exec gcc $fl ${1+"$@"}
EOF
chmod 755 %{buildroot}%{_prefix}/bin/c?9

cd ..
# Remove binaries we will not be including, so that they don't end up in
# gcc-debuginfo
rm -f %{buildroot}%{_prefix}/%{_lib}/{libffi*,libiberty.a} || :
rm -f $FULLEPATH/install-tools/{mkheaders,fixincl}
rm -f %{buildroot}%{_prefix}/lib/{32,64}/libiberty.a
rm -f %{buildroot}%{_prefix}/%{_lib}/libssp*
rm -f %{buildroot}%{_prefix}/%{_lib}/libvtv* || :
rm -f %{buildroot}%{_prefix}/bin/%{_target_platform}-gfortran || :
rm -f %{buildroot}%{_prefix}/bin/%{_target_platform}-gccgo || :
rm -f %{buildroot}%{_prefix}/bin/%{_target_platform}-gcj || :
rm -f %{buildroot}%{_prefix}/bin/%{_target_platform}-gcc-ar || :
rm -f %{buildroot}%{_prefix}/bin/%{_target_platform}-gcc-nm || :
rm -f %{buildroot}%{_prefix}/bin/%{_target_platform}-gcc-ranlib || :
rm -f %{buildroot}%{_prefix}/bin/%{_target_platform}-gdc || :

%ifarch %{multilib_64_archs}
# Remove libraries for the other arch on multilib arches
rm -f %{buildroot}%{_prefix}/lib/lib*.so*
rm -f %{buildroot}%{_prefix}/lib/lib*.a
rm -f %{buildroot}/lib/libgcc_s*.so*
%if %{build_go}
rm -rf %{buildroot}%{_prefix}/%{_lib}/go/%{gcc_version}/%{gcc_target_platform}
%ifnarch sparc64 ppc64 ppc64p7
ln -sf %{multilib_32_arch}-%{_vendor}-%{_target_os} %{buildroot}%{_prefix}/lib/go/%{gcc_version}/%{gcc_target_platform}
%endif
%endif
%else
%ifarch sparcv9 ppc
rm -f %{buildroot}%{_prefix}/lib64/lib*.so*
rm -f %{buildroot}%{_prefix}/lib64/lib*.a
rm -f %{buildroot}/lib64/libgcc_s*.so*
%if %{build_go}
rm -rf %{buildroot}%{_prefix}/lib64/go/%{gcc_version}/%{gcc_target_platform}
%endif
%endif
%endif

rm -f %{buildroot}%{mandir}/man3/ffi*
# /\/\/\
# native
%else
# cross
# \/\/\/
# additional install for cross
# remove some obsolete files
ln -sf %{cross_gcc_target_platform}-gcc %{buildroot}%{_prefix}/bin/%{cross_gcc_target_platform}-cc
set -x
rm -rRf %buildroot/%{_prefix}/lib/libiberty.a
rm -rRf %buildroot/%{_prefix}/share
find %{buildroot} -name \*.la | xargs rm -f
rm -rRf %buildroot/%{_prefix}/lib/libcc1*
set +x
# /\/\/\
# cross
%endif

%if !%{crossbuild}
# checking and split packaging for native ...
# native
# \/\/\/

# Clean up info dir
rm -rf %{buildroot}%{_datadir}info/dir

# Help plugins find out nvra.
echo gcc-%{gcc_version}.%{_arch} > $FULLPATH/rpmver

%check
%if 0
cd obj-%{gcc_target_platform}

# run the tests.
make %{?_smp_mflags} -k check ALT_CC_UNDER_TEST=gcc ALT_CXX_UNDER_TEST=g++ RUNTESTFLAGS="--target_board=unix/'{,-fstack-protector-strong}'" || :
echo ====================TESTING=========================
( LC_ALL=C ../contrib/test_summary || : ) 2>&1 | sed -n '/^cat.*EOF/,/^EOF/{/^cat.*EOF/d;/^EOF/d;/^LAST_UPDATED:/d;p;}'
echo ====================TESTING END=====================
mkdir testlogs-%{_target_platform}-%{version}-%{release}
for i in `find . -name \*.log | grep -F testsuite/ | grep -v 'config.log\|acats\|ada'`; do
  ln $i testlogs-%{_target_platform}-%{version}-%{release}/ || :
done
tar cf - testlogs-%{_target_platform}-%{version}-%{release} | bzip2 -9c \
  | uuencode testlogs-%{_target_platform}.tar.bz2 || :
rm -rf testlogs-%{_target_platform}-%{version}-%{release}
%endif

# Don't add %post -p /sbin/ldconfig here, see comment below

%post -n libgo -p /sbin/ldconfig

%postun -n libgo -p /sbin/ldconfig

%files
%attr(755,root,root) %{_prefix}/bin/go.gcc
%{_prefix}/bin/gccgo
%attr(755,root,root) %{_prefix}/bin/gofmt.gcc
%{_mandir}/man1/gccgo.1*
%{_mandir}/man1/go.1*
%{_mandir}/man1/gofmt.1*
%dir %{_prefix}/%{_lib}/gcc
%dir %{_prefix}/%{_lib}/gcc/%{gcc_target_platform}
%dir %{_prefix}/%{_lib}/gcc/%{gcc_target_platform}/%{gcc_version}
%{_prefix}/%{_lib}/gcc/%{gcc_target_platform}/%{gcc_version}/crt*.o
%{_prefix}/%{_lib}/gcc/%{gcc_target_platform}/%{gcc_version}/libgcc.a
%{_prefix}/%{_lib}/gcc/%{gcc_target_platform}/%{gcc_version}/libgcc_eh.a
%{_prefix}/%{_lib}/gcc/%{gcc_target_platform}/%{gcc_version}/libgcc_s.so
%{_prefix}/%{_lib}/gcc/%{gcc_target_platform}/%{gcc_version}/libgcov.a
%dir %{_prefix}/libexec/gcc
%dir %{_prefix}/libexec/gcc/%{gcc_target_platform}
%dir %{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_version}
%{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_version}/cc1
%{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_version}/cc1plus
%{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_version}/collect2
%{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_version}/lto1
%{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_version}/lto-wrapper
%{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_version}/liblto_plugin.so
%{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_version}/go1
%attr(755,root,root) %{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_version}/cgo
%attr(755,root,root) %{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_version}/buildid
%attr(755,root,root) %{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_version}/test2json
%attr(755,root,root) %{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_version}/vet
%ifarch %{multilib_64_archs}
%dir %{_prefix}/%{_lib}/gcc/%{gcc_target_platform}/%{gcc_version}/32
%{_prefix}/%{_lib}/gcc/%{gcc_target_platform}/%{gcc_version}/32/libgo.so
%{_prefix}/%{_lib}/gcc/%{gcc_target_platform}/%{gcc_version}/32/libgo.a
%{_prefix}/%{_lib}/gcc/%{gcc_target_platform}/%{gcc_version}/32/libgobegin.a
%{_prefix}/%{_lib}/gcc/%{gcc_target_platform}/%{gcc_version}/32/libgolibbegin.a
%endif
%ifarch sparcv9 ppc %{multilib_64_archs}
%{_prefix}/%{_lib}/gcc/%{gcc_target_platform}/%{gcc_version}/libgo.so
%endif
%doc rpm.doc/go/*

%files -n libgo
%attr(755,root,root) %{_prefix}/%{_lib}/libgo.so.22*
%doc rpm.doc/libgo/*

%files -n libgo-devel
%dir %{_prefix}/%{_lib}/gcc
%dir %{_prefix}/%{_lib}/gcc/%{gcc_target_platform}
%dir %{_prefix}/%{_lib}/gcc/%{gcc_target_platform}/%{gcc_version}
%dir %{_prefix}/%{_lib}/go
%dir %{_prefix}/%{_lib}/go/%{gcc_version}
%{_prefix}/%{_lib}/go/%{gcc_version}/%{gcc_target_platform}
%ifarch %{multilib_64_archs}
%ifnarch sparc64 ppc64 ppc64p7
%dir %{_prefix}/%{_lib}/go
%dir %{_prefix}/%{_lib}/go/%{gcc_version}
%{_prefix}/%{_lib}/go/%{gcc_version}/%{gcc_target_platform}
%endif
%endif
%ifnarch sparcv9 sparc64 ppc ppc64 ppc64p7
%{_prefix}/%{_lib}/gcc/%{gcc_target_platform}/%{gcc_version}/libgobegin.a
%{_prefix}/%{_lib}/gcc/%{gcc_target_platform}/%{gcc_version}/libgolibbegin.a
%{_prefix}/%{_lib}/gcc/%{gcc_target_platform}/%{gcc_version}/libgo.so
%endif

%files -n libgo-static
%dir %{_prefix}/%{_lib}/gcc
%dir %{_prefix}/%{_lib}/gcc/%{gcc_target_platform}
%dir %{_prefix}/%{_lib}/gcc/%{gcc_target_platform}/%{gcc_version}
%ifnarch sparcv9 sparc64 ppc ppc64 ppc64p7
%{_prefix}/%{_lib}/gcc/%{gcc_target_platform}/%{gcc_version}/libgo.a
%endif
%endif
