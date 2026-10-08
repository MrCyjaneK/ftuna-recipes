#!/bin/sh
set -eu

ARCH=aarch64
while getopts "hja:t:w:" OPTION; do
	case $OPTION in
	a) ARCH=$OPTARG ;;
	*) ;;
	esac
done

arch=$(uname -m)
rm -rf tdlib tg_owt
mkdir -p tdlib tg_owt
cp -a /opt/yast/tdlib/$arch tdlib/$ARCH
cp -a /opt/yast/tg_owt/$arch tg_owt/$ARCH
