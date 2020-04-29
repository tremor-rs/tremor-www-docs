## Lexical Preprocessor

In order to support the module mechanism with minimal changes to the API and runtime,
a preprocessor loads all externally referenced modules used in tremor logic defined
in tremor-script or tremor-query and loads them inline into a preprocessed file.

It is an error to attempt to deploy a tremor-script or tremor-query file that uses the
module mechanism as source. The API only accepts non-modular files for backward compatibility
or preprocessed files. The latter constraint is to ensure that logic deployed into the
runtime is always traceable to source loaded by a user. Tremor explicitly avoids possibilities
of modular logic changing at runtime.

The preprocessor defends this guarantee on behalf of our users.

# Directives

The preprocessor has two directives

1. The `#!line` directive
2. The `#!config` directive

## Line directive

This directive tells the preprocessor that it is now in a logically different position of the file.

For each folder/directory that an included source traverses a module statement is injected into the consolidated source.

The `#!line` directive is a implementation detail mentioned here for the same of completeness and not meant to be used or relied on by end users. It may, without prior warning, be removed in the future.

## Config directive

This directive allows compile-time configuration paraemters to be passed into tremor

## Example preprocessed tremor-script

```tremor
#!line 0 0 0 1 ./foo/bar/snot.tremor
mod snot with
#!line 0 0 0 1 ./foo/bar/snot.tremor
const snot = "beep";
end;
#!line 19 1 0 0 script.tremor
#!line 0 0 0 2 ./foo/baz/badger.tremor
mod badger with
#!line 0 0 0 2 ./foo/baz/badger.tremor
const badger = "boop";
end;
#!line 41 1 0 0 script.tremor

let c = "{snot::snot}{badger::badger}";

emit c
```
