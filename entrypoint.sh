#!/bin/sh
# dump env vars ให้ cron อ่านได้
printenv | grep -v "^_=" > /etc/environment
cron -f
