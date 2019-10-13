#!/usr/bin/env bash

PHILLIPSIP=10.27.151.106
PHILLIPSPORT=80

#20 identical API calls that should not trigger a brute force
#test_token="abcdefghijklmnop"
#for i in {1..20}
#do
#    curl -s -o /dev/null http://localhost:9010/api/"$test_token"/lights
#    sleep 0.5
#done

#echo "finished 20 identical api calls.  Should not have triggered brute force"
#sleep 5

#20 calls to get a token
#for i in {1..20}
#do
#    curl -s -o /dev/null http://localhost:9010/api
#    sleep 0.5
#done

#echo "finished 20 token requests.  Should have triggered brute force"
#sleep 5

# Many api calls with random tokens should trigger a brute force
for i in {1..20}
do
    # bash generate random 16 character alphanumeric string (upper and lowercase) 
    NEW_UUID=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 16 | head -n 1)

    curl -s -o /dev/null http://${PHILLIPSIP}:${PHILLIPSPORT}/api/"$NEW_UUID"/lights
    sleep 0.5
done

echo "finished 20 random token api calls.  Should have triggered brute force"

