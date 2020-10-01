# Glossary of Terms

A set of terms in common or standardised usage by the tremor project and/or team

|Term|Definition|
|---|---|
|Artefact|A unit of configuration management in tremor. As and from tremor v0.4|
|DAG|Directed Acyclic Graph - A graph with no cycles and unidirectional edges|
|Pipeline|An artefact that describes a graph ( DAG ) of tremor operators|
|Operator|A vertex ( node ) in a tremor pipeline graph. Operators perform work in a tremor pipeline graph|
|Source, Onramp|An artefact that describes a connector of primarily inbound data available for pipelines to ingest|
|Sink, Offramp|An artefact that describes a connector of primarily outbound data produced by pipelines available for egress|
|Peer, Linked Transport|An artefact that describes a connector with both inbound and outbound data that can be routed through a pipeline conversationally|
|Link|A link is an edge or connection between operators in a pipeline or between pipelines and onramps/offramps|
|Binding|A specification of ( set of links ), describing one-or-many interconnections to/from pipelines|
|Mapping|A configuration of, ( set of bindings ), and set of key/value replacements that describes how to deploy pipelines and how to interconnect binding specifications and map to running instances of tremor artefacts|
|Repository|An in memory cache that tremor uses to store artefacts. Like a git repository for artefacts|
|Registry|An in memory cache that tremor uses to store running onramps, offramps and pipelines. Like the DNS registry for running code that can send, receive or process events|
|Publish|The act of publishing an artefact or deploying a running instance|
|Find|The act of finding an artefact or running instance by id|
|Bind|The act of deploying artefacts and making them runnable|
|Publish-Find-Bind|An Enterprise Integration Pattern common in Registry/Repository services for Application Server Platforms|
|Deploy|The act of publishing a tremor mapping, the side-effect of which MAY be the deployment of onramps, offramps and/or pipelines|
|Undeploy|The act of unpublishing a tremor mapping, the side-effect of which MAY be the undeployment of onramps, offramps and/or pipelines|
|Meta Variables|Global event metadata variables (prefixed with `$` in tremor-script), accessible across pipeline nodes as well as offramps |
|WAL, Write-ahead Log|An in-memory or persistent data log used by the guaranteed delivery mechanism|
|CB, Circuit-breaker|A mechanism that can react to failure in sources and sinks in a robust and recoverable way|
|GD, Guaranteed delivery|A mechanism that guarantees that events that reach a pipeline are processed to completion. Depending on the source/sink this may extend end-to-end|
|End to end GD|A configuration of GD whereby the primary sources and sinks for a use case are guaranteed not to lose messages during normal processing conditions|
