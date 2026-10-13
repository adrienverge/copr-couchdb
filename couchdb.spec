# Copyright 2020 Adrien Vergé

# Do not include debuginfo symlinks from /usr/lib/.build-id because they
# conflict with other erlang packages:
%define _build_id_links none

# Prebuilt binaries: no debuginfo, no rpath check, no shebang mangling
%global debug_package %{nil}
%global __brp_check_rpaths %{nil}
%global __brp_mangle_shebangs %{nil}

Name:          couchdb
Version:       3.5.3
Release:       1%{?dist}
Summary:       A document database server, accessible via a RESTful JSON API
Group:         Applications/Databases
License:       Apache
URL:           http://couchdb.apache.org/
Source0:       https://apache.jfrog.io/artifactory/couchdb-rpm/el9/x86_64/couchdb-%{version}-1.el9.x86_64.rpm
Source1:       %{name}.service
Source2:       %{name}.sysusers
Source3:       usr-bin-couchdb
# ICU 67.1 from EL9. Needed for couch_ejson_compare.so.
Source4:       https://mirror.rabisu.com/mirrors/rockylinux/9.8/BaseOS/x86_64/os/Packages/l/libicu-67.1-10.el9_6.x86_64.rpm

BuildRequires: cpio
BuildRequires: systemd
%{?systemd_requires}
BuildRequires: systemd-rpm-macros
# Only needed for < Fedora 42:
%{?sysusers_requires_compat}

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
%setup -q -c -T
rpm2cpio %{SOURCE0} | cpio -idm --quiet
mkdir icu
(cd icu && rpm2cpio %{SOURCE4} | cpio -idm --quiet)


%build
rm opt/couchdb/bin/couchdb.cmd

rm -r opt/couchdb/data opt/couchdb/var

# Remove SpiderMonkey's couchjs which is useless with QuickJS
rm opt/couchdb/bin/couchjs
rm opt/couchdb/lib/couch-%{version}/priv/couchjs

# Don't package development header files (.h for C, .hrl for Erlang),
# documentation, ERTS source files
rm -r opt/couchdb/lib/*/include
rm -r opt/couchdb/erts-*/doc
rm -r opt/couchdb/erts-*/src
rm -r opt/couchdb/erts-*/include
rm -r opt/couchdb/share/docs
rm -r opt/couchdb/share/server
rm -r opt/couchdb/share/www/docs

# Don't ship Nouveau, mostly to reduce package size. Nouveau requires a Java
# runtime environment and is disabled by default in CouchDB configuration.
# https://docs.couchdb.org/en/stable/install/nouveau.html
rm -r opt/couchdb/nouveau


%install
mkdir -p %{buildroot}/opt

cp -r opt/couchdb %{buildroot}/opt

install -p -D -m 0755 %{SOURCE3} %{buildroot}%{_bindir}/%{name}

install -d %{buildroot}/opt/couchdb/libicu67
# These are the only needed Shared Object files for couch_ejson_compare.so.
for l in uc i18n data; do
    install -p icu/usr/lib64/libicu$l.so.67.1 %{buildroot}/opt/couchdb/libicu67/
    ln -s libicu$l.so.67.1 %{buildroot}/opt/couchdb/libicu67/libicu$l.so.67
done

# Have conf in /etc/couchdb, not /opt/couchdb/etc
mkdir -p %{buildroot}%{_sysconfdir}
mv %{buildroot}/opt/couchdb/etc %{buildroot}%{_sysconfdir}/%{name}

# Store databases in /var/lib/couchdb
sed -i 's|\./data\b|%{_sharedstatedir}/%{name}|g' \
    %{buildroot}%{_sysconfdir}/%{name}/default.ini

# Use QuickJS as JavaScript engine
sed -i 's|^;js_engine = spidermonkey|js_engine = quickjs|' \
    %{buildroot}%{_sysconfdir}/%{name}/default.ini

install -p -D -m 0644 %{SOURCE1} %{buildroot}%{_unitdir}/%{name}.service
install -p -D -m 0644 %{SOURCE2} %{buildroot}%{_sysusersdir}/%{name}.conf

mkdir -p %{buildroot}%{_sharedstatedir}/%{name}


%pre
# Only needed for < Fedora 42:
%sysusers_create_compat %{SOURCE2}

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
%config(noreplace) %attr(0644, %{name}, %{name}) %{_sysconfdir}/%{name}/nouveau.yaml

%dir %attr(0755, %{name}, %{name}) %{_sharedstatedir}/%{name}

%{_unitdir}/%{name}.service
%{_sysusersdir}/%{name}.conf


%changelog
* Tue Oct 13 2026 Baptiste Ravier 3.5.3-1
- Update to CouchDB 3.5.3
- Repackage from the official RHEL9 RPM
- Enable QuickJS by default

* Thu Oct 30 2025 Adrien Vergé 3.5.0-2
- Use systemd-sysusers for user 'couchdb' and drop group 'couchdb'

* Tue May 06 2025 Adrien Vergé 3.5.0-1
- Update to CouchDB 3.5.0

* Tue Oct 15 2024 Adrien Vergé 3.4.1-1
- Update to CouchDB 3.4.1 + QuickJS + Erlang 26 + other changes

* Thu Jan 04 2024 Adrien Vergé <adrienverge@gmail.com> 3.3.3-2
- Use Erlang 24.3.4.15 (previously 24.3.4.5) to fix a memory leak

* Tue Dec 05 2023 Adrien Vergé <adrienverge@gmail.com> 3.3.3-3
- Update to new upstream version

* Fri Nov 10 2023 Baptiste Ravier <baptiste.ravier@gmail.com> 3.3.2-2
- Use custom re-packaged mozjs91 (previously: 78) for EPEL 8+ and Fedora 38+

* Thu Apr 27 2023 Baptiste Ravier <baptiste.ravier@gmail.com> 3.3.2-1
- Update to new upstream version

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
