FROM php:8.4-fpm-alpine@sha256:c0e41e0c856bf97b2e749f40a804031ce938d0d496c4c7d91ad416d993172826
RUN apk add --no-cache nginx icu-libs libzip libpng libjpeg-turbo freetype libpq libxml2 \
 && apk add --no-cache --virtual .build-deps $PHPIZE_DEPS postgresql-dev icu-dev libzip-dev libpng-dev libjpeg-turbo-dev freetype-dev libxml2-dev \
 && docker-php-ext-configure gd --with-freetype --with-jpeg \
 && docker-php-ext-install -j4 pgsql intl zip gd soap opcache exif \
 && apk del .build-deps
ARG MOODLE_URL=https://download.moodle.org/download.php/direct/stable503/moodle-5.3.1.tgz
ARG MOODLE_SHA256=820ee2bcd89acc6b91df255b2010bbbab108f29952ab78895a79c4feabf541e7
RUN curl -fsSL "$MOODLE_URL" -o /tmp/moodle.tgz \
 && echo "$MOODLE_SHA256  /tmp/moodle.tgz" | sha256sum -c - \
 && tar -xzf /tmp/moodle.tgz -C /var/www && rm /tmp/moodle.tgz \
 && mkdir -p /var/moodledata && chown www-data:www-data /var/moodledata
RUN curl -fsSL https://codeload.github.com/microsoft/moodle-auth_oidc/tar.gz/5866154d55fa56ea5a112386fac9722c3a58ac7b -o /tmp/oidc.tgz \
 && echo "75c7bc1d6fd66158363df4dc19547d3091d67af31605d7f4d5a4d59fab6fc659  /tmp/oidc.tgz" | sha256sum -c - \
 && mkdir /var/www/moodle/public/auth/oidc \
 && tar -xzf /tmp/oidc.tgz --strip-components=1 -C /var/www/moodle/public/auth/oidc && rm /tmp/oidc.tgz
COPY nginx.conf /etc/nginx/nginx.conf
COPY moodle.ini /usr/local/etc/php/conf.d/moodle.ini
COPY entrypoint.sh /usr/local/bin/moodle-entrypoint
ENTRYPOINT ["moodle-entrypoint"]
CMD ["moodle-web"]
COPY web.sh /usr/local/bin/moodle-web
