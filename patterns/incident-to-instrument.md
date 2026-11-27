# Incident to instrument

*Leave production easier to see into than it was when the pager went off.*

At 2 a.m., payment webhooks start timing out. Customers get charged, invoices stay marked unpaid, and the retry queue backs up for forty minutes. Two engineers spend half the morning piecing together what happened by grepping container logs, guessing at database lock wait times, and correlating timestamps by hand against the payment provider's dashboard. Eventually they find it: a batch renewal job held a row lock on the account table while webhook retries piled up behind it.

They fix the lock ordering and close the incident. A month later, a different background job slows down the same table, and nobody on call can tell whether the payment provider is flaky, the queue is stalled, or the database is locked. The logs still just say `webhook handler failed: timeout`.

Some bugs belong in a [persistent reproducer](./persistent-reproducer.md). Emergent production failures usually do not. You can spend three days trying to recreate a lock-contention storm with synthetic threads in CI and still miss the next trigger. When a failure depends on live concurrency, queue depth, or a third-party dependency misbehaving, the durable thing to leave behind is telemetry that answers the question you got stuck on at 2 a.m.

## Instrument the question you could not answer

During a messy incident, you always hit two or three moments where somebody says, "I wish we knew whether..." Write those down while you still remember them.

In the billing timeout, the missing facts were small and specific:

- Which phase of the webhook handler actually timed out (signature check, database lock wait, invoice update, or downstream call)?
- Was this the first delivery of `evt_001` or retry attempt four?
- Did the handler fail because of a duplicate, a lock timeout, or a rejected payload?

Adding ten generic `INFO` log lines around the handler will not help much. Emit one structured event per handled webhook with the fields you needed during the outage, plus a small set of low-cardinality metrics for alerting and dashboards.

Here is an adaptation sketch in Python showing the shape of a structured handler summary (separate from the in-memory billing lab):

```python
logger.info(
    "webhook_processed",
    extra={
        "event_id": event.id,
        "attempt": event.delivery_attempt,
        "outcome": outcome,          # applied | duplicate | lock_timeout | error
        "lock_wait_ms": lock_wait_ms,
        "handler_ms": total_ms,
    },
)
```

Notice what sits where. High-cardinality fields like `event_id` belong in structured logs or distributed trace attributes, where you filter down to one stuck payment. Low-cardinality fields like `outcome` belong on counters and histograms (`billing_webhook_duration_ms{outcome="lock_timeout"}`), where you plot trends and page on spikes. Putting `invoice_id` or `customer_id` into a metric label is one of the fastest ways to blow up a metrics backend and turn an observability improvement into an outage of its own.

[OpenTelemetry's signals documentation](https://opentelemetry.io/docs/concepts/signals/) spells out this split between metrics, traces, and logs well: metrics tell you *that* lock timeouts jumped at 02:14, traces and structured events tell you *which* path and *which* event got stuck.

## Keep sensitive data out of telemetry

Incident debugging makes people reach for raw request dumps. Do not log full webhook payloads, card metadata, auth headers, or customer emails just because they were handy when you were tired.

Log internal IDs, status categories, retry counts, and timings. If you need to cross-reference a payment provider's dashboard, the provider's opaque event ID (`evt_001`) is usually enough without copying the customer's billing address into a log aggregator that half the company can search.

## Prove the signal before closing the incident

Untested instrumentation fails quietly. A field name has a typo, a metric never gets registered, or a log parser drops nested JSON, and nobody notices until the next 2 a.m. page.

Before you call the follow-up done:

- Trigger the failure path in staging or a local integration test and inspect the actual emitted log line, trace span, or metric series.
- Run the exact query you wish you had during the outage and save it in the service runbook or dashboard, linked right next to the alert.
- Check that the new signal separates the failure class you care about from normal noise (for instance, a legitimate `duplicate` delivery should not page anyone unless retries spike).

Google's SRE chapter on [Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/) makes the key distinction between symptoms and causes: page humans on customer-facing symptoms (unpaid invoices piling up, webhook error rate rising), and use cause-level instrumentation (`lock_wait_ms`, retry attempt counts) to narrow the diagnosis in minutes instead of hours.

## When to stop adding signals

Every metric series, log volume bump, and dashboard panel has a carrying cost. Log ingestion bills climb quietly, noisy alerts train the team to mute Slack channels, and dashboards filled with thirty stale graphs from 2023 make the three useful ones harder to find.

Keep the bar plain: add instrumentation for a blind spot that actually slowed down a real investigation, or for a failure mode you know is about to get riskier (like a payment provider swap). Skip adding speculative metrics for every branch of every helper function.

When you retire an endpoint, feature flag, or background job, delete its alerts, dashboards, and custom counters in the same cleanup. Orphaned telemetry is just another form of dead code, except it also sends false pages.

## What this unlocks later

The immediate win is obvious: the next time a slow migration or lock holds up billing webhooks, on-call sees `outcome=lock_timeout` and `lock_wait_ms` climb in two minutes instead of burning a morning correlating logs.

The bigger payoff shows up on work that has nothing to do with the original incident. Once you have clean, trusted signals on webhook outcomes and delivery paths, you can safely run shadow traffic during [differential verification](./differential-verification.md), prove whether a legacy path still has hidden consumers during a [subtraction investigation](./subtraction-investigation.md), and spot regressions during rollouts before customers file tickets.

When an incident *can* be reproduced cheaply and deterministically in code, pair this with a [persistent reproducer](./persistent-reproducer.md) rather than relying on production alerts alone. Periodically audit whether your custom metrics and alerts are still pulling their weight during an [investment retrospective](./investment-retrospective.md).
