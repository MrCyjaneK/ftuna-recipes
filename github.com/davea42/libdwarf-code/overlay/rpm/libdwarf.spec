#
# spec file for package libdwarf
#
# Copyright (c) 2023 SUSE LLC
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


Name:           libdwarf
Version:        0.7.0
Release:        0
Summary:        Access DWARF debugging information
License:        GPL-2.0-or-later AND LGPL-2.1-or-later
Group:          Development/Libraries/C and C++
URL:            https://prevanders.net/dwarf.html
Source:         %{name}-%{version}.tar.bz2
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  binutils-devel
BuildRequires:  elfutils-libelf-devel
BuildRequires:  libtool
BuildRequires:  pkgconfig(zlib)

%description
libdwarf is a library of functions to provide read/write DWARF
debugging records.

%package -n libdwarf0
Summary:        Library to access DWARF information in object files
License:        LGPL-2.1-or-later
Group:          System/Libraries
Conflicts:      libdwarf1

%description -n libdwarf0
Library of functions to provide creation of DWARF debugging
information records, DWARF line number information, DWARF address
range and pubnames information, weak names information, and DWARF
frame description information.

%package devel
Summary:        Development files for libdwarf
License:        LGPL-2.1-or-later
Group:          Development/Libraries/C and C++
Requires:       libdwarf0 = %{version}
Requires:       elfutils-libelf-devel

%description devel
Contains the static libraries and header files of libdwarf.

libdwarf is a library of functions to provide read/write DWARF
debugging records.

%package tools
Summary:        DWARF-related tools
License:        GPL-2.0-or-later
Group:          Development/Tools/Building
# Debian name for the package; provide it for cross-discoverability.
Provides:       dwarfutils = %{version}-%{release}

%description tools
Contains dwarfdump, a tool to access DWARF debug information.

%package doc
Summary:        Documentation for libdwarf
License:        GPL-2.0-or-later
Group:          Documentation/Other

%description doc
Documentation for libdwarf.

%prep
%autosetup -p1

%build
sh autogen.sh
export CFLAGS="%{optflags}"
CFLAGS="$CFLAGS -fPIC" LDFLAGS="-pie" %configure --enable-shared
%make_build

%install
%make_install
mkdir %{buildroot}%{_includedir}/libdwarf
cp -l %{buildroot}%{_includedir}/libdwarf-0/*.h %{buildroot}%{_includedir}/libdwarf

%post -n libdwarf0 -p /sbin/ldconfig
%postun -n libdwarf0 -p /sbin/ldconfig

%files -n libdwarf0
%license src/lib/libdwarf/LIBDWARFCOPYRIGHT src/lib/libdwarf/LGPL.txt
%{_libdir}/libdwarf.so.0*

%files devel
%{_libdir}/libdwarf.so
%{_libdir}/libdwarf.a
%{_libdir}/pkgconfig/libdwarf.pc
%{_includedir}/libdwarf
%{_includedir}/libdwarf-0

%files tools
%license src/bin/dwarfdump/GPL.txt
%doc src/bin/dwarfdump/README
%{_bindir}/dwarfdump
%{_mandir}/man1/dwarfdump*
%dir %{_datadir}/dwarfdump
%{_datadir}/dwarfdump/dwarfdump.conf

%files doc
%doc doc/*.pdf
%doc src/lib/libdwarf/README

%changelog
