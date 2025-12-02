#!/bin/bash

set -e
printenv | grep -v "no_proxy" >> /etc/environment
cron -f
