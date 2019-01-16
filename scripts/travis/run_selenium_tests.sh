#!/usr/bin/env bash

# Run this from travis

# Print runtime variable
echo "Running GeoSAFE Selenium test"
echo "COMPOSE_PROJECT_NAME=$COMPOSE_PROJECT_NAME"
echo "COMPOSE_FILE=$COMPOSE_FILE"

# Note that Selenium test need to preserve test db (not delete it after the test)
# This is because, Selenium had the database connection shared, so when it tries to
# do a cleanup when deleting the database it will fail to do so, because there are other threads
# who have the connection open.
TEST_ARG="geosafe.tests.selenium --noinput --liveserver=0.0.0.0:8000 --nomigrations --keepdb"

echo "Test argument: ${TEST_ARG}"

until docker-compose exec django /bin/bash -c "export SELENIUM_UNIT_TEST_FLAG=True; python manage.py test ${TEST_ARG}"; do
	# Retrieve exit code
	exit_code=$?
	echo "EXIT CODE: $exit_code"

	if [ "$exit_code" -eq "1" ]; then
		echo "Unittests failed"
		echo "Print docker inasafe headless log"
		echo
		docker-compose logs inasafe-headless
		echo
		echo "Print db log"
		docker-compose logs db
		echo
		echo "Print django log"
		docker-compose logs django
		echo
		echo "Print compose ps"
		docker-compose ps
		echo
		echo "Print docker ps"
		docker ps
		echo
		exit 1
	fi
	# investigate why it failed
	echo "Is it memory error?"
	journalctl -k | grep -i -e memory -e oom

	echo "Docker inspect"
	docker inspect geonode-docker_django_1

	# Restart attempt
	echo "$PWD"
	make up
	sleep 10
done

echo "Testing finished"
