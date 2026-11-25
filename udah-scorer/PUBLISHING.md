# Publishing udah-scorer to PyPI

The package is published from the owner's PyPI account. Two ways, both free.

## A. Trusted Publishing from GitHub (recommended: no token is stored anywhere)

1. Create an account at https://pypi.org and turn on two-factor authentication.
2. On PyPI, open **Your account > Publishing > Add a new pending publisher** and enter:
   - PyPI project name: `udah-scorer`
   - Owner: `luoxuejian000`
   - Repository: `traceai-udah-scorer-poc`
   - Workflow: `udah-publish.yml`
   - Environment: `pypi`
3. In the GitHub repository, open **Settings > Environments**, create `pypi`, and add yourself
   as a required reviewer, so that every release waits for your approval.
4. To release: raise `version` in `udah-scorer/pyproject.toml` and `__version__` in
   `src/udah_scorer/__init__.py`, push, then on GitHub open **Releases > Draft a new release**
   with the tag `udah-scorer-v0.1.0`. The workflow builds, runs the tests and publishes.

## B. By hand

```bash
cd udah-scorer
python -m pip install build twine
python -m build
python -m twine check dist/*
python -m twine upload dist/*
```

`twine upload` asks for an API token from **PyPI > Account settings > API tokens**.

Before the first real upload you can try the whole path on https://test.pypi.org with
`twine upload --repository testpypi dist/*`.
