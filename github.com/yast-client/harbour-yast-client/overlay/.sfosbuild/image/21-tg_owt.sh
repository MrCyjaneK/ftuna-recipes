#!/bin/sh
# https://github.com/yast-client/tg_owt babb73fdd922d5d22407c60a87765d7427b1dbe7
# libvpx 1024874c5919305883187e2953de8fcb4c3d7fa6
set -eu

export MAKEFLAGS="-j$(nproc)"

zypper --non-interactive in --force-resolution \
	ca-certificates \
	git \
	cmake \
	ninja \
	make \
	nasm \
	openssl1.1-devel \
	'pkgconfig(opus)' \
	'pkgconfig(libavcodec)' \
	'pkgconfig(libavformat)' \
	'pkgconfig(libavutil)' \
	'pkgconfig(libswresample)' \
	'pkgconfig(libswscale)' \
	'pkgconfig(libjpeg)' \
	'pkgconfig(libpulse)'
case $(uname -m) in
i486|i686|i386) zypper --non-interactive in --force-resolution yasm ;;
esac

src=/tmp/tg-owt-src
git clone https://github.com/yast-client/tg_owt "$src"
git -C "$src" checkout --detach babb73fdd922d5d22407c60a87765d7427b1dbe7
git -C "$src" submodule update --init --recursive
sed -i 's/GIT_TAG v1.16.0/GIT_TAG 1024874c5919305883187e2953de8fcb4c3d7fa6/; /GIT_SHALLOW/d' "$src/cmake/libvpx.cmake"

cmake -S "$src" -B "$src/build" -G Ninja \
	-DCMAKE_BUILD_TYPE=Release \
	-DBUILD_SHARED_LIBS=OFF \
	-DCMAKE_POSITION_INDEPENDENT_CODE=ON \
	-DCMAKE_C_FLAGS=-fPIC \
	-DCMAKE_CXX_FLAGS=-fPIC \
	-DCMAKE_INSTALL_LIBDIR=lib \
	-DCMAKE_INSTALL_PREFIX=/opt/yast/tg_owt/$(uname -m) \
	-DTG_OWT_USE_PIPEWIRE=OFF \
	-DTG_OWT_USE_X11=OFF \
	-DTG_OWT_BUILD_AUDIO_BACKENDS=ON
cmake --build "$src/build" --target install
