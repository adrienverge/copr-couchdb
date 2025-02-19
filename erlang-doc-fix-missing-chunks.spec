Name:           erlang-doc-fix-missing-chunks
Version:        26.2.5.8
Release:        1%{?dist}
Summary:        Fix missing chunks directories
License:        GPL-3.0-or-later

BuildRequires: erlang-doc = %{version}

%description
On 2024-10-15 on Fedora 40 and 41 the 3 following dirs are missing:
    /usr/share/doc/erlang-26.2.5.3/lib/erl_interface-5.5.1/chunks
    /usr/share/doc/erlang-26.2.5.3/lib/jinterface-1.14/chunks
    /usr/share/doc/erlang-26.2.5.3/lib/erl_docgen-1.5.2/chunks
… and make the build of CouchDB 3.4.1 crash on the last step ("==> rel
(generate)") with:
    ERROR: Unable to generate spec: read file info
    /usr/lib64/erlang/lib/erl_interface-5.5.1/doc/chunks failed
Let's create them.

%install
for d in $(ls %{_datarootdir}/doc/erlang-%{version}/lib); do
  if [ ! -e %{_datarootdir}/doc/erlang-%{version}/lib/$d/chunks ]; then
    mkdir -p %{buildroot}%{_datarootdir}/doc/erlang-%{version}/lib/$d/chunks
  fi
done

%files
%{_datarootdir}/doc/erlang-%{version}/lib

%changelog
* Wed Feb 19 2025 Adrien Vergé 26.2.5.8-1
- Update for Fedora 42 (beta) and 43 (rawhide), which have Erlang 26.2.5.8

* Wed Feb 19 2025 Adrien Vergé 26.2.5.6-1
- Update for Fedora 41, which has Erlang 26.2.5.6

* Tue Oct 15 2024 Adrien Vergé 26.2.5.4-1
- Update for Fedora 42 (rawhide), which has Erlang 26.2.5.4

* Tue Oct 15 2024 Adrien Vergé 26.2.5.3-1
- Create package (for Erlang 26.2.5.3)
