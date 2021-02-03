## Tremor Script `mod`
<!-- .slide: data-background="#FF7733" -->

This course introduces user-defined modules

>>>

### Module definition

![Module Declaration rule](https://docs.tremor.rs/tremor-script/grammar/diagram/Module.png)

![Module Expression rule](https://docs.tremor.rs/tremor-script/grammar/diagram/ModuleExpr.png)

Modules provide a logical and physical name space on the file system for organizing constants
and functions. Tremor provides a set of standard modules and the facility for specifying user
defined modules is essentially the same.

>>>

### Module Path - Physical

The module path can be a mix of physical namespaces separated by sub-folders on the file system
where each module root is exposed to tremor via the `TREMOR_PATH` environment variable.

```text
 +-- foo
    +-- bar
      +-- snot.tremor
    +-- baz
      +-- badger.tremor
```

```bash
export TREMOR_PATH=/opt/tremor/lib:/my/path/to/modules
```

<div style='font-size: 20px;'>
The `foo::bar::snot` and `foo::baz::badger` defined external to a referencing script
</div>

>>>

### Module Path - Logical

```tremor
mod foo with
  mod bar with
    mod snot with
      # ...
    end
  end
  mod baz with
    mod badger with
      # ...
    end
  end
end
```

<div style='font-size: 20px;'>
The `foo::bar::snot` and `foo::baz::badger` defined inline with a referencing script
</div>

>>>


### Using inline modules

```tremor [12-13]
mod foo with
  mod bar with
    const snot = "beep";
  end;
  mod baz with
    const badger = "boop";
  end;
end;

let snot = foo::bar::snot;
let badger = foo::baz::badger;

"#{snot}-#{badger}";
```

>>>

### Using external modules

```tremor [1-3|4-5|7-8]
# ```shell
# export TREMOR_PATH=/opt/tremor/lib:/opt/myproject/lib
# ```
use foo::bar;
use foo as tremolo; # alias renaming

let snot = bar::snot;
let badger = tremolo::baz::badger;

"#{snot}-#{badger}";
```

<div style='font-size: 20px'>
The `use` clause leverages `TREMOR_PATH` to resolve external modular functions and constants
</div>

>>>

### End of `mod` guide
<!-- .slide: data-background="#77FF33" -->

This is the end of the `mod` getting started guide

Note: This will only appear in speaker notes window

