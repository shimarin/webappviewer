.PHONY: install clean

PYTHON_USER_SITE=$(shell python -c "import site; print(site.getusersitepackages())")
APPS_DIR=$(PYTHON_USER_SITE)/webappviewer_apps

install:
	echo "Installing webappviewer to $(PYTHON_USER_SITE)"
	cp webappviewer.py $(PYTHON_USER_SITE)/webappviewer.py
	mkdir -p $(APPS_DIR)
	cp -r webappviewer_apps/*.py $(APPS_DIR)

clean:
	rm -rf dist build webappviewer.spec
