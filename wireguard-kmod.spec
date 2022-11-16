%if 0%{?fedora}
%global buildforkernels akmod
%global debug_package %{nil}
%endif

Name:           wireguard-kmod
Summary:        Kernel module (kmod) for Wireguard
Version:        1.0.20220627
Release:        1%{?dist}
License:        GPLv2

URL:            https://www.wireguard.com/
Source0:        https://git.zx2c4.com/wireguard-linux-compat/snapshot/wireguard-linux-compat-%{version}.tar.xz
Patch0:         0001-compat-account-for-latest-c8s-backports.patch
Patch1:         0002-compat-account-for-grsecurity-backports-and-changes.patch
Patch2:         0003-crypto-curve25519-x86_64-solve-register-constraints-.patch
Patch3:         0001-compat-update-for-RHEL-8.5.patch

BuildRequires:  kmodtool
%{!?kernels:BuildRequires: gcc, elfutils-libelf-devel, buildsys-build-rpmfusion-kerneldevpkgs-%{?buildforkernels:%{buildforkernels}}%{!?buildforkernels:current}-%{_target_cpu} }

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

%setup -q -c -T -a 0
(cd wireguard-linux-compat-%{version}
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
)

for kernel_version  in %{?kernel_versions} ; do
  cp -a wireguard-linux-compat-%{version} _kmod_build_${kernel_version%%___*}
done


%build
for kernel_version  in %{?kernel_versions} ; do
# We don't override kernel wireguard module (unless forced) until the packages are obsoleted by f32
%if 0%{!?_with_kmod_wireguard_override:1}
  if [[ ${kernel_version%%___*} -ge 5.6 ]] ; then
    continue
  fi
%endif
  make V=1 %{?_smp_mflags} -C ${kernel_version##*___} M=${PWD}/_kmod_build_${kernel_version%%___*}/src modules
done


%install
for kernel_version in %{?kernel_versions}; do
 mkdir -p %{buildroot}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/
# We don't override kernel wireguard module (unless forced) until the packages are obsoleted by f32
%if 0%{!?_with_kmod_wireguard_override:1}
  if [[ ${kernel_version%%___*} -ge 5.6 ]] ; then
    continue
  fi
%endif
 install -D -m 755 -t %{buildroot}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/ $(find _kmod_build_${kernel_version%%___*}/ -name '*.ko')
 chmod u+x %{buildroot}%{_prefix}/lib/modules/*/extra/*/*
done
%{?akmod_install}


%changelog
* Wed Nov 16 2022 Nicolas Chauvet <kwizart@gmail.com> - 1.0.20220627-1
- Update to 1.0.20220627

* Fri Nov 19 2021 Nicolas Chauvet <kwizart@gmail.com> - 1.0.20210606-3
- Update for EL8.5

* Thu Oct 14 2021 Nicolas Chauvet <kwizart@gmail.com> - 1.0.20210606-2
- Backport patches

* Tue Jun 08 2021 Nicolas Chauvet <kwizart@gmail.com> - 1.0.20210606-1
- Update to 1.0.20210606

* Sun Mar 21 2021 Nicolas Chauvet <kwizart@gmail.com> - 1.0.20210219-1
- Update to 1.0.20210219

* Sun Feb 07 2021 Nicolas Chauvet <kwizart@gmail.com> - 1.0.20210124-1
- Update to 1.0.20210124

* Mon Dec 21 2020 Nicolas Chauvet <kwizart@gmail.com> - 1.0.20201221-1
- Update to 1.0.20201221

* Tue Apr 14 2020 Nicolas Chauvet <kwizart@gmail.com> - 0.0.20191219-3
- Disable wireguard until obsoleted

* Thu Apr 09 2020 Leigh Scott <leigh123linux@gmail.com> - 0.0.20191219-2
- Patch for kernel-5.5.15

* Fri Dec 20 2019 Leigh Scott <leigh123linux@googlemail.com> - 0.0.20191219-1
- Release 0.0.20191219

* Thu Dec 05 2019 Robert-André Mauchin <zebob.m@gmail.com> - 0.0.20191205-1
- Release 0.0.20191205

* Thu Dec 05 2019 Robert-André Mauchin <zebob.m@gmail.com> - 0.0.20191127-1
- Release 0.0.20191127

* Sun Oct 13 2019 Robert-André Mauchin <zebob.m@gmail.com> - 0.0.20191012-1
- Release 0.0.20191012

* Sun Sep 15 2019 Leigh Scott <leigh123linux@googlemail.com> - 0.0.20190913-1
- Release 0.0.20190913

* Wed Sep 04 2019 Leigh Scott <leigh123linux@googlemail.com> - 0.0.20190702-3
- Rebuild for new el7 kernel and generate kmod package

* Fri Aug 09 2019 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 0.0.20190702-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Fri Jul 05 2019 Robert-André Mauchin <zebob.m@gmail.com> - 0.0.20190702-1
- Release 0.0.20190702

* Fri May 31 2019 Robert-André Mauchin <zebob.m@gmail.com> - 0.0.20190531-1
- Release 0.0.20190531

* Sat Apr 06 2019 Robert-André Mauchin <zebob.m@gmail.com> - 0.0.20190406-1
- Release 0.0.20190406

* Thu Apr 04 2019 Robert-André Mauchin <zebob.m@gmail.com> - 0.0.20190227-3
- Rebuilt for akmods-ostree-post scriptlet

* Tue Mar 05 2019 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 0.0.20190227-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Thu Feb 28 2019 Robert-André Mauchin <zebob.m@gmail.com> - 0.0.20190227-1
- Release 0.0.20190227

* Tue Feb 19 2019 Robert-André Mauchin <zebob.m@gmail.com> - 0.0.20190123-1
- Release 0.0.20190123

* Tue Dec 18 2018 Robert-André Mauchin <zebob.m@gmail.com> - 0.0.20181218-1
- Release 0.0.20181218
- Use make modules instead of make module

* Mon Nov 19 2018 Robert-André Mauchin <zebob.m@gmail.com> - 0.0.20181119-1
- Release 0.0.20181119

* Fri Nov 16 2018 Robert-André Mauchin <zebob.m@gmail.com> - 0.0.20181115-1
- Release 0.0.20181115

* Thu Oct 18 2018 Robert-André Mauchin <zebob.m@gmail.com> - 0.0.20181018-1
- Release 0.0.20181018

* Sun Oct 07 2018 Robert-André Mauchin <zebob.m@gmail.com> - 0.0.20181007-1
- Release 0.0.20181007

* Sat Oct 06 2018 Robert-André Mauchin <zebob.m@gmail.com> - 0.0.20181006-1
- Release 0.0.20181006

* Tue Sep 25 2018 Robert-André Mauchin <zebob.m@gmail.com> - 0.0.20180925-1
- Release 0.0.20180925

* Sun Sep 23 2018 Robert-André Mauchin <zebob.m@gmail.com> - 0.0.20180918-1
- Initial package
