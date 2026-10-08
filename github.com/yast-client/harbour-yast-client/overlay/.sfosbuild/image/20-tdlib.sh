#!/bin/sh
# https://github.com/yast-client/td 721867254ad8885a7c3ad0a4c9d3c74855c48bde
set -eu

zypper --non-interactive in --force-resolution \
	ca-certificates \
	git \
	cmake \
	ninja \
	gperf \
	zlib-devel \
	openssl1.1-devel

src=/tmp/tdlib-src
git clone https://github.com/yast-client/td "$src"
git -C "$src" checkout --detach 721867254ad8885a7c3ad0a4c9d3c74855c48bde

lto=ON
case $(uname -m) in
i486|i686) lto=OFF ;;
esac
cmake -S "$src" -B "$src/build" -G Ninja \
	-DCMAKE_BUILD_TYPE=Release \
	-DCMAKE_INSTALL_PREFIX=/tmp/tdlib \
	-DCMAKE_INSTALL_LIBDIR=lib \
	-DTD_ENABLE_LTO=$lto
cmake --build "$src/build" --target install

lib=/opt/yast/tdlib/$(uname -m)/lib
mkdir -p "$lib"
cp -a /tmp/tdlib/lib/libtdjson.so* "$lib/"
