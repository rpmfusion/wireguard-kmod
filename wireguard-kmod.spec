%global buildforkernels akmod
%global debug_package %{nil}

Name:           wireguard-kmod
Summary:        Kernel module (kmod) for Wireguard
Version:        0.0.20181007
Release:        1%{?dist}
License:        GPLv2

URL:            https://www.wireguard.com/
Source0:        https://git.zx2c4.com/WireGuard/snapshot/WireGuard-%{version}.tar.xz

BuildRequires:  kmodtool
BuildRequires:  elfutils-libelf-devel
%{!?kernels:BuildRequires: buildsys-build-rpmfusion-kerneldevpkgs-%{?buildforkernels:%{buildforkernels}}%{!?buildforkernels:current}-%{_target_cpu} }

# kmodtool does its magic here
%{expand:%(kmodtool --target %{_target_cpu} --repo rpmfusion --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }

%description
WireGuard is a novel VPN that runs inside the Linux Kernel and utilizes 
state-of-the-art cryptography. It aims to be faster, simpler, leaner, 
and more useful than IPSec, while avoiding the massive headache. It intends 
to be considerably more performant than OpenVPN. WireGuard is designed as a 
general purpose VPN for running on embedded interfaces and super computers 
alike, fit for many different circumstances. It runs over UDP.

This package contains the kmod module for WireGuard.


%prep
# error out if there was something wrong with kmodtool
%{?kmodtool_check}

# print kmodtool output for debugging purposes:
kmodtool  --target %{_target_cpu} --repo rpmfusion --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null

%autosetup -c -T -a 0

for kernel_version  in %{?kernel_versions} ; do
  cp -a WireGuard-%{version} _kmod_build_${kernel_version%%___*}
done


%build
for kernel_version  in %{?kernel_versions} ; do
  make V=1 %{?_smp_mflags} -C _kmod_build_${kernel_version%%___*} -C src M=${PWD}/_kmod_build_${kernel_version%%___*} module
done


%install
for kernel_version in %{?kernel_versions}; do
 mkdir -p %{buildroot}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/
 install -D -m 755 -t %{buildroot}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/ $(find _kmod_build_${kernel_version%%___*}/ -name '*.ko')
 chmod u+x %{buildroot}%{_prefix}/lib/modules/*/extra/*/*
done
%{?akmod_install}


%changelog
* Sun Oct 07 2018 Robert-André Mauchin <zebob.m@gmail.com> - 0.0.20181007-1
- Release 0.0.20181007

* Tue Sep 25 2018 Robert-André Mauchin <zebob.m@gmail.com> - 0.0.20180925-1
- Release 0.0.20180925

* Sun Sep 23 2018 Robert-André Mauchin <zebob.m@gmail.com> - 0.0.20180918-1
- Initial package
