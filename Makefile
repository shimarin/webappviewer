.PHONY: all install clean

PYTHON_USER_SITE=$(shell python -c "import site; print(site.getusersitepackages())")
APPS_DIR=$(PYTHON_USER_SITE)/webappviewer_apps

all:
	@echo "Nothing to build, webappviewer is a pure Python script."
	@echo "You can install it using 'make install'."

install:
	@echo "Installing webappviewer to $(PYTHON_USER_SITE)"
	cp webappviewer.py $(PYTHON_USER_SITE)/webappviewer.py
	mkdir -p $(APPS_DIR)
	cp -r webappviewer_apps/*.py $(APPS_DIR)
	@echo "Installation complete. You can now run webappviewer apps using 'python -m webappviewer <app_name>'."

clean:
	rm -rf __pycache__ webappviewer_apps/__pycache__

