---
id: KB-M07
title: Refund a customer
audience: merchant
category: Refunds and disputes
last_updated: 2026-11-01
---

# Refund a customer

You can refund a payment fully or partly, up to **180 days** after the payment.

## From the app or dashboard

1. Go to **Payments** and find the payment.
2. Tap **Refund**, choose **Full** or **Partial**, and enter the amount.
3. Confirm. The customer gets an SMS with the refund reference number.

## Using the API

Call `POST /v1/payments/{payment_id}/refunds` with the amount in paise. See "Accept payments online: API keys".

## Where the money comes from

The refund is taken from your **next settlement**. If your settlement balance is too low, the refund waits until enough payments come in, for up to 7 days, and then fails. You'll get an email if that happens.

## How long until the customer gets it

| Customer paid with | Refund reaches them in |
| --- | --- |
| Kuberix Wallet | Instantly |
| UPI | 1 to 3 working days |
| Cards and net banking | 5 to 7 working days |

## Can I cancel a refund?

No. Once confirmed, a refund can't be cancelled.

## Fees

Refunds are free, but the original payment fee isn't returned.
