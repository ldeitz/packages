# forthebirds

This is a Python package that enables birders to find locations anywhere in the world with birds of interest. This is a partial wrapper for the [eBird API](https://documenter.getpostman.com/view/664302/S1ENwy59) that uses some, but not all, of the endpoints. The main functions return dataframes with recent observations, notable observations, and observations specific to certain locations. This package can search at a country, state, or 'substate' level (equivalent to county-level in the United States).

## Installation

```bash
$pip install -i https://test.pypi.org/simple/ forthebirds```
```

## Usage

To use this package, you must have an eBird API token. This is available for free through the eBird website if you have an account.

## License

`forthebirds` was created by Lauren Deitz. It is licensed under the terms of the MIT license.

## Credits

`forthebirds` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
