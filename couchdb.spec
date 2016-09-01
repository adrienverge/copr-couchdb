# Copyright 2016 Adrien Vergé
#
# Inspired from
# http://copr-dist-git.fedorainfracloud.org/cgit/gorbyo/epel7-couchdb/couchdb.git/tree/couchdb.spec?h=epel7&id=6d5a4ac1e3f04981af41bbf6f49022754a83d416

%define package_version  2.0.0RC4
%define upstream_version 2.0.0-RC4

Name:          couchdb
Version:       %{package_version}
Release:       4%{?dist}
Summary:       A document database server, accessible via a RESTful JSON API
Group:         Applications/Databases
License:       Apache
URL:           http://couchdb.apache.org/
Source0:       https://couchdb-ci.s3-eu-west-1.amazonaws.com/release-candidate/apache-couchdb-%{upstream_version}.tar.gz
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
BuildRequires: js-devel
BuildRequires: libicu-devel
BuildRequires: libtool
BuildRequires: perl-Test-Harness
BuildRequires: systemd

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
%setup -q -n apache-couchdb-%{upstream_version}

# Have conf in /etc/couchdb, not /opt/couchdb/etc
sed -i 's|$ROOTDIR/etc/vm.args|/%{_sysconfdir}/%{name}/vm.args|' \
  rel/overlay/bin/couchdb


%build
./configure --skip-deps

# Have conf in /etc/couchdb, not /opt/couchdb/etc
sed -i 's|filename:join(code:root_dir(), "etc")|"%{_sysconfdir}/%{name}"|' \
  src/config/src/config_app.erl

make release %{?_smp_mflags}


%install
mkdir -p %{buildroot}/opt
cp -r rel/couchdb %{buildroot}/opt

# Have conf in /etc/couchdb, not /opt/couchdb/etc
mkdir -p %{buildroot}%{_sysconfdir}
mv %{buildroot}/opt/couchdb/etc %{buildroot}%{_sysconfdir}/%{name}
mkdir %{buildroot}%{_sysconfdir}/%{name}/local.d
mkdir %{buildroot}%{_sysconfdir}/%{name}/default.d

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

%dir %{_sysconfdir}/%{name}
%dir %{_sysconfdir}/%{name}/local.d
%dir %{_sysconfdir}/%{name}/default.d
%config %{_sysconfdir}/%{name}/default.ini
%config(noreplace) %{_sysconfdir}/%{name}/local.ini
%config(noreplace) %{_sysconfdir}/%{name}/vm.args

%{_unitdir}/%{name}.service


%changelog
* Thu Sep 1 2016 Adrien Vergé <adrienverge@gmail.com> 2.0.0RC4-4
- Don't install `npm` because Fauxton is already built
- Remove `--disable-docs` because they are already built

* Thu Sep 1 2016 Adrien Vergé <adrienverge@gmail.com> 2.0.0RC4-3
- Use dist version from Apache instead of git sources
- Remove unneeded Requires
- Remove unneeded BuildRequires `help2man`

* Wed Aug 31 2016 Adrien Vergé <adrienverge@gmail.com> 2.0.0RC4-2
- Put conf files in /etc/couchdb instead of /opt/couchdb/etc

* Wed Aug 31 2016 Adrien Vergé <adrienverge@gmail.com> 2.0.0RC4-1
- Initial RPM release
