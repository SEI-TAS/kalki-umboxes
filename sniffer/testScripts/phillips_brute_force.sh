#!/usr/bin/env bash

#20 identical API calls that should not trigger a brute force
test_token="abcdefghijklmnop"
for i in {1..20}
do
    curl -s -o /dev/null http://localhost:9010/api/"$test_token"/lights
    sleep 0.5
done

echo "finished 20 identical api calls.  Should not have triggered brute force"
sleep 5

#20 api calls with random tokens should trigger a brute force
for i in {1..20}
do
    # bash generate random 16 character alphanumeric string (upper and lowercase) 
    NEW_UUID=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 16 | head -n 1)

    curl -s -o /dev/null http://localhost:9010/api/"$NEW_UUID"/lights
    sleep 0.5
done

echo "finished 20 random token api calls.  Should have triggered brute force"

