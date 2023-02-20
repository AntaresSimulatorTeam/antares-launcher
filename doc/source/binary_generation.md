In order to generate the binary file, execute the following command (require pyinstaller):

To install pyinstaller, you can run:

```shell
pip install -e .[pyinstaller]
```

Then run the following command to compile the application on you platform:

```
pyinstaller -F antareslauncher/basic_launch.py -n Antares_Launcher
```

The generated binary file will be in `dist` directory.
Note that pyinstaller does not enable the multi-platform cross-compilation.
For instance the binary file generated on Windows can be executed only on the Windows OS.
