# Generate Sphinx documentation

> NOTE: you can also run: `make docs` to build the documentation using the Makefile.

Here is a step-by-step documentation:

Install tre required dependencies:

```shell
pip install -e .[docs]
```

Then, generate the API documentation and the HTML pages:

```shell
sphinx-apidoc -fMe -o doc/source/api antareslauncher/ -t doc/source/_templates/
sphinx-build -b html -d build/docs/doctrees doc/source dist/docs/html
```

Open the `index.html` file available in the folder `dist/docs/html` to display the documentation
