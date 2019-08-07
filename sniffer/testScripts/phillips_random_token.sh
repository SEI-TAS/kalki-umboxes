#!/usr/bin/env bash
export http_proxy='';

# bash generate random 16 character alphanumeric string (upper and lowercase) 
NEW_UUID=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 16 | head -n 1)

#curl -s -o /dev/null http://localhost:9010/api/"$NEW_UUID"/lights

curl -s -o /dev/null -X DELETE http://localhost:9010/api/"$NEW_UUID"/lights/123

