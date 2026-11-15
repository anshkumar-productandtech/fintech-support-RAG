---
id: KB-M11
title: Webhooks: get notified about payments
audience: merchant
category: Developers
last_updated: 2026-11-01
---

# Webhooks: get notified about payments

Webhooks tell your server when something happens, like a payment succeeding, so you don't have to keep asking the API.

## Set up a webhook

1. Go to **Developers > Webhooks > Add endpoint**.
2. Enter your server's HTTPS URL.
3. Choose the events, for example `payment.captured`, `payment.failed`, `refund.processed`, `settlement.processed`, `dispute.created`.
4. Set a **webhook secret**.

## Check every webhook is really from Kuberix

Each webhook has a header `X-Kuberix-Signature`. It's an HMAC-SHA256 of the raw request body, using your webhook secret. Calculate it on your server and compare. **Reject any webhook whose signature doesn't match.**

## Respond quickly

Return a **2xx status within 5 seconds**. Do slow work, like sending emails, after you've responded.

## Retries

If your server doesn't respond with 2xx, Kuberix retries with increasing gaps for up to **24 hours**. After that the webhook is marked failed. You can resend it from **Developers > Webhooks > Logs**.

The same event can arrive more than once. Use the `event_id` to ignore duplicates.

## Webhook not arriving?

1. Check **Developers > Webhooks > Logs** for the response your server sent.
2. Make sure your URL is public and uses HTTPS with a valid certificate.
3. Check that your firewall allows requests from Kuberix.
