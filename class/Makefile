
all:
	@echo "Specify init or clean goals"

init:
	virtualenv -v --setuptools env

clean:
	rm -rf $(shell fd -I -e pyc -tf)
	rm -rf __pycache__
