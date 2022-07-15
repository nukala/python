
init:
	virtualenv -v --setuptools env

clean:
	rm -rf __pycache__
	rm -rf $(shell find . -name "*.pyc" -type f)
	@echo ""
	$(shell cd ./basern; make clean)
