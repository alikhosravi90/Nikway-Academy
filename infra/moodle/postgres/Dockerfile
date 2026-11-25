FROM postgres:17-alpine@sha256:f9cf3e1f0066f0eb0c48707d864f0ac5941e9ff454a072077d97a4d278d07d73
# Upstream privilege-drop invocation is gosu postgres COMMAND. The distro C
# implementation su-exec preserves this interface and avoids bundled Go stdlib.
RUN apk add --no-cache --upgrade libxml2=2.13.9-r3 su-exec=0.3-r0 \
    && test -x /sbin/su-exec \
    && unlink /usr/local/bin/gosu \
    && sed -i 's/exec gosu postgres/exec \/sbin\/su-exec postgres/' /usr/local/bin/docker-entrypoint.sh \
    && /sbin/su-exec postgres id -u
