# Setting up MkDocs on Manjaro 

This is a step-by-step guideline for installing and running the MkDocs Documentation on Manjaro Linux distribution.

## MkDocs Installation

As you may already know, MkDocs is Python-based. Therefore, you need to install a recent version of Python as well as its package manager, `Pip`. Luckily, both of these are installed by default on Manjaro (like on most Linux distros). If you are using the latest version of Python, then Pip is definitely installed by default.

You may, however, need to upgrade Pip to the latest version if it's not up-to-date.

```bash
pip install --upgrade pip
```

To check for the version of Python and Pip you are using:

```bash
python --version
pip --version
```

You can now install MkDocs using Pip:

```bash
pip install mkdocs
```

## Install Dependencies

```bash
pip install -r requirements.txt
pip install -r python_scripts/requirements.txt
```

Clone `Lexer`, a Tremor-specific syntax highlighting tool into Tremor:

```bash
.github/scripts/install-lexer.sh
```

Install CMake, an open-source, cross-platform family of tools designed to build, test and package software. CMake will help in the compilation process, and to generate native makefiles.

Use `pacman`, the package manager from upstream Arch Linux, for the installation from root:

```bash
sudo pacman -S cmake
```

Install `Clang`, a compiler front end, using `Pamac`, Manjaro's package manager.

```bash
pamac install clang
```

## Generate Dynamic Documentation and Configuration

```bash
make clean
make
```

`make clean` gets rid of object and executable files that had been created in the meantime so as to get a fresh start and make a clean build. Sometimes, the compiler may link or compile files incorrectly; you only need to recompile the files you changed and link the newly created object files with the pre-existing ones. `make` auto-generates the doc files for tremor stdlib and cli and also produces the default config file for mkdocs, (`mkdocs.yml`) file, at the end (with the right navigation references to the generated stdlib docs).

## Build Documentation

```bash
mkdocs build
```

## Local Doc Service

Run the built-in development server:

```bash
mkdocs serve
```

The doc site will be available on your localhost, at [http://127.0.0.1:8000/](http://127.0.0.1:8000/), for reviewing (supports live-reload as you edit).
