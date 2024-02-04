SRC_DIR = dashboard/consumption

lint:
	python -m black $(SRC_DIR)
	python -m isort $(SRC_DIR)
	python -m bandit -r $(SRC_DIR)
	python -m flake8 --ignore=E265,E501,E741 $(SRC_DIR)

