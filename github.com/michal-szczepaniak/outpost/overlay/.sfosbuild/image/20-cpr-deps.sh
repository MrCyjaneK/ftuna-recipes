#!/bin/sh
# cpr e3413506f73eeeafcecabb4ac652aa5560b8fde7 fetches these during cmake.
# zlib-ng tag 2.1.3, curl 7.80.0.
set -eu

dest=/opt/outpost
mkdir -p "$dest"

zlib="$dest/zlib-ng-2.1.3.tar.gz"
curl -fL --retry 3 -o "$zlib" "https://github.com/zlib-ng/zlib-ng/archive/refs/tags/2.1.3.tar.gz"
echo "d20e55f89d71991c59f1c5ad1ef944815e5850526c0d9cd8e504eaed5b24491a  ${zlib}" | sha256sum -c

curl_tar="$dest/curl-7.80.0.tar.xz"
curl -fL --retry 3 -o "$curl_tar" "https://github.com/curl/curl/releases/download/curl-7_80_0/curl-7.80.0.tar.xz"
echo "a132bd93188b938771135ac7c1f3ac1d3ce507c1fcbef8c471397639214ae2ab  ${curl_tar}" | sha256sum -c
