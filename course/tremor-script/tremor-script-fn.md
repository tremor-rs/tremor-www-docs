## Tremor Script `fn`
<!-- .slide: data-background="#FF7733" -->

This course introduces the user-defined functions

>>>

### Function definition

![Function Declaration rule](https://docs.tremor.rs/tremor-script/grammar/diagram/FnDecl.png)

* Intrinsic Functions - Denotes a function as buit-in or runtime provided
* Standard Functions -  Is an ordinary function, with arguments that may be tail-recursive.
* Match Functions - Is a function whose arguments are resolved via pattern matching.

>>>

### Intrinsic Functions

![Intrinsics rule](https://docs.tremor.rs/tremor-script/grammar/diagram/IntrinsicFnDecl.png)

```tremor [|7]
mod std of
  mod string of
    # an intrinsic function is runtime provided and as such
    # documents the function signature,  the body of the function
    # is written in the Rust programming language and registered
    # to the scripting environment automatically
    intrinsic fn lowercase(input) as string::lowercase;
  end
end
```

<div style='font-size: 20px'>
Intrinsic functions are runtime provided and implemented in rust
</div>

>>>

### Standard Functions

![Standard Fn rule](https://docs.tremor.rs/tremor-script/grammar/diagram/SimpleFnDecl.png)

```tremor [|1-4|6-9]
## Summation
fn sum(a, b) with
  a + b
end;

## Token pasting
fn paste(a, b) with
  "#{a}#{b}"
end;
```

<div style='font-size: 20px'>
Standard functions are like functions in most other PLs
</div>

>>>

### Match Functions

![Matching Fn rule](https://docs.tremor.rs/tremor-script/grammar/diagram/MatchingFnDecl.png)


```tremor [|1-4|2|7-9]
fn fib_(a, b, n) of # fixed arity of 3
  case (a, b, n) when n > 0 => recur(b, a + b, n - 1) # recursive case
  default => a
end;

## Calculates the fibonacci sequence of size `n`
fn fib(n) with
  fib_(0, 1, n)
end
```

<div style='font-size: 20px;'>
Hint: Notice that matching functions are `of` qualified and standard or simple functions are `with` qualified.
Here, we have used both forms and tail recursion to implement fibonacci.
</div>

>>>

### The Tremor Path

It should be noted that modules and functions are relative to the `TREMOR_PATH` environment variable.
If set, modules and functions are resolved relative to this path. The module system and module and
function references are covered in the [`mod`](./mod.html) course and guide.

>>>

### End of `fn` guide
<!-- .slide: data-background="#77FF33" -->

This is the end of the `fn` getting started guide

Note: This will only appear in speaker notes window


