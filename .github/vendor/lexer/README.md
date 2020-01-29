# **tremor-mkdocs-lexer**

A pygments lexer suitable for usage in mkdocs tremor documentation.

Currently, parses and syntax highlights tremor-script v0.5.

# Local setup on Mac OS X

```bash
$ git clone git@git.csnzoo.com:tremor/tremor-mkdocs-lexer
$ python3 ./setup.py install
```

# Local console based teesting

```bash
$ pygmentize -l tremor /path/to/file.tremor
```

# Mkdocs setup

No setup required for local testing, the module will be automatically registered to mkdocs and available
in markdown through the following code:

<pre>
```tremor
drop "snot";
```
</pre>

# Mkdocs integration test

```
$ mkdocs serve
```
