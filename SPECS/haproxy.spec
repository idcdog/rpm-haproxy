%define haproxy_user    haproxy
%define haproxy_group   %{haproxy_user}
%define haproxy_home    %{_localstatedir}/lib/haproxy
%define haproxy_confdir %{_sysconfdir}/haproxy
%define haproxy_datadir %{_datadir}/haproxy
 
%global _hardened_build 1

Summary: HA-Proxy is a TCP/HTTP reverse proxy for high availability environments
Name: haproxy
Version: %{version}
Release: 1
License: GPL
Group: System Environment/Daemons
URL: http://www.haproxy.org/
Source0: http://www.haproxy.org/download/1.6/src/devel/%{name}-%{version}.tar.gz
Source1:        %{name}.service
Source2:        %{name}.cfg
Source3:        %{name}.logrotate
Source4:        %{name}.sysconfig
Source5:        halog.1

BuildRoot: %{_tmppath}/%{name}-%{version}-root

BuildRequires: pcre-devel
BuildRequires:  zlib-devel
BuildRequires:  openssl-devel
BuildRequires:  systemd-units

Requires(pre):      shadow-utils
Requires(post):     systemd
Requires(preun):    systemd
Requires(postun):   systemd

%description
HA-Proxy is a TCP/HTTP reverse proxy which is particularly suited for high
availability environments. Indeed, it can:
- route HTTP requests depending on statically assigned cookies
- spread the load among several servers while assuring server persistence
  through the use of HTTP cookies
- switch to backup servers in the event a main one fails
- accept connections to special ports dedicated to service monitoring
- stop accepting connections without breaking existing ones
- add/modify/delete HTTP headers both ways
- block requests matching a particular pattern

It needs very little resource. Its event-driven architecture allows it to easily
handle thousands of simultaneous connections on hundreds of instances without
risking the system's stability.

%prep
%setup -q

# We don't want any perl dependecies in this RPM:
%define __perl_requires /bin/true

%build
regparm_opts=
%ifarch %ix86 x86_64
regparm_opts="USE_REGPARM=1"
%endif
 
%{__make} %{?_smp_mflags} CPU="generic" TARGET="linux2628" USE_OPENSSL=1 USE_PCRE=1 USE_ZLIB=1 ${regparm_opts} ADDINC="%{optflags}" USE_LINUX_TPROXY=1 ADDLIB="%{__global_ldflags}" DEFINE=-DTCP_USER_TIMEOUT=18
 
pushd contrib/halog
%{__make} halog OPTIMIZE="%{optflags}"
popd
 
pushd contrib/iprange
%{__make} iprange OPTIMIZE="%{optflags}"
popd

%install
%{__make} install-bin DESTDIR=%{buildroot} PREFIX=%{_prefix} TARGET="linux2628"
%{__make} install-man DESTDIR=%{buildroot} PREFIX=%{_prefix}
 
%{__install} -p -D -m 0644 %{SOURCE1} %{buildroot}%{_unitdir}/%{name}.service
%{__install} -p -D -m 0644 %{SOURCE2} %{buildroot}%{haproxy_confdir}/%{name}.cfg
%{__install} -p -D -m 0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
%{__install} -p -D -m 0644 %{SOURCE4} %{buildroot}%{_sysconfdir}/sysconfig/%{name}
%{__install} -p -D -m 0644 %{SOURCE5} %{buildroot}%{_mandir}/man1/halog.1
%{__install} -d -m 0755 %{buildroot}%{haproxy_home}
%{__install} -d -m 0755 %{buildroot}%{haproxy_datadir}
%{__install} -d -m 0755 %{buildroot}%{_bindir}
%{__install} -p -m 0755 ./contrib/halog/halog %{buildroot}%{_bindir}/halog
%{__install} -p -m 0755 ./contrib/iprange/iprange %{buildroot}%{_bindir}/iprange
%{__install} -p -m 0644 ./examples/errorfiles/* %{buildroot}%{haproxy_datadir}
 
for httpfile in $(find ./examples/errorfiles/ -type f)
do
    %{__install} -p -m 0644 $httpfile %{buildroot}%{haproxy_datadir}
done
 
%{__rm} -rf ./examples/errorfiles/
 
find ./examples/* -type f ! -name "*.cfg" -exec %{__rm} -f "{}" \;
 
for textfile in $(find ./ -type f -name "*.txt" -o -name README)
do
    %{__mv} $textfile $textfile.old
    iconv --from-code ISO8859-1 --to-code UTF-8 --output $textfile $textfile.old
    %{__rm} -f $textfile.old
done
 
%pre
getent group %{haproxy_group} >/dev/null || groupadd -f -g 188 -r %{haproxy_group}
if ! getent passwd %{haproxy_user} >/dev/null ; then
    if ! getent passwd 188 >/dev/null ; then
        useradd -r -u 188 -g %{haproxy_group} -d %{haproxy_home} -s /sbin/nologin -c "haproxy" %{haproxy_user}
    else
        useradd -r -g %{haproxy_group} -d %{haproxy_home} -s /sbin/nologin -c "haproxy" %{haproxy_user}
    fi
fi
 
%post
%systemd_post %{name}.service
 
%preun
%systemd_preun %{name}.service
 
%postun
%systemd_postun_with_restart %{name}.service
 
%files
%defattr(-,root,root,-)
%doc doc/* examples/
%doc CHANGELOG LICENSE README ROADMAP VERSION
%dir %{haproxy_confdir}
%dir %{haproxy_datadir}
%{haproxy_datadir}/*
%config(noreplace) %{haproxy_confdir}/%{name}.cfg
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%{_unitdir}/%{name}.service
%{_sbindir}/%{name}
%{_sbindir}/%{name}-systemd-wrapper
%{_bindir}/halog
%{_bindir}/iprange
%{_mandir}/man1/*
%attr(-,%{haproxy_user},%{haproxy_group}) %dir %{haproxy_home}
 
%changelog
* Mon May 01 2017 Ryan O'Hara <rohara@redhat.com> - 1.5.18-6
- Use KillMode=mixed in systemd service file (#1444709)