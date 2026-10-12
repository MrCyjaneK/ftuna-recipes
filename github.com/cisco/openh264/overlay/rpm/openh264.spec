#
# spec file for package openh264
#
# Copyright (c) 2021 Red Hat, Inc.
# Copyright (c) 2022 Neal Gompa <ngompa@opensuse.org>.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via https://bugs.opensuse.org/
#


%global somajor 7
%global libname lib%{name}-%{somajor}
%global devname lib%{name}-devel

Name:           openh264
Version:        2.3.1
Release:        0
Summary:        H.264 codec library
Group:          Productivity/Multimedia/Other
License:        BSD-2-Clause
URL:            https://www.openh264.org/
Source0:        %{name}-%{version}.tar.bz2

BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  nasm

%description
OpenH264 is a codec library which supports H.264 encoding and decoding. It is
suitable for use in real time applications such as WebRTC.


%package     -n %{libname}
Summary:        H.264 codec library
Group:          System/Libraries

%description -n %{libname}
OpenH264 is a codec library which supports H.264 encoding and
decoding. It is suitable for use in real time applications such as
WebRTC.

This package contains libraries used by applications that use %{name}.

%package     -n %{devname}
Summary:        Development files for %{name}
Group:          Development/Libraries/C and C++
Provides:       %{name}-devel = %{version}-%{release}
Provides:       %{name}-devel%{?_isa} = %{version}-%{release}
Requires:       %{libname}%{?_isa} = %{version}-%{release}

%description -n %{devname}
This package contains libraries and header files for developing
applications that use %{name}.


%prep
%autosetup


%build
# Update the makefile with our build options
# Must be done in %%build in order to pick up correct LDFLAGS.
sed -i -e 's|^CFLAGS_OPT=.*$|CFLAGS_OPT=%{build_cflags}|' Makefile
sed -i -e 's|^PREFIX=.*$|PREFIX=%{_prefix}|' Makefile
sed -i -e 's|^LIBDIR_NAME=.*$|LIBDIR_NAME=%{_lib}|' Makefile
sed -i -e 's|^SHAREDLIB_DIR=.*$|SHAREDLIB_DIR=%{_libdir}|' Makefile
%if 0%{?suse_version} > 1550
sed -i -e '/^CFLAGS_OPT=/i LDFLAGS=%{build_ldflags}' Makefile
%endif

%make_build


%install
%make_install


%files -n %{libname}
%license LICENSE
%doc README.md
%{_libdir}/libopenh264.so.%{somajor}
%{_libdir}/libopenh264.so.%{version}

%files -n %{devname}
%{_includedir}/wels/
%{_libdir}/libopenh264.so
%{_libdir}/libopenh264.a
%{_libdir}/pkgconfig/openh264.pc


%changelog
