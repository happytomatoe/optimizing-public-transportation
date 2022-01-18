VENV_NAME?=venv
VENV_ACTIVATE=. $(VENV_NAME)/bin/activate
PYTHON_VENV=${VENV_NAME}/bin/python3
PYSPARK_VENV=${VENV_NAME}/bin/pyspark
PYTHON_LOCAL=python3


prepare-dev:
	sudo apt-get -y install python3.8 python3-pip

create-venv:	
	python3 -m pip install virtualenv

compose:
	docker-compose up -d

create-connector:
	curl -XPOST -H "Content-type: application/json" -H "Accept: application/json" --data "@./connect/postgres-source.json" 'http://localhost:8083/connectors'


producer:
	python3 -m pip install virtualenv
	test -d $(VENV_NAME) || virtualenv -p python3 $(VENV_NAME)
	${PYTHON_VENV} -m pip install -U pip
	${PYTHON_VENV} -m pip  install  -r producers/requirements.txt
	touch $(VENV_NAME)/bin/activate
	${VENV_ACTIVATE}&&${PYTHON_LOCAL} producers/simulation.py


clean:
	rm -rf venv
	find -iname "*.pyc" -delete