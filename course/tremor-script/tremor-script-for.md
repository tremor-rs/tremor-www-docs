## Tremor Script `for`
<!-- .slide: data-background="#FF7733" -->

This course introduces the `for` statement

>>>

### `for` statement

![For rule](https://docs.tremor.rs/tremor-script/grammar/diagram/For.png)

![For Case Clause rule](https://docs.tremor.rs/tremor-script/grammar/diagram/ForCaseClause.png)

>>>

### `for` template

```tremor [|1|2-3|4-5]
for <expression> of
  # non-guarded case variant
  case (index, value) => <expression>
  # guarded case variant
  case (index, value) when <predicate> => <expression>
end
```

<div style='font-size: 20px' data-fragment-index=1>
For comprehends array-like structures allowing iteration over each item
</div>

>>>

### `for` example - unguarded

```tremor
for [ "foo", "bar" ] of
  case (index, element) => { "{index}": element }
end
```

Produces

```tremor
# indexing is 0 based
[ { "0": "foo" }, { "1":  "bar" } ]}
```

<div style='font-size: 20px'>
Array comprehension returning an array of index/value records
</div>

>>>

### `for` example - guarded
```tremor
for [ "foo", "bar" ] of
  case (index, element) when index % 2 == 0 => { "even #{index}": element },
  case (index, element) => { "odd #{index}": element },
end
```

Produces

```tremor
[ { "even 0": "foo" }, { "odd 1": "bar" }]
```

<div style='font-size: 20px'>
Use a case guard to discriminate even and odd indexes
</div>

>>>

### End of `for` guide
<!-- .slide: data-background="#77FF33" -->

This is the end of the `for` getting started guide

Note: This will only appear in speaker notes window


