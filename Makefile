default: all


all: init

init:
	@echo 'INIT: Not sure how we can use an env if running as a script from anywhere'
	# pip3 freeze > req2
	# pip3 install -r requirements.txt

mkreq: 
	pip3 freeze > requirements.txt

env: requirements.txt
	python3 -m venv --without-pip --symlinks --system-site-packages env

clean:
	rm -rf __pycache__
	rm -rf $(shell find . -name "*.pyc" -type f)
	rm -rf $(shell find ./env -type f)
	rm -rf $(shell /usr/local/bin/fd -e env -tf)
	@echo ""
	$(shell cd ./basern; make clean)

# to add a new "requirement" 
#  pip3 install --dry-run pyclip
#  pip3 install --verbose pyclip
