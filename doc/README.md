# Generate Sphinx documentation
/!\\ In construction
This is a test
To generate the documentation, you will need Sphinx, a
Documentation building tool, and a nice-looking custom
[Sphinx theme similar to the one of readthedocs.io](https://sphinx-rtd-theme.readthedocs.io/en/latest/):
```
pip install sphinx sphinx_rtd_theme recommonmark
```
Then in the current folder:
```
sphinx-apidoc -fMe -o source/ ../antareslauncher/ -t source/_templates/
sphinx-build -b html ./source ./build
```
The html will be available within the folder doc/build.

