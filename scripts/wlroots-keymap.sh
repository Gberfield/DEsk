#!/bin/sh
# Apply the parent-keymap fix only to the private wlroots source build.
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
patch_file=$root/patches/wlroots-0.18-parent-keymap.patch
if [ "$#" -eq 3 ] && [ "$1" = --check-installed ]; then
    # PKG_CONFIG_PATH alone permits fallback to an unrelated system copy.
    # Keep that fallback for dependencies, but verify wlroots itself is private.
    prefix=$(CDPATH= cd -- "$2" && pwd -P) || exit 1
    pcdir=$prefix/lib/pkgconfig
    [ -f "$pcdir/wlroots-0.18.pc" ] || exit 1
    export PKG_CONFIG_PATH="$pcdir:$prefix/share/pkgconfig"
    pkg-config --exact-version="$3" wlroots-0.18 || exit 1
    found=$(pkg-config --variable=pcfiledir wlroots-0.18) || exit 1
    found=$(CDPATH= cd -- "$found" && pwd -P) || exit 1
    expected=$(CDPATH= cd -- "$pcdir" && pwd -P) || exit 1
    [ "$found" = "$expected" ] || exit 1
    libdir=$(pkg-config --variable=libdir wlroots-0.18) || exit 1
    libdir=$(CDPATH= cd -- "$libdir" && pwd -P) || exit 1
    expected=$(CDPATH= cd -- "$prefix/lib" && pwd -P) || exit 1
    [ "$libdir" = "$expected" ] || exit 1
    library=$libdir/libwlroots-0.18.so
    [ -f "$library" ] || exit 1
    library=$(readlink -f -- "$library") || exit 1
    case "$library" in "$libdir"/*) exit 0 ;; *) exit 1 ;; esac
fi
if [ "$#" -ne 1 ]; then
    echo "usage: $0 --fingerprint | WLROOTS_SOURCE | --check-installed PREFIX VERSION" >&2
    exit 2
fi
if [ "$1" = --fingerprint ]; then
    patch_sum=$(sha256sum "$patch_file")
    printf '%s\n' "${patch_sum%% *}"
    exit 0
fi
patch --batch --forward --directory="$1" -p1 < "$patch_file"
