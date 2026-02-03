# Guacamole Container - RHEL 8.10 Base
# Multi-stage build for guacamole-server and guacamole-client

FROM registry.access.redhat.com/ubi8/ubi:8.10 AS builder

# Install build dependencies for guacamole-server
RUN dnf install -y \
    gcc \
    gcc-c++ \
    make \
    cairo-devel \
    libjpeg-turbo-devel \
    libpng-devel \
    libtool \
    uuid-devel \
    freerdp-devel \
    pango-devel \
    libssh2-devel \
    libvncserver-devel \
    pulseaudio-libs-devel \
    openssl-devel \
    libvorbis-devel \
    libwebp-devel \
    libwebsockets-devel \
    && dnf clean all

# Copy and build guacamole-server
COPY guacamole-server-1.6.0.tar.gz /tmp/
RUN cd /tmp && \
    tar -xzf guacamole-server-1.6.0.tar.gz && \
    cd guacamole-server-1.6.0 && \
    ./configure --with-init-dir=/etc/init.d && \
    make && \
    make install && \
    ldconfig

# Final runtime image
FROM registry.access.redhat.com/ubi8/ubi:8.10

# Install runtime dependencies
RUN dnf install -y \
    cairo \
    libjpeg-turbo \
    libpng \
    uuid \
    freerdp \
    pango \
    libssh2 \
    libvncserver \
    pulseaudio-libs \
    openssl \
    libvorbis \
    libwebp \
    libwebsockets \
    java-11-openjdk-headless \
    tomcat \
    && dnf clean all

# Copy compiled guacamole-server from builder
COPY --from=builder /usr/local/lib/libguac*.so* /usr/local/lib/
COPY --from=builder /usr/local/lib/freerdp2/guac*.so /usr/local/lib/freerdp2/
COPY --from=builder /usr/local/sbin/guacd /usr/local/sbin/
RUN ldconfig

# Set up environment
ENV CATALINA_HOME=/usr/share/tomcat
ENV GUACAMOLE_HOME=/etc/guacamole

# Create directories
RUN mkdir -p ${GUACAMOLE_HOME}/extensions \
    ${GUACAMOLE_HOME}/lib \
    /var/log/guacamole

# Copy guacamole.war
COPY guacamole-1.6.0.war ${CATALINA_HOME}/webapps/guacamole.war

# Copy configuration
COPY guacamole.properties ${GUACAMOLE_HOME}/
COPY user-mapping.xml ${GUACAMOLE_HOME}/ 2>/dev/null || true

# Expose ports
EXPOSE 8080 4822

# Create entrypoint
RUN echo '#!/bin/bash' > /usr/local/bin/docker-entrypoint.sh && \
    echo 'set -e' >> /usr/local/bin/docker-entrypoint.sh && \
    echo 'echo "Starting guacd..."' >> /usr/local/bin/docker-entrypoint.sh && \
    echo '/usr/local/sbin/guacd -b 0.0.0.0 -l 4822 -L info &' >> /usr/local/bin/docker-entrypoint.sh && \
    echo 'sleep 3' >> /usr/local/bin/docker-entrypoint.sh && \
    echo 'echo "Starting Tomcat..."' >> /usr/local/bin/docker-entrypoint.sh && \
    echo 'exec /usr/libexec/tomcat/server start' >> /usr/local/bin/docker-entrypoint.sh && \
    chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
