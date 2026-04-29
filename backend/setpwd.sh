#!/bin/bash
echo "ALTER USER postgres WITH PASSWORD 'postgres';" | sudo -u postgres psql
