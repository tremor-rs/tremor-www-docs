<!-- .slide: data-background="#333333" -->

## Contributors Guide

This course is a basic introduction to development practices and
a high level overview of how to contribute to the tremor project
for the uninitiated.

>>>

### Practical Matters

In this section we look at the mechanics of contributing to tremor.

---

### Bug Reports

<div style='font-size: 20px'>
One of the most valuable contributions is a bug report for a feature,
capability or artifact that doesn't seem quite right to you. If in doubt,
please raise an issue on our issues list.
</div>

<br/>

1. Identify similar [existing issues](https://github.com/tremor-rs/tremor-runtime/search?q=&type=Issues&utf8=%E2%9C%93) to up-vote.
2. If none found, [raise a new issue](https://github.com/tremor-rs/tremor-runtime/issues/new).
3. Be descriptive with your testcase

---

### Security Issues


<div style='font-size: 20px'>
If you believe you have found a security issue, we have a separate process
for raising security issues and vulnerabilities. You should also search for
existing issues.
</div>

<br/>

[Reporting Security Vulnerabilities](https://docs.tremor.rs/policies/security)

---

### Feature Requests

<div style='font-size: 20px'>
Small incremental improvements that do not change or break existing features,
functions or capabilities can be submitted via a pull request to the relevant
repository. For significant contributions, we follow an open RFC Process.
</div>

<br/>

1. Read the [RFC Process](https://github.com/tremor-rs/tremor-rfcs/blob/main/README.md)
2. Familarise with [existing RFCs](https://github.com/tremor-rs/tremor-rfcs)
3. Talk to the maintainers via [Tremor discord](https://bit.ly/tremor-discord)

---

### Pull Requests

<div style='font-size: 20px'>
Great, you've talked to the maintainers and proceeded to implement a new
feature, perhaps even with an RFC.
</div>

<br/>

1. We use the [fork and pull](https://help.github.com/articles/about-collaborative-development-models/)
2. Make sure to maintain or improve code coverage
3. Make sure to get a clean run via  lint tools

---

### Write Documentation

<div style='font-size: 20px'>
If you found some of our documentation difficult to parse, understand or apply
then you found a bug. We value contributions to documentation and tooling that
improves tremor for its community very highly.
</div>

<br/>

1. Main documentation [Tremor Documentation](https://github.com/tremor-rs/tremor-www-docs)
2. Search for documentation related [issues](https://github.com/tremor-rs/tremor-www-docs/issues?q=is%3Aopen%20is%3Aissue%20label%3Adoc)

>>>

### Contribute By Skill

<div style='font-size: 20px'>
Tremor is a lot more than rust code. If you are a polyglot developer
there are many ways to contribute. Lets explore a few!
</div>

---

### Rustacean

<br/>

1. The main tremor [runtime](https://github.com/tremor-rs/tremor-runtime) is rust based.
2. The tremor language server - [trill](https://github.com/tremor-rs/tremor-runtime) is rust based.
3. Contribute to [simd-json-rs](https://github.com/simd-lite/simd-json), a sister project.

---

### Javascript

<div style='font-size: 20px'>
Its more than likely your javascript skills are better than ours. Our Visual Studio Code
extension is implemented in your language. Please make our plugin better!
</div>

<br/>

[Tremor VS Code Repo](https://github.com/tremor-rs/tremor-vscode)

---

### Erlang / Quickcheck


<div style='font-size: 20px'>
If you love Erlang like we do, and you really like property based testing then
perhaps extending our language tests would be a great way to contribute?
</div>

<br/>

[Tremor EQC tests](https://github.com/tremor-rs/tremor-runtime/tree/main/tremor-erl)
<br/>

---

### Pythonista

<div style='font-size: 20px'>
If Python is your thing, then improving our pygments syntax highlighting
extension is one way to contribute to tremor
</div>

[Tremor Pygments Extension](https://github.com/tremor-rs/tremor-mkdocs-lexer)

---

### Tremolo

<div style='font-size: 20px'>
If you are using tremor and you can already write code in `tremor-script` and
`tremor-query` or build data distribution and eventing solutions with tremor
then there are lots of ways to contribute through providing solution examples
through to designing labs around specific use cases ( eg: logs, security, gateways ).

<br/>

Please get in touch!

</div>

>>>

### Contribute By Need

<div style='font-size: 20px'>
You may be here because you want something very specific from tremor and it isn't
something we support. If that's the case then this section might be for you
</div>

---

### New Sources

<div style='font-size: 20px'>
I want to distribute data into tremor from <b>BLANK</b>
</div>
<br/>

1. Read existing [sinks](https://docs.tremor.rs/artefacts/offramps/) documentation?
2. No. You will need to write a new one.
3. Refer to existing [sources](https://github.com/tremor-rs/tremor-runtime/tree/main/src/source) and talk to us!

<br/>
<div style='font-size: 20px'>
Suits: Rust programmers. Complexity: Moderate. Time: Typically than a week.
</div>

---

### New Sinks

<div style='font-size: 20px'>
I want to distribute data from tremor into <b>BLANK</b>
</div>
<br/>

1. Read existing [sinks](https://docs.tremor.rs/artefacts/offramps/) documentation?
2. No. You will need to write a new one.
3. Refer to existing [sinks](https://github.com/tremor-rs/tremor-runtime/tree/main/src/sink) and talk to us!

<br/>
<div style='font-size: 20px'>
Suits: Rust programmers. Complexity: Moderate. Time: Typically than a week.
</div>

---

### New Builtin Functions

<div style='font-size: 20px'>
I want to extend tremor with a new function for <b>BLANK</b>
</div>
<br/>

1. Read existing [function](https://docs.tremor.rs/tremor-script/functions/) library reference?
2. Nothing suitable? You will need to write a new one.
3. Refer to existing [std-lib](https://github.com/tremor-rs/tremor-runtime/tree/main/tremor-script/src/std_lib) and talk to us!

<br/>
<div style='font-size: 20px'>
Suits: Rust programmers. Complexity: Typically easy. Time: Typically less than a day.
</div>

---

### New Query Operators

<div style='font-size: 20px'>
I want to extend tremor query with a new operator for <b>BLANK</b>
</div>
<br/>

1. Read existing [operator](https://docs.tremor.rs/tremor-query/operators/) library reference?
2. Nothing suitable? You will need to write a new one.
3. Refer to existing [std-lib](https://github.com/tremor-rs/tremor-runtime/tree/main/tremor-pipeline/src/op) and talk to us!

<br/>
<div style='font-size: 20px'>
Suits: Rust programmers. Complexity: Can be complex. Time: Significant investment
</div>

---

### New Features and Capabilities


<div style='font-size: 20px'>
Outside of the above examples investment in time, effort, complexity becomes
non-trivial and will likely require following the RFC process, and engaging
with other stakeholders, collaborators and the maintenance team to nurse the
contribution into the project.
</div>

<br/>

<div style='font-size: 20px'>
Please talk to us at the earliest opportunity!
</div>

>>>

### End of `contributing` guide
<!-- .slide: data-background="#33FF77" -->

This is the end of the contributors getting started guide

Note: This will only appear in speaker notes window
