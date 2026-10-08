#!/bin/sh
# model_version from xiph/rnnoise 70f1d256acd4b34a572f999a05c87bf00b67730d
set -eu

hash=0a8755f8e2d834eff6a54714ecc7d75f9932e845df35f8b59bc52a7cfe6e8b37
tmp=/tmp/rnnoise_data.tar.gz
curl -fL --retry 3 -o "$tmp" "https://media.xiph.org/rnnoise/models/rnnoise_data-${hash}.tar.gz"
echo "${hash}  ${tmp}" | sha256sum -c
mkdir -p /opt/yast/rnnoise-model
tar -C /opt/yast/rnnoise-model -xzf "$tmp"
rm -f "$tmp"
