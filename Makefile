default: all

all: init

init:
	@echo 'INIT: Not sure how we can use an env if running as a script from anywhere'
	# pip3 --debug freeze --local > requirements.txt
	# pip3 install -r requirements.txt

mkreq: 
	pip3 freeze --local > requirements.txt
	pip3 freeze --verbose --all >> requirements.txt
	@echo " NOTE-PRE-COMMIT> Remove pip/pywin32 not-cross-platform deps manually"

## pip25 requires local installation?
venv: requirements.txt
	python3 -m venv --symlinks --system-site-packages venv
#	python3 -m venv --symlinks --system-site-packages venv --clear --without-pip 

deep-clean: clean
	rm -rf ./env
	rm -rf ./venv
#	@echo "no-dir done"

# -I cleans up virtual env also
clean:
	rm -rf $(shell fd -IH -E venv -tf -e pyc)
	@echo " >> pyc done"
	rm -rf $(shell fd -IH -E venv -td __pycache__ )
	@echo " >> cache done"
	@echo ""

# to add a new "requirement" 
#  pip3 install --dry-run pyclip
#  pip3 install --verbose pyclip
