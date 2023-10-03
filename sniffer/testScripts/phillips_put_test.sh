#!/usr/bin/env bash
curl -d '{"hue": 25000}' -X PUT http://10.27.151.106/api/newdeveloper/lights/1/state
