#!/bin/sh
set -eu
install -m 640 -o root -g www-data /run/moodle/config.php /var/www/moodle/config.php
mkdir -p /var/moodledata
chown -R www-data:www-data /var/moodledata
exec docker-php-entrypoint "$@"
