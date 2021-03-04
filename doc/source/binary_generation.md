In order to generate the binary file, execute the following command (require pyinstaller):


```
pyinstaller -F antareslauncher/main_launcher.py -n Antares_Launcher
```

The generated binary file will be in dist directory. Note that pyinstaller does not enable the multi-platform cross-compilation. For instance the binary file generated on Windows can be executed only on the Windows OS.
