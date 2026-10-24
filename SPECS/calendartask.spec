Name:           calendartask
Version:        1.0.9
Release:        3%{?dist}
Summary:        CalendarTask desktop time-management application

# The upstream archive contains prebuilt binaries and no corresponding sources.
%global debug_package %{nil}

License:        Proprietary
URL:            https://www.xdiarys.com/
Source0:        calendartask_linux_x86.deb
Source1:        calendartask-compat.c
Source2:        ubuntu-os-release
Source3:        calendartask-wrapper
BuildArch:      x86_64

# Runtime ELF dependencies are generated from the executable and bundled plugins.
# This accurately maps their SONAME requirements to the Fedora package database.
BuildRequires:  binutils
BuildRequires:  tar
BuildRequires:  xz
BuildRequires:  gcc

%description
CalendarTask is a desktop calendar and task-management application from Xiaowei
Cloud Inc.

%prep
%setup -q -c -T
ar p %{SOURCE0} data.tar.xz > data.tar.xz
tar -xJf data.tar.xz
# Upstream plugins contain a stale absolute build-tree RUNPATH.  Retarget it
# to their installed directory without changing the ELF string-table layout.
for library in opt/CalendarTask/lib/lib*_plugin.so; do
  perl -0777 -pi -e 'my $old = q{/home/luwei/code/linux/pccalendar/linux/flutter/ephemeral}; my $new = q{$ORIGIN} . "\0" x (length($old) - length(q{$ORIGIN})); s/\Q$old\E/$new/ or die "missing upstream RUNPATH\n";' "$library"
done
gcc -shared -fPIC -Wl,-z,now -Wl,-z,relro -ldl -o opt/CalendarTask/lib/libcalendartask-compat.so %{SOURCE1}
mv opt/CalendarTask/CalendarTask opt/CalendarTask/CalendarTask.bin
cp %{SOURCE2} opt/CalendarTask/data/ubuntu-os-release
cp %{SOURCE3} opt/CalendarTask/CalendarTask
chmod 0755 opt/CalendarTask/CalendarTask
mv usr/share/applications/CalendarTask.desktop usr/share/applications/com.xdiarys.www.desktop
printf '\nStartupWMClass=com.xdiarys.www\n' >> usr/share/applications/com.xdiarys.www.desktop

%install
rm -rf %{buildroot}
install -d %{buildroot}
cp -a opt usr %{buildroot}/

%files
/opt/CalendarTask
%{_datadir}/applications/com.xdiarys.www.desktop
%{_datadir}/icons/hicolor/*/apps/com.xdiarys.www.png

%changelog
* Sat Oct 24 2026 CalendarTask RPM conversion <root@localhost> - 1.0.9-3
- Match the desktop file ID to the embedded GTK/Wayland application ID.
- Add StartupWMClass for X11 window matching.
- Add Fedora-to-Ubuntu process-local compatibility for the login API.
- Retarget bundled plugin RUNPATHs to $ORIGIN.
