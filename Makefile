default: all


all: init

init:
	@echo 'INIT: Not sure how we can use an env if running as a script from anywhere'
	# pip3 freeze > req2
	# pip3 install -r requirements.txt
#	python3 -m venv --without-pip --symlinks --system-site-packages env

clean:
	rm -rf __pycache__
	rm -rf $(shell find . -name "*.pyc" -type f)
	@echo ""
	$(shell cd ./basern; make clean)
