#!/bin/sh
# https://static.rust-lang.org/dist/rust-1.75.0
set -eu
case $(uname -m) in
aarch64) triple=aarch64-unknown-linux-gnu sum=30828cd904fcfb47f1ac43627c7033c903889ea4aca538f53dcafbb3744a9a73 ;;
armv7l) triple=armv7-unknown-linux-gnueabihf sum=bd876a75f72040d96be2fb882770b16b482ac0ab15d7e3ad24e6d25b7c74bcf7 ;;
i486|i686) triple=i686-unknown-linux-gnu sum=107b8d8825deab338f338b15f047829da6225bb34644790847e96f0957c6678f ;;
*)
	echo "23-rust.sh: unknown arch $(uname -m)" >&2
	exit 1
	;;
esac
ver=1.75.0
tmp=/tmp/rust.tar.gz
curl -fL --retry 3 -o "$tmp" "https://static.rust-lang.org/dist/rust-${ver}-${triple}.tar.gz"
echo "${sum}  ${tmp}" | sha256sum -c
tar -C /tmp -xzf "$tmp"
/tmp/rust-${ver}-${triple}/install.sh --prefix=/opt/yast/rust --disable-ldconfig
rm -rf /tmp/rust-${ver}-${triple} "$tmp"
