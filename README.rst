CouchDB 2 and 3
===============

This repository provides unofficial packages of CouchDB 2 and CouchDB 3 for
CentOS 7+ and Fedora 24+. They are available at:

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
   && sudo dnf install -y ~/rpmbuild/RPMS/x86_64/couchdb-3.*.x86_64.rpm \
   && sudo systemctl restart couchdb \
   && journalctl -fu couchdb

Rebuild the package cleanly
---------------------------

The following examples are for CentOS 8. Please adapt if needed.

.. code:: shell

 cp couchdb.service usr-bin-couchdb ~/rpmbuild/SOURCES
 rpmbuild -bs couchdb.spec
 mock -r epel-8-x86_64 --rebuild ~/rpmbuild/SRPMS/couchdb-3.*.src.rpm
