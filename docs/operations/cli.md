# Tremor tool v0.9

Tremor cli - Command Line Interface


# Scope

This document summarises tremor tool commands

# Audience

Tremor operators and developers

# General flags and switches

        

**Arguments**

|Name|Switch|Kind|Multiple|Description|
|----|------|----|--------|-----------|
|verbose|None|switch/flag|yes|Sets the level of verbosity|

**Subcommands**

|Command|Description|
|-------|-----------|
|[completions](#command-completions)|Generate shell completions to stdout. Tries to guess the shell if no subcommand is given.|
|[server](#command-server)|Tremor server|
|[test](#command-test)|Testing facilities|
|[dbg](#command-dbg)|Advanced debugging commands|
|[run](#command-run)|Run tremor script or query files against stdin or a json data archive, the data will be read from STDIN or an archive and written to STDOUT.|
|[doc](#command-doc)|Generates documention from tremor script files|
|[api](#command-api)|Tremor API client|

#### Command: **completions**

Generate shell completions to stdout. Tries to guess the shell if no subcommand is given.


**Subcommands**

|Command|Description|
|-------|-----------|
|[guess](#command-completions-guess)|Generate completion based on active shell|
|[bash](#command-completions-bash)|Generate bash shell completions|
|[zsh](#command-completions-zsh)|Generate zsh shell completions|
|[elvish](#command-completions-elvish)|Generate elvish shell completions|
|[fish](#command-completions-fish)|Generate fish shell completions|
|[powershell](#command-completions-powershell)|Generate powershell shell completions|

##### Command: completions **guess**

Generate completion based on active shell

**Usage**

```
tremor completions guess
```

##### Command: completions **bash**

Generate bash shell completions

**Usage**

```
tremor completions bash
```

##### Command: completions **zsh**

Generate zsh shell completions

**Usage**

```
tremor completions zsh
```

##### Command: completions **elvish**

Generate elvish shell completions

**Usage**

```
tremor completions elvish
```

##### Command: completions **fish**

Generate fish shell completions

**Usage**

```
tremor completions fish
```

##### Command: completions **powershell**

Generate powershell shell completions

**Usage**

```
tremor completions powershell
```

#### Command: **server**

Tremor server


**Subcommands**

|Command|Description|
|-------|-----------|
|[run](#command-server-run)|Runs the tremor server process|

##### Command: server **run**

Runs the tremor server process

**Usage**

```
tremor server run
```

**Arguments**

|Name|Switch|Kind|Multiple|Description|
|----|------|----|--------|-----------|
|artefacts|None|switch/flag|yes|Paths to files containing pipelines, onramps, offramps to provision|
|storage-directory|None|switch/flag|no|Directory to cache/store runtime type information|
|pid|None|switch/flag|no|Captures process id if set and stores in a file|
|no-api|None|switch/flag|no|Disable the API|
|api-host|None|switch/flag|no|The `host:port` to listen for the API|
|instance|None|switch/flag|no|Instance identifier|
|logger-config|None|switch/flag|no|log4rs config|
|recursion-limit|None|switch/flag|no|function tail-recursion stack depth limit|

#### Command: **test**

Testing facilities

**Usage**

```
tremor test [<MODE>] [<PATH>]
```

**Arguments**

|Name|Switch|Kind|Multiple|Description|
|----|------|----|--------|-----------|
|MODE|None|switch/flag|no|One of `all`, `api`, `bench`, `command`, `integration`, `rest`, or `unit`|
|PATH|None|switch/flag|no|The root test path|
|REPORT|None|switch/flag|no|Should generate a test report to specified path|
|INCLUDES|None|switch/flag|yes|Optional tags to filter test executions by|
|EXCLUDES|None|switch/flag|yes|Optional tags to filter test executions by|

#### Command: **dbg**

Advanced debugging commands


**Arguments**

|Name|Switch|Kind|Multiple|Description|
|----|------|----|--------|-----------|
|no-banner|None|switch/flag|no|do not print the banner|
|no-highlight|None|switch/flag|no|do not highlight output|

**Subcommands**

|Command|Description|
|-------|-----------|
|[dot](#command-dbg-dot)|prints the .dot representation for a trickle file|
|[ast](#command-dbg-ast)|prints the AST of the source|
|[preprocess](#command-dbg-preprocess)|prints the preprocessed source|
|[lex](#command-dbg-lex)|prints lexemes|
|[src](#command-dbg-src)|prints source|

##### Command: dbg **dot**

prints the .dot representation for a trickle file

**Usage**

```
tremor dbg dot [<SCRIPT>]
```

**Arguments**

|Name|Switch|Kind|Multiple|Description|
|----|------|----|--------|-----------|
|SCRIPT|None|switch/flag|no|trickle script filename|

##### Command: dbg **ast**

prints the AST of the source

**Usage**

```
tremor dbg ast [<SCRIPT>]
```

**Arguments**

|Name|Switch|Kind|Multiple|Description|
|----|------|----|--------|-----------|
|SCRIPT|None|switch/flag|no|tremor/json/trickle script filename|

##### Command: dbg **preprocess**

prints the preprocessed source

**Usage**

```
tremor dbg preprocess [<SCRIPT>]
```

**Arguments**

|Name|Switch|Kind|Multiple|Description|
|----|------|----|--------|-----------|
|SCRIPT|None|switch/flag|no|tremor/json/trickle script filename|

##### Command: dbg **lex**

prints lexemes

**Usage**

```
tremor dbg lex [<SCRIPT>]
```

**Arguments**

|Name|Switch|Kind|Multiple|Description|
|----|------|----|--------|-----------|
|SCRIPT|None|switch/flag|no|tremor/json/trickle script filename|

##### Command: dbg **src**

prints source

**Usage**

```
tremor dbg src [<SCRIPT>]
```

**Arguments**

|Name|Switch|Kind|Multiple|Description|
|----|------|----|--------|-----------|
|SCRIPT|None|switch/flag|no|tremor/json/trickle script filename|

#### Command: **run**

Run tremor script or query files against stdin or a json data archive, the data will be read from STDIN or an archive and written to STDOUT.


**Usage**

```
tremor run [<SCRIPT>]
```

**Arguments**

|Name|Switch|Kind|Multiple|Description|
|----|------|----|--------|-----------|
|SCRIPT|None|switch/flag|no|filename to run the data through|
|interactive|None|switch/flag|no|Should not output to consumed source / produced synthetic data or errors|
|pretty|None|switch/flag|no|Should not pretty print data [ when in interactive mode ]|
|ENCODER|None|switch/flag|no|The codec to use for encoding the data|
|DECODER|None|switch/flag|no|The codec to use for decoding the data|
|INFILE|None|switch/flag|no|input file|
|OUTFILE|None|switch/flag|no|output file|
|PREPROCESSOR|None|switch/flag|no|preprocessor to pass data through before decoding|
|POSTPROCESSOR|None|switch/flag|no|postprocessor to pass data through after encoding|
|output-port|None|switch/flag|no|selects the port to pull output|

#### Command: **doc**

Generates documention from tremor script files


**Usage**

```
tremor doc [<DIR>] [<OUTDIR>]
```

**Arguments**

|Name|Switch|Kind|Multiple|Description|
|----|------|----|--------|-----------|
|interactive|None|switch/flag|no|generates output to standard output|
|DIR|None|switch/flag|no|directory or source to generate documents for|
|OUTDIR|None|switch/flag|no|directory to generate documents into|

#### Command: **api**

Tremor API client


**Arguments**

|Name|Switch|Kind|Multiple|Description|
|----|------|----|--------|-----------|
|FORMAT|None|switch/flag|no|Sets the output format|
|CONFIG|None|switch/flag|no|Sets a custom config file|

**Subcommands**

|Command|Description|
|-------|-----------|
|[version](#command-api-version)|Get tremor version|
|[target](#command-api-target)|Target one or many tremor server instances|
|[binding](#command-api-binding)|Query/update binding specification repository|
|[pipeline](#command-api-pipeline)|Query/update pipeline specification repository|
|[onramp](#command-api-onramp)|Query/update onramp specification repository|
|[offramp](#command-api-offramp)|Query/update offramp specification repository|

##### Command: api **version**

Get tremor version

**Usage**

```
tremor api version
```

##### Command: api **target**

Target one or many tremor server instances


**Subcommands**

|Command|Description|
|-------|-----------|
|[list](#command-api-target-list)|List registered targets|
|[create](#command-api-target-create)|Create a new API target|
|[delete](#command-api-target-delete)|Delete an existing API target|

###### Command: api target **list**

List registered targets

**Usage**

```
tremor api target list
```

###### Command: api target **create**

Create a new API target

**Usage**

```
tremor api target create [<TARGET_ID>] [<SOURCE>]
```

**Arguments**

|Name|Switch|Kind|Multiple|Description|
|----|------|----|--------|-----------|
|TARGET_ID|None|switch/flag|no|The unique target id for the targetted tremor servers|
|SOURCE|None|switch/flag|no|JSON or YAML file request body|

###### Command: api target **delete**

Delete an existing API target

**Usage**

```
tremor api target delete [<TARGET_ID>]
```

**Arguments**

|Name|Switch|Kind|Multiple|Description|
|----|------|----|--------|-----------|
|TARGET_ID|None|switch/flag|no|The unique target id for the targetted tremor servers|

##### Command: api **binding**

Query/update binding specification repository


**Subcommands**

|Command|Description|
|-------|-----------|
|[list](#command-api-binding-list)|List registered binding specifications|
|[fetch](#command-api-binding-fetch)|Fetch a binding by artefact id|
|[delete](#command-api-binding-delete)|Delete a binding by artefact id|
|[create](#command-api-binding-create)|Create and register a binding specification|
|[instance](#command-api-binding-instance)|Fetch an binding instance by artefact id and instance id|
|[activate](#command-api-binding-activate)|Activate a binding by artefact id and servant instance id|
|[deactivate](#command-api-binding-deactivate)|Activate a binding by artefact id and servant instance id|

###### Command: api binding **list**

List registered binding specifications

**Usage**

```
tremor api binding list
```

###### Command: api binding **fetch**

Fetch a binding by artefact id

**Usage**

```
tremor api binding fetch [<ARTEFACT_ID>]
```

**Arguments**

|Name|Switch|Kind|Multiple|Description|
|----|------|----|--------|-----------|
|ARTEFACT_ID|None|switch/flag|no|The unique artefact id for the binding specification|

###### Command: api binding **delete**

Delete a binding by artefact id

**Usage**

```
tremor api binding delete [<ARTEFACT_ID>]
```

**Arguments**

|Name|Switch|Kind|Multiple|Description|
|----|------|----|--------|-----------|
|ARTEFACT_ID|None|switch/flag|no|The unique artefact id for the binding specification|

###### Command: api binding **create**

Create and register a binding specification

**Usage**

```
tremor api binding create [<SOURCE>]
```

**Arguments**

|Name|Switch|Kind|Multiple|Description|
|----|------|----|--------|-----------|
|SOURCE|None|switch/flag|no|JSON or YAML file request body|

###### Command: api binding **instance**

Fetch an binding instance by artefact id and instance id

**Usage**

```
tremor api binding instance [<ARTEFACT_ID>] [<INSTANCE_ID>]
```

**Arguments**

|Name|Switch|Kind|Multiple|Description|
|----|------|----|--------|-----------|
|ARTEFACT_ID|None|switch/flag|no|The unique artefact id for the binding specification|
|INSTANCE_ID|None|switch/flag|no|The unique instance id for the binding specification|

###### Command: api binding **activate**

Activate a binding by artefact id and servant instance id

**Usage**

```
tremor api binding activate [<ARTEFACT_ID>] [<INSTANCE_ID>] [<SOURCE>]
```

**Arguments**

|Name|Switch|Kind|Multiple|Description|
|----|------|----|--------|-----------|
|ARTEFACT_ID|None|switch/flag|no|The unique artefact id for the binding specification|
|INSTANCE_ID|None|switch/flag|no|The unique instance id for the binding specification|
|SOURCE|None|switch/flag|no|JSON -r YAML file request body|

###### Command: api binding **deactivate**

Activate a binding by artefact id and servant instance id

**Usage**

```
tremor api binding deactivate [<ARTEFACT_ID>] [<INSTANCE_ID>]
```

**Arguments**

|Name|Switch|Kind|Multiple|Description|
|----|------|----|--------|-----------|
|ARTEFACT_ID|None|switch/flag|no|The unique artefact id for the binding specification|
|INSTANCE_ID|None|switch/flag|no|The unique instance id for the binding specification|

##### Command: api **pipeline**

Query/update pipeline specification repository


**Subcommands**

|Command|Description|
|-------|-----------|
|[list](#command-api-pipeline-list)|List registered pipeline specifications|
|[fetch](#command-api-pipeline-fetch)|Fetch a pipeline by artefact id|
|[delete](#command-api-pipeline-delete)|Delete a pipeline by artefact id|
|[create](#command-api-pipeline-create)|Create and register a pipeline specification|
|[instance](#command-api-pipeline-instance)|Fetch an pipeline instance by artefact id and instance id|

###### Command: api pipeline **list**

List registered pipeline specifications

**Usage**

```
tremor api pipeline list
```

###### Command: api pipeline **fetch**

Fetch a pipeline by artefact id

**Usage**

```
tremor api pipeline fetch [<ARTEFACT_ID>]
```

**Arguments**

|Name|Switch|Kind|Multiple|Description|
|----|------|----|--------|-----------|
|ARTEFACT_ID|None|switch/flag|no|The unique artefact id for the pipeline specification|

###### Command: api pipeline **delete**

Delete a pipeline by artefact id

**Usage**

```
tremor api pipeline delete [<ARTEFACT_ID>]
```

**Arguments**

|Name|Switch|Kind|Multiple|Description|
|----|------|----|--------|-----------|
|ARTEFACT_ID|None|switch/flag|no|The unique artefact id for the pipeline specification|

###### Command: api pipeline **create**

Create and register a pipeline specification

**Usage**

```
tremor api pipeline create [<SOURCE>]
```

**Arguments**

|Name|Switch|Kind|Multiple|Description|
|----|------|----|--------|-----------|
|SOURCE|None|switch/flag|no|JSON or YAML file request body|

###### Command: api pipeline **instance**

Fetch an pipeline instance by artefact id and instance id

**Usage**

```
tremor api pipeline instance [<ARTEFACT_ID>] [<INSTANCE_ID>]
```

**Arguments**

|Name|Switch|Kind|Multiple|Description|
|----|------|----|--------|-----------|
|ARTEFACT_ID|None|switch/flag|no|The unique artefact id for the pipeline specification|
|INSTANCE_ID|None|switch/flag|no|The unique instance id for the pipeline specification|

##### Command: api **onramp**

Query/update onramp specification repository


**Subcommands**

|Command|Description|
|-------|-----------|
|[list](#command-api-onramp-list)|List registered onramp specifications|
|[fetch](#command-api-onramp-fetch)|Fetch an onramp by artefact id|
|[delete](#command-api-onramp-delete)|Delete an onramp by artefact id|
|[create](#command-api-onramp-create)|Create and register an onramp specification|
|[instance](#command-api-onramp-instance)|Fetch an onramp instance by artefact id and instance id|

###### Command: api onramp **list**

List registered onramp specifications

**Usage**

```
tremor api onramp list
```

###### Command: api onramp **fetch**

Fetch an onramp by artefact id

**Usage**

```
tremor api onramp fetch [<ARTEFACT_ID>]
```

**Arguments**

|Name|Switch|Kind|Multiple|Description|
|----|------|----|--------|-----------|
|ARTEFACT_ID|None|switch/flag|no|The unique artefact id for the onramp specification|

###### Command: api onramp **delete**

Delete an onramp by artefact id

**Usage**

```
tremor api onramp delete [<ARTEFACT_ID>]
```

**Arguments**

|Name|Switch|Kind|Multiple|Description|
|----|------|----|--------|-----------|
|ARTEFACT_ID|None|switch/flag|no|The unique artefact id for the onramp specification|

###### Command: api onramp **create**

Create and register an onramp specification

**Usage**

```
tremor api onramp create [<SOURCE>]
```

**Arguments**

|Name|Switch|Kind|Multiple|Description|
|----|------|----|--------|-----------|
|SOURCE|None|switch/flag|no|JSON or YAML file request body|

###### Command: api onramp **instance**

Fetch an onramp instance by artefact id and instance id

**Usage**

```
tremor api onramp instance [<ARTEFACT_ID>] [<INSTANCE_ID>]
```

**Arguments**

|Name|Switch|Kind|Multiple|Description|
|----|------|----|--------|-----------|
|ARTEFACT_ID|None|switch/flag|no|The unique artefact id for the onramp specification|
|INSTANCE_ID|None|switch/flag|no|The unique instance id for the onramp specification|

##### Command: api **offramp**

Query/update offramp specification repository


**Subcommands**

|Command|Description|
|-------|-----------|
|[list](#command-api-offramp-list)|List registered offramp specifications|
|[fetch](#command-api-offramp-fetch)|Fetch an offramp by artefact id|
|[delete](#command-api-offramp-delete)|Delete an offramp by artefact id|
|[create](#command-api-offramp-create)|Create and register an offramp specification|
|[instance](#command-api-offramp-instance)|Fetch an offramp instance by artefact id and instance id|

###### Command: api offramp **list**

List registered offramp specifications

**Usage**

```
tremor api offramp list
```

###### Command: api offramp **fetch**

Fetch an offramp by artefact id

**Usage**

```
tremor api offramp fetch [<ARTEFACT_ID>]
```

**Arguments**

|Name|Switch|Kind|Multiple|Description|
|----|------|----|--------|-----------|
|ARTEFACT_ID|None|switch/flag|no|The unique artefact id for the offramp specification|

###### Command: api offramp **delete**

Delete an offramp by artefact id

**Usage**

```
tremor api offramp delete [<ARTEFACT_ID>]
```

**Arguments**

|Name|Switch|Kind|Multiple|Description|
|----|------|----|--------|-----------|
|ARTEFACT_ID|None|switch/flag|no|The unique artefact id for the offramp specification|

###### Command: api offramp **create**

Create and register an offramp specification

**Usage**

```
tremor api offramp create [<SOURCE>]
```

**Arguments**

|Name|Switch|Kind|Multiple|Description|
|----|------|----|--------|-----------|
|SOURCE|None|switch/flag|no|JSON or YAML file request body|

###### Command: api offramp **instance**

Fetch an offramp instance by artefact id and instance id

**Usage**

```
tremor api offramp instance [<ARTEFACT_ID>] [<INSTANCE_ID>]
```

**Arguments**

|Name|Switch|Kind|Multiple|Description|
|----|------|----|--------|-----------|
|ARTEFACT_ID|None|switch/flag|no|The unique artefact id for the offramp specification|
|INSTANCE_ID|None|switch/flag|no|The unique instance id for the offramp specification|
