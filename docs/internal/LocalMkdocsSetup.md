# Local MkDocs Testing

This is a short canned synopsis for running [MkDdocs](https://www.mkdocs.org/) locally while editing the docs.

## Install mkdocs

```bash
#  mkdocs is python-based
pip3 install mkdocs

# or on mac systems
brew install mkdocs
```

## Install extensions

```bash
pip3 install -r requirements.txt
```

This installs the `mkdocs-material` theme which we use, along with other dependencies.

## Generate mkdocs configuration

```
make
```

This auto-generates the doc files for tremor stdlib and cli, and also produces the default config file for
mkdocs (`mkdocs.yml`) file at the end (with the right navigation references to the generated stdlib docs).

## Build documentation

```bash
mkdocs build
```

## Local doc service

```bash
mkdocs serve
```

Now the docs will be available at http://127.0.0.1:8000/ for reviewing as you edit them (supports live-reload).
