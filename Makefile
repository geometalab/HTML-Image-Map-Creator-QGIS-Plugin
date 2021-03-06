
# install directory
INST_DIR = ~/.qgis/python/plugins/html_image_map_creator

# python qt4 binaries
PYRCC = /usr/bin/pyrcc4
PYUIC = /usr/bin/pyuic4

# qt-ui input and py-output file
# input (file is output of Qt-Designer)
UI_UI_FILE = src/html_image_map_creator_gui.ui
# output
UI_PY_FILE = src/ui_html_image_map_creator_gui.py

# resouce input and output file
# input
RC_QRC_FILE = src/html_image_map_creator_resources.qrc
# output
RC_PY_FILE = src/html_image_map_creator_rc.py




# 'compile' all ui and resource files
all: $(RC_PY_FILE) $(UI_PY_FILE)
# compile resource to resource python file (depends on the qrc file)
$(RC_PY_FILE): $(RC_QRC_FILE)
	$(PYRCC) -o $(RC_PY_FILE) $(RC_QRC_FILE)
# compile the qt4-ui file to the ui python file
$(UI_PY_FILE): $(UI-UI_FILE)
	$(PYUIC) -o $(UI_PY_FILE) $(UI_UI_FILE)


dist: cleandist
	mkdir -p dist/html_image_map_creator/doc
	cp *.* dist/html_image_map_creator
	cp doc/*.* dist/html_image_map_creator/doc/
	rm -f bin/html_image_map_creator.zip
	cd dist; zip -9rv bin/html_image_map_creator.zip  html_image_map_creator

cleandist:
	rm -rf dist

# install (depends on 'all')
install: all
	mkdir -p $(INST_DIR)/doc
	cp src/*.py $(INST_DIR)/
	cp -r src/doc/* $(INST_DIR)/doc/

clean:
	killall qgis
	rm -f $(RC_PY_FILE) $(UI_PY_FILE)
	rm -f src/*.pyc
	# clean up install directory
	rm -rf $(INST_DIR)

