default: all


all: init

init:
	@echo 'INIT: Not sure how we can use an env if running as a script from anywhere'
	# pip3 --debug freeze --local > requirements.txt
	# pip3 install -r requirements.txt

mkreq: 
	pip3 freeze --local > requirements.txt

## pip25 requires local installation?
venv: requirements.txt
	python3 -m venv --symlinks --system-site-packages venv
#	python3 -m venv --symlinks --system-site-packages venv --clear --without-pip 

clean:
	rm -rf $(shell fd -I -tf -e pyc)
#	@echo "pyc done"
	rm -rf ./env
	rm -rf ./venv
#	@echo "no-dir done"
	rm -rf $(shell fd -I -td __pycache__ )
#	rm -rf __pycache__
	@echo ""
#	$(shell cd ./basern; make clean)
#	$(shell cd ./concurrent; make clean)
#	$(shell cd ./class; make clean)

# to add a new "requirement" 
#  pip3 install --dry-run pyclip
#  pip3 install --verbose pyclip
