# Copyright 2020 Adrien Vergé

# Do not include debuginfo symlinks from /usr/lib/.build-id because they
# conflict with other erlang packages:
%define _build_id_links none
# Needed to avoid build error: No build ID note found in [...].o
%undefine _missing_build_ids_terminate_build

Name:          couchdb
Version:       3.3.1
Release:       1%{?dist}
Summary:       A document database server, accessible via a RESTful JSON API
Group:         Applications/Databases
License:       Apache
URL:           http://couchdb.apache.org/
Source0:       http://apache.mirrors.ovh.net/ftp.apache.org/dist/couchdb/source/%{version}/apache-couchdb-%{version}.tar.gz
Source1:       %{name}.service
Source2:       usr-bin-couchdb

%if 0%{?rhel} && 0%{?rhel} < 9
BuildRequires: erlang = 24.1.7
%else
BuildRequires: erlang = 24.3.4.5
%endif
BuildRequires: gcc
BuildRequires: gcc-c++
BuildRequires: libicu-devel
BuildRequires: systemd
%if 0%{?rhel} && 0%{?rhel} < 9
BuildRequires: mozjs60-devel
%else
BuildRequires: mozjs78-devel
%endif

%if 0%{?rhel} && 0%{?rhel} < 9
Requires: mozjs60
%else
Requires: mozjs78
%endif
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
%setup -q -n apache-couchdb-%{version}


%build
%if 0%{?rhel} && 0%{?rhel} < 9
./configure --skip-deps --disable-docs --spidermonkey-version 60
%else
./configure --skip-deps --disable-docs --spidermonkey-version 78
%endif

make release %{?_smp_mflags}

# Store databases in /var/lib/couchdb
sed -i 's|\./data\b|%{_sharedstatedir}/%{name}|g' rel/couchdb/etc/default.ini


%install
mkdir -p %{buildroot}/opt
rm rel/couchdb/bin/couchdb.cmd
cp -r rel/couchdb %{buildroot}/opt

install -D -m 755 %{SOURCE2} %{buildroot}%{_bindir}/%{name}

# Have conf in /etc/couchdb, not /opt/couchdb/etc
mkdir -p %{buildroot}%{_sysconfdir}
mv %{buildroot}/opt/couchdb/etc %{buildroot}%{_sysconfdir}/%{name}

install -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/%{name}.service

mkdir -p %{buildroot}%{_sharedstatedir}/%{name}

rmdir %{buildroot}/opt/couchdb/var/log %{buildroot}/opt/couchdb/var

# Added by Adrien, because /usr/lib/rpm/check-rpaths complained about openssl.
# Other option: try %global __brp_check_rpaths %{nil}
export QA_RPATHS=$(( 0x0001|0x0002 ))


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
%{_bindir}/%{name}

%config %attr(0644, %{name}, %{name}) %{_sysconfdir}/%{name}/default.d/README
%config %attr(0644, %{name}, %{name}) %{_sysconfdir}/%{name}/default.ini
%config %attr(0644, %{name}, %{name}) %{_sysconfdir}/%{name}/local.d/README
%config(noreplace) %attr(0644, %{name}, %{name}) %{_sysconfdir}/%{name}/local.ini
%config(noreplace) %attr(0644, %{name}, %{name}) %{_sysconfdir}/%{name}/vm.args

%dir %attr(0755, %{name}, %{name}) %{_sharedstatedir}/%{name}

%{_unitdir}/%{name}.service


%changelog
* Wed Jan 11 2023 Baptiste Ravier <baptiste.ravier@gmail.com> 3.3.1-1
- Update to new upstream version

* Thu Jan 05 2023 Baptiste Ravier <baptiste.ravier@gmail.com> 3.3.0-1
- Update to new upstream version

* Tue Nov 15 2022 Adrien Vergé <adrienverge@gmail.com> 3.2.2-3
- Use custom re-packaged mozjs78 for EPEL 9

* Mon Nov 14 2022 Adrien Vergé <adrienverge@gmail.com> 3.2.2-2
- Use Erlang 24.3.4.5 and shut down check-rpaths to compile for Fedora 37

* Tue Apr 19 2022 Hoël Iris <hoel.iris@gmail.com> 3.2.2-1
- Update to new upstream version
- Use Erlang = 24.1.7 (previously: >= 23, < 25) for Fedora 35+

* Thu Nov 25 2021 Baptiste Ravier <baptiste.ravier@gmail.com> 3.2.1-2
- Use Erlang >= 23 (previously: >= 22) for CentOS 8 and Fedora 34+

* Mon Nov 08 2021 Baptiste Ravier <baptiste.ravier@gmail.com> 3.2.1-1
- Update to new upstream version

* Wed Oct 13 2021 Baptiste Ravier <baptiste.ravier@gmail.com> 3.2.0-2
- Use mozjs78 (previously: 68) for Fedora 34+

* Tue Oct 12 2021 Baptiste Ravier <baptiste.ravier@gmail.com> 3.2.0-1
- Update to new upstream version
- Use Erlang >= 22 and < 25 for CentOS 8 and Fedora 34+
- Drop CentOS 7 support

* Tue Oct 5 2021 Adrien Vergé <adrienverge@gmail.com> 3.1.2-1
- Update to new upstream version

* Mon Sep 21 2020 Adrien Vergé <adrienverge@gmail.com> 3.1.1-1
- Update to new upstream version

* Sun Jul 19 2020 Adrien Vergé <adrienverge@gmail.com> 3.1.0-2
- Backport CouchDB 3 to CentOS 7

* Thu Jul 02 2020 Adrien Vergé <adrienverge@gmail.com> 3.1.0-1
- Upgrade to CouchDB 3

* Mon Jun 29 2020 Adrien Vergé <adrienverge@gmail.com> 2.3.1-8
- Rebuild for CentOS 8

* Mon Dec 23 2019 Adrien Vergé <adrienverge@gmail.com> 2.3.1-7
- Improve logging when Systemd wait for CouchDB stop
- Update patch for -couch_ini since pull request

* Mon Nov 25 2019 Adrien Vergé <adrienverge@gmail.com> 2.3.1-6
- Properly wait termination on systemd 'systemctl stop couchdb'

* Fri Nov 01 2019 Adrien Vergé <adrienverge@gmail.com> 2.3.1-5
- Update patch for -couch_ini since pull request
- Support Fedora 31

* Thu Oct 10 2019 Adrien Vergé <adrienverge@gmail.com> 2.3.1-4
- Support CentOS 8

* Mon Oct 7 2019 Adrien Vergé <adrienverge@gmail.com> 2.3.1-3
- Do not include debuginfo symlinks from /usr/lib/.build-id

* Tue Oct 1 2019 Adrien Vergé <adrienverge@gmail.com> 2.3.1-2
- Use couch-js-devel instead of couch-js, and update docs

* Mon Mar 18 2019 Adrien Vergé <adrienverge@gmail.com> 2.3.1-1
- Update to new upstream version
- Use Erlang 21 (previously: 20) for CentOS 7 and Fedora 30+

* Mon Jan 28 2019 Adrien Vergé <adrienverge@gmail.com> 2.3.0-2
- Apply a patch to add snooze_period_ms for finer tuning, see https://github.com/apache/couchdb/pull/1880

* Tue Dec 11 2018 Adrien Vergé <adrienverge@gmail.com> 2.3.0-1
- Update to new upstream version (skip 2.2 that has bugs)
- Customizing args file is now supported upstream

* Mon Sep 24 2018 Adrien Vergé <adrienverge@gmail.com> 2.1.2-2
- Use Erlang 20 (previously: 16)

* Mon Jul 16 2018 Adrien Vergé <adrienverge@gmail.com> 2.1.2-1
- Update to new upstream version
- Build our custom couch-js like described on https://github.com/apache/couchdb-pkg/tree/7768c00/js

* Mon Apr 9 2018 Adrien Vergé <adrienverge@gmail.com> 2.1.1-2
- Increase number of open file descriptors

* Tue Dec 5 2017 Adrien Vergé <adrienverge@gmail.com> 2.1.1-1
- Update to new upstream version

* Fri Oct 6 2017 Adrien Vergé <adrienverge@gmail.com> 2.1.0-2
- Increase number of open file descriptors

* Tue Sep 5 2017 Adrien Vergé <adrienverge@gmail.com> 2.1.0-1
- Update to new upstream version

* Sat Jul 15 2017  Adrien Vergé <adrienverge@gmail.com> 2.0.0-5
- Remove patch https://github.com/apache/couchdb-couch/pull/194/commits/9970f18
- Rebuild to fix view doc error in Fedora 26

* Sat Dec 3 2016 Adrien Vergé <adrienverge@gmail.com> 2.0.0-4
- Improve signal forwarding (both SIGINT and SIGTERM)

* Mon Sep 26 2016 Adrien Vergé <adrienverge@gmail.com> 2.0.0-3
- Forward signals received by launcher script

* Sat Sep 24 2016 Adrien Vergé <adrienverge@gmail.com> 2.0.0-2
- Provide a launcher script in /usr/bin

* Sat Sep 24 2016 Adrien Vergé <adrienverge@gmail.com> 2.0.0-1
- Update to stable version 2.0.0
- Update patch to take config files from environment
- Remove unneeded systemd BuildRequires

* Fri Sep 9 2016 Adrien Vergé <adrienverge@gmail.com> 2.0.0RC4-8
- Add patch to take config files from environment

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
