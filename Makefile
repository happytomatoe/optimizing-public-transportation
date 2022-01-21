VENV_NAME?=venv
VENV_ACTIVATE=. $(VENV_NAME)/bin/activate
PYTHON_VENV=${VENV_NAME}/bin/python3
PYSPARK_VENV=${VENV_NAME}/bin/pyspark
PYTHON_LOCAL=python3


prepare-dev:
	sudo apt-get -y install python3.8 python3-pip

create-venv:	
	python3 -m pip install virtualenv
	test -d $(VENV_NAME) || virtualenv -p python3 $(VENV_NAME)
	${PYTHON_VENV} -m pip install -U pip

compose:
	docker-compose up -d

logs:
	docker-compose logs -f --tail="20"

producers-prepare: create-venv
	${PYTHON_VENV} -m pip  install  -r producers/requirements.txt
	touch $(VENV_NAME)/bin/activate

producer: producers-prepare
	${VENV_ACTIVATE}&&${PYTHON_VENV} producers/simulation.py

connector:
	curl -X DELETE http://localhost:8083/connectors/stations
	${VENV_ACTIVATE}&&${PYTHON_VENV} producers/connector.py

consumers-prepare: create-venv
	${PYTHON_VENV} -m pip  install  -r consumers/requirements.txt
	touch $(VENV_NAME)/bin/activate

faust: consumers-prepare
	${VENV_ACTIVATE}&&cd consumers&&faust -A faust_stream worker -l info

ksql: consumers-prepare
	${VENV_ACTIVATE}&&cd consumers&&../${PYTHON_VENV} ksql.py

consumer: consumers-prepare
	${VENV_ACTIVATE}&&cd consumers&&../${PYTHON_VENV} server.py

clean:
	rm -rf venv
	find -iname "*.pyc" -delete
	docker-compose down -v
	rm -rf zoo
