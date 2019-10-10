CouchDB 2
=========

This repository provides unofficial packages of CouchDB 2.x for CentOS 7+ and
Fedora 24+. They are available at:

https://copr.fedorainfracloud.org/coprs/adrienverge/couchdb/

Use the repo to install CouchDB
-------------------------------

Fedora:

.. code:: shell

 sudo dnf copr enable adrienverge/couchdb
 sudo dnf install couchdb

CentOS:

.. code:: shell

 sudo yum install yum-plugin-copr
 sudo yum copr enable adrienverge/couchdb
 sudo yum install couchdb

Running
-------

When using this repo, you shouldn't just call ``couchdb``. Instead, use the
systemd service with:

.. code:: shell

 sudo systemctl start couchdb

Hack and rebuild the package quickly
------------------------------------

Quick and dirty, on your own system:

.. code:: shell

 cp couchdb.service *.patch usr-bin-couchdb ~/rpmbuild/SOURCES \
   && rpmbuild -ba couchdb.spec \
   && sudo dnf remove -y couchdb \
   && sudo dnf install -y ~/rpmbuild/RPMS/x86_64/couchdb-2.*.x86_64.rpm \
   && sudo systemctl restart couchdb \
   && journalctl -fu couchdb

Rebuild the package cleanly
---------------------------

The following examples are for CentOS 7. Please adapt if needed.

1. We need to compile and ship our own ``js`` package, because of reasons
   described at https://github.com/apache/couchdb-pkg/tree/7768c00/js.

   So first, you need to create ``couch-js`` and ``couch-js-devel``:

   .. code:: shell

    git clone git@github.com:apache/couchdb-pkg.git /tmp/couchdb-pkg
    cd /tmp/couchdb-pkg
    cp js/src/js185-1.0.0.tar.gz js/rpm/SOURCES/* ~/rpmbuild/SOURCES/
    rpmbuild -bs js/rpm/SPECS/js.spec
    mock -r epel-7-x86_64 --rebuild ~/rpmbuild/SRPMS/couch-js-1.8.5-21.*.src.rpm

   ... and save the RPM somewhere for later:

   .. code:: shell

    cp /var/lib/mock/epel-7-x86_64/result/couch-js-*.rpm /tmp/

2. Then build ``couchdb``, after install ``couch-js`` and ``couch-js-devel`` in
   the mock environment:

   .. code:: shell

    cp couchdb.service *.patch usr-bin-couchdb ~/rpmbuild/SOURCES
    rpmbuild -bs couchdb.spec
    mock -r epel-7-x86_64 --install /tmp/couch-js-1.8.5-21.*.x86_64.rpm /tmp/couch-js-devel-1.8.5-21.*.x86_64.rpm
    mock -r epel-7-x86_64 --no-clean --rebuild ~/rpmbuild/SRPMS/couchdb-2.3.1-4.*.src.rpm

Note for CentOS 7
-----------------

For CentOS (where Erlang 17+ is not packaged), you need to add this to
``/etc/mock/epel-7-x86_64.cfg``:

.. code::

 [erlang-solutions]
 name=Centos $releasever - $basearch - Erlang Solutions
 baseurl=http://packages.erlang-solutions.com/rpm/centos/$releasever/$basearch
 gpgcheck=0
 gpgkey=http://packages.erlang-solutions.com/debian/erlang_solutions.asc
 enabled=1
