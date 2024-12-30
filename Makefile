default: all


all: init

init:
	@echo 'INIT: Not sure how we can use an env if running as a script from anywhere'
	# pip3 --debug freeze --local > requirements.txt
	# pip3 install -r requirements.txt

mkreq: 
	pip3 freeze --local > requirements.txt

env: requirements.txt
	python3 -m venv --without-pip --symlinks --system-site-packages env

clean:
	rm -rf $(shell fd -I -tf -e pyc)
	rm -rf $(shell fd -I -tf ./env)
	rm -rf $(shell fd -I -tf -e env)
	rm -rf $(shell fd -I -td __pycache__ )
#	rm -rf __pycache__
	@echo ""
#	$(shell cd ./basern; make clean)
#	$(shell cd ./concurrent; make clean)
#	$(shell cd ./class; make clean)

# to add a new "requirement" 
#  pip3 install --dry-run pyclip
#  pip3 install --verbose pyclip
