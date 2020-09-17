# Circuit Breakers and Guaranteed Delivery

With tremor 0.9 we introduced logic for Guaranteed Delivery (GD) and Circuit Breakers (CB) so it is
worth discussing this addition and what to expect from them. The features are complementary but have
different tradeoffs.

We start with looking at a short comparison.

|         | support                | perf impact    | guarantee                 |
| ------- | ---------------------- | -------------- | ------------------------- |
| pre 0.9 | all sources & sinks    | baseline       | if we can                 |
| 0.9 CB  | most sources & sinks   | virtually none | stop on known disconnect  |
| 0.9 GD  | select sources & sinks | significant    | guaranteed where possible |

Let's add some clarification to this:

## pre 0.9

- guarantee: we send the data with a best effort to deliver it but have no control over
  malfunctioning downstream systems.

## 0.9 CB

- support: Where the underlying transport supports it we support stopping consumption, as
  an example UDP has no support of stopping ingestion.
- perf impact: virtually none - there is a theoretical impact on this but it was small enough to be
  not measurable in our test.
- guarantee: If a sink sends a CB event the source will stop producing data, however
  any events send until them might be lost.

## 0.9 GD

- support: Unless explicitly noted by sources / sinks notes differently there are no guarantees.
- perf: As GD requires acknowledgments for delivered messages the impact of this is significant
  compared to other methods.
- guarantee: using GD will provide the minimum guarantee that the used sink and source offers.

## Example

To emphasize on those differences we'll go through an example of how those methods work together.
With the release we updated our integration tests, including the web-socket test. The test works
by creating two tremor instances. One working as a producer, having a file source and a web-socket
sink. The other being a consumer having a web-socket source and a file sink.

The test is supposed to validate that all the data that the producer sends arrives at the consumer.
There is an issue with that, since they are two different processes there is no guarantee the
consumer is ready by the time the producer starts sending data.

Web-sockets do support circuit breakers so the web-socket sink will report that its counterpart is
down and stop reading the file. However for the CB logic to trigger and propagate some time passes
so we observed the first 3 messages being 'lost' before the circuit breakers could kick in.

This demonstrates the limitations of circuit breakers nicely, they do react to a bad sink but
the reaction isn't instantaneous so we risk loosing a few messages. To get around this we can use
the `qos::wal` operator that provides a higher delivery guarantee then the web-socket offramp.

With the `qos::wal` operator we do get all the messages since the web-socket sink never acknowledges
sending the message and it is considered failed. There is a caveat in this however, since
web-sockets are not fully GD aware we only get a GD error when the web-socket can not send the
message. If we had an intermittent failure that drops a few messages the `qos::wal` won't help as GD
does only offer the weakest guarantee of the components involved - in this case the web-socket
sink.
