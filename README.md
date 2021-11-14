# twitchdrives

Welcome to the world's worst way to drive a vehicle.

New locations will be pushed to the car every 5 minutes or when the car makes it to the destination, whichever comes first.

Please note that the driver will be mainly focused on the road and accepting destination changes at the safest convienence.

## development
```
virtualenv env/
pip install -r requirements.txt

source env/bin/activate
```

## Commands
* t!info           - The car's current information? h*ck yeah!
* t!drive          - [LOCATION] to take us places.
* t!vote anarchy   - Place a vote to set waypoints with anarchy.
* t!vote democracy - Place a vote to set waypoints with democracy.
* t!vote average   - Place a vote to set waypoints with averages.

## Waypoint modes
* Anarchy     - The first person to !drive after the timer reaches 0 will be pushed to the car.
* Democracy   - The location that has the most votes when the timer reaches 0 will be pushed to the car.
* Average     - The average of all locations will be pushed to the car.

## Testimonial
* ![](https://i.imgur.com/P9YJtRV.jpg)
* "someone come yell at erin. she wants to make twitch drives"
* "that doesn’t seem safe in the slightest!"

## Copyright
* Map data © OpenStreetMap contributors
* Imagery © Mapbox
* Map powered by Leaflet
* `tesla-py` Copyright (c) 2019 Tim Dorssers MIT
