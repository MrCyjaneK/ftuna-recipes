#!/bin/sh
# https://github.com/yast-client/tlottie b6b01b833c900142639afc7c3fc5f502a1237471
set -eu
src=/tmp/tlottie
git clone https://github.com/yast-client/tlottie "$src"
git -C "$src" checkout --detach b6b01b833c900142639afc7c3fc5f502a1237471
export PATH=/opt/yast/rust/bin:$PATH
export CARGO_HOME=/opt/yast/cargo
cargo fetch --locked --manifest-path "$src/Cargo.toml"
rm -rf "$src"
