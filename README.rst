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

Hack and rebuild packages locally
---------------------------------

Quick and dirty, on your own system:

.. code:: shell

 cp couchdb.service *.patch usr-bin-couchdb ~/rpmbuild/SOURCES \
   && rpmbuild -ba couchdb.spec \
   && sudo dnf remove -y couchdb \
   && sudo dnf install -y ~/rpmbuild/RPMS/x86_64/couchdb-2.*.x86_64.rpm \
   && sudo systemctl restart couchdb \
   && journalctl -fu couchdb

Cleanly, for CentOS 7:

.. code:: shell

 cp couchdb.service *.patch usr-bin-couchdb ~/rpmbuild/SOURCES \
   && rpmbuild -bs couchdb.spec && \
 mock -r epel-7-x86_64 --rebuild ~/rpmbuild/SRPMS/couchdb-2.*.src.rpm

For CentOS (where Erlang 17+ is not packaged), you need to add this to
``/etc/mock/epel-7-x86_64.cfg``:

.. code::

 [erlang-solutions]
 name=Centos $releasever - $basearch - Erlang Solutions
 baseurl=http://packages.erlang-solutions.com/rpm/centos/$releasever/$basearch
 gpgcheck=0
 gpgkey=http://packages.erlang-solutions.com/debian/erlang_solutions.asc
 enabled=1

Custom couch-js package
-----------------------

We need to compile and ship our own ``js`` package, because of reasons
described at https://github.com/apache/couchdb-pkg/tree/7768c00/js.
The SRPM can be quickly built by running:

.. code:: shell

 git clone git@github.com:apache/couchdb-pkg.git /tmp/couchdb-pkg
 cd /tmp/couchdb-pkg
 cp js/src/js185-1.0.0.tar.gz js/rpm/SOURCES/* ~/rpmbuild/SOURCES/
 rpmbuild -bs js/rpm/SPECS/js.spec
 mock -r epel-7-x86_64 --rebuild ~/rpmbuild/SRPMS/couch-js-1.8.5-21.fc28.src.rpm
