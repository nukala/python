PYTHON=python
PIP=pip

default: all

all: init

init:
	@echo 'INIT: Not sure how we can use an env if running as a script from anywhere'
	# ${PIP} --debug freeze --local > requirements.txt
	# ${PIP} install -r requirements.txt

mkreq: 
	${PIP} freeze --local > requirements.txt
	# all includes installation stuff too
	#${PIP} freeze --verbose --all >> requirements.txt
	@echo " NOTE-PRE-COMMIT> Remove pip/pywin32 not-cross-platform deps manually"

## pip25 requires local installation?
venv: requirements.txt
	${PYTHON} -m venv --symlinks --system-site-packages venv
#	${PYTHON} -m venv --symlinks --system-site-packages venv --clear --without-pip 

deep-clean: clean
	@rm -rf ./env
	@echo " >> env deep-cleaned"
	@rm -rf ./venv
	@echo " >> venv deep-cleaned"
	@echo ""

# -I cleans up virtual env also
clean:
	@rm -rf $(shell fd -IH -tf -E venv -e pyc)
	@echo " >> pyc cleaned"
	@rm -rf $(shell fd -IH -td -E venv -E env __pycache__ )
	@echo " >> cache cleaned"
	@echo ""

# to add a new "requirement" 
#  ${PIP} install --dry-run pyclip
#  ${PIP} install --verbose pyclip
#  ${PIP} install -r requirements.txt --upgrade --verbose
#  ${PYTHON} -m pip install --upgrade pip --verbose
#  ${PIP} install --ignore-installed --local --verbose --dry-run pyclip
