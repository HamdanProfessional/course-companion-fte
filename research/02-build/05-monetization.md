# Monetization

**Source:** https://developers.openai.com/apps-sdk/build/monetization
**Phase:** Build
**Last Updated:** February 2026

---

## Overview

When building a ChatGPT app, developers choose how to monetize. Today, the **recommended** and **generally available** approach is **external checkout**. **Instant Checkout** is available in private beta for select marketplace partners.

---

## Monetization Approaches

### ✅ External Checkout (Recommended)

Direct users from ChatGPT to your merchant-hosted checkout flow.

**Flow:**
1. User interacts with app in ChatGPT
2. App presents purchasable items ("Upgrade", "Buy now", "Subscribe")
3. User clicks → Redirected to your external checkout
4. Payment, billing, taxes handled on your domain
5. User returns to ChatGPT with confirmation

**Benefits:**
- Full control over checkout flow
- Your payment processor
- Your compliance handling
- Works for all use cases

---

### Instant Checkout (Private Beta)

In-chat payment UI for select marketplace partners.

**Flow:**
1. Server prepares checkout session
2. Widget renders cart preview
3. Widget calls `requestCheckout(session_data)`
4. ChatGPT opens Instant Checkout UI
5. Server finalizes via `complete_checkout` tool

**Limitations:**
- Limited to select marketplaces today
- Not available to all users
- Requires approval

---

## External Checkout Implementation

### Simple Link Pattern

```typescript
{
  "structuredContent": {
    "title": "Upgrade to Premium",
    "features": ["Unlimited access", "Priority support"],
    "action_url": "https://yourapp.com/checkout?plan=premium"
  }
}
```

### Widget Button Pattern

```typescript
export function UpgradeButton() {
  const handleUpgrade = () => {
    window.openai.openExternal({
      url: "https://yourapp.com/checkout?plan=premium"
    });
  };

  return (
    <button onClick={handleUpgrade}>
      Upgrade to Premium
    </button>
  );
}
```

---

## Instant Checkout Implementation

### Step 1: Prepare Checkout Session

Server returns checkout session data:

```typescript
{
  "structuredContent": {
    "checkout_session": {
      "id": "cs_12345",
      "payment_provider": {
        "provider": "stripe",
        "merchant_id": "merchant_abc123",
        "supported_payment_methods": ["card", "apple_pay", "google_pay"]
      },
      "status": "ready_for_payment",
      "currency": "USD",
      "totals": [
        {
          "type": "subtotal",
          "display_text": "Subtotal",
          "amount": 300
        },
        {
          "type": "tax",
          "display_text": "Tax",
          "amount": 30
        },
        {
          "type": "total",
          "display_text": "Total",
          "amount": 330
        }
      ],
      "links": [
        { "type": "terms_of_use", "url": "https://yourapp.com/terms" },
        { "type": "privacy_policy", "url": "https://yourapp.com/privacy" }
      ],
      "payment_mode": "live"
    }
  }
}
```

---

### Step 2: Widget Calls `requestCheckout`

```typescript
async function handleCheckout(sessionJson: string) {
  const session = JSON.parse(sessionJson);

  if (!window.openai?.requestCheckout) {
    throw new Error("requestCheckout is not available");
  }

  const order = await window.openai.requestCheckout({
    ...session,
    id: checkout_session_id,
  });

  return order;
}
```

### Widget Component Example

```typescript
export function CheckoutButton() {
  const [isLoading, setIsLoading] = useState(false);
  const [order, setOrder] = useState(null);
  const checkoutSessionJson = JSON.stringify(checkoutSession);

  return (
    <>
      <Button
        onClick={async () => {
          setIsLoading(true);
          try {
            const orderResponse = await handleCheckout(checkoutSessionJson);
            setOrder(orderResponse);
          } catch (error) {
            console.error(error);
          } finally {
            setIsLoading(false);
          }
        }}
      >
        {isLoading ? "Loading..." : "Checkout"}
      </Button>

      {order && <OrderConfirmation order={order} />}
    </>
  );
}
```

---

### Step 3: Implement `complete_checkout` Tool

```typescript
@tool(description="")
async def complete_checkout(
    self,
    checkout_session_id: str,
    buyer: Buyer,
    payment_data: PaymentData,
) -> types.CallToolResult:
    # Integrate with your PSP to charge payment
    charge_result = await charge_payment(payment_data)

    # Persist order in backend
    order = await create_order(checkout_session_id, charge_result)

    return types.CallToolResult(
        content=[{
            "type": "text",
            "text": f"Order {order.id} completed successfully!"
        }],
        structuredContent={
            "id": checkout_session_id,
            "status": "completed",
            "currency": "USD",
            "order": {
                "id": order.id,
                "checkout_session_id": checkout_session_id,
                "permalink_url": order.receipt_url,
            },
        },
        _meta={META_SESSION_ID: "checkout-flow"},
        isError=False,
    )
```

---

## Error Handling

### Error Display

| Error Code | Display Location |
|------------|------------------|
| `payment_declined` | Instant Checkout UI |
| `requires_3ds` | Instant Checkout UI |
| All others | Widget (response to `requestCheckout`) |

### Widget Error Handling

```typescript
async function handleCheckout(sessionJson: string) {
  try {
    const order = await window.openai.requestCheckout(session);
    return order;
  } catch (error) {
    // Display error in widget
    showError(error.message);
  }
}
```

---

## Test Payment Mode

Set `payment_mode` to `"test"` for testing:

```typescript
const checkoutRequest = {
  id: checkoutSessionId,
  payment_provider: {
    provider: "stripe",
    merchant_id: "test_merchant_id", // May differ from live
    supported_payment_methods: ["card"],
  },
  status: "ready_for_payment",
  currency: "USD",
  totals: [
    {
      type: "total",
      display_text: "Total",
      amount: 330,
    },
  ],
  links: [
    { type: "terms_of_use", url: "https://yourapp.com/terms" },
    { type: "privacy_policy", url: "https://yourapp.com/privacy" }
  ],
  payment_mode: "test",  // Enables test cards
};

const response = await window.openai.requestCheckout(checkoutRequest);
```

**Test Cards:** Use test cards (e.g., Stripe 4242) without moving real funds.

---

## PSP Integration Guides

| Provider | Guide |
|----------|-------|
| **Stripe** | [Stripe Integration Guide](https://stripe.com/docs) |
| **Adyen** | [Adyen Integration Guide](https://docs.adyen.com) |

---

## Implementation Checklist

1. [ ] Define checkout session model (id, provider, totals, links)
2. [ ] Return session from MCP tool in `structuredContent`
3. [ ] Render session in widget for review
4. [ ] Call `requestCheckout(session_data)` on user action
5. [ ] Implement `complete_checkout` MCP tool
6. [ ] Integrate with PSP to charge payment
7. [ ] Return authoritative order/receipt data
8. [ ] Test end-to-end with test mode

---

## Best Practices

1. **Render preview** - Show cart items, totals, terms before checkout
2. **Handle errors** - Display clear error messages
3. **Test thoroughly** - Use test mode before going live
4. **Persist orders** - Store order data in your backend
5. **Provide receipts** - Return permalink_url for order confirmation

---

## Common Pitfalls

### Mistake 1: Missing Legal Links

❌ **Don't:** Omit terms and privacy links

✅ **Do:** Include `terms_of_use` and `privacy_policy` links

---

### Mistake 2: Not Handling Test Mode

❌ **Don't:** Use same `merchant_id` for test and live

✅ **Do:** Use different merchant IDs for test vs live

---

### Mistake 3: Forgetting Error Handling

❌ **Don't:** Let checkout errors fail silently

✅ **Do:** Catch errors and display in widget

---

## Related Resources

- **Previous:** [State Management](./04-state-management.md)
- **Next:** [Examples](./06-examples.md)
- **PSP Guides:** [Stripe](https://stripe.com/docs) | [Adyen](https://docs.adyen.com)

---

## Minimal Checkout Request Example

```typescript
const checkoutRequest = {
  id: checkoutSessionId,
  payment_provider: {
    provider: "<PSP_NAME>",
    merchant_id: "<MERCHANT_ID>",
    supported_payment_methods: ["card", "apple_pay", "google_pay"],
  },
  status: "ready_for_payment",
  currency: "USD",
  totals: [
    {
      type: "total",
      display_text: "Total",
      amount: 330,
    },
  ],
  links: [
    { type: "terms_of_use", url: "<TERMS_URL>" },
    { type: "privacy_policy", url: "<PRIVACY_URL>" }
  ],
  payment_mode: "live",
};

const response = await window.openai.requestCheckout(checkoutRequest);
```
