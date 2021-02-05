## Tremor Script expressions
<!-- .slide: data-background="#FF7733" -->

<p style='font-size: 20px'>
This course introduces the expression oriented `tremor-script` ( `tremor` for short )
domain specific language. The `tremor-script` language is defined to work on continuous
streams of data in the context of an event based data-distribution engine.
</p>

<p style='font-size: 20px'>
The language can be used independently of the tremor runtime, although it is primarily
designed to be used inside the `tremor` runtime.
</p>

>>>

### expressions - literals

```tremor
null         # an undefined value
true false   # boolean
1 2 3        # integer
1.23e10      # floating point
"string"     # utf-8 string
[1,2,3]      # array-like
{ "k": "v" } # record-like

"""
Strings and heredocs support #{foo} interpolation
"""
```

>>>

### expressions - unary and binary

<p style='font-size: 20px'>
Tremor supports logical, bitwise, binary, equality, comparative
shift, additive, multiplicative and unary operations in a similar
way to other languages ( C/Java precedence ).
</p>

```tremor
# pseudocode
a ( or xor and ) b  # logical or, xor, and
a ( | ^ & )  b      # bitwise or, xor, and
a ( || && ) b       # binary xor, and
a ( == != ) b       # equals, not equals
a ( >= > <= < ) b   # comparative
a ( >> <<<  << ) b  # shift
a ( + - ) b         # additive
a ( * / % ) b       # multiplicative
( + - not ) a       # unary
```

>>>

### expressions - simple

<div style='font-size: 20px'>
Tremor also supports convenience expressions such as
</div>

```tremor
# pseudocode
$foo.bar[10].baz["snot"]  # path expressions
present <path>            # presence
absent <path>             # absence
( <expr )                 # parenthetic sub-expressions
badger(foo, bar, 1)       # aliased / local function calls
module::snot::badger(foo) # modular / absolute function calls
let foo = <expr>          # mutable path bindings
const foo = <expr>        # immutable path bindings
```

>>>

### expressions - streams

<div style='font-size: 20px'>
As tremor is designed to operate on streaming data it has stream control expressions
</div>

```tremor
emit "snot"              # stop control flow and emit `snot` to the default outbound stream, on the default out port
emit "snot" => badger    # stop control flow and emit `snot` to the default outbound stream on the user defined `badger` port
drop "snot"              # drop and stop processing with `snot` as the error value for the standard error stream
```

>>>

### `<path>` expressions

<div style='font-size: 20px'>
A path expression operates similarly to JSON or XML Path expressions using the `.` character
to index into nested record fields and `[]` to index into arrays or record fields by name
</div>

```tremor
# pseudocode
$foo           # the meta variable `foo`
foo            # the local variable `foo`
foo[0]         # first element of variable `foo`, assuming it is an array-like value
foo['tremolo'] # the element named 'tremolo', assuming `foo` is a record-like value
```

<div style='font-size: 20px'>
The atoms `$`, `event`, `state`, `args` have specific meaning in `tremor-script`. They can be
indexed against using path expressions but their values are context dependent and provided by
the tremor runtime.
</div>

>>>

### `<path>` specific atoms

|Atom|Description|
|---|---|
|$|The `$` atom references global metadata state that is shared to the executing context|
|event|The `event` atom references the current event streaming through the script|
|state|The `state` atom references state stored within the script that persists for the lifetime of the script|
|args|The `args` atom references arguments, such as arguments to user defined functions|

>>>

### expressions - structural

<div style='font-size: 20px'>
Richer structural expression forms with separate courses:
</div>

|Atom|Description|Guide|
|---|---|---|
|[`for`](./for.html)|`for` comprehensions|
|[`fn`](./fn.html)|Function definitions|
|[`mod`](./mod.html)|Module definitions|
|[`match`](./match.html)|Data structure pattern matching|
|[`merge`](./merge.html)|Data structure merge operations|
|[`patch`](./patch.html)|Data structure patch operations|

>>>

### End of `expression` guide
<!-- .slide: data-background="#77FF33" -->

This is the end of the `expression` getting started guide

Note: This will only appear in speaker notes window


