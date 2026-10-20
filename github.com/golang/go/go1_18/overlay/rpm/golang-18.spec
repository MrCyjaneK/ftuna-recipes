Name:           golang-18
Version:        1.18.10
Release:        0
Summary:        Go 1.18 compiler and tools
License:        BSD-3-Clause
URL:            https://go.dev/
Source0:        %{name}-%{version}.tar.bz2
BuildRequires:  bash
BuildRequires:  binutils
BuildRequires:  gcc
BuildRequires:  gcc-go
BuildRequires:  glibc-devel

# The toolchain stores its own paths. Stripping and debuginfo are not useful here.
%define debug_package %{nil}
%global __strip /bin/true

# src and misc contain Plan 9 and perl helpers. They are not used to run the compiler.
%global __requires_exclude_from ^/usr/lib/golang-18/(src|misc)/.*$

%global goroot %{_prefix}/lib/golang-18

%description
Go 1.18.10, bootstrapped with GCC's Go compiler.
The whole toolchain is installed under %{goroot}, so another
Go version can be installed beside it.

%prep
%setup -q

%build
boot=%{_builddir}/go-bootstrap
rm -rf "$boot"
mkdir -p "$boot/bin"
cat > "$boot/bin/go" << 'EOF'
#!/bin/sh
# make.bash points GOROOT at this directory. gccgo's go tool must keep
# its own GOROOT, where libgo's sources live.
unset GOROOT
exec /usr/bin/go.gcc "$@"
EOF
chmod 755 "$boot/bin/go"

export GOROOT_BOOTSTRAP=$boot
export GOROOT_FINAL=%{goroot}
export GOCACHE=%{_builddir}/go-cache
export GO111MODULE=off
export GOPROXY=off
cd src
bash ./make.bash

%install
rm -rf %{buildroot}
dest=%{buildroot}%{goroot}
mkdir -p "$dest"
cd %{_builddir}/%{name}-%{version}
rm -rf pkg/bootstrap pkg/obj
for part in api bin lib misc pkg src VERSION LICENSE PATENTS; do
  if [ -e "$part" ]; then
    cp -a "$part" "$dest/"
  fi
done

%check
export GOROOT=%{_builddir}/%{name}-%{version}
export PATH="$GOROOT/bin:$PATH"
export GO111MODULE=off
export GOPROXY=off
go version
cat > %{_builddir}/hello.go << 'EOF'
package main

import "fmt"

func main() {
	fmt.Println("ok")
}
EOF
go run %{_builddir}/hello.go

%files
%license LICENSE
%dir %{goroot}
%{goroot}/*

%changelog
