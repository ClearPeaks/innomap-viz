# Python Template

Python template repository

# Get started

Install Python dependencies placed in [requirements.txt](requirements.txt) running:

```sh
pip install -e .
```

If you want to install the test dependencies (recommended for development), run:

```sh
pip install -e ".[dev]"
```

To run the project simply do:

```sh
python src/example.py
```

## Test

The tests are placed in the `tests` folder. To run them, you can simply run:

```sh
pytest -sv tests/unit
```

### codecoverage

To check the coverage of your project, you first must have your code gathered in unit tests, and latter you can run these set of commands:

```sh
coverage run --source=src/ --branch -m pytest tests/unit --junitxml=build/test.xml -v
coverage xml -i -o build/coverage.xml
coverage report
```

## Use pre-commit for code linting and security analysis

To assure the code quality we use various tools that check for security issues and best practices.
They can be executed automatically before each git commit using pre-commit.

In order to use pre-commit, it is necessary to install these libraries:

- Install https://pre-commit.com/
- Install https://flake8.pycqa.org/en/latest/ & https://pypi.org/project/flake8-annotations/
- Install https://pypi.org/project/isort/
- Install https://bandit.readthedocs.io/en/latest/start.html

They are included in the development requirements, so you can install them with this command:

`pip install -e .[dev]`

Once you have all the libraries installed, run the following command in order to execute the pre-commit hooks every time you perform a commit from your machine:

`pre-commit install`

You can manually run the checks without attempting to commit with the command:

`pre-commit run -a`
