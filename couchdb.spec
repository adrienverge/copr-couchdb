# Copyright 2016 Adrien Vergé
#
# Inspired from
# http://copr-dist-git.fedorainfracloud.org/cgit/gorbyo/epel7-couchdb/couchdb.git/tree/couchdb.spec?h=epel7&id=6d5a4ac1e3f04981af41bbf6f49022754a83d416

%define package_version  2.0.0RC4
%define upstream_version 2.0.0-RC4

Name:          couchdb
Version:       %{package_version}
Release:       7%{?dist}
Summary:       A document database server, accessible via a RESTful JSON API
Group:         Applications/Databases
License:       Apache
URL:           http://couchdb.apache.org/
Source0:       https://couchdb-ci.s3-eu-west-1.amazonaws.com/release-candidate/apache-couchdb-%{upstream_version}.tar.gz
Source1:       %{name}.service
Patch1:        0001-Trigger-cookie-renewal-on-_session.patch

BuildRequires: erlang
BuildRequires: erlang-asn1
BuildRequires: erlang-erts >= R13B
BuildRequires: erlang-eunit >= R15B
BuildRequires: erlang-os_mon
BuildRequires: erlang-xmerl
BuildRequires: js-devel
BuildRequires: libicu-devel
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
%patch1 -p1 -b .cookie-renewal

# Have conf in /etc/couchdb, not /opt/couchdb/etc
sed -i 's|$ROOTDIR/etc/vm.args|/%{_sysconfdir}/%{name}/vm.args|' \
  rel/overlay/bin/couchdb


%build
./configure --skip-deps --disable-docs

# Have conf in /etc/couchdb, not /opt/couchdb/etc
sed -i 's|filename:join(code:root_dir(), "etc")|"%{_sysconfdir}/%{name}"|' \
  src/config/src/config_app.erl

make release %{?_smp_mflags}

# Store databases in /var/lib/couchdb
sed -i 's|\./data\b|%{_sharedstatedir}/%{name}|g' rel/couchdb/etc/default.ini


%install
mkdir -p %{buildroot}/opt
cp -r rel/couchdb %{buildroot}/opt

# Have conf in /etc/couchdb, not /opt/couchdb/etc
mkdir -p %{buildroot}%{_sysconfdir}
mv %{buildroot}/opt/couchdb/etc %{buildroot}%{_sysconfdir}/%{name}
mkdir %{buildroot}%{_sysconfdir}/%{name}/local.d
mkdir %{buildroot}%{_sysconfdir}/%{name}/default.d

install -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/%{name}.service

mkdir -p %{buildroot}%{_sharedstatedir}/%{name}

rmdir %{buildroot}/opt/couchdb/var/log %{buildroot}/opt/couchdb/var


%pre
getent group %{name} >/dev/null || groupadd -r %{name}
getent passwd %{name} >/dev/null || \
  useradd -r -g %{name} -d %{_sharedstatedir}/%{name} -s /sbin/nologin %{name}

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service


%files
/opt/couchdb

%dir %{_sysconfdir}/%{name}
%dir %{_sysconfdir}/%{name}/local.d
%dir %{_sysconfdir}/%{name}/default.d
%config %attr(0644, %{name}, %{name}) %{_sysconfdir}/%{name}/default.ini
%config(noreplace) %attr(0644, %{name}, %{name}) %{_sysconfdir}/%{name}/local.ini
%config(noreplace) %attr(0644, %{name}, %{name}) %{_sysconfdir}/%{name}/vm.args

%dir %attr(0755, %{name}, %{name}) %{_sharedstatedir}/%{name}

%{_unitdir}/%{name}.service


%changelog
* Thu Sep 8 2016 Adrien Vergé <adrienverge@gmail.com> 2.0.0RC4-7
- Store data in /var/lib/couchdb instead of /opt/couchdb/data
- Remove unneeded BuildRequires
- Remove unused /opt/couchdb/var/log dir

* Fri Sep 2 2016 Adrien Vergé <adrienverge@gmail.com> 2.0.0RC4-6
- Patch https://github.com/apache/couchdb-couch/pull/194/commits/9970f18

* Thu Sep 1 2016 Adrien Vergé <adrienverge@gmail.com> 2.0.0RC4-5
- Restore `--disable-docs` because they take 12 MiB

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
