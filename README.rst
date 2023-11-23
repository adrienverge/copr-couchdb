RPM packages for CouchDB 3
==========================

This repository provides unofficial packages of CouchDB 3 for Fedora 24+ and
CentOS 7+ / Rocky Linux 9+. They are available at:

https://copr.fedorainfracloud.org/coprs/adrienverge/couchdb/

Use the repo to install CouchDB
-------------------------------

.. code:: shell

 sudo dnf copr enable adrienverge/couchdb
 sudo dnf install couchdb

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

The following examples are for Rocky Linux 9. Please adapt if needed.

First, download official CouchDB source code into ``~/rpmbuild/SOURCES``. The
file name must match the one of ``Source0`` in ``couhdb.spec``, e.g.
``apache-couchdb-3.3.2.tar.gz``.

.. code:: shell

 cp couchdb.service usr-bin-couchdb ~/rpmbuild/SOURCES
 rpmbuild -bs couchdb.spec
 mock -r rocky+epel-9-x86_64 --rebuild ~/rpmbuild/SRPMS/couchdb-3.*.src.rpm

In case the ``mock`` command needs to find a ``BuildRequires`` package from a
special repository, it can be provided by addind this to the mock configuration
file (e.g. ``/etc/mock/rocky+epel-9-x86_64.cfg`` for Rocky Linux 9):

.. code:: python

 config_opts['dnf.conf'] += """
 [adrienverge-couchdb]
 name=Copr repo for couchdb owned by adrienverge
 baseurl=https://copr-be.cloud.fedoraproject.org/results/adrienverge/couchdb/epel-$releasever-$basearch/
 type=rpm-md
 gpgcheck=1
 gpgkey=https://copr-be.cloud.fedoraproject.org/results/adrienverge/couchdb/pubkey.gpg
 repo_gpgcheck=0
 enabled=1
 enabled_metadata=1
 """

In case the ``mock`` command needs to find a ``BuildRequires`` package from a
local file, it can be pre-installed using ``install`` first, then
``--no-clean``. For instance:

.. code:: shell

 mock -r fedora-39-x86_64 install erlang-24.3.4.5-2.fc39.x86_64.rpm
 mock -r fedora-39-x86_64 --no-clean rebuild ~/rpmbuild/SRPMS/….src.rpm
