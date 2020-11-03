## Tremor Script `merge`
<!-- .slide: data-background="#FF7733" -->

This course introduces the `merge` statement

>>>

### `merge` statement

![Merge rule](https://docs.tremor.rs/tremor-script/grammar/diagram/Merge.png)

>>>

### `merge` template

```tremor [|1|2]
merge <expression> of
  <expression>
end
```

<div style='font-size: 20px' data-fragment-index=1>
Expressions can be any legal tremor-script expression
</div>

>>>

### `merge` example - 1

```tremor
merge { "foo": "bar" } of
  { "snot": "badger" }
end
```

Produces

```tremor
{ "foo": "bar", "snot": "badger" }
```

<div style='font-size: 20px'>
Addition of new fields
</div>

>>>

### `merge` example - 2

```tremor
merge { "foo": "bar" } of
  { "foo": "baz" }
end
```

Produces

```tremor
{ "foo": "baz" }
```

<div style='font-size: 20px'>
Update or change an existing field
</div>

>>>

### `merge` example - 3

```tremor
merge { "foo": "bar" } of
  { "foo": null }
end
```

Produces

```tremor
{ }
```

<div style='font-size: 20px'>
Remove an existing field
</div>

>>>

### `merge` limitations

The `merge` statement cannot set a null value on an existing field.
For this the `patch` statement should be used.

>>>

### End of `merge` guide
<!-- .slide: data-background="#77FF33" -->

This is the end of the `merge` getting started guide

Note: This will only appear in speaker notes window


