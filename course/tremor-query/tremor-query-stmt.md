## Tremor Query statements 
<!-- .slide: data-background="#FF7733" -->

<p style='font-size: 20px'>
This course introduces the statement oriented `tremor-query` ( `trickle` for short )
domain specific language. The `tremor-query` language is defined to work on continuous
streams of data in the context of an event based data-distribution engine.
</p>

<p style='font-size: 20px'>
The language can be used independently of the tremor runtime, although it is primarily
designed to be used inside the `tremor` runtime.
</p>

>>>

### concepts - statements

![Tremor Query Statements](https://docs.tremor.rs/tremor-query/grammar/diagram/Query.png)

<p style='font-size: 20px'>
Tremor query statements are `;` semi-colon delimited. There must be
at least one statement in a well-formed legal query.
</p>

---

### concepts - streams

<p style='font-size: 20px'>
Queries are compiled by the tremor runtime into directed acyclic graphs. The graphs are
deployed into the runtime and continuously process events. There are three default streams
provided by the runtime:
</p>

|Stream Kind|Id|Description|
|---|---|---|
|Incoming events|`in`|Events flowing into query|
|Outbound events|`out`|events flowing out of query|
|Error events|`err`|runtime processing failures|

<p style='font-size: 20px'>
User defined streams can be created via the `create stream` statement.
</p>

---

### concepts - select

<p style='font-size: 20px'>
The basic connective tissue to wire up different query operations into
a connected data-low processing graph or pipeline is the select statement.
</p>

```trickle
# Echo or passthrough inbound data unmodified
select from in into out;
```

<p style='font-size: 20px'>
The `select` statement is the workhorse of the query language
and will be covered in depth in later sections. We will use it
in its simplest form to introduce other foundational concepts
at this stage.
</p>

---

### User defined streams

![Tremor Query Create Stream](https://docs.tremor.rs/tremor-query/grammar/diagram/CreateStreamDefn.png)

```trickle
create stream passthrough; # A user defined stream

## Forward inbound events
select from in into passthrough;

## Forward passthrough outbound
select from passhtrough into out;
```

<p style='font-size: 20px'>
All `create` statements in the query language result in modifying the query graph.
These constructs may affect the processing, routing and handling of events
at runtime.
</p>

---

### branching

<div class='mermaid'>
graph LR
  In[in] --> |select in into a| A(a)
  In[in] --> |select in into a| B(b)
  In[in] --> |select in into a| C(c)
</div>

```trickle
create stream a;
create stream b;
create stream c;

select from in into a;
select from in into b;
select from in into c;
```

---

### unioning

<div class='mermaid'>
graph LR
  A[a] --> |select a into out| Out(out)
  B[b] --> |select b into out| Out(out)
  C[c] --> |select c into out| Out(out)
</div>

```trickle
create stream a;
create stream b;
create stream c;

# ...

select from a into out;
select from b into out;
select from c into out;
```

>>>

### operators

<p style='font-size: 20px'>
Operators are nodes in a tremor query graph that process event data.
Operators may transform event data, enhance metadata, buffer events
or provide a means to modify the runtime behaviour of the pipeline
or runtime.
</p>
<p style='font-size: 20px'>
By default operators have an `in`, `out` and `err` streams just like
queries themselves.
</p>
<p style='font-size: 20px'>
Common operators or operations like `select` have their own syntax
in the language, but most operators have an interface and behaviour
that is not directly describable in tremor query syntax, or that cannot
be described ( or is not efficiently implementable in ) tremor script
syntax.
</p>

>>>

### builtin operators

Builtin operators are implemented in the rust programming language
and need to be declared in a query to be used. In tremor query the
`define` and `create` statements are used to define and configure
operators and to create in the query graph.

[Builtin Query Operators](https://docs.tremor.rs/tremor-query/operators/)

---

### operator definition

![Tremor Query Define Operator](https://docs.tremor.rs/tremor-query/grammar/diagram/DefineOperatorDefn.png)
<br/>
![Tremor Query Parameters](https://docs.tremor.rs/tremor-query/grammar/diagram/WithParams.png)

```trickle
# define the builting bucketing operator with default parameters
define grouper::bucket operator kfc;
```

<div style='font-size: 20px'>
A `define` statement does not insert a node into the running query graph. It specifies
a template from which running nodes can be created.
</div>

---

### operator creation

![Tremor Query Create Operator](https://docs.tremor.rs/tremor-query/grammar/diagram/CreateOperatorDefn.png)
<br/>
![Tremor Query Parameters](https://docs.tremor.rs/tremor-query/grammar/diagram/WithParams.png)

```trickle
create operator kfc;

select event in into kfc;
select event from kfc into out;
```

<div style='font-size: 20px'>
A `create` statement creates a running instance of the `kfc` operator.
The instance can override default parameters for that operator. The select
statement can be used to connect to/from the operator.
</div>

>>>

### script definition

![Tremor Query Script Operator](https://docs.tremor.rs/tremor-query/grammar/diagram/DefineScriptDefn.png)
![Tremor Query With Partial Params](https://docs.tremor.rs/tremor-query/grammar/diagram/WithPartialParams.png)

```trickle
# Use a builtin operator
define grouper::bucket operator kfc;
# Invent our own `categorize` scripted operator
define script categorize
script
  let $rate = 1;
  let $class = event.`group`;
  { "event": event, "rate": $rate, "class": $class };
end;
```

<div style='font-size: 20px'>
The `script` operator can be used to embed [tremor-script](https://docs.tremor.rs/tremor-script/) into the
query language. This is the primary mechanism by which user defined operators can be engineered by users of
tremor.
</div>

---

### script creation

```trickle
create script categorize;
# Stream ingested data into categorize script
select event from in into categorize;

create operator kfc;
# Stream scripted events into kfc bucket operator
select event from categorize into kfc;

# Stream bucketed events into out stream
select event from kfc into out;
```

<div style='font-size: 20px'>
Once defined our custom categorization can be used in
the same way as a bulitin.
</div>

>>>

### select operator

![Tremor Query Select Statement](https://docs.tremor.rs/tremor-query/grammar/diagram/SelectStmt.png)
![Tremor Query From Clause](https://docs.tremor.rs/tremor-query/grammar/diagram/FromClause.png)
![Tremor Query Into Clause](https://docs.tremor.rs/tremor-query/grammar/diagram/IntoClause.png)

<div style='font-size: 20px'>
In its most basic form, select is used to connect operators and streams
</div>

---

### select as filter

![Tremor Query Where Clause](https://docs.tremor.rs/tremor-query/grammar/diagram/WhereClause.png)
![Tremor Query Having Clause](https://docs.tremor.rs/tremor-query/grammar/diagram/HavingClause.png)

```trickle [2-3|3|6-7|7]
# Filter unselected events from incoming events
select event from in
where in.selected = true into out;

# Filter events based on the ingest timestamp on the event
select event from in into out
having system::ingest_ns() % 2 == 0;
```

<div style='font-size: 20px'>
The `where` and `having` clauses use predicate expressions to filter
event streams. The `where` operation filters into the operator. The `having`
operation filters on the output event from the operator.
</div>
---

### select as transformer

```trickle
select {
  "snot": "badger",
  "received": event,
  "extracting": event.record.array[10],
  "computing": for event.record.array of
     case (i, e) => { "#{i}": e }
  end
} into out;
```

<div style='font-size: 20px'>
The target expression of a select operation can be any legal `tremor-script`
expression as these always return types.
</div>

---

### select as grouper

![Tremor Query Group By Clause](https://docs.tremor.rs/tremor-query/grammar/diagram/GroupByClause.png)
![Tremor Query Group By Clause](https://docs.tremor.rs/tremor-query/grammar/diagram/GroupByDimension.png)
![Tremor Query Group By Clause](https://docs.tremor.rs/tremor-query/grammar/diagram/SetBasedGroup.png)
![Tremor Query Group By Clause](https://docs.tremor.rs/tremor-query/grammar/diagram/EachBasedGroup.png)

```trickle
select event
from in
group by each(event.topic)
into out;
```

>>>

### tumbling wall clock windows

![Tremor Query Window Statement](https://docs.tremor.rs/tremor-query/grammar/diagram/DefineWindowDefn.png)

```trickle [|2-5|8|9|10]
# A 15 second window
define tumbling window fifteen_secs
with
    interval = core::datetime::with_seconds(15),
end;

# A windowed select
select aggr::stats::hdr(event.count)
from in[fifteen_secs]
group by each(event.topic)
into stats
having count > 0
```

<div style='font-size: 20px'>
A fifteen second grouped tumbling window based on the wall clock
</div>

---

### tumbling event clock windows

```trickle [|2-7|10|11|12]
# A 15 second window
define tumbling window fifteen_secs
with
    interval = core::datetime::with_seconds(15)
script
  event.timestamp
end;

# A windowed select
select aggr::stats::hdr(event.count)
from in[fifteen_secs]
group by each(event.topic)
into stats
having count > 0
```

<div style='font-size: 20px'>
A fifteen second grouped tumbling window based on the timestamp ( data ) clock
</div>

---

### tumbling window mechanics

<script type="WaveDrom">
// Tumbling window [wavedrom]
{signal: [
  {name: 'time (clock, seconds)', wave: 'p............|.'},
  {name: 'event (data)', wave: 'z3z3z3z3z3zzz|z', data: ['1', '2', '3', '4', '5']},
  {},
  {name: 'windows 2 events wide', wave: 'z7..z7..z7|....', data: ['w0', 'w1', 'w2', 'w3']},
  {name: 'emissions', wave: 'zzzz9zzz9zzzz|z', data: ['a', 'b']},
  {},
  {name: 'windows 10 seconds wide', wave: 'z7........7..|.', data: ['w0', 'w1']},
  {name: 'emissions', wave: 'zzzzzzzzzz9zz|z', data: ['a']},
  {},
],
 head: {
   text: 'Tumbling Window Mechanics',
   tick: 0
 }
}
</script>

<div style='font-size: 20px'>
A tumbling window captures a succession of events and emits an aggregate
synthetic events after a number of events or a time period has passed with
no overlap and no gaps between windows.
</div>

---

### Tilt-Frames

### A tilt frame is a succession of windows where the output from one
window forms the input into the next and subsequent frames. This allows
a 15-second aggregate to be aggregated 4 times into a 1 minute aggregate
and so on ...

```trickle
select event
from in[`15-secs`,`1-min`,`1-hour`]
group by each(event'host)
into out;
```

---

### Tilt-Frame Mechanics

<script type="WaveDrom">
// tilting [wavedrom]
{signal: [
  {name: '1 hour', wave: 'z9...........9|', node: '.a............j' },
  {},
  {},
  {},
  {name: '15 minutes', wave: 'z9..9..9..9..9|', node: '.a..e..f..g..h.' },
  {},
  {},
  {},
  {name: '5 minutes', wave: 'z9999999999999|', node: '.123456789abc...' },
],
  edge: [
    '1~>e', '2~>e', '3~>e merge',
    '4~>f', '5~>f', '6~>f merge',
    '7~>g', '8~>g', '9~>g merge',
    'a~>h', 'b~>h', 'c~>h merge',
    'e~>j merge', 'f~>j merge', 'g~>j merge', 'h~>j merge'
  ],
 head: {
   text: 'Tilt Frame Mechanics',
 }
}
</script>

<p style='font-size: 20px'>Tilt-frames are merge based operations and are based on
aggregate functions that can be efficiently merged, often without summary amplification
errors - for example the hdr and dds histogram aggregates are merge based and work well
with tilt frames</p>

>>>

### Modules

<p style='font-size: 20px'>
Any `define` query statement can be modularized for reuse and stored in
separate files. These files can use the `use` statement to import them
into the current query for use.
</p>

---

### Modules - Path-based

```shell
$ export TREMOR_PATH=/opt/my-project/lib
$ tree /opt/my-project/lib
. /opt/my-project/lib
  +-- foo
    +-- bar
      +-- snot.trickle
    +-- baz
      +-- badger.trickle
```

```trickle
use foo::bar::snot; # snot is a ref to 'foo/bar/snot.trickle'
use foo::baz::badger; # badger is a ref to 'foo/bar/badger.trickle'

select event
from in[snot::second, badger::minute] # use our imported window definitions
into out;
```

---

### Modules - Logical

```trickle
mod foo with
  mod bar with
    define tumbling window second with
      interval = 1000
    end;
  end;
  mod baz with
    define tumbling window minute with
      interval = 60000
    end;
  end;
end;

select event
from in[snot::second, badger::minute] # use our imported window definitions
into out;
```

<p style='font-size: 20px'>The same module hierarchy defined logically and inline</p>

>>>

### End of `tremor-query` guide
<!-- .slide: data-background="#77FF33" -->

This is the end of the `tremor-query` getting started guide

Note: This will only appear in speaker notes window


