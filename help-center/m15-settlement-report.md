---
id: KB-M15
title: Reading your settlement report
audience: merchant
category: Settlements
last_updated: 2026-11-01
---

# Reading your settlement report

Download it from **Settlements**, tap a settlement, then **Download report** (CSV or Excel).

## Columns

| Column | What it means |
| --- | --- |
| payment_id | Kuberix's ID for the payment |
| order_id | Your own order ID, if you sent one |
| method | UPI, card, net banking or wallet |
| amount | What the customer paid |
| fee | Kuberix fee for this payment |
| gst | GST on the fee |
| refunds | Refunds taken from this settlement |
| chargebacks | Chargeback amounts held or deducted |
| adjustments | Rentals and other charges |
| net_settled | What reached your bank |
| utr | Bank reference for the settlement |

## The maths

`net_settled = amount − fee − gst − refunds − chargebacks − adjustments`, added up over all rows.

## Doesn't add up?

Check the **refunds** and **chargebacks** columns first; they're the most common reason a settlement is smaller than expected. If it still doesn't match, raise a ticket from **Help > Settlement issue** with the UTR.
