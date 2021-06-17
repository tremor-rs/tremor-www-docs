<!-- .slide: data-background="#333333" -->

## Debugging Guide

This course is a basic introduction to debugging. The techniques described here are generic and not specific to tremor. However, we will use tremor for examples.

> This course uses the `speaker view` to provide additional information
> when it is consumed without an instructor.
>
> Press 'S' to open the speaker's view.


>>>

### The (lofty) Goal

Be able to:
* debug complex systems
* reduce a moderately hard bug
* report that finding
* get that issue resolved
* make friends on the way

>>>

### Why?

* It's hard
* Complexity can generally be reduced

Note:
Debugging complex systems is non-trivial and it's easy to get lost. This complexity can be reduced by applying the practices we will discuss here.

Look in the slides below to see some key factors that make debugging so hard.

---

### Complexity

* Fundamental problem
* Main goal: reduce complexity

Note:
The single biggest problem when debugging complex systems is that they are, well, complex. So reducing complexity is key.

---

### Dependencies

* External dependencies
* Couples external environments
* Hardest to replicate

Note:
The second factor that makes debugging complex systems hard is that issues are often first spotted in a live environment and in interaction with other systems.

---

### Data characteristics

* Is the problem data-dependent?
* Patterns
* Volumetric
* Throughput
* Content

Note:
Like the previous dimensions, issues can surface based on specific characteristics of data that do not exist in a test. This can relate to many factors like, flow characteristics (throughput, bursts, order), relation between data, or shape of data.

---

### External factors

* CPU
* Memory
* Network
* Virtualization / noisy neighbor
* etc.

Note:
While tests are usually run in a very controlled environment, issues often surface in a living, chaotic environment with a wide number of external conditions. Networking, DNS, CPU load, noisy neighbors, other applications and external tasks, scheduling, and IO constraints, to name a few.

>>>

### Social aspects of debugging

* **Not** a purely technical exercise
* **Empathy** is important
* Debugging is a **team** sport

Note:
Empathy is key to efficient debugging. After all, nobody likes being told they're wrong, so it's worth approaching debugging with some care. Understanding context is key to communicating across disciplines whilst debugging across people or teams.

---

### Principle of Internalization

* Start with 'It's something I did'
* Try to rule it in or out
* Avoids the 'blame game'
* Tracks valuable insights and assumptions

Note:
This one is uncomfortable to get used to, but is extremely powerful. The basic idea is to always start with the assumption: "I did something wrong", and try to prove this. There are some aspects to that:

1. It is a good starting point (as good as any other)
2. It shows humbleness and makes any discussion more pleasant
3. It quickly rules out a whole range of causes

---

### Documentation

* Share information
* Prevent duplicate work
* Helps learning and teaching

Note:
The more effort put into documenting the debugging process and steps, the easier and more helpful it will be for others. It will save everyone's time and save duplication of effort so that the same path doesn't need to be followed again.

Additionally, a good record of a debugging session can also be a wonderful teaching tool for helping others improve their debugging skills. For example, capture an incident and debugging report for each occurrence.

We'll cover a bit more about this in a later section when we talk about how to file reports in an efficient way.

---

### Take ownership

* Follow up
* Try to understand steps of others
* The value is as much in the process as the result

Note:
Once you start an investigation, try to see it through. When seeking help, be inquisitive and try to stay informed. More often then not, the path of the journey to a resolution is more important than the outcome.

>>>

### The business side

* Tension between MTTR and throw investation
* No right answer
* Needs compromise

Note:
When in a life situation, there are opposing interests. Often, the primary business interest is to keep the MTTR (mean time to recover) low while we might want to investigate carefully.

---

### recover

* Recovery can destroy evidence
* Makes debugging hard or impossible
* Can lead to never-fixed bugs

Note:
If we recover to satisfy the business need, we can loose evidence and end up in a repeating cycle of reoccurring incidents.

---

### investigate

* Can destroy the business
* Makes production hard or impossible
* Can lead to never-fixed bugs

Note:
If we only focus on investigating the issue, we can end up killing the business, which is not great, and makes it also impossible to fix the bug.

### compromise

* Negotiate
* Preserve evidence
* Prepare

Note:
So what can we do? There are a few things: understand the business impact, and negotiate a middle ground. We need both continuity and a long-term resolution.

The second part is: preserve as much evidence as possible. Can we store logs? Can we make a machine snapshot? Can we perhaps move production load to a fresh system?

Prepare: make sure that the next time the incident pops up, you are prepared. Have a standby instance to fail over, do additional debugging, and have spare capacity. That takes away the pressure.

>>>

### Reproducibility

* Precise and focused
* Small
* Self-contained

Note:
This brings us to the first part of debugging: **Reproducibility**.

An issue that can't be reproduced is nearly impossible to fix, so when debugging, our priority should always be to create a reproducible set of circumstances that trigger our issue.

---

### Data

* Minimal
* Synthetic
* Consistent

Note:
Ideally, reproduction data should be minimal. For tremor, whenever possible, we use files with static data if the shape of the data is significant. Or, if the shape is not important, the metronome source.

---

### External services

* Remove if possible
* Simplify/abstract if not

Note:
We often use docker-compose to set up suites of services to reproduce an issue. That guarantees that the configuration is exactly the same between runs. As a good side effect, the effort this takes encourages minimal reproduction examples.

---

### Minimalism

* The smaller, the better
* Few moving parts
* Domain-agnostic
* Self-contained

Note:
As general rule: the smaller a reproduction is, the better. Smaller means less moving parts; the  less external influence there is, the easier it is to fine isolate the underlying issue.

In the next sections, we'll talk about two methods to achieve this.

>>>

### Distillation

* Capture incident and simplify
* Good if you're unsure about the cause

Note:
The first method we're going to talk about is a method that can be seen as 'tearing down' the system until only the relevant parts are left. This is a good process point if you have a large system and are not sure what is relevant. It is also the simpler process, but it requires more effort.

What we're going to do is remove one element at a time until there is nothing left to remove without resolving the issue.

---

### Starting point

* Start big
* For tremor:
  * sources -> metronome
  * sinks -> debug

Note:
It's good to start with the biggest chunks first. The larger the part we can cut down is, the quicker we can reduce.

For tremor, the largest parts to eliminate are usually sinks and sources, if we can remove one or both of them and replace them with 'simple' ones such as the `debug` sink or the `metronome` source.

Next, we would look at scripts and finally operators.

---

### Common mistakes

* Stopping too early
* Finding **a** cause, not **the** cause
* Not distilling fully

Note:
Once we've found something that when removed, will resolve the issue, it is important to not just stop. Just because we found **an** element that when removed, resolves the issue doesn't mean we have a minimal case, nor does it mean we have isolated the issue.

---

### Follow through

* Continue until a single change:
  * avoids the issue
  * is still a valid reproduction
* Document

Note:
To avoid the mistake mentioned above, we continue with removing parts until every element left in the setup would either resolve the issue or make the reproduction unusable.

So, in tremor, we couldn't remove all the sinks, as that would make the reproduction unusable.

---

### Tremor-specific

* Sources and sinks
* Remove operators
* Simplify scripts

Note:
For tremor, one of the things to remember is that in a script, we also have layers of complexity, and depending on other elements still in the reproduction, we can remove some of them, simplifying the script as much as possible.

>>>

### Guided Discovery

* Start 'empty'
* Introduce complexity
* Find the breaking point

Note:
The alternative method is building up from a known, working, clean-slate system and adding more complexity until we introduce breakage per the incident. This method works well if you have a good hunch of what causes the issue and what doesn't, as it allows to very quickly introduce potential breaking points.

---

### Starting point

* Empty setup
* No externalities
* Known clean starting state

Note:
The ideal starting point is a clean system, as we discussed before. Docker-compose works well if the incident is not related to the production environment, but to the components in the environment.

---

### Common mistakes

* Not distilling after reproduction
* Not considering effects of interaction

Note:
The biggest common mistake in this process is stopping once we introduced the issue we're looking for. The work isn't done at this point as we have not yet determined if the issue is related to the last element added, or a combination of multiple elements added before.

So, once we introduce the issue, what we have to do is start removing elements again, as described in the tearing down process, until every removal leads to resolving the issue.

---

### Tremor specific

* Setup of docker-compose
* Source: `metronome` or `file`
* Sink: `debug`

Note:
For tremor, we like using the tremor image along with a metronome or file onramp, and again the debug offramp, unless ramps are what cause the issue.

>>>

### Change tracking

* Requires full control & a long-running/evolving system
* If possible, highly effective as a starting point
* Risky and easy to get wrong
* Quick way to form a first hypothesis

Note:
If it is possible to pin an incident to a specific change in the system that can provide a starting point. This is only possible if we have a changing, evolving system and full control and understanding of all involved components.

---

### What changed

* Figure out what changed
* See if rolling back that change resolves the issue
* Repeat

Note:
What we do is a binary search between the last known good state and try to find out at what point things went bad. This allows for a quick first idea of what we're dealing with.

---

### Common mistakes pt. 1

* Ignores interactions between systems
* Is often not sufficient to find the origins of an incident
* Assume change equals cause

Note:
If only looking for the triggering change, then it can ignore interactions between parts of the system. Stopping at that point assumes that the change is the cause, which isn't always true and rarely ever enough information to debug the issue.

---

### Common mistakes pt. 2

* Ignores the principle of internalisation
* Can leads to blame instead of debugging
* Can be an 'easy win' without seeing it through

Note:
By looking for the change, we ignore the `principle of internalisation` and it can quickly lead to the impression that we are looking for blame, not a resolution. It is tempting to call it a 'win' without following through on the debugging exercise.

---

### Common mistakes pt. 3

* Assuming the system was 'correct' before
* Can lead to bug compatibility instead of correctness
* Changes can be too big

Note:
This can lead to the wrong assumption that a system was correct only because we didn't see something before. Following this path can lead to creating 'bug compatible' systems that get more and more out of hand instead of finding the problem and correcting it. Changes can often be massive; this makes the change on its own not a very good indicator of a cause.

### Mitigation

* Use with a lot of care
* Always follow up with creating a reproduction to the minimal case
* Only ever use as a starting point

Note:
Despite its shortcomings, this method can be very effective when used with care. To prevent falling into one of the pitfalls, it's important to understand that the triggering change isn't the end but only the beginning of debugging. We should never straight-out assume that the change is the cause; it may only be what makes the symptoms visible.

>>>

### Reporting

* Tickets are better than messages
* Be descriptive
* Cover the 3 main points:
    1. Intent
    2. Observation
    3. Expectation

Note:
Once we have found the issue and debugged it to the point of a minimal reproduction, we're nearly done, but not entirely. Next, we'll take a quick look at how to report an issue effectively.

We'll structure this in three sections, and a fourth with the supporting material that we've gathered as we have been debugging.

Tickets are the preferable way to share issues and debugging results as they guarantee searchability and are themselves part of the documentation.

If possible, capture the reproduction process and decision points.

---

### Intent

* What have I been doing (the what)?
* Why have I been doing it (the why)?
* How have I been doing it (the how)?

Note:
The first part of a good bug report covers "what have I been doing?". Details here are important. Unfortunately, as we've been debugging and taking notes, we already know what the key details are!

---

### Observations

* What happened?
* Captured artefacts
* Process steps

Note:
This is close to the previous section; it is important to spell out what happened. Together, those two sections contain a trove of information that helps understand the situation, while on their own, they fall short of conveying the problem.

---

### Expectation

* What did you expect to happen?
* Why did you expect it to happen?
* How does observation differ from expectation?

Note:
When facing any issue, the core is that an expectation we had wasn't met. It is extremely important to spell out what we expected to happen and why we expected this. Beware that different people with different needs can have different expectations. Sometimes, the 'observed' behavior is the intended behavior. Even so, it isn't what you expected that opens up a discussion, if the intentions are as expected or not.

---

### Example

Lets look at an intentionally short example of this:

---

### Example: Intention

> We've set up tremor to distribute messages via round-robin to multiple WebSocket endpoints.

* Introduction
* Intent
* Components

Note:
This sets the scene with an introduction to the setup, some intent behind it, and the related components.

---

### Example: Observation

> When one of the endpoints has a failure, all messages stop.

Note:
This is the observation that makes us believe there is an issue. It includes some insight into our debugging, namely, that a single endpoint failure is enough to make all message flow stop.

---

### Example: Expectation

> We would have expected round-robin to skip downed endpoints but continue with the rest to ensure
> a degree of resiliency and fault-tolerance.

Note:
The expectation explains what we expected to happen in contrast to our observation. In this example, it also explains our intent as to why we expected this. The intent here can be important since it gives information about our needs and can open a conversation.

---

### Example: Reproduction pt. 1

> We've attached a docker-compose setup that sends data from a metronome to three websocat
> instances (we picked 3, but found the number has no effect on the issue).

Note:
This introduces the material we submitted.

---

### Example: Reproduction pt. 2

> Once started, you should see a message on each websocat every 3 seconds.

Note:
We next explain how to run the experiment.
---

### Example: Reproduction pt. 3

And add how to introduce the issue we found.

> When stopping one of the websocat instances, the flow to the remaining two stops too.

---

### Example: Reproduction pt. 4

> We would have expected to see it continue with the messages being evenly distributed between them.

Note:
We close with a reinforcement of the expectation linked to this example.

>>>
### Lab

> Tremor isn't working!

Requirements:

1. docker-compose
2. `xz` and `tar`
2. the [lab file](lab.tar.xz)

---

### Lab: running

1. Uncompress the archive: `xz -d lab.tar.xz; tar xf lab.tar`
2. Enter the directory: `cd lab`
3. Look at the `README.md` for context
4. Run the lab: `docker-compose up`
5. Debug!

---
### Lab: Solution

Please try to solve the lab yourself first, but here is the [solution](lab-solved.tar.xz).

>>>

### End of `debugging` guide
<!-- .slide: data-background="#33FF77" -->

This is the end of the debugging guide.