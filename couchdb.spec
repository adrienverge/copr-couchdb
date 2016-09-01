# Copyright 2016 Adrien Vergé
#
# Inspired from
# http://copr-dist-git.fedorainfracloud.org/cgit/gorbyo/epel7-couchdb/couchdb.git/tree/couchdb.spec?h=epel7&id=6d5a4ac1e3f04981af41bbf6f49022754a83d416
#
# Build locally with:
#   rpmbuild -bs couchdb.spec
#   mock -r epel-7-x86_64 rebuild ~/rpmbuild/SRPMS/couchdb-2.0.0*.src.rpm

%define package_version  2.0.0RC4
%define upstream_version 2.0.0-RC4

%define nodejs_src https://rpm.nodesource.com/pub_4.x/el/7/x86_64/nodejs-4.5.0-1nodesource.el7.centos.x86_64.rpm

Name:          couchdb
Version:       %{package_version}
Release:       1%{?dist}
Summary:       A document database server, accessible via a RESTful JSON API
Group:         Applications/Databases
License:       Apache
URL:           http://couchdb.apache.org/
# The source packages needs to contain a git index. Generate with:
#   git clone git://github.com/apache/couchdb.git -b 2.0.0-RC4
#   tar -czf couchdb-2.0.0-RC4.tar.gz couchdb
Source0:       couchdb-%{upstream_version}.tar.gz
Source1:       %{name}.service

BuildRequires: autoconf
BuildRequires: autoconf-archive
BuildRequires: automake
BuildRequires: curl-devel >= 7.18.0
BuildRequires: erlang
BuildRequires: erlang-asn1
BuildRequires: erlang-erts >= R13B
BuildRequires: erlang-eunit >= R15B
BuildRequires: erlang-os_mon
BuildRequires: erlang-xmerl
BuildRequires: git
BuildRequires: help2man
BuildRequires: js-devel
BuildRequires: libicu-devel
BuildRequires: libtool
BuildRequires: perl-Test-Harness
BuildRequires: systemd

#Requires:      erlang-crypto%{?_isa}
#Requires:      erlang-erts%{?_isa} >= R16B
#Requires:      erlang-ibrowse%{?_isa} >= 4.0.1
#Requires:      erlang-inets%{?_isa}
#Requires:      erlang-kernel%{?_isa}
#Requires:      erlang-mochiweb%{?_isa}
#Requires:      erlang-oauth%{?_isa}
#Requires:      erlang-os_mon%{?_isa}
#Requires:      erlang-sd_notify%{?_isa}
#Requires:      erlang-snappy%{?_isa}
#Requires:      erlang-ssl%{?_isa}
#Requires:      erlang-stdlib%{?_isa} >= R16B
#Requires:      erlang-tools%{?_isa}
#Requires:      erlang-xmerl%{?_isa}

Requires(pre): shadow-utils
Requires(post): systemd
Requires(preun): systemd


%description
Apache CouchDB is a distributed, fault-tolerant and schema-free
document-oriented database accessible via a RESTful HTTP/JSON API.
Among other features, it provides robust, incremental replication
with bi-directional conflict detection and resolution, and is
queryable and indexable using a table-oriented view engine with
JavaScript acting as the default view definition language.


%prep
%setup -q -n couchdb

# Install Node.js 4 and npm locally.
# Cannot put as BuildRequires because Node.js 4 isn't packaged for CentOS 7.
pushd %{_builddir}
curl -s %{nodejs_src} | rpm2cpio - | cpio -idm
sed -i 's|/usr/bin/node|/usr/bin/env node|g' \
  usr/lib/node_modules/npm/bin/npm-cli.js
popd


%build
./configure --disable-docs
PATH=%{_builddir}/usr/bin:$PATH make release %{?_smp_mflags}


%install
mkdir -p %{buildroot}/opt
cp -r rel/couchdb %{buildroot}/opt

install -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/%{name}.service


%pre
getent group %{name} >/dev/null || groupadd -r %{name}
getent passwd %{name} >/dev/null || \
  useradd -r -g %{name} -d /opt/couchdb -s /sbin/nologin %{name}

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service


%files
%defattr(-, %{name}, %{name})
/opt/couchdb
%{_unitdir}/%{name}.service


%changelog
* Wed Aug 31 2016 Adrien Vergé <adrienverge@gmail.com> 2.0.0RC4-1
- Initial RPM release
