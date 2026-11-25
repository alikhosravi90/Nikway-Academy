FROM postgres:16-alpine@sha256:f2f98726820d0342055351c6e9d36e705f5bfffb3dd53ff556325114b08afb6d
# Upstream privilege-drop invocation is gosu postgres COMMAND. The distro C
# implementation su-exec preserves this interface and avoids bundled Go stdlib.
RUN apk add --no-cache --upgrade libxml2=2.13.9-r3 su-exec=0.3-r0 \
    && test -x /sbin/su-exec \
    && unlink /usr/local/bin/gosu \
    && unlink /usr/local/bin/su-exec \
    && sed -i 's/exec gosu postgres/exec \/sbin\/su-exec postgres/' /usr/local/bin/docker-entrypoint.sh \
    && /sbin/su-exec postgres id -u
