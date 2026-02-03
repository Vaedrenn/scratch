# Stage 1: Build environment using UBI 8.10
FROM redhat/ubi8/ubi:8.10 AS builder

# Install development tools and dependencies
RUN dnf install -y \
    gcc \
    make \
    autoconf \
    automake \
    libtool \
    pkgconfig \
    libjpeg-turbo-devel \
    libpng-devel \
    uuid-devel \
    cairo-devel \
    openssl-devel \
    libssh2-devel \
    pango-devel \
    libvncserver-devel \
    pulseaudio-libs-devel \
    libvorbis-devel \
    libwebp-devel && \
    dnf clean all

# Copy and extract the source
COPY guacamole-server-1.6.0.tar.gz /tmp/
RUN tar -xzf /tmp/guacamole-server-1.6.0.tar.gz -C /tmp/

WORKDIR /tmp/guacamole-server-1.6.0

# Configure and compile
RUN ./configure --with-init-dir=/etc/init.d && \
    make && \
    make install

# Stage 2: Clean Runtime environment
FROM redhat/ubi8/ubi:8.10

# Install only the necessary runtime libraries
RUN dnf install -y \
    cairo \
    libjpeg-turbo \
    libpng \
    libtool-ltdl \
    uuid \
    libssh2 \
    pango \
    libvncserver \
    pulseaudio-libs \
    libvorbis \
    libwebp && \
    dnf clean all

# Copy binaries and libraries from builder
COPY --from=builder /usr/local/sbin/guacd /usr/local/sbin/
COPY --from=builder /usr/local/lib/ /usr/local/lib/

# Update the shared library cache
RUN ldconfig

EXPOSE 4822
CMD ["/usr/local/sbin/guacd", "-b", "0.0.0.0", "-f"]
