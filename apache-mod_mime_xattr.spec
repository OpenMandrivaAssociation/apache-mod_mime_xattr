#Module-Specific definitions
%define mod_name mod_mime_xattr
%define mod_conf A96_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	Lets you use file system extended attributes data for MIME type detection
Name:		apache-%{mod_name}
Version:	0.4
Release:	%mkrel 3
Group:		System/Servers
License:	Apache License
URL:		http://0pointer.de/lennart/projects/mod_mime_xattr/
Source0:	http://0pointer.de/lennart/projects/mod_mime_xattr/mod_mime_xattr-%{version}.tar.gz
Source1:	%{mod_conf}
Patch0:		mod_mime_xattr-0.4-no_silly_checks_because_we_know_the_apache_version_is_ok.diff
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache >= 2.2.0
Requires:	apache-conf >= 2.2.0
Requires:	apache >= 2.2.0
Requires:	apache-mod_dav >= 2.2.0
Requires:	apache-mod_userdir >= 2.2.0
BuildRequires:	autoconf2.5
BuildRequires:	automake1.8
BuildRequires:	apache-devel >= 2.2.0
BuildRequires:	libattr-devel
BuildRequires:	file
BuildRequires:	lynx
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
mod_mime_xattr is a module for the Apache HTTPD 2.2 which may be used to set a
range of MIME properties of files served from a document tree with extended
attributes (EAs) as supported by the underlying file system. The current
version of mod_mime_xattr has support for Linux style EAs which are supported
by Linux 2.4 with the ACL/EA patches applied and vanilla Linux 2.6. The
following attributes may be used:

 * user.mime_type: set the MIME type of a file explicitly. This
   attribute is compatible with the [17]shared MIME database
   specification as published by [18]freedesktop.org
 * user.charset: set the charset used in a file
 * user.mime_encoding: set the MIME encoding of a file (e.g. gzip)
 * user.apache_handler: set the apache handler of a file explicitly

%prep

%setup -q -n %{mod_name}-%{version}
%patch0 -p0

cp %{SOURCE1} %{mod_conf}

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

%build
rm -f configure
libtoolize --force --copy; aclocal-1.8 ; autoheader; automake-1.8 --add-missing --copy --foreign; autoconf

%configure2_5x

%make


%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -d %{buildroot}%{_libdir}/apache-extramodules
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d

install -m0755 src/.libs/*.so %{buildroot}%{_libdir}/apache-extramodules/
install -m0644 %{mod_conf} %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

install -d %{buildroot}%{_var}/www/html/addon-modules
ln -s ../../../..%{_docdir}/%{name}-%{version} %{buildroot}%{_var}/www/html/addon-modules/%{name}-%{version}

%post
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc LICENSE README doc/README.html doc/style.css
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}
%{_var}/www/html/addon-modules/*
