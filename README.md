# Interview problem solutions

The repository contains a CLI tool for VirusTotal API.
The tests for each module are located in a corresponding test module
within the same folder. The test module for each problem is named after
the problem's module, prefixed with `test_`. Tests can be run using the pytest tool.

---

The repository is powered by [Pants](https://www.pantsbuild.org/). You can easily
install it using this manual [installing Pants](https://www.pantsbuild.org/2.21/docs/getting-started/installing-pants).

The easiest way to run the CLI tool is to first package it using Pants by running:

```shell
pants package app/::
```

which will create a file located in `dist/app/virustotal.pex` and then just
using that file from CLI.
Tool accepts 3 CLI arguments:
1. --source/-S - the path to the source file with IOCs. Expected to be a JSON array
2. --debug (optional) - enables the debug mode, changes default INFO log level to DEBUG
3. --api-key - your API key for VirusTotal API

So the command with the debug mode to lookup IPs will look like:

```shell
./virustotal.pex --debug lookup_ips --source="PATH/TO/SOURCE.json" --api-key="YOUR_KEY"
```

and for URL lookup:

```shell
./virustotal.pex --debug lookup_urls --source="PATH/TO/SOURCE.json" --api-key="YOUR_KEY"
```

The tool uses Python's Click lib that has help capabilities so
if you just call `./virustotal.pex` it should help you with promts. 

You can also easily run the tests by:
and then running:

```shell
pants test problems/::
```

If you would like to contribute to the project, you can format your code
and lint it using [black](https://black.readthedocs.io/en/stable/) and 
[flake8](https://flake8.pycqa.org/en/latest/) 
to ensure your code is consistent with the existing codebase. To do that
first run:

```shell
pants fmt problems/::
```

to format the code using `black` and then lint it with `flake8` by running:

```shell
pants lint problems/::
```

The MyPy static type checker is also enabled, and you can run it with the following command:

```shell
pants check problems/::
```