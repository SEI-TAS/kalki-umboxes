#!/usr/bin/env bash
export http_proxy='';
HOST=localhost
watch -n 1 curl -s -o /dev/null -w "Status: %{http_code}\n" -u Username:Password http://${HOST}:9010/test_server.sh
