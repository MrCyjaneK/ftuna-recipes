Name:           tdlib
Summary:        tdlib
Version:        1.8.68
Release:        1%{?dist}
License:        Boost Software License 1.0
Source0:        %{name}-%{version}.tar.bz2
BuildRequires:	cmake
BuildRequires:	gperf
BuildRequires:	zlib-devel
BuildRequires:	openssl-devel

%description

%prep
%autosetup -n %{name}-%{version}

%build
mkdir build
cd build
%cmake .. -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=Off
make %{?_smp_mflags} -j$(nproc)


%install
rm -rf $RPM_BUILD_ROOT
cd build
make install DESTDIR=$RPM_BUILD_ROOT


%clean
rm -rf build
rm -rf $RPM_BUILD_ROOT

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
/usr/include/td/telegram/Client.h
/usr/include/td/telegram/Log.h
/usr/include/td/telegram/td_api.h
/usr/include/td/telegram/td_api.hpp
/usr/include/td/telegram/td_json_client.h
/usr/include/td/telegram/td_log.h
/usr/include/td/telegram/tdjson_export.h
/usr/include/td/tl/TlObject.h
/usr/lib/cmake/Td/TdConfig.cmake
/usr/lib/cmake/Td/TdConfigVersion.cmake
/usr/lib/cmake/Td/TdTargets-release.cmake
/usr/lib/cmake/Td/TdTargets.cmake
/usr/lib/cmake/Td/TdStaticTargets-release.cmake
/usr/lib/cmake/Td/TdStaticTargets.cmake
/usr/lib/libtdactor.a
/usr/lib/libtdclient.a
/usr/lib/libtdcore.a
/usr/lib/libtddb.a
/usr/lib/libtdjson.so
/usr/lib/libtdjson.so.%{version}
/usr/lib/libtdjson_private.a
/usr/lib/libtdjson_static.a
/usr/lib/libtdnet.a
/usr/lib/libtdsqlite.a
/usr/lib/libtdapi.a
/usr/lib/libtdutils.a
/usr/lib/libtde2e.a
/usr/lib/libtdmtproto.a
/usr/lib/pkgconfig/tdactor.pc
/usr/lib/pkgconfig/tdapi.pc
/usr/lib/pkgconfig/tdclient.pc
/usr/lib/pkgconfig/tdcore.pc
/usr/lib/pkgconfig/tddb.pc
/usr/lib/pkgconfig/tdjson.pc
/usr/lib/pkgconfig/tdjson_private.pc
/usr/lib/pkgconfig/tdjson_static.pc
/usr/lib/pkgconfig/tdnet.pc
/usr/lib/pkgconfig/tdsqlite.pc
/usr/lib/pkgconfig/tdutils.pc
/usr/lib/pkgconfig/tde2e.pc
/usr/lib/pkgconfig/tdmtproto.pc
%defattr(-,root,root,-)