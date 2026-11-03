# Cash on Delivery — Decision Note

**Status:** deferred. COD is not offered in Milestone 3.  
**Owner:** founder (business decision) + finance (cash-flow impact).

## Why COD is common in Indian D2C

- A significant share of Indian online orders are still COD, especially outside
  metros and for first-time buyers who do not yet trust the brand.
- Refusing COD reduces conversion, particularly for footwear where fit anxiety
  drives the purchase decision.

## Fraud and abuse risks

| Risk | Detail |
|---|---|
| Fake orders / prank orders | No prepayment intent; a phone-verified OTP or address-verification step can reduce but not eliminate these. |
| Non-delivery / RTO (return to origin) | The courier attempts delivery and the buyer refuses the package. The seller absorbs both outbound and return shipping. For footwear, this cost is material because shoe boxes are heavy and bulky. |
| Weight-based fraud | The buyer opens the package at the door, swaps contents and refuses. Hard to prove without tamper-evident packaging and unboxing video evidence. |
| Address farming | Fake orders to accumulate real addresses for resale or social engineering. |
| Repeat offenders | Without authentication, the same guest can place unlimited COD orders under different email or phone numbers. |

## Return-cost questions for COD

These must be answered before COD can ship. Each is blocked on a named owner.

| Question | Blocked on |
|---|---|
| What is the average outbound + RTO cost per shipment for a shoe box (weight class ~1.5 kg, volumetric ~6 kg)? | 3PL partner |
| What is the acceptable RTO rate before COD becomes margin-negative at the current MRP? | Founder + CA |
| Should COD carry a surcharge (common: ₹50–₹100) to offset RTO risk? If so, is it refundable on successful delivery? | Founder |
| Should COD orders require phone OTP verification before the shipment is created? | Founder |
| Should a COD blocklist track phone numbers or addresses that have caused more than N RTOs? | Founder |
| What is the maximum order value eligible for COD? High-value orders amplify RTO loss. | Founder + CA |
| Should COD orders delay shipment by 24 h to allow a confirmation call or SMS nudge, reducing impulsive RTOs? | Founder |
| Does the 3PL support partial COD (e.g., ₹200 prepaid online + remainder on delivery)? | 3PL partner |

## Implementation sketch (when approved)

1. Add `payment_method` to the order model: `prepaid` or `cod`.
2. COD orders skip the Razorpay flow; status goes directly to `confirmed` (new
   state) after an OTP or address check.
3. Stock is reserved on order creation but the reservation window is longer
   (e.g., until shipment + delivery window + RTO window).
4. Payment is confirmed only when the courier marks the shipment as delivered
   and remits the collection.
5. COD refunds on return mean the seller never collected the money; only the
   shipping cost is a loss.
6. A `cod_surcharge_paise` column on the order stores the surcharge separately
   from the product total so it can be refunded independently.

## Recommendation

Launch prepaid-only (Milestone 3). Introduce COD only after:

1. The 3PL partner quotes RTO shipping costs for the footwear weight class.
2. The founder sets an RTO tolerance and decides on a surcharge.
3. Authentication ships (Milestone 5+) so repeat-offender tracking is possible.
4. Phone OTP verification is available for guest COD orders.

This avoids absorbing unquantified RTO costs before the brand has any delivery
data to calibrate fraud rules.

