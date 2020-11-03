## Tremor Script `patch`
<!-- .slide: data-background="#FF7733" -->

This course introduces the `patch` statement

>>>

### `patch` statement

![Patch rule](https://docs.tremor.rs/tremor-script/grammar/diagram/Patch.png)

![Patch Operation rule](https://docs.tremor.rs/tremor-script/grammar/diagram/PatchOperation.png)

>>>

### `patch` template

```tremor [|1|2|3|4|5|6|7]
patch <expression> of
  insert <field-expr> => <expression> # insert field if not present or error
  update <field-expr> => <expression> # update field if present or error
  upsert <field-expr> => <expression> # update field if present else insert
  erase <field-expr>                  # remove a field
  merge <field-expr> => <expression>  # merge field if present with value provided
  merge <expression>                  # merge expression into patch target
end
```

<div style='font-size: 20px' data-fragment-index=1>
Patch executes one or many operations in turn over the target expression
</div>

>>>

### `patch` example - `insert`

```tremor
patch { "foo": "bar" } of
  insert snot => "badger"
end
```

Produces

```tremor
{ "foo": "bar", "snot": "badger" }
```

<div style='font-size: 20px'>
Addition of new field via patch `insert` operation
</div>

>>>

### `patch` example - `update`
```tremor
patch { "foo": "bar" } of
  update foo => "badger"
end
```

Produces

```tremor
{ "foo": "badger" }
```

<div style='font-size: 20px'>
Overwrite of existing field via patch `update` operation
</div>
>>>

### `patch` example - `upsert`

```tremor
patch { "foo": "bar" } of
  upsert bar => "badger",
  upsert foo => "snot",
end
```

Produces

```tremor
{ "foo": "snot", "bar": "badger" }
```

<div style='font-size: 20px'>
Add or overwrite field regardless of target disposition
</div>

>>>

### `patch` example - `erase`

```tremor
patch { "foo": "bar" } of
  erase foo
end
```

Produces

```tremor
{ }
```

<div style='font-size: 20px'>
Remove an existing field from the `patch` target

>>>

### `patch` example - `merge` 1

```tremor
patch { "foo": "bar", "baz": {} } of
  merge baz => { "snot": "badger" }
end
```

Produces

```tremor
{ "foo": "bar", "baz": { "snot": "badger" } }
```

<div style='font-size: 20px'>
Merge field value based on a `merge` template
</div>

>>>

### `patch` example - `merge` 2

```tremor
patch { "foo": "bar", "baz": {} } of
  erase foo,
  erase baz,
  merge => { "snot": "badger" }
end
```

Produces

```tremor
{ "snot": "badger" }
```

<div style='font-size: 20px'>
Patch can also be used with a convenient `merge` to replace the target document entirely
</div>

>>>

### `patch` limitations

The `patch` statement can set a `null` value on an existing field.
Patch can also process field and top-level merge templates in addition
to the more basic operations of `insert`, `update`, `upsert` and `erase`

However, the `patch` operation is considerably more verbose than merge.

>>>

### End of `patch` guide
<!-- .slide: data-background="#77FF33" -->

This is the end of the `patch` getting started guide

Note: This will only appear in speaker notes window


