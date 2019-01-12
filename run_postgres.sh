#!/bin/bash

PASSWORD="docker"
PORTS="5432:5432"
PATH="postgres:/var/lib/postgresql/data"
CONTAINER="postgres"
NAME="app"

docker run --rm --name $CONTAINER -e POSTGRES_PASSWORD=$PASSWORD -e POSTGRES_DB=$NAME -d -p $PORTS -v $PATH  postgres