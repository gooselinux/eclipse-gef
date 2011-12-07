%if 0%{?rhel} >= 6
%global debug_package %{nil}
%endif

%global eclipse_base     %{_libdir}/eclipse
%global eclipse_dropin   %{_datadir}/eclipse/dropins
%global contextQualifier v20100224-1200

Name:      eclipse-gef
Version:   3.5.2
Release:   1%{?dist}
Summary:   Graphical Editing Framework (GEF) Eclipse plugin
Group:     System Environment/Libraries
License:   EPL
URL:       http://www.eclipse.org/gef/

# source tarball and the script used to generate it from upstream's source control
# script usage:
# $ sh get-gef.sh
Source0:   gef-%{version}.tar.gz
Source1:   get-gef.sh

# disable examples source plugins (you can still get them through the new
# example project wizard)
# TODO: figure out why this stopped building between rc6 and final
Patch0:    %{name}-disable-examples-source.patch

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%if 0%{?rhel} >= 6
ExclusiveArch: i686 x86_64
%else
BuildArch: noarch
%endif

BuildRequires:    java-devel
BuildRequires:    java-javadoc
BuildRequires:    jpackage-utils
BuildRequires:    eclipse-pde >= 1:3.5.1
Requires:         java
Requires:         jpackage-utils
Requires:         eclipse-platform >= 1:3.5.1

%description
The Graphical Editing Framework (GEF) allows developers to create a rich
graphical editor from an existing application model. GEF is completely
application neutral and provides the groundwork to build almost any
application, including but not limited to: activity diagrams, GUI builders,
class diagram editors, state machines, and even WYSIWYG text editors.

%package   sdk
Summary:   Eclipse GEF SDK
Group:     System Environment/Libraries
Requires:  java-javadoc
Requires:  eclipse-pde >= 1:3.5.1
Requires:  %{name} = %{version}-%{release}

%description sdk
Documentation and source for the Eclipse Graphical Editing Framework (GEF).

%package   examples
Summary:   Eclipse GEF examples
Group:     System Environment/Libraries
Requires:  %{name} = %{version}-%{release}

%description examples
Installable versions of the example projects from the SDK that demonstrates how
to use the Eclipse Graphical Editing Framework (GEF) plugin.

%prep
%setup -q -n gef-%{version}

%patch0 -p0

# link to local java api javadocs
sed -i -e "s|link http://java.sun.com/j2se/1.4.2/docs/api|linkoffline %{_javadocdir}/java %{_javadocdir}/java|" \
  org.eclipse.gef.doc.isv/gefOptions \
  org.eclipse.draw2d.doc.isv/draw2dOptions

# make sure upstream hasn't sneaked in any jars we don't know about
JARS=""
for j in `find -name "*.jar"`; do
  if [ ! -L $j ]; then
    JARS="$JARS $j"
  fi
done
if [ ! -z "$JARS" ]; then
   echo "These jars should be deleted and symlinked to system jars: $JARS"
   exit 1
fi

%build
# We build the gef and examples features seperately, rather than just
# building the "all" feature, because it makes the files section easier to
# maintain (i.e. we don't have to know when upstream adds a new plugin)

# Note: Use the tag in get-gef.sh as the context qualifier because it's
#       later than the tags of the individual plugins.

# build gef features
%{eclipse_base}/buildscripts/pdebuild -f org.eclipse.gef \
  -a "-DforceContextQualifier=%{contextQualifier}"
%{eclipse_base}/buildscripts/pdebuild -f org.eclipse.zest \
  -a "-DforceContextQualifier=%{contextQualifier}"
%{eclipse_base}/buildscripts/pdebuild -f org.eclipse.gef.sdk \
  -a "-DforceContextQualifier=%{contextQualifier} -DJAVADOC14_HOME=%{java_home}/bin"
%{eclipse_base}/buildscripts/pdebuild -f org.eclipse.zest.sdk \
  -a "-DforceContextQualifier=%{contextQualifier} -DJAVADOC14_HOME=%{java_home}/bin"

# build examples features
%{eclipse_base}/buildscripts/pdebuild -f org.eclipse.gef.examples

%install
rm -rf %{buildroot}
install -d -m 755 %{buildroot}%{eclipse_dropin}
unzip -q -n -d %{buildroot}%{eclipse_dropin}/gef          build/rpmBuild/org.eclipse.gef.zip
unzip -q -n -d %{buildroot}%{eclipse_dropin}/gef          build/rpmBuild/org.eclipse.zest.zip
unzip -q -n -d %{buildroot}%{eclipse_dropin}/gef-sdk      build/rpmBuild/org.eclipse.gef.sdk.zip
unzip -q -n -d %{buildroot}%{eclipse_dropin}/gef-sdk      build/rpmBuild/org.eclipse.zest.sdk.zip
unzip -q -n -d %{buildroot}%{eclipse_dropin}/gef-examples build/rpmBuild/org.eclipse.gef.examples.zip

# the non-sdk builds are a subset of the sdk builds, so delete duplicate features & plugins from the sdks
(cd %{buildroot}%{eclipse_dropin}/gef-sdk/eclipse/features && ls %{buildroot}%{eclipse_dropin}/gef/eclipse/features | xargs rm -rf)
(cd %{buildroot}%{eclipse_dropin}/gef-sdk/eclipse/plugins  && ls %{buildroot}%{eclipse_dropin}/gef/eclipse/plugins  | xargs rm -rf)

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{eclipse_dropin}/gef
%doc org.eclipse.gef-feature/rootfiles/*

%files sdk
%defattr(-,root,root,-)
%{eclipse_dropin}/gef-sdk
%doc org.eclipse.gef.sdk-feature/rootfiles/*

%files examples
%defattr(-,root,root,-)
%{eclipse_dropin}/gef-examples
%doc org.eclipse.gef.examples-feature/rootfiles/*

%changelog
* Mon Mar 15 2010 Alexander Kurtakov <akurtako@redhat.com> 3.5.2-1
- Update to 3.5.2.

* Fri Feb 12 2010 Andrew Overholt <overholt@redhat.com> 3.5.1-4
- Don't build debuginfo if building arch-specific packages.

* Mon Dec 21 2009 Andrew Overholt <overholt@redhat.com> 3.5.1-3
- x86{,_64} only.

* Tue Nov 8 2009 Mat Booth <fedora@matbooth.co.uk> 3.5.1-2
- Update context qualifier to be later than the tags of the individual plugins.

* Tue Oct 27 2009 Alexander Kurtakov <akurtako@redhat.com> 3.5.1-1
- Update to 3.5.1 upstream version.

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.5.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Jul 02 2009 Mat Booth <fedora@matbooth.co.uk> 3.5.0-2
- SDK requires PDE for example plug-in projects.

* Wed Jul 01 2009 Mat Booth <fedora@matbooth.co.uk> 3.5.0-1
- Update to 3.5.0 final release (Galileo).
- Build the features seperately to allow for a saner %%files section.
- Use %%global instead of %%define.

* Wed May 27 2009 Alexander Kurtakov <akurtako@redhat.com> 3.5.0-0.2.RC2
- Update to 3.5.0 RC2.

* Sat Apr 18 2009 Mat Booth <fedora@matbooth.co.uk> 3.5.0-0.1.M6
- Update to Milestone 6 release of 3.5.0.
- Require Eclipse 3.5.0.

* Tue Apr 7 2009 Alexander Kurtakov <akurtako@redhat.com> 3.4.2-3
- Fix directory ownership.
- Drop gcj support.

* Mon Mar 23 2009 Alexander Kurtakov <akurtako@redhat.com> 3.4.2-2
- Rebuild to not ship p2 context.xml.
- Remove context.xml from %%files section.

* Sat Feb 28 2009 Mat Booth <fedora@matbooth.co.uk> 3.4.2-1
- Update for Ganymede SR2.

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.4.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Dec 22 2008 Mat Booth <fedora@matbooth.co.uk> 3.4.1-2
- Rebuild GCJ DB during post and postun in sub-packages.

* Fri Nov 20 2008 Mat Booth <fedora@matbooth.co.uk> 3.4.1-1
- New maintainer.
- Updated to verion 3.4.1.
- Update package for new Eclipse plugin guidelines.
- Own the gcj/%%{name} directory.
- The 'examples.ui.pde' plugin is actually part of the SDK feature.

* Thu Jul 17 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 3.3.0-3
- fix license tag

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 3.3.0-2
- Autorebuild for GCC 4.3

* Mon Aug 27 2007 Andrew Overholt <overholt@redhat.com> 3.3.0-1
- 3.3.

* Thu Jun 14 2007 Andrew Overholt <overholt@redhat.com> 3.2.1-5
- Add EPEL5 patches from Rob Myers.

* Tue Jan 30 2007 Andrew Overholt <overholt@redhat.com> 3.2.1-4
- Use copy-platform in %%{eclipse_base}.

* Mon Nov 06 2006 Andrew Overholt <overholt@redhat.com> 3.2.1-3
- Use copy-platform in %%{_libdir}.
- Use binary launcher rather than startup.jar to guard against future
  osgi.sharedConfiguration.area changes.

* Thu Oct 19 2006 Andrew Overholt <overholt@redhat.com> 3.2.1-2
- Fix buildroot (don't know how the wrong one slipped in).

* Thu Oct 19 2006 Andrew Overholt <overholt@redhat.com> 3.2.1-1
- 3.2.1.

* Tue Aug 29 2006 Andrew Overholt <overholt@redhat.com> 3.2.0-2
- First release for Fedora.

* Tue Aug 22 2006 Andrew Overholt <overholt@redhat.com> 3.2.0-1jpp_2rh
- -devel -> -sdk to match upstream..

* Tue Jul 25 2006 Andrew Overholt <overholt@redhat.com> 3.2.0-1jpp_1rh
- 3.2.0.

* Tue May 02 2006 Ben Konrath <bkonrath@redhat.com> 3.1.1-1jpp_2rh
- Remove -debug from compile line.
- Add expamples package.

* Mon Apr 3 2006 Ben Konrath <bkonrath@redhat.com> 3.1.1-1jpp_1rh
- Add devel package. 
- Update sources to 3.1.1.
- Some general spec file cleanup.
- Add patch to stop the gefbuilder plugin from setting bootclasspath.
- Change copyright to license.
- Add instructions for generating source drop.

* Tue Sep 6 2005 Aaron Luchko  <aluchko@redhat.com> 3.1.0-1
- change to match eclipse-changelog.spec and fixed typos

* Thu Aug 4 2005 Aaron Luchko  <aluchko@redhat.com>
- Updated to 3.1.0
- added createTarball.sh, gefSource.sh, and build.xml.patch
- added native build
- changes to use eclipsebuilder
- fixes from Matthias Saou

* Mon Jun 27 2005 Aaron Luchko <aluchko@redhat.com> 3.0.1-8
- Added x86_64

* Mon May 2 2005 Ben Konrath <bkonrath@redhat.com> 3.0.1-7
- Build against Eclipse 3.0.2.

* Thu Mar 31 2005 Phil Muldoon <pmuldoon@redhat.com> 3.0.1-6
- Migrate RHEL-3 sources to RHEL-4

* Mon Nov 1 2004 Phil Muldoon  <pmuldoon@redhat.com> 3.0.1-5
- Stopped ant trying to replace about.mappings

* Mon Nov 1 2004 Phil Muldoon  <pmuldoon@redhat.com> 3.0.1-4
- Changed tar name to new tar

* Mon Nov 1 2004 Phil Muldoon  <pmuldoon@redhat.com> 3.0.1-3
- Touch build scripts to point to 3.0.1

* Mon Nov 1 2004 Phil Muldoon  <pmuldoon@redhat.com> 3.0.1-2
- Explicitly set -DJAVADOC14_HOME=%%{java_home}/bin to build javadocs

* Sun Oct 31 2004 Phil Muldoon <pmuldoon@redhat.com> 3.0.1-1
- Initial Import
