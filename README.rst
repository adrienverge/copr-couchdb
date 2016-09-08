CouchDB 2.0
===========

This repository provides unofficial packages of CouchDB 2.0 for CentOS 7+ and
Fedora 24+. They are available at:

https://copr.fedorainfracloud.org/coprs/adrienverge/couchdb/

Install
-------

.. code:: shell

 sudo yum install yum-plugin-copr
 sudo yum copr enable adrienverge/couchdb
 sudo yum install couchdb

Hack
----

.. code:: shell

 rpmbuild -bs couchdb.spec
 mock -r epel-7-x86_64 rebuild ~/rpmbuild/SRPMS/couchdb-2.0.0*.src.rpm
