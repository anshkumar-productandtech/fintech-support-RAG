---
id: KB-M10
title: Accept payments online: API keys
audience: merchant
category: Developers
last_updated: 2026-11-01
---

# Accept payments online: API keys

To accept payments on your website or app, your developer connects to the **Kuberix Payments API** using API keys.

## Test and live keys

| | Test mode | Live mode |
| --- | --- | --- |
| Use for | Building and testing | Real customer payments |
| Real money moves | No | Yes |
| Key ID starts with | `kbx_test_` | `kbx_live_` |
| Available | Right after sign-up | After your account is approved |

## Generate keys

1. Go to **Developers > API keys** on business.kuberix.example.
2. Choose **Test** or **Live** and click **Generate key**.
3. You'll see a **Key ID** and a **Key secret**. **The secret is shown only once.** Store it safely, for example in your server's secret manager.

## Keep your secret safe

- Use the key secret **only on your server**. Never put it in your website's JavaScript, your mobile app or a public code repository.
- Anyone with your secret can create payments and refunds on your account.

## If a secret leaks

Go to **Developers > API keys**, click **Regenerate**. The old key stops working immediately, so update your server straight away.

## Base URL

`https://api.kuberix.example/v1/`

All requests use HTTPS and basic authentication with your key ID and secret. Amounts are always in **paise** (₹1 = 100 paise).
