%define use_ccache	1
%define ccachedir	~/.ccache-OOo%{mdvsuffix}
%{?_with_ccache: %global use_ccache 1}
%{?_without_ccache: %global use_ccache 0}


%define debug_package            %{nil}

%global nspr_version 4.8.7
%global nss_version 3.12.9
%global cairo_version 1.10
%global freetype_version 2.1.9
%global lcms_version 1.18
%global sqlite_version 3.7.6

%global mozappdir   %{_libdir}/bluegriffon
%global tarballdir  mozilla-2.0
%global svnmain     0
%global svnlocales  0
%global prever      %nil
#pre1

%global withxulrunner    0
%global gecko_version   2.0.1
#-1
%global srcversion      4.0.1

Summary:        The next-generation Web Editor
Summary(fr):    La nouvelle génération d'éditeur web
Summary(it):    La nuova generazione editor di web
Name:           bluegriffon
Version:        1.6.2
Release:        3
URL:            http://bluegriffon.org/
License:        MPLv1.1 or GPLv2+ or LGPLv2+
Group:          Editors
Source0:        firefox-%{srcversion}.tar.bz2
Source1:        %{name}-%{version}.tar.bz2
Source2:        %{name}-l10n-%{version}.tar.bz2

Source10:       %{name}.sh.in
Source11:       %{name}.sh
Source12:       %{name}.desktop

# build patches
Patch0:         %{name}-build.patch
Patch1:         mozilla-bz736961.patch
Patch2:         mozilla-bz722975.patch
Patch3:         bluegriffon.nsEditorApp.patch

BuildRoot:      %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

BuildRequires:  desktop-file-utils
BuildRequires:  autoconf2.1
BuildRequires:  alsa-lib
BuildRequires:  alsa
BuildRequires:  pkgconfig(alsa)
BuildRequires:  yasm
BuildRequires:  libmesagl-devel
%if %{withxulrunner}
BuildRequires:  xulrunner-devel
%endif
# = %{gecko_version}
#gecko-devel = %{gecko_version}


%if %{withxulrunner}
BuildRequires:  xulrunner2-devel >= %{xulrunner_version}
#xulrunner2-devel
Requires:       xulrunner2 >= %{xulrunner_version}
Conflicts:      xulrunner2 >= %{xulrunner_version_max}
%if %mdkversion >= 201000
BuildRequires:  gecko-devel = %{gecko_version}
%endif
%else
BuildRequires:  zip
BuildRequires:  libIDL-devel
BuildRequires:  gtk2-devel
BuildRequires:  gnome-vfs2-devel
BuildRequires:  pkgconfig(libgnomeui-2.0)
BuildRequires:  krb5-devel
BuildRequires:  pango-devel
BuildRequires:  freetype2-devel >= 2.1.9
%if %mdkversion >= 201010
%ifarch %ix86
BuildRequires:  pkgconfig(xt)
%endif
%ifarch x86_64
BuildRequires:  lib64xt-devel
%endif
%else
%ifarch %ix86
BuildRequires:  pkgconfig(xt)
%endif
%if %mdkversion >= 201010
%ifarch x86_64
BuildRequires:  lib64xt-devel
%endif
%endif
%if %mdkversion < 201010
%ifarch x86_64
BuildRequires:  lib64xt6-devel
%endif
%endif
%endif
BuildRequires:  pkgconfig(xrender)
BuildRequires:  startup-notification-devel
BuildRequires:  wireless-tools libiw-devel

# BR from Xulrunner
BuildRequires:  sqlite-devel
# >= %{sqlite_version}
BuildRequires:  nspr-devel >= %{nspr_version}
BuildRequires:  nss-devel >= %{nss_version}
BuildRequires:  hunspell-devel
BuildRequires:  cairo-devel
# >= %{cairo_version}
BuildRequires:  pkgconfig(libnotify)
BuildRequires:  lcms-devel >= %{lcms_version}
BuildRequires:  pkgconfig(libpng)
BuildRequires:  jpeg-devel = 1:1.2.1-1:2012.1
BuildRequires:  bzip2-devel
BuildRequires:  zlib-devel
BuildRequires:  libgnome-devel
#BuildRequires:  alsa-lib-devel
#BuildRequires:  autoconf213
#BuildRequires:  mesa-libGL-devel

Requires:       nss >= %{nss_version}
Requires:       nspr >= %{nspr_version}

%if %{withxulrunner}
%global xulbin xulrunner
%global grecnf gre
#Requires:       gecko-libs%{?_isa} = %{gecko_version}
%endif
%endif %{withxulrunner}

%description
BlueGriffon is a new WYSIWYG content editor for the World Wide Web.

Powered by Gecko, the rendering engine of Firefox 4, it's a modern
and robust solution to edit Web pages in conformance to the latest
Web Standards.

%description -l fr
BlueGriffon est un nouvel éditeur de page web WYSIWYG.

Basé sur Gecko, le moteur de rendu de Firefox 4, c'est une solution
moderne et fiable pour éditer des pages Web conformes aux dernières
normes w3c.

%description -l it
BlueGriffon è un nuovo editor di pagine web WYSIWYG.

Basato su Gecko, il motore di rendering di Firefox 4, Ã¨ una soluzione
moderna e robusta per un editor di pagine Web conforme alle piÃ¹ recenti
norme w3c.

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

# Upstream patches
%patch1 -p1 -b .bz736961
%patch2 -p1 -b .bz722975

#new patch
%patch3 -p1

#See http://bluegriffon.org/pages/Build-BlueGriffon
cat <<EOF_MOZCONFIG > .mozconfig 
mk_add_options MOZ_OBJDIR=@TOPSRCDIR@

ac_add_options --enable-application=%{name}

# --with-system-png is disabled because Mozilla requires APNG support in libpng
#ac_add_options --with-system-png
ac_add_options --prefix="\$PREFIX"
ac_add_options --libdir="\$LIBDIR"
ac_add_options --disable-cpp-exceptions
%if %mdkversion >= 200900
ac_add_options --enable-system-sqlite
%endif
%if %mdkversion < 201010
%ifarch %ix86
ac_add_options --with-system-nspr
ac_add_options --with-system-nss
%endif
%ifarch x86_64
#ac_add_options --with-system-nspr
#ac_add_options --with-system-nss
%endif
%endif
ac_add_options --enable-system-hunspell
%if %mdkversion >= 201100
ac_add_options --enable-system-cairo
%else
ac_add_options --disable-system-cairo
%endif
ac_add_options --enable-libnotify
#%else
#ac_add_options --disable-libnotify

ac_add_options --enable-system-lcms

%ifarch ppc ppc64
ac_add_options --disable-necko-wifi
ac_add_options --disable-ipc
%endif
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
%if %mdkversion >= 201100
ac_add_options --enable-libxul
%else
ac_add_options --disable-libxul
%endif
ac_add_options --disable-necko-wifi
ac_add_options --disable-ipc
EOF_MOZCONFIG

#%if %{withxulrunner}
echo ""  >> .mozconfig
%if %{withxulrunner}
echo "ac_add_options --with-libxul-sdk=\
$(pkg-config --variable=sdkdir libxul)" >> .mozconfig
%endif

%build
MOZ_OPT_FLAGS=$(echo $RPM_OPT_FLAGS | \
                     %{__sed} -e 's/-Wall//' -e 's/-fexceptions/-fno-exceptions/g')
export CFLAGS=$MOZ_OPT_FLAGS
export CXXFLAGS=$MOZ_OPT_FLAGS

export PREFIX='%{_prefix}'
export LIBDIR='%{_libdir}'

MOZ_SMP_FLAGS=-j1
[ -z "$RPM_BUILD_NCPUS" ] && \
     RPM_BUILD_NCPUS="`/usr/bin/getconf _NPROCESSORS_ONLN`"
[ "$RPM_BUILD_NCPUS" -gt 1 ] && MOZ_SMP_FLAGS=-j$RPM_BUILD_NCPUS

MOZ_APP_DIR=%{_libdir}/%{name}

export LDFLAGS="-Wl,-rpath,${MOZ_APP_DIR}"
make -f client.mk build STRIP="/bin/true" MOZ_MAKE_FLAGS="$MOZ_SMP_FLAGS"


%install
%{__rm} -rf $RPM_BUILD_ROOT

# No Make install for now :(
mkdir -p $RPM_BUILD_ROOT/%{mozappdir}
tar --create --file - --dereference --directory=dist/bin --exclude xulrunner . \
  | tar --extract --file - --directory $RPM_BUILD_ROOT/%{mozappdir}

# Launcher
%if %{withxulrunner}
install -d -m 755 $RPM_BUILD_ROOT%{_bindir}
XULRUNNER_DIR=`pkg-config --variable=libdir libxul | %{__sed} -e "s,%{_libdir},,g"`
%{__cat} %{SOURCE10} | %{__sed} -e "s,XULRUNNER_DIRECTORY,$XULRUNNER_DIR,g" \
                     | %{__sed} -e "s,XULRUNNER_BIN,%{xulbin},g" \
		     | %{__sed} -e "s,GRE_CONFIG,%{grecnf},g"  \
  > $RPM_BUILD_ROOT%{_bindir}/%{name}
%{__chmod} 755 $RPM_BUILD_ROOT%{_bindir}/%{name}
%else
install -D -m 755 %{SOURCE11} $RPM_BUILD_ROOT%{_bindir}/%{name}
%endif

# Shortcut
desktop-file-install  \
  --dir $RPM_BUILD_ROOT%{_datadir}/applications \
  --add-category Development \
  --add-category Network \
  %{SOURCE12}

# Icons
install -D -m 644  bluegriffon/app/icons/default16.png  $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/16x16/apps/%{name}.png
install -D -m 644  bluegriffon/app/icons/default32.png  $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/32x32/apps/%{name}.png
install -D -m 644  bluegriffon/app/icons/default48.png  $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/48x48/apps/%{name}.png
install -D -m 644  bluegriffon/app/icons/default50.png  $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/16x16/apps/%{name}.png
install -D -m 644  bluegriffon/app/icons/%{name}128.png $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/128x128/apps/%{name}.png

# install languages
cp bluegriffon/langpacks/*.xpi $RPM_BUILD_ROOT%{_libdir}/bluegriffon/extensions/



# Use the system hunspell dictionaries
%{__rm} -rf $RPM_BUILD_ROOT/%{mozappdir}/dictionaries
ln -s %{_datadir}/myspell $RPM_BUILD_ROOT%{mozappdir}/dictionaries


%post
update-desktop-database &> /dev/null || :
touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
if [ -x %{_bindir}/gtk-update-icon-cache ]; then
  %{_bindir}/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor || :
fi


%postun
if [ $1 -eq 0 ] ; then
    touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi
update-desktop-database &> /dev/null || :

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{_bindir}/%{name}
%{mozappdir}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/16x16/apps/%{name}.png
%{_datadir}/icons/hicolor/32x32/apps/%{name}.png
%{_datadir}/icons/hicolor/48x48/apps/%{name}.png
%{_datadir}/icons/hicolor/128x128/apps/%{name}.png


%changelog



