<!-- .slide: data-background="#333333" -->

## Testing `tremor` solutions

This course is based around the tremor testing tooling which can
be invoked via the `tremor` command. In this course we will use
the command packaged with `docker` to avoid lengthy install times

```shell
$ tremor test # ... arguments
```

>>>

### Setup `docker`

This course assumes an installation of [docker](https://www.docker.com)

```shell [1|2|3|4-5]
$ export TREMOR_IMAGE=tremorproject/tremor:latest # set to `edge` if you feel lucky
$ docker pull $TREMOR_IMAGE
alias trecker=
  'docker run -i -v `pwd`:/pwd $TREMOR_IMAGE $*'
```

Validate the docker based tremor environment:

```shell
$ trecker -h
```

---

### Demo: `verify trecker setup`

![Check setup recording](./assets/check-setup.gif)

<div style='font-size: 20px'>
Hint: Pass `-e "TERM=xterm-256color"` to enable help syntax highlighting
</div>

>>>

### Setup `TREMOR_PATH`

```shell [|1-2|3-4]
# docker packaged standard modules
export TREMOR_PATH=/opt/local/tremor/lib
# docker and user defined mounted modules
export TREMOR_PATH=/opt/local/tremor/lib:/pwd/lib
```

<div style='font-size: 20px'>
Hint: The `TREMOR_PATH` environment variable controls visible modular libraries
available to trecker or tremor. For trecker we mount via `pwd` and expect `lib`
sub-folder in this course
</div>

---

### Local docker

```shell [|1-2|3-4]
# standard modules
export TREMOR_PATH=/path/to/tremor/lib
#  standard and user defined modules
export TREMOR_PATH=/path/to/tremor/lib:/my/project/lib
```

<div style='font-size: 20px'>
Hint: When building and running tremor locally the standard library can be found
in `tremor-script/lib` relative to your git clone. User defined module paths can
be provided to TREMOR_PATH which is a `:` delimited list of paths.
</div>

