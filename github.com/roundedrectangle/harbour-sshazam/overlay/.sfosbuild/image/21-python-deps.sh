#!/bin/sh
# shazamio 0.8.1 / shazamio-core 1.1.2, built from the sdist with maturin.
# pasimple 0.0.3
set -eu

zypper --non-interactive in --force-resolution \
	clang-devel \
	alsa-lib-devel \
	python3-devel \
	python3-pip

libdir=/usr/lib
if [ -e /usr/lib64/libclang.so.15 ]; then
	libdir=/usr/lib64
fi
if [ ! -e "$libdir/libclang.so" ]; then
	ln -sf libclang.so.15 "$libdir/libclang.so"
fi

export LIBCLANG_PATH="$libdir"
export PATH=/opt/sshazam/rust/bin:$PATH
export CARGO_HOME=/opt/sshazam/cargo
export CARGO_PROFILE_RELEASE_STRIP=symbols
rustc --version

python3 -m pip install --no-cache-dir 'maturin[patchelf]==1.4.0'

sum=e26e6b967286eca82e3fb90a20695d5e13f163e30c57e2543fe2ca98ec6dfa51
tmp=/tmp/shazamio_core.tar.gz
curl -fL --retry 3 -o "$tmp" \
	https://files.pythonhosted.org/packages/a4/96/973f87fbb5d9b1384b0495475af28a688f7ea353ac137ea9fa03fd3f2f56/shazamio_core-1.1.2.tar.gz
echo "${sum}  ${tmp}" | sha256sum -c
src=/tmp/shazamio_core-src
rm -rf "$src"
mkdir -p "$src"
tar -C "$src" -xzf "$tmp"
set -- "$src"/*
cd "$1"

wheels=/tmp/shazamio-wheels
rm -rf "$wheels"
mkdir -p "$wheels"
python3 -m maturin build --release --interpreter python3 --out "$wheels"

dest=/opt/sshazam/deps
rm -rf "$dest"
mkdir -p "$dest"
python3 -m pip install --no-cache-dir --target="$dest" \
	"$wheels"/shazamio_core-*.whl \
	'shazamio==0.8.1' \
	'pasimple==0.0.3'
rm -rf "$dest/bin" "$src" "$tmp" "$wheels"
