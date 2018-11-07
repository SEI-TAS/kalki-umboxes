#!/usr/bin/env bash
curl -s -o /dev/null -w "Status: %{http_code}\n" -u Username:Password http://localhost:9010/test_server.sh
