Name:           golang-19
Version:        1.19.13
Release:        0
Summary:        Go 1.19 compiler and tools
License:        BSD-3-Clause
URL:            https://go.dev/
Source0:        %{name}-%{version}.tar.bz2
BuildRequires:  bash
BuildRequires:  binutils
BuildRequires:  gcc
BuildRequires:  glibc-devel
BuildRequires:  golang-18

# The toolchain stores its own paths. Stripping and debuginfo are not useful here.
%define debug_package %{nil}
%global __strip /bin/true

# src and misc contain Plan 9 and perl helpers. They are not used to run the compiler.
%global __requires_exclude_from ^/usr/lib/golang-19/(src|misc)/.*$

%global goroot %{_prefix}/lib/golang-19
%global bootstrap_goroot %{_prefix}/lib/golang-18

%description
Go 1.19.13, bootstrapped with the Go 1.18 toolchain.
The whole toolchain is installed under %{goroot}, so another
Go version can be installed beside it.

%prep
%setup -q

%build
export GOROOT_BOOTSTRAP=%{bootstrap_goroot}
export GOROOT_FINAL=%{goroot}
export GOCACHE=%{_builddir}/go-cache
export GO111MODULE=off
export GOPROXY=off
# Native 32-bit cmd/compile fills its own address space (the failure was
# 3938353152 bytes mapped, then a 4MB allocation failed). The host was not
# out of RAM. One package at a time and GOGC=10 keep that native compile
# under 4GB. aarch64 is unchanged.
case $(uname -m) in
aarch64|arm64|x86_64) ;;
*) export GOMAXPROCS=1 GOGC=10 ;;
esac
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
