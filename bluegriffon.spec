%define _enable_debug_packages %{nil}
%define debug_package %{nil}
%global __requires_exclude ^libxul.*$
%global tarballdir  gecko-dev-042b84a

%global gecko_version   2.0.1
%global srcversion      042b84a

Summary:	The next-generation Web Editor
Name:		bluegriffon
Version:	3.1
Release:	1
License:	MPLv1.1 or GPLv2+ or LGPLv2+
Group:		Editors
Url:		http://bluegriffon.org/
Source0:	gecko-dev-%{srcversion}.tar.gz
Source1:	%{name}-%{version}.tar.gz

Source10:	%{name}.sh.in
Source11:	%{name}.sh
Source12:	%{name}.desktop


# build patches
Patch0:		fix-wformat-flag.patch
Patch1:		fix-link-flag-passing.patch
Patch2:		fix-for-bsdtar.patch
#Patch3:		fix-nss-version.patch
#Patch4:		firefox-gcc49.patch

# upstream patches
Patch10:	improve-resiliance-of-SystemResourceMonitor.stop.patch
Patch11:	remove-unused-variables-from-baseconfig.mk.patch
Patch12:	remove-version-number-from-install-dir.patch
Patch13:	fix-chrome-unicode-includes.patch

# custom default settings
Patch30:        bluegriffon-3.1-updates.patch

# op1 russian patch
#Patch31:        bluegriffon-1.7.2-op1-i18n.patch

BuildRequires:	autoconf2.1
BuildRequires:	desktop-file-utils
BuildRequires:	yasm
BuildRequires:	rust
BuildRequires:	cargo
BuildRequires:	pkgconfig(libpulse)
BuildRequires:	hunspell-devel
BuildRequires:	pkgconfig(gl)
#BuildRequires:	wireless-tools
BuildRequires:	zip
BuildRequires:	krb5-devel
BuildRequires:	libiw-devel
BuildRequires:	pkgconfig(freetype2)
#BuildRequires:	pkgconfig(gnome-vfs-2.0)
BuildRequires:	pkgconfig(gtk+-3.0)
BuildRequires:  pkgconfig(gtk+-2.0)
BuildRequires:	pkgconfig(gconf-2.0)
#BuildRequires:	pkgconfig(libgnomeui-2.0)
BuildRequires:	pkgconfig(libIDL-2.0)
BuildRequires:	pkgconfig(libstartup-notification-1.0)
#BuildRequires:	pkgconfig(pango)
BuildRequires:	pkgconfig(xrender)
BuildRequires:	pkgconfig(xt)

BuildRequires:	bzip2-devel
BuildRequires:	jpeg-devel
BuildRequires:	nss-static-devel
#BuildRequires:	pkgconfig(cairo)
BuildRequires:	pkgconfig(hunspell)
BuildRequires:	pkgconfig(lcms)
BuildRequires:	pkgconfig(libnotify)
BuildRequires:	pkgconfig(libpng)
BuildRequires:	pkgconfig(nspr)
BuildRequires:	pkgconfig(nss)
BuildRequires:	pkgconfig(sqlite)
BuildRequires:	pkgconfig(zlib)

Requires:	nss
Requires:	nspr

AutoProv:	no
Autoreq:	0

%description
BlueGriffon is a new WYSIWYG content editor for the World Wide Web.

Powered by Gecko, the rendering engine of Firefox, it's a modern
and robust solution to edit Web pages in conformance to the latest
Web Standards.

%files
%{_bindir}/%{name}
%{_libdir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.png

#----------------------------------------------------------------------------

%prep
echo TARGET %{name}-%{version}-%{release}
%setup -q -n %{tarballdir}
#tar xjf %{SOURCE0}
mkdir %{name}
tar xjf %{SOURCE1} --strip-components=1 --directory %{name}

patch -p1 <%{_builddir}/%{tarballdir}/%{name}/config/gecko_dev_content.patch
patch -p1 <%{_builddir}/%{tarballdir}/%{name}/config/gecko_dev_idl.patch
%patch0 -p1
%patch1 -p1
%patch2 -p1
#%%patch5 -p1

%patch10 -p1
%patch11 -p1
%patch12 -p1
%patch13 -p1

%patch30 -p1

# Otherwise build fails because it expects this dir to exist
mkdir -p js/src/.deps

# See http://bluegriffon.org/pages/Build-BlueGriffon
cat <<EOF_MOZCONFIG > .mozconfig 
CC=gcc
CXX=g++
#CC=/usr/bin/clang
#CXX=/usr/bin/clang++
#ac_add_options --enable-clang-plugin
#ac_add_options --enable-llvm-hacks

mk_add_options PYTHON=/usr/bin/python2
mk_add_options MOZ_OBJDIR=@TOPSRCDIR@/opt
mk_add_options MOZ_MAKE_FLAGS="-j16"
ac_add_options --enable-release
ac_add_options --with-distribution-id="OpenMandriva-Lx"
ac_add_options --enable-application=%{name}
ac_add_options --with-system-png
ac_add_options --prefix="\$PREFIX"
ac_add_options --libdir="\$LIBDIR"
ac_add_options --enable-system-sqlite
ac_add_options --with-system-nspr
ac_add_options --with-system-nss
ac_add_options --enable-system-hunspell
ac_add_options --enable-system-cairo
ac_add_options --enable-system-pixman
ac_add_options --with-system-jpeg
ac_add_options --with-system-zlib
ac_add_options --with-system-bz2
ac_add_options --with-pthreads
ac_add_options --disable-strip
ac_add_options --disable-tests
ac_add_options --disable-debug
ac_add_options --enable-optimize="-fpermissive \$MOZ_OPT_FLAGS -fPIC "
ac_add_options --enable-default-toolkit=cairo-gtk3
ac_add_options --enable-startup-notification
ac_add_options --disable-crashreporter
ac_add_options --enable-safe-browsing
ac_add_options --disable-updater
ac_add_options --enable-strip
EOF_MOZCONFIG


%build
MOZ_OPT_FLAGS=$(echo %{optflags} | sed -e 's/-Wall//' -e 's/-fexceptions/-fno-exceptions/g' -e 's/-gdwarf-4//')
export CFLAGS=$MOZ_OPT_FLAGS
export CXXFLAGS=$MOZ_OPT_FLAGS

export PREFIX='%{_prefix}'
export LIBDIR='%{_libdir}'

MOZ_APP_DIR=%{_libdir}/%{name}

#%%patch31 -p1

export LDFLAGS="-Wl,-rpath,${MOZ_APP_DIR}"

make -f client.mk build
#./mach build

%install
# No Make install for now :(
mkdir -p %{buildroot}%{_libdir}/%{name}
tar --create --file - --dereference --directory=opt/dist/bin --exclude xulrunner . \
  | tar --extract --file - --directory %{buildroot}%{_libdir}/%{name}

# Launcher
install -D -m 755 %{SOURCE11} %{buildroot}%{_bindir}/%{name}

# Shortcut
desktop-file-install  \
  --dir %{buildroot}%{_datadir}/applications \
  --add-category Development \
  --add-category Network \
  %{SOURCE12}

# Icons
install -D -m 644  bluegriffon/app/icons/default16.png  %{buildroot}%{_datadir}/icons/hicolor/16x16/apps/%{name}.png
install -D -m 644  bluegriffon/app/icons/default32.png  %{buildroot}%{_datadir}/icons/hicolor/32x32/apps/%{name}.png
install -D -m 644  bluegriffon/app/icons/default48.png  %{buildroot}%{_datadir}/icons/hicolor/48x48/apps/%{name}.png
install -D -m 644  bluegriffon/app/icons/default50.png  %{buildroot}%{_datadir}/icons/hicolor/16x16/apps/%{name}.png
install -D -m 644  bluegriffon/app/icons/%{name}128.png %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/%{name}.png

# install languages
# No longer needed as far as I can tell. itchka@compuserve.com
#cp bluegriffon/langpacks/*.xpi %{buildroot}%{_libdir}/%{name}/extensions/

# Use the system hunspell dictionaries
rm -rf %{buildroot}%{_libdir}/%{name}/dictionaries
ln -s %{_datadir}/myspell %{buildroot}%{_libdir}/%{name}/dictionaries

