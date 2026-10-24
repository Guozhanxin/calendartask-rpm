#!/usr/bin/env bash
set -euo pipefail

repo_root=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
deb_path="${CALENDARTASK_DEB:-$repo_root/calendartask_linux_x86.deb}"
install_after_build=0

usage() {
    printf 'Usage: %s [--install] [path/to/calendartask_linux_x86.deb]\n' "$0"
}

while (($#)); do
    case "$1" in
        --install) install_after_build=1 ;;
        -h|--help) usage; exit 0 ;;
        -*) printf 'Unknown option: %s\n' "$1" >&2; usage >&2; exit 2 ;;
        *) deb_path=$1 ;;
    esac
    shift
done

[[ -f "$deb_path" ]] || {
    printf 'DEB not found: %s\n' "$deb_path" >&2
    printf 'Place calendartask_linux_x86.deb in the repository root or pass its path.\n' >&2
    exit 1
}

for command_name in ar gcc rpmbuild rpm tar xz; do
    command -v "$command_name" >/dev/null || {
        printf 'Missing command: %s\n' "$command_name" >&2
        printf 'On Fedora: sudo dnf install -y rpm-build gcc binutils tar xz rpm\n' >&2
        exit 1
    }
done

build_top="$repo_root/.rpmbuild"
temp_top="${TMPDIR:-/tmp}/calendartask-rpm-tmp"
dist_dir="$repo_root/dist"
rm -rf "$build_top" "$dist_dir" "$temp_top"
mkdir -p "$build_top"/{BUILD,BUILDROOT,RPMS,SRPMS,SOURCES,SPECS} "$dist_dir" "$temp_top"

cp "$deb_path" "$build_top/SOURCES/calendartask_linux_x86.deb"
cp "$repo_root/SPECS/calendartask.spec" "$build_top/SPECS/"
cp "$repo_root/SOURCES/calendartask-compat.c" "$build_top/SOURCES/"
cp "$repo_root/SOURCES/calendartask-wrapper" "$build_top/SOURCES/"
cp "$repo_root/SOURCES/ubuntu-os-release" "$build_top/SOURCES/"

rpmbuild \
    --define "_topdir $build_top" \
    --define "_tmppath $temp_top" \
    -ba "$build_top/SPECS/calendartask.spec"

rpm_path=$(find "$build_top/RPMS" -type f -name 'calendartask-*.rpm' -print -quit)
[[ -n "$rpm_path" ]] || { printf 'RPM was not generated\n' >&2; exit 1; }
cp "$rpm_path" "$dist_dir/"
rpm_path="$dist_dir/$(basename "$rpm_path")"

rpm -K "$rpm_path"
printf 'Built: %s\n' "$rpm_path"

if ((install_after_build)); then
    sudo dnf install -y "$rpm_path"
fi
