%global tcuid 53

Name:           tomcat
Version:        9.0.115
Release:        1%{?dist}
Summary:        Apache Tomcat Servlet and JSP Engine

License:        Apache-2.0
URL:            https://tomcat.apache.org/
Source0:        apache-tomcat-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  java-17-openjdk-devel
Requires:       java-17-openjdk-headless

%description
Apache Tomcat is an open source software implementation of the Java
Servlet and JavaServer Pages technologies.

%prep
%autosetup -n apache-tomcat-%{version}

# No compilation, just prepare distribution

%build
# Nothing to build

%pre
# add the tomcat user and group
getent group tomcat >/dev/null || %{_sbindir}/groupadd -f -g %{tcuid} -r tomcat
if ! getent passwd tomcat >/dev/null ; then
    if ! getent passwd %{tcuid} >/dev/null ; then
        %{_sbindir}/useradd -r -u %{tcuid} -g tomcat -d %{homedir} -s /sbin/nologin -c "Apache Tomcat" tomcat
        # Tomcat uses a reserved ID, so there should never be an else
    fi
fi
exit 0


%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/usr/share/%{name}
mkdir -p %{buildroot}/etc/%{name}
mkdir -p %{buildroot}/usr/bin
mkdir -p %{buildroot}/usr/lib/systemd/system

# Copy entire distribution
cp -a . %{buildroot}/usr/share/%{name}/

# Move config files to /etc if you want them configurable
mv %{buildroot}/usr/share/%{name}/conf %{buildroot}/etc/%{name}/

# Wrapper script
cat > %{buildroot}/usr/bin/tomcat << 'EOF'
#!/bin/sh
exec /usr/share/tomcat/bin/catalina.sh "$@"
EOF
chmod +x %{buildroot}/usr/bin/tomcat

# Systemd unit
cat > %{buildroot}/usr/lib/systemd/system/tomcat.service << 'EOF'
[Unit]
Description=Apache Tomcat Web Application Container
After=network.target

[Service]
Type=forking
Environment=JAVA_HOME=/usr/lib/jvm/jre
Environment=CATALINA_PID=/var/run/tomcat.pid
ExecStart=/usr/share/tomcat/bin/startup.sh
ExecStop=/usr/share/tomcat/bin/shutdown.sh
User=tomcat
Group=tomcat

[Install]
WantedBy=multi-user.target
EOF

%files
%doc LICENSE NOTICE RELEASE-NOTES
/etc/%{name}
/usr/share/%{name}
/usr/bin/tomcat
/usr/lib/systemd/system/tomcat.service

%changelog
* Tue Feb 03 2026 Your Name <you@example.com> - 9.0.115-1
- Initial packaging for Tomcat 9.0.115 using only apache-tomcat-9.0.115.tar.gz
