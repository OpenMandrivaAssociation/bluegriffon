%define _enable_debug_packages %{nil}
%define debug_package %{nil}

%global tarballdir  mozilla-2.0

%global withxulrunner   0
%global gecko_version   2.0.1
%global srcversion      9db46ddfb517

Summary:	The next-generation Web Editor
Name:		bluegriffon
Version:	1.7.2
Release:	2
License:	MPLv1.1 or GPLv2+ or LGPLv2+
Group:		Editors
Url:		http://bluegriffon.org/
Source0:	firefox-%{srcversion}.tar.bz2
Source1:	%{name}-%{version}.tar.bz2
Source2:	%{name}-l10n-%{version}.tar.bz2

Source10:	%{name}.sh.in
Source11:	%{name}.sh
Source12:	%{name}.desktop

# build patches
Patch0:		bluegriffon-build.patch
Patch1:		mozilla-2.0-build-env.patch
Patch2:		mozilla-2.0-no-sig-verify.patch

# upstream patches
Patch10:	firefox-cairo_shared.patch

# custom default settings
Patch30:	bluegriffon-1.7.2-updates.patch

BuildRequires:	autoconf2.1
BuildRequires:	desktop-file-utils
BuildRequires:	yasm
BuildRequires:	pkgconfig(alsa)
BuildRequires:	pkgconfig(gl)

%if %{withxulrunner}
%global xulbin xulrunner
%global grecnf gre
BuildRequires:	pkgconfig(libxul)
Requires:	xulrunner
#BuildRequires:	gecko-devel = %{gecko_version}
%else
BuildRequires:	wireless-tools
BuildRequires:	zip
BuildRequires:	krb5-devel
BuildRequires:	libiw-devel
BuildRequires:	pkgconfig(freetype2)
BuildRequires:	pkgconfig(gnome-vfs-2.0)
BuildRequires:	pkgconfig(gtk+-2.0)
BuildRequires:	pkgconfig(libgnomeui-2.0)
BuildRequires:	pkgconfig(libIDL-2.0)
BuildRequires:	pkgconfig(libstartup-notification-1.0)
BuildRequires:	pkgconfig(pango)
BuildRequires:	pkgconfig(xrender)
BuildRequires:	pkgconfig(xt)

# BR from Xulrunner
BuildRequires:	bzip2-devel
BuildRequires:	jpeg-devel
BuildRequires:	nss-static-devel
BuildRequires:	pkgconfig(cairo)
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
%endif %{withxulrunner}

AutoProv:	no

%description
BlueGriffon is a new WYSIWYG content editor for the World Wide Web.

Powered by Gecko, the rendering engine of Firefox 4, it's a modern
and robust solution to edit Web pages in conformance to the latest
Web Standards.

%prep
echo TARGET %{name}-%{version}-%{release}
%setup -q -n %{tarballdir}
%if %{withxulrunner}
echo use GECKO %{gecko_version}
%else
echo use Bundled GECKO
%endif
tar xjf %{SOURCE1}
tar xjf %{SOURCE2} --directory %{name}

%patch0 -p0 -b .build
%patch1 -p1
%patch2 -p1

%patch10 -p1

%patch30 -p1

# Otherwise build fails because it expects this dir to exist
mkdir -p js/src/.deps

# See http://bluegriffon.org/pages/Build-BlueGriffon
cat <<EOF_MOZCONFIG > .mozconfig 
mk_add_options MOZ_OBJDIR=@TOPSRCDIR@

ac_add_options --enable-application=%{name}

#--with-system-png requires APNG support in libpng
ac_add_options --with-system-png
ac_add_options --prefix="\$PREFIX"
ac_add_options --libdir="\$LIBDIR"
ac_add_options --disable-cpp-exceptions
ac_add_options --enable-system-sqlite
ac_add_options --with-system-nspr
ac_add_options --with-system-nss
ac_add_options --enable-system-hunspell
ac_add_options --enable-system-cairo
ac_add_options --enable-libnotify
ac_add_options --enable-system-lcms
ac_add_options --with-system-jpeg
ac_add_options --with-system-zlib
ac_add_options --with-system-bz2
ac_add_options --with-pthreads
ac_add_options --disable-strip
ac_add_options --disable-activex
ac_add_options --disable-activex-scripting
ac_add_options --disable-tests
ac_add_options --disable-airbag
ac_add_options --enable-places
ac_add_options --enable-storage
ac_add_options --enable-shared
ac_add_options --disable-static
ac_add_options --disable-mochitest
ac_add_options --disable-installer
ac_add_options --disable-debug
ac_add_options --enable-optimize="\$MOZ_OPT_FLAGS"
ac_add_options --enable-xinerama
ac_add_options --enable-default-toolkit=cairo-gtk2
ac_add_options --disable-xprint
ac_add_options --enable-pango
ac_add_options --enable-svg
ac_add_options --enable-canvas
ac_add_options --enable-startup-notification
ac_add_options --disable-javaxpcom
ac_add_options --disable-crashreporter
ac_add_options --enable-safe-browsing
ac_add_options --disable-updater
ac_add_options --enable-gio
ac_add_options --disable-gnomevfs
ac_add_options --enable-libxul
EOF_MOZCONFIG

%if %{withxulrunner}
echo "ac_add_options --with-libxul-sdk=\
$(pkg-config --variable=sdkdir libxul)" >> .mozconfig
%endif

%build
MOZ_OPT_FLAGS=$(echo %{optflags} | sed -e 's/-Wall//' -e 's/-fexceptions/-fno-exceptions/g' -e 's/-gdwarf-4//')
export CFLAGS=$MOZ_OPT_FLAGS
export CXXFLAGS=$MOZ_OPT_FLAGS

export PREFIX='%{_prefix}'
export LIBDIR='%{_libdir}'

MOZ_APP_DIR=%{_libdir}/%{name}

export LDFLAGS="-Wl,-rpath,${MOZ_APP_DIR}"

make -f client.mk build

%install
# No Make install for now :(
mkdir -p %{buildroot}%{_libdir}/%{name}
tar --create --file - --dereference --directory=dist/bin --exclude xulrunner . \
  | tar --extract --file - --directory %{buildroot}%{_libdir}/%{name}

# Launcher
%if %{withxulrunner}
install -d -m 755 %{buildroot}%{_bindir}
XULRUNNER_DIR=`pkg-config --variable=libdir libxul | sed -e "s,%{_libdir},,g"`
cat %{SOURCE10} | sed -e "s,XULRUNNER_DIRECTORY,$XULRUNNER_DIR,g" \
                     | sed -e "s,XULRUNNER_BIN,%{xulbin},g" \
                     | sed -e "s,GRE_CONFIG,%{grecnf},g"  \
  > %{buildroot}%{_bindir}/%{name}
chmod 755 %{buildroot}%{_bindir}/%{name}
%else
install -D -m 755 %{SOURCE11} %{buildroot}%{_bindir}/%{name}
%endif

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
cp bluegriffon/langpacks/*.xpi %{buildroot}%{_libdir}/%{name}/extensions/

# Use the system hunspell dictionaries
rm -rf %{buildroot}%{_libdir}/%{name}/dictionaries
ln -s %{_datadir}/myspell %{buildroot}%{_libdir}/%{name}/dictionaries

%files
%{_bindir}/%{name}
%{_libdir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/16x16/apps/%{name}.png
%{_datadir}/icons/hicolor/32x32/apps/%{name}.png
%{_datadir}/icons/hicolor/48x48/apps/%{name}.png
%{_datadir}/icons/hicolor/128x128/apps/%{name}.png

