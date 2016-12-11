Name:     rohc
Summary:  The RObust Header Compression (ROHC) library
Group:    System Environment/Libraries
License:  LGPLv2+
URL:      https://rohc-lib.org/

Epoch:    0
Version:  2.0.0
Release:  1.%{packager}

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Source: %{name}-%{version}.tar.xz

Patch1: %{name}-%{version}-install-rohc_stats.sh.patch
Patch2: %{name}-%{version}-gnuplot-not-mandatory-for-build.patch
Patch3: %{name}-%{version}-fix-gcc61-warnings.patch

# do we build and run tests?
# libpcap and cmocka required by unit tests
#  - RHEL >= 6
#  - CentOS >= 6
#  - all others
%if 0%{?rhel_version} || 0%{?centos_ver}
# RHEL or CentOS
%if 0%{?rhel_version} >= 600
%define autoconf 1
%define no_frame_larger_than_warning 0
%define rohc_sniffer 1
%define rohc_test 1
%define pcap_name libpcap1
%else
%if 0%{?centos_ver} >= 6
%define autoconf 1
%define no_frame_larger_than_warning 0
%define rohc_sniffer 1
%define rohc_test 1
%define pcap_name libpcap
%else
# CentOS 5 is unable to cope with newer autoconf and automake scripts
%define autoconf 0
# CentOS 5 gcc does not handle -Wframe-larger-than=N
%define no_frame_larger_than_warning 1
# CentOS 5 does not handle O_NOFOLLOW required by the sniffer
%define rohc_sniffer 0
# CentOS 5 does not provide cmocka, even in EPEL
%define rohc_test 0
%define pcap_name libpcap
%endif
%endif
# end RHEL or CentOS
%else
# !RHEL && !CentOS
%define autoconf 1
%define no_frame_larger_than_warning 0
%define rohc_sniffer 1
%define rohc_test 1
%define pcap_name libpcap
# end !RHEL && !CentOS
%endif

%if %{rohc_test}
BuildRequires: libcmocka-devel
%endif
BuildRequires: %{pcap_name}-devel

%global _hardened_build 1

# do we generate documentation?
#  - RHEL >= 6
#  - CentOS >= 6
#  - all others
%if 0%{?rhel_version} || 0%{?centos_ver}
# RHEL or CentOS
%if 0%{?rhel_version} >= 600
%define rohc_doc 1
%else
%if 0%{?centos_ver} >= 6
%define rohc_doc 1
%else
%define rohc_doc 0
%endif
%endif
# end RHEL or CentOS
%else
# !RHEL && !CentOS
%define rohc_doc 1
# end !RHEL && !CentOS
%endif

%description
The ROHC library implements the RObust Header Compression (ROHC)
algorithms as defined by the IETF in RFC3095.


%package tools
Summary:       Miscellaneous tools that come along the ROHC library
Group:         Development/Libraries
Requires:      %{name} = %{epoch}:%{version}-%{release}
Requires:      %{pcap_name}
BuildRequires: %{pcap_name}-devel
# rohc_stats.sh uses gnuplot to draw graphs
Requires:      gnuplot
%if %{rohc_doc}
BuildRequires: help2man
%endif
%if %{autoconf} == 0
BuildRequires: gnuplot
%endif

%description tools
Miscellaneous tools that come along the ROHC library.

The ROHC library implements the RObust Header Compression (ROHC)
algorithms as defined by the IETF in RFC3095.


%package devel
Summary:       Files for development of applications which will use the ROHC library
Group:         Development/Libraries
BuildArch:     noarch
Requires:      %{name} = %{epoch}:%{version}-%{release}

%description devel
Files for development of applications which will use the ROHC library.

The ROHC library implements the RObust Header Compression (ROHC)
algorithms as defined by the IETF in RFC3095.


%package doc
Summary:       API documentation of the ROHC library
Group:         Development/Libraries
BuildArch:     noarch
Requires:      %{name} = %{epoch}:%{version}-%{release}
%if %{rohc_doc}
BuildRequires: doxygen
BuildRequires: graphviz
# Fedora 24 (and greater?) requires to choose between libgs.so implementations
%if 0%{?fedora} >= 24
BuildRequires: ghostscript-core
%endif
%endif

%description doc
API documentation of the ROHC library.

The ROHC library implements the RObust Header Compression (ROHC)
algorithms as defined by the IETF in RFC3095.


%prep
# unpack sources
%setup -q
# apply bugfix patches
%if %{autoconf}
%patch1 -p 1
%patch2 -p 1
%endif
%if %{no_frame_larger_than_warning}
sed -i -e 's|-Wframe-larger-than=1024||g' configure
%endif
%patch3 -p 1

%build
# patch changed configure.ac
%if %{autoconf}
aclocal || :
libtoolize --force || :
autoconf || :
autoheader || :
automake --add-missing || :
%endif
# configure for tools, doc and tests
%configure \
	--enable-app-performance \
%if %{rohc_sniffer}
	--enable-app-sniffer \
%endif
	--enable-app-stats \
%if %{rohc_doc}
	--enable-doc \
%endif
	--enable-examples \
	--disable-fail-on-warning \
	--disable-fortify-sources \
%if %{rohc_test}
	--enable-rohc-tests \
%endif
	--enable-shared \
	--disable-static
make clean
# build the library, tools and doc
make %{?_smp_mflags} all

%if %{rohc_test}
%check
# build and run tests
make %{?_smp_mflags} check
%endif

%install
rm -rf %{buildroot}
# install library, tools and doc
make install DESTDIR=%{buildroot}
# remove useless libtool .la file
rm -f %{buildroot}/%{_libdir}/librohc.la

%clean
rm -rf %{buildroot}

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%defattr(0644, root, root, 0755)
# libraries
%{_libdir}/librohc.so
%{_libdir}/librohc.so.3
%{_libdir}/librohc.so.3.0.0
# basic documentation
%dir %{_defaultdocdir}/%{name}/
%{_docdir}/%{name}/AUTHORS.md
%{_docdir}/%{name}/AUTHORS
%{_docdir}/%{name}/COPYING
%{_docdir}/%{name}/ChangeLog
%{_docdir}/%{name}/INSTALL.md
%{_docdir}/%{name}/INSTALL
%{_docdir}/%{name}/README.md
%{_docdir}/%{name}/README
# general man pages
%if %{rohc_doc}
%{_mandir}/man7/rohc.7.gz
%{_mandir}/man7/rohc_protocol.7.gz
%{_mandir}/man7/rohc_library.7.gz
%endif

%files tools
%defattr(0644, root, root, 0755)
# library tools
%{_bindir}/rohc_test_performance
%{_bindir}/rohc_gen_stream
%{_bindir}/rohc_stats
%if %{autoconf}
%{_bindir}/rohc_stats.sh
%endif
%if %{rohc_sniffer}
%{_sbindir}/rohc_sniffer
%endif
# tools man pages
%{_mandir}/man1/*.1.gz

%files devel
%defattr(0644, root, root, 0755)
# pkgconfig definition
%{_libdir}/pkgconfig/rohc.pc
# library headers
%dir %{_includedir}/%{name}/
%{_includedir}/%{name}/rohc.h
%{_includedir}/%{name}/rohc_buf.h
%{_includedir}/%{name}/rohc_comp.h
%{_includedir}/%{name}/rohc_decomp.h
%{_includedir}/%{name}/rohc_packets.h
%{_includedir}/%{name}/rohc_time.h
%{_includedir}/%{name}/rohc_traces.h
# code examples
%dir %{_docdir}/%{name}/
%dir %{_docdir}/%{name}/examples/
%{_docdir}/%{name}/examples/*.c

%files doc
%defattr(0644, root, root, 0755)
# doxygen documentation in HTML format
%if %{rohc_doc}
%dir %{_docdir}/%{name}/
%dir %{_docdir}/%{name}/html/
%{_docdir}/%{name}/html/*
# man pages for development
%{_mandir}/man3/*.3.gz
%endif

%changelog
* Sun Dec 11 2016 Didier Barvaux <didier@barvaux.org>
- Disable unit tests on CentOS < 6 and RHEL < 6
- Do not build man pages for tools on CentOS < 6 and RHEL < 6
- Install rohc_stats.sh script
- Make gnuplot check non fatal at build time, this is a runtime dep
- Do not force build flags, let distributions choose
- Do not stop on build warnings, be robust to new warnings
- Fedora 24 (and greater?) requires to choose between libgs.so implementations
- Fix GCC 6.1 warnings on Fedora 24
- Disable patches that require autoconf rebuild on CentOS 5
- Disable ROHC sniffer on CentOS 5
- Disable GCC -Wframe-larger-than=N on CentOS 5
* Sat Jun 25 2016 Didier Barvaux <didier@barvaux.org>
- Remove deprecated tunnel and fuzzer apps
- Install man pages
- Remove now useless latex dependency for doc
* Mon May 20 2013 Didier Barvaux <didier@barvaux.org>
- Replace --enable-rohc-apps by --enable-app-fuzzer --enable-app-tunnel
  --enable-app-performance --enable-app-sniffer.
* Thu May  9 2013 Didier Barvaux <didier@barvaux.org>
- depend on libpcap1 on RHEL >= 6
- define devel and doc subpackages as noarch
- add texlive-bin as build dependency for OpenSuse
- add texlive-latex-bin-bin dependency for Fedora >= 18
- _replace _defaultdocdir by _docdir
- rework the way we decide whether doc shall be generated or not
- use libpcap1-devel instead of libpcap-devel on RHEL6
- do not generate documentation on CentOS5 and RHEL5
- add graphviz-gd as build dependency on OpenSuse
* Wed May  8 2013 Didier Barvaux <didier@barvaux.org>
- add the test archive as additional source
- add graphviz as build dependency for doc subpackage
- add texlive-latex as build dependency for doc subpackage
- split tools in a subpackage
- add build and runtime dependencies for tools
- first version.
