# CalendarTask RPM for Fedora

This repository rebuilds the proprietary CalendarTask Linux DEB as an RPM for
Fedora. The upstream Flutter bundle contains an absolute development RUNPATH;
the spec changes it to `$ORIGIN` so bundled plugins load from the installed
application directory.

The Fedora compatibility wrapper is process-local. It maps the application's
reads of `/etc/os-release`, `/usr/lib/os-release`, and `/etc/lsb-release` to an
Ubuntu-compatible file. It does not modify the host system. This works around
CalendarTask server-side handling that returned HTTP 500 for Fedora's release
identity. The application remains `src: linux` and its original version.

## Build

Install the Fedora build tools:

```bash
sudo dnf install -y rpm-build gcc binutils tar xz rpm
```

Place the upstream file at `calendartask_linux_x86.deb`, then run:

```bash
./build.sh
```

Or pass the DEB explicitly:

```bash
./build.sh /path/to/calendartask_linux_x86.deb
```

The RPM is written to `dist/`. To build and install it in one step:

```bash
./build.sh --install /path/to/calendartask_linux_x86.deb
```

The upstream DEB is intentionally not committed because it is a proprietary
binary and is ignored by Git.

The desktop entry is installed as `com.xdiarys.www.desktop` to match the
application ID embedded in the Flutter Linux runner. This is required for the
correct GNOME Wayland Alt+Tab icon; `StartupWMClass` is also provided for X11.
