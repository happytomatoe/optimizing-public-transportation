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
	docker-compose up -d --scale connect=1

create-connector:
	curl -XPOST -H "Content-type: application/json" -H "Accept: application/json" --data "@./connect/postgres-source.json" 'http://localhost:8083/connectors'

logs:
	docker-compose logs -f

producer: create-venv
	${PYTHON_VENV} -m pip  install  -r producers/requirements.txt
	touch $(VENV_NAME)/bin/activate
	${VENV_ACTIVATE}&&${PYTHON_LOCAL} producers/simulation.py


faust: create-venv
	${PYTHON_VENV} -m pip  install  -r consumers/requirements.txt
	touch $(VENV_NAME)/bin/activate
	${VENV_ACTIVATE}&&cd consumers&&faust -A faust_stream worker -l info

clean:
	rm -rf venv
	find -iname "*.pyc" -delete
	docker-compose down -v
	rm -rf zoo
