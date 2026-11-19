# Answer review sheet

13 answered questions from `results/answers_rewrite.csv`: 10 picked with seed 7, plus Q01, Q28, Q37 added by hand. 8 customer, 5 merchant, 8 Hinglish.
Each answer is shown with the 5 sources it was given, rebuilt from the database.
Rate each one in `results/human_ratings.csv` with y or n:

- **faithful**: every claim is backed by the source it cites.
- **complete**: it includes every fee, limit, time and condition from the sources that applies to the question.
- **language**: it replies in the question's language (Hinglish, Hindi or English).

---

## Q01 · customer · Hinglish

**Question:** paisa kat gaya but payment failed dikha raha hai, kab wapas aayega?

**Rewritten query:** Money deducted but payment failed refund status

**Answer** (cites [1], [3], [4]):

> Paisa apne aap wapas bank account mein aa jata hai, aapko kuch karne ki zarurat nahi hai [3][4]. 
>
> Agar samay par paisa wapas nahi aaye, toh:
> 1. **History** mein jayein, payment par tap karein, aur **Raise an issue > Money debited, payment failed** par tap karein [1].
> 2. Apne paas **UPI reference number** rakhein kyunki bank ko iski zarurat padegi [1].
> 3. Aap apne bank se direct contact karke reversal aur delay compensation ke liye bhi pooch sakte hain [1].
>
> Agar yeh issue 30 din ke andar solve na ho, toh "Complaints and escalation" dekhein [1].

### Sources

**[1] Money was debited but my payment failed** · `KB-C06#3` · cited

> Money was debited but my payment failed
>
> ## If the money hasn't come back in time
>
> 1. Go to **History**, tap the payment, then tap **Raise an issue > Money debited, payment failed**.
> 2. Keep the **UPI reference number** handy. Your bank needs it.
> 3. You can also contact your bank directly and ask for the reversal and the delay compensation.
>
> If your issue isn't solved within 30 days, see "Complaints and escalation".

**[2] When will I get a refund from a shop or website?** · `KB-C08#5`

> When will I get a refund from a shop or website?
>
> ## Not a refund?
>
> If your payment **failed** and money was debited, that's different. See "Money was debited but my payment failed".

**[3] Money was debited but my payment failed** · `KB-C06#1` · cited

> Money was debited but my payment failed
>
> Sometimes money leaves your account but the payment fails. **The money comes back automatically. You don't need to do anything.**

**[4] My payment is pending** · `KB-C05#4` · cited

> My payment is pending
>
> ## If the payment fails after money was taken
>
> The money comes back to your bank account automatically. See "Money was debited but my payment failed" for the timelines.

**[5] When will I get a refund from a shop or website?** · `KB-C08#3`

> When will I get a refund from a shop or website?
>
> ## The merchant says they refunded, but I don't see it
>
> 1. Ask the merchant for the **refund reference number** (sometimes called ARN or RRN).
> 2. Check your bank or card statement for that number. Refunds sometimes show as a credit with a different description.
> 3. If the timeline above has passed, go to **History**, tap the original payment, then **Raise an issue > Refund not received**.

---

## Q02 · customer · Hinglish

**Question:** sent 2000 to my brother 3 days back, money debited but he didnt get it. compensation milega?

**Rewritten query:** UPI transaction failed money debited compensation eligibility

**Answer** (cites [1], [4]):

> Haan, compensation milega! Sending money to a person (UPI transfer) ke liye RBI timeline T + 1 day hai (T = transaction day) [4]. Agar isse zyada der hoti hai, toh aapka bank aapko delay ke liye ₹100 har din dega [4]. 
>
> Aapko kya karna hai:
> 1. **History** mein jayein, payment par tap karein, phir **Raise an issue > Money debited, payment failed** par tap karein [1].
> 2 Apne bank ke liye **UPI reference number** tayyar rakhein [1].
> 3. Aap apne bank se direct contact karke reversal aur delay compensation bhi maang sakte hain [1].
>
> Agar aapka issue 30 din ke andar solve nahi hota, toh "Complaints and escalation" dekhein [1]. 
>
> *Note: Kabhi bhi apna UPI PIN, OTP, password ya full card number share na karein.*

### Sources

**[1] Money was debited but my payment failed** · `KB-C06#3` · cited

> Money was debited but my payment failed
>
> ## If the money hasn't come back in time
>
> 1. Go to **History**, tap the payment, then tap **Raise an issue > Money debited, payment failed**.
> 2. Keep the **UPI reference number** handy. Your bank needs it.
> 3. You can also contact your bank directly and ask for the reversal and the delay compensation.
>
> If your issue isn't solved within 30 days, see "Complaints and escalation".

**[2] I sent money to the wrong person** · `KB-C07#1`

> I sent money to the wrong person
>
> A successful UPI payment can't be cancelled or reversed by Kuberix. The money is now in the receiver's bank account, and only they can return it.

**[3] Send money with UPI** · `KB-C03#6`

> Send money with UPI
>
> ## Related
>
> - "UPI limits on Kuberix"
> - "I sent money to the wrong person"

**[4] Money was debited but my payment failed** · `KB-C06#2` · cited

> Money was debited but my payment failed
>
> ## When will I get my money back?
>
> These timelines are set by the Reserve Bank of India (RBI) for failed transactions. "T" is the day of the transaction.
>
> | Type of payment | Money back by | If later |
> | --- | --- | --- |
> | Sending money to a person (UPI transfer) | T + 1 day | Your bank pays you ₹100 for each day of delay |
> | Paying a shop or website (merchant payment) | T + 5 days | ₹100 for each day of delay |
> | Paying from Kuberix Wallet at a merchant | T + 1 day | ₹100 for each day of delay |
>
> Most reversals happen within a few hours.

**[5] My payment is pending** · `KB-C05#5`

> My payment is pending
>
> ## If the receiver says they didn't get it
>
> If the status shows **Successful**, the money has reached the receiver's bank. Ask them to check their bank statement, not just their app. Share the **UPI reference number** (12 digits, shown on the payment receipt) so they can trace it with their bank.

---

## Q03 · customer · English

**Question:** payment stuck on pending since morning, should i pay again??

**Rewritten query:** payment pending since morning should I pay again

**Answer** (cites [1], [2], [4]):

> Aapko dobara pay nahi karna hai, warna agar pehla payment successful ho gaya toh aap do baar pay kar denge [1]. 
>
> Almost always pending payments 48 hours se kam time me clear ho jaate hain [2]. Agar payment 48 hours ke baad bhi pending rahe, toh **History** me jaakar payment par tap karein aur **Raise an issue** par tap karein [2]. Most pending payments kuch ghanton me final status le lete hain aur **History** me status khud-b-khud **Successful** ya **Failed** update ho jaata hai [1]. Agar bill payment pending hai toh biller ke confirm karne ke liye up to 3 working days ka wait karein [4].

### Sources

**[1] My payment is pending** · `KB-C05#2` · cited

> My payment is pending
>
> ## What to do
>
> 1. **Don't pay again yet.** If the first payment goes through, you'll have paid twice.
> 2. Wait. Most pending payments get a final status within a few hours.
> 3. Check the payment in **History**. The status updates by itself to **Successful** or **Failed**.

**[2] My payment is pending** · `KB-C05#3` · cited

> My payment is pending
>
> ## How long can it stay pending?
>
> Almost always less than 48 hours. If a payment is still pending after 48 hours, go to **History**, tap the payment, then tap **Raise an issue**.

**[3] My payment is pending** · `KB-C05#5`

> My payment is pending
>
> ## If the receiver says they didn't get it
>
> If the status shows **Successful**, the money has reached the receiver's bank. Ask them to check their bank statement, not just their app. Share the **UPI reference number** (12 digits, shown on the payment receipt) so they can trace it with their bank.

**[4] Pay bills and check bill payment status** · `KB-C14#4` · cited

> Pay bills and check bill payment status
>
> ## Bill payment pending or failed
>
> - **Pending:** wait up to 3 working days for the biller to confirm.
> - **Failed:** refunded automatically. UPI and wallet payments come back within T + 1 day; cards within 5 to 7 working days.

**[5] My payment is pending** · `KB-C05#4`

> My payment is pending
>
> ## If the payment fails after money was taken
>
> The money comes back to your bank account automatically. See "Money was debited but my payment failed" for the timelines.

---

## Q05 · customer · Hinglish

**Question:** galti se wrong upi id pe 5000 bhej diya, reverse kar do please

**Rewritten query:** wrong UPI id transaction reversal

**Answer** (cites [1], [2], [5]):

> A successful UPI payment ko Kuberix cancel ya reverse nahi kar sakta kyunki paise receiver ke bank account mein chale gaye hain, aur sirf wahi wapas kar sakte hain [1]. 
>
> Aap ye steps try kar sakte hain:
> 1. Agar aap receiver ko jaante hain toh unse contact karein aur paise wapas bhejne ko kahein [5].
> 2. App mein request raise karein: **History** mein jayein, payment par tap karein, phir **Raise an issue > Sent to wrong person** select karein. Kuberix aapki request receiver ke bank ko bhejega, jo receiver se contact karega [5].
> 3. UPI reference number ke sath apne bank se contact karein. Banks receiving bank se help mang sakte hain [5].
>
> Next time se UPI PIN enter karne se pehle Kuberix par name zaroor check karein [2].

### Sources

**[1] I sent money to the wrong person** · `KB-C07#1` · cited

> I sent money to the wrong person
>
> A successful UPI payment can't be cancelled or reversed by Kuberix. The money is now in the receiver's bank account, and only they can return it.

**[2] I sent money to the wrong person** · `KB-C07#5` · cited

> I sent money to the wrong person
>
> ## Avoid this next time
>
> Always check the name Kuberix shows before entering your UPI PIN.

**[3] Money was debited but my payment failed** · `KB-C06#3`

> Money was debited but my payment failed
>
> ## If the money hasn't come back in time
>
> 1. Go to **History**, tap the payment, then tap **Raise an issue > Money debited, payment failed**.
> 2. Keep the **UPI reference number** handy. Your bank needs it.
> 3. You can also contact your bank directly and ask for the reversal and the delay compensation.
>
> If your issue isn't solved within 30 days, see "Complaints and escalation".

**[4] Send money with UPI** · `KB-C03#6`

> Send money with UPI
>
> ## Related
>
> - "UPI limits on Kuberix"
> - "I sent money to the wrong person"

**[5] I sent money to the wrong person** · `KB-C07#2` · cited

> I sent money to the wrong person
>
> ## What you can do
>
> 1. **Contact the receiver** if you know them, and ask them to send it back.
> 2. **Raise a request in the app:** go to **History**, tap the payment, then **Raise an issue > Sent to wrong person**. Kuberix passes your request to the receiver's bank, which contacts the receiver.
> 3. **Contact your own bank** with the UPI reference number. Banks can ask the receiving bank to help.

---

## Q12 · merchant · English

**Question:** started a refund by mistake, can i cancel it

**Rewritten query:** cancel refund request

**Answer** (cites [1], [3]):

> No, ek baar confirm hone ke baad refund cancel nahi kiya ja sakta [1]. Aap payment ke **180 days** tak full ya partial refund kar sakte hain [3].

### Sources

**[1] Refund a customer** · `KB-M07#6` · cited

> Refund a customer
>
> ## Can I cancel a refund?
>
> No. Once confirmed, a refund can't be cancelled.

**[2] Chargebacks and payment disputes** · `KB-M09#6`

> Chargebacks and payment disputes
>
> ## Already refunded the customer?
>
> Upload the refund reference number as evidence. You won't pay twice.

**[3] Refund a customer** · `KB-M07#1` · cited

> Refund a customer
>
> You can refund a payment fully or partly, up to **180 days** after the payment.

**[4] Refund a customer** · `KB-M07#2`

> Refund a customer
>
> ## From the app or dashboard
>
> 1. Go to **Payments** and find the payment.
> 2. Tap **Refund**, choose **Full** or **Partial**, and enter the amount.
> 3. Confirm. The customer gets an SMS with the refund reference number.

**[5] Refund a customer** · `KB-M07#3`

> Refund a customer
>
> ## Using the API
>
> Call `POST /v1/payments/{payment_id}/refunds` with the amount in paise. See "Accept payments online: API keys".

---

## Q16 · merchant · Hinglish

**Question:** settlement on hold dikha raha hai, why??

**Rewritten query:** Settlement on hold reason

**Answer** (cites [1], [4]):

> Settlement on hold dikhane ke common reasons yeh ho sakte hain:
> - **Verification pending:** Kuch documents check ho rahe hain, ise **Account > Verification** me complete karein [1].
> - **Risk review:** Unusual payment pattern ya sudden very large payment ke liye yeh review **3 se 5 working days** leta hai, aur hum invoices ya delivery proof maang sakte hain [1].
> - **Open chargeback:** Disputed amount tab tak hold par rehti hai jab tak chargeback decide nahi hota [1]. 
>
> Status check karne ke liye **Settlements** open karein [4].

### Sources

**[1] My settlement is delayed or on hold** · `KB-M05#2` · cited

> My settlement is delayed or on hold
>
> ## Common reasons for a hold
>
> - **Verification pending:** some of your documents are still being checked. Finish them in **Account > Verification**.
> - **Risk review:** an unusual payment pattern, such as a sudden very large payment. Reviews take **3 to 5 working days**. We may ask you for invoices or delivery proof.
> - **Open chargeback:** the disputed amount is held until the chargeback is decided. See "Chargebacks and payment disputes".

**[2] When will I receive my money? (Settlements)** · `KB-M04#6`

> When will I receive my money? (Settlements)
>
> ## Settlement late?
>
> See "My settlement is delayed or on hold".

**[3] My settlement is delayed or on hold** · `KB-M05#3`

> My settlement is delayed or on hold
>
> ## Settlement failed
>
> Usually the bank account is closed, frozen or its details changed. Update it in **Account > Bank account**. A new account needs verification, which takes 1 working day. Failed settlements are retried automatically after that.

**[4] My settlement is delayed or on hold** · `KB-M05#1` · cited

> My settlement is delayed or on hold
>
> ## Check the status first
>
> Open **Settlements**. Each settlement shows one of these:
>
> | Status | Meaning |
> | --- | --- |
> | Processed | Sent to your bank. Use the UTR number to trace it with your bank |
> | Scheduled | Will be sent on the date shown |
> | On hold | Kuberix has paused it. The reason is shown |
> | Failed | Your bank rejected it |

**[5] My settlement is delayed or on hold** · `KB-M05#4`

> My settlement is delayed or on hold
>
> ## Processed, but not in my bank
>
> Allow until the end of the working day, then give your bank the **UTR number**. If your bank can't find it, raise a ticket from **Help > Settlement issue**.

---

## Q19 · merchant · English

**Question:** settlement failed, i changed my bank account last week

**Rewritten query:** settlement failed after changing bank account

**Answer** (cites [1]):

> Aapka naya bank account verify hone mein 1 working day lagta hai [1]. Failed settlements iske baad automatically retry kiye jaate hain [1].

### Sources

**[1] My settlement is delayed or on hold** · `KB-M05#3` · cited

> My settlement is delayed or on hold
>
> ## Settlement failed
>
> Usually the bank account is closed, frozen or its details changed. Update it in **Account > Bank account**. A new account needs verification, which takes 1 working day. Failed settlements are retried automatically after that.

**[2] My settlement is delayed or on hold** · `KB-M05#4`

> My settlement is delayed or on hold
>
> ## Processed, but not in my bank
>
> Allow until the end of the working day, then give your bank the **UTR number**. If your bank can't find it, raise a ticket from **Help > Settlement issue**.

**[3] When will I receive my money? (Settlements)** · `KB-M04#6`

> When will I receive my money? (Settlements)
>
> ## Settlement late?
>
> See "My settlement is delayed or on hold".

**[4] Refund a customer** · `KB-M07#4`

> Refund a customer
>
> ## Where the money comes from
>
> The refund is taken from your **next settlement**. If your settlement balance is too low, the refund waits until enough payments come in, for up to 7 days, and then fails. You'll get an email if that happens.

**[5] When will I receive my money? (Settlements)** · `KB-M04#2`

> When will I receive my money? (Settlements)
>
> ## Standard settlement
>
> | You collected | Money in your bank |
> | --- | --- |
> | Monday to Friday | Next working day, by 1 pm |
> | Saturday, Sunday or a bank holiday | Next working day after that, by 1 pm |
>
> Payments are counted from midnight to midnight. Rentals and fees (for example Soundbox rental) are deducted before settlement.

---

## Q20 · customer · Hinglish

**Question:** ek din me upi se max kitna bhej sakte hai

**Rewritten query:** maximum daily UPI transaction limit Kuberix

**Answer** (cites [1], [2], [3], [4]):

> Ek din me Kuberix par sabhi UPI payments mila kar maximum ₹1,00,000 tak bhej sakte hain aur daily maximum 20 payments ki ja sakti hain [2]. Per UPI payment limit bhi ₹1,00,000 hai [2]. Naye phone par pehle 24 ghante me total ₹5,000 ki limit hai [2]. Daily limits midnight (raat ke 12 baje) reset hoti hain [1]. 
>
> Bahut si banks kam daily limit set karti hain (jaise ₹25,000 se ₹1,00,000) aur kuch banks naye payee ko pehle 24 ghante me bhejne wali rashi par bhi limit lagati hain [3]. Agar payment "Limit exceeded" error ki wajah se decline ho, toh apni bank se check karein [3]. Limit se zyada amount ke liye bank ke app se NEFT, RTGS ya IMPS use karein, kyunki Kuberix individual users ke liye UPI limits nahi badha sakta [4].

### Sources

**[1] UPI limits on Kuberix** · `KB-C04#4` · cited

> UPI limits on Kuberix
>
> ## When do limits reset?
>
> Daily limits reset at midnight.

**[2] UPI limits on Kuberix** · `KB-C04#2` · cited

> UPI limits on Kuberix
>
> ## Kuberix limits
>
> | Limit | Amount |
> | --- | --- |
> | Per UPI payment | ₹1,00,000 |
> | Per day, all UPI payments | ₹1,00,000 |
> | Payments per day | 20 |
> | First 24 hours on a new phone | ₹5,000 in total |
> | UPI Lite, per payment | ₹1,000 |

**[3] UPI limits on Kuberix** · `KB-C04#3` · cited

> UPI limits on Kuberix
>
> ## Your bank's limits
>
> Many banks set a lower daily limit, often ₹25,000 to ₹1,00,000 depending on the account. Some banks also limit how much you can send to a new payee in the first 24 hours. Check with your bank if a payment is declined with "Limit exceeded" even though you're within Kuberix's limits.

**[4] UPI limits on Kuberix** · `KB-C04#5` · cited

> UPI limits on Kuberix
>
> ## Need to send more?
>
> For amounts above your UPI limit, use NEFT, RTGS or IMPS from your bank's own app. Kuberix can't raise UPI limits for individual users.

**[5] UPI Lite: small payments without a PIN** · `KB-C12#2`

> UPI Lite: small payments without a PIN
>
> ## Limits on Kuberix
>
> - Up to **₹1,000** per payment
> - Up to **₹5,000** UPI Lite balance

---

## Q22 · customer · Hinglish

**Question:** 3 baar galat pin daala, ab payment nahi ho raha

**Rewritten query:** UPI PIN blocked 3 wrong attempts payment failed

**Answer** (cites [3], [6]):

> Aapne 3 baar galat PIN dala hai, isliye aapke bank ne us account ke liye UPI payments 24 ghante (hours) ke liye block kar diye hain [3]. Kuberix is block ko nahi hata sakta [3]. 
>
> Kuberix ya koi aur kabhi bhi aapka UPI PIN nahi maangega [3][6].

### Sources

**[1] Money was debited but my payment failed** · `KB-C06#3`

> Money was debited but my payment failed
>
> ## If the money hasn't come back in time
>
> 1. Go to **History**, tap the payment, then tap **Raise an issue > Money debited, payment failed**.
> 2. Keep the **UPI reference number** handy. Your bank needs it.
> 3. You can also contact your bank directly and ask for the reversal and the delay compensation.
>
> If your issue isn't solved within 30 days, see "Complaints and escalation".

**[2] I sent money to the wrong person** · `KB-C07#5`

> I sent money to the wrong person
>
> ## Avoid this next time
>
> Always check the name Kuberix shows before entering your UPI PIN.

**[3] Set or reset your UPI PIN** · `KB-C02#5` · cited

> Set or reset your UPI PIN
>
> ## Good to know
>
> - After 3 wrong PIN attempts, your bank blocks UPI payments for that account for 24 hours. Kuberix can't remove this block.
> - After resetting your PIN, the first 24 hours may have a lower limit set by your bank.
> - Kuberix will never call you to ask for your UPI PIN. Entering your PIN is only ever needed to **send** money, never to **receive** it.

**[4] Set or reset your UPI PIN** · `KB-C02#2`

> Set or reset your UPI PIN
>
> ## Set your UPI PIN for the first time
>
> 1. Go to **Profile > Bank accounts** and tap the account.
> 2. Tap **Set UPI PIN**.
> 3. Choose **Debit card** or **Aadhaar**.
>    - Debit card: enter the last 6 digits and the expiry date.
>    - Aadhaar: enter the first 6 digits of your Aadhaar number. Your bank account must be linked to Aadhaar.
> 4. Enter the OTP your bank sends by SMS.
> 5. Enter your new UPI PIN twice.

**[5] Set or reset your UPI PIN** · `KB-C02#1`

> Set or reset your UPI PIN
>
> Your UPI PIN is a 4 or 6 digit number that approves every UPI payment. It belongs to your bank account, not to the Kuberix app, so the same PIN works in any UPI app for that account.

**Note:** the answer cites [6], but only 5 sources were sent.

---

## Q28 · customer · Hinglish

**Question:** full kyc ke baad wallet me max kitna rakh sakte hai

**Rewritten query:** maximum wallet balance after full KYC

**Answer** (cites [1]):

> Full KYC ke baad Kuberix Wallet mein maximum balance ₹2,00,000 tak rakh sakte hain [1]. Add money per month ki koi monthly limit nahi hai, bas balance limit tak add kar sakte hain [1]. Isme aap doosre logon ko ₹1,00,000 per month tak bhej sakte hain, apni bank mein transfer kar sakte hain, aur merchants ko pay kar sakte hain [1]. Iski koi expiry nahi hoti hai [1].

### Sources

**[1] Kuberix Wallet: KYC levels and limits** · `KB-C09#2` · cited

> Kuberix Wallet: KYC levels and limits
>
> ## Wallet levels
>
> | | Minimum KYC | Full KYC |
> | --- | --- | --- |
> | How to get it | Verify your mobile number and PAN or another ID | Complete Video KYC |
> | Maximum balance | ₹10,000 | ₹2,00,000 |
> | Add money per month | ₹10,000 | No monthly limit, up to the balance limit |
> | Pay merchants | Yes | Yes |
> | Send to other people | No | Yes, up to ₹1,00,000 per month |
> | Transfer to your bank | No | Yes |
> | Validity | Must upgrade to Full KYC within 12 months | No expiry |

**[2] Kuberix Wallet: KYC levels and limits** · `KB-C09#4`

> Kuberix Wallet: KYC levels and limits
>
> ## What if I don't upgrade within 12 months?
>
> You won't be able to add money. You can still spend your balance at merchants.

**[3] Complete your KYC with Video KYC** · `KB-C11#1`

> Complete your KYC with Video KYC
>
> Video KYC upgrades your Kuberix Wallet to Full KYC in about 5 minutes, on a video call with a Kuberix agent.

**[4] Kuberix Wallet: KYC levels and limits** · `KB-C09#3`

> Kuberix Wallet: KYC levels and limits
>
> ## Why can't I send wallet money to a friend?
>
> Sending money to other people and transferring to your bank need Full KYC. See "Complete your KYC with Video KYC".

**[5] Close your Kuberix account** · `KB-C20#1`

> Close your Kuberix account
>
> ## Before you close
>
> - **Empty your Kuberix Wallet.** Full KYC users can transfer the balance to their bank. Minimum KYC users can spend it at merchants, or contact support to return it to the source.
> - **Cancel all AutoPay mandates** in **Profile > AutoPay**.
> - **Turn off UPI Lite** so the balance goes back to your bank.
> - Download any statements you need (see "Transaction history and statements").

---

## Q30 · customer · Hinglish

**Question:** phone chori ho gaya, account block kaise karu

**Rewritten query:** how to block account stolen phone

**Answer** (cites [1], [2]):

> Aap apne account ko block karne ke liye kisi bhi browser se **kuberix.example/block** par ja sakte hain [1][2]. App mein **Help > Help > Block my account** par bhi ja sakte hain [2]. Iske alawa, apne mobile operator se SIM block karwayein aur same number par replacement SIM lein, aur bank se UPI block karne ko kahein [1]. Fraud ke liye National Cybercrime Helpline par 1930 par call karein ya cybercrime.gov.in par complaint file karein, aur Kuberix par **History** mein payment tap karke **Report fraud** select karein [2].

### Sources

**[1] Lost phone, new phone or changed SIM** · `KB-C18#1` · cited

> Lost phone, new phone or changed SIM
>
> ## Lost or stolen phone
>
> 1. Block your account at **kuberix.example/block** from any browser.
> 2. Ask your mobile operator to block your SIM, then get a replacement SIM with the same number.
> 3. Ask your bank to block UPI until you're set up again.
>
> Your money stays safe in your bank account. Nobody can make UPI payments without your UPI PIN.

**[2] Report fraud or an unauthorised payment** · `KB-C17#2` · cited

> Report fraud or an unauthorised payment
>
> ## Do these right now
>
> 1. **Block your Kuberix account:** go to **Help > Block my account**. If you can't open the app, use **kuberix.example/block** from any browser.
> 2. **Call your bank** and ask them to block UPI on your account.
> 3. **Report it to the National Cybercrime Helpline: call 1930** or file a complaint at **cybercrime.gov.in**.
> 4. **Report it to Kuberix:** go to **History**, tap the payment, then **Report fraud**.

**[3] Receive money and request money** · `KB-C22#4`

> Receive money and request money
>
> ## Block requests
>
> If someone keeps sending you requests, tap the request and choose **Block**. Never approve a request you don't recognise; approving a request **sends** money.

**[4] I sent money to the wrong person** · `KB-C07#5`

> I sent money to the wrong person
>
> ## Avoid this next time
>
> Always check the name Kuberix shows before entering your UPI PIN.

**[5] Report fraud or an unauthorised payment** · `KB-C17#1`

> Report fraud or an unauthorised payment
>
> Act fast. The sooner you report, the better the chance of stopping the money.

---

## Q36 · merchant · English

**Question:** lost my api secret, how do i get a new one

**Rewritten query:** regenerate api secret

**Answer** (cites [1], [2], [3]):

> Agar aapka API secret leak ya lost ho gaya hai, toh aap **Developers > API keys** par jaakar **Regenerate** par click kar sakte hain [1]. Isse purana key turant kaam karna band kar deta hai, isliye apna server turant update karein [1]. Agar koi team member remove kiya gaya tha aur woh Developer the, toh bhi aapko apni API keys regenerate karni hongi [2]. 
>
> Nayi key generate karne ke liye business.kuberix.example par **Developers > API keys** par jayein, **Test** ya **Live** choose karein aur **Generate key** par click karein [3]. Ek **Key ID** aur **Key secret** dikhega, aur **secret sirf ek baar hi dikhaya jata hai** [3]. Ise apne server ke secret manager jaisi jagah par surakshit store karein [3].

### Sources

**[1] Accept payments online: API keys** · `KB-M10#5` · cited

> Accept payments online: API keys
>
> ## If a secret leaks
>
> Go to **Developers > API keys**, click **Regenerate**. The old key stops working immediately, so update your server straight away.

**[2] Team members, roles and account security** · `KB-M13#4` · cited

> Team members, roles and account security
>
> ## Remove someone
>
> Go to **Account > Team**, tap the person and choose **Remove**. Their access ends immediately. If they were a Developer, also regenerate your API keys.

**[3] Accept payments online: API keys** · `KB-M10#3` · cited

> Accept payments online: API keys
>
> ## Generate keys
>
> 1. Go to **Developers > API keys** on business.kuberix.example.
> 2. Choose **Test** or **Live** and click **Generate key**.
> 3. You'll see a **Key ID** and a **Key secret**. **The secret is shown only once.** Store it safely, for example in your server's secret manager.

**[4] Accept payments online: API keys** · `KB-M10#4`

> Accept payments online: API keys
>
> ## Keep your secret safe
>
> - Use the key secret **only on your server**. Never put it in your website's JavaScript, your mobile app or a public code repository.
> - Anyone with your secret can create payments and refunds on your account.

**[5] Accept payments online: API keys** · `KB-M10#2`

> Accept payments online: API keys
>
> ## Test and live keys
>
> | | Test mode | Live mode |
> | --- | --- | --- |
> | Use for | Building and testing | Real customer payments |
> | Real money moves | No | Yes |
> | Key ID starts with | `kbx_test_` | `kbx_live_` |
> | Available | Right after sign-up | After your account is approved |

---

## Q37 · merchant · English

**Question:** payment.captured webhook not reaching my server

**Rewritten query:** payment.captured webhook not reaching server

**Answer** (cites [1], [4], [5]):

> Agar `payment.captured` webhook aapke server tak nahi pahunch raha hai, toh yeh steps follow karein:
>
> 1. **Developers > Webhooks > Logs** par check karein ki aapke server ne kya response bheja hai [1].
> 2. Ensure karein ki aapka URL public hai aur valid certificate ke sath HTTPS use karta hai [1].
> 3. Check karein ki aapka firewall Kuberix se requests allow karta hai [1].
> 4. Aapka server **5 seconds ke andar 2xx status** return kare [5]. Slow kaam jaise email bhejna response dene ke baad karein [5].
> 5. Agar server 2xx se respond nahi karta, toh Kuberix **24 hours** tak badhte gaps ke sath retries karta hai, uske baad webhook failed mark ho jata hai [4]. Aap ise **Developers > Webhooks > Logs** se resend kar sakte hain [4]. Duplicate events ke liye `event_id` use karein [4].

### Sources

**[1] Webhooks: get notified about payments** · `KB-M11#6` · cited

> Webhooks: get notified about payments
>
> ## Webhook not arriving?
>
> 1. Check **Developers > Webhooks > Logs** for the response your server sent.
> 2. Make sure your URL is public and uses HTTPS with a valid certificate.
> 3. Check that your firewall allows requests from Kuberix.

**[2] Webhooks: get notified about payments** · `KB-M11#2`

> Webhooks: get notified about payments
>
> ## Set up a webhook
>
> 1. Go to **Developers > Webhooks > Add endpoint**.
> 2. Enter your server's HTTPS URL.
> 3. Choose the events, for example `payment.captured`, `payment.failed`, `refund.processed`, `settlement.processed`, `dispute.created`.
> 4. Set a **webhook secret**.

**[3] Webhooks: get notified about payments** · `KB-M11#1`

> Webhooks: get notified about payments
>
> Webhooks tell your server when something happens, like a payment succeeding, so you don't have to keep asking the API.

**[4] Webhooks: get notified about payments** · `KB-M11#5` · cited

> Webhooks: get notified about payments
>
> ## Retries
>
> If your server doesn't respond with 2xx, Kuberix retries with increasing gaps for up to **24 hours**. After that the webhook is marked failed. You can resend it from **Developers > Webhooks > Logs**.
>
> The same event can arrive more than once. Use the `event_id` to ignore duplicates.

**[5] Webhooks: get notified about payments** · `KB-M11#4` · cited

> Webhooks: get notified about payments
>
> ## Respond quickly
>
> Return a **2xx status within 5 seconds**. Do slow work, like sending emails, after you've responded.
