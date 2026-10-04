import { useState } from 'react';
import axios from 'axios';

export default function OrderForm({ onOrderCreated }) {
  const [form, setForm] = useState({ product: '', quantity: '1', amount: '' });
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState(null);

  function updateField(event) {
    setForm((current) => ({ ...current, [event.target.name]: event.target.value }));
    setMessage(null);
  }

  async function submitOrder(event) {
    event.preventDefault();
    setSubmitting(true);
    setMessage(null);
    try {
      const response = await axios.post('/orders', {
        product: form.product.trim(),
        quantity: Number(form.quantity),
        amount: Number(form.amount),
      });
      setMessage({ type: 'success', text: `${response.data.order_id} was sent to Kafka.` });
      setForm({ product: '', quantity: '1', amount: '' });
      onOrderCreated();
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.error || 'Could not send the order. Check that the API is running.',
      });
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="panel form-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Order management</p>
          <h2>Create new order</h2>
        </div>
        <span className="section-mark" aria-hidden="true">＋</span>
      </div>
      <form className="order-form" onSubmit={submitOrder}>
        <label className="field field-product">
          <span>Product</span>
          <input
            name="product"
            value={form.product}
            onChange={updateField}
            placeholder="e.g. Laptop"
            maxLength="100"
            required
          />
        </label>
        <label className="field">
          <span>Quantity</span>
          <input
            name="quantity"
            type="number"
            value={form.quantity}
            onChange={updateField}
            min="1"
            step="1"
            required
          />
        </label>
        <label className="field">
          <span>Amount (₹)</span>
          <input
            name="amount"
            type="number"
            value={form.amount}
            onChange={updateField}
            min="0.01"
            step="0.01"
            placeholder="0.00"
            required
          />
        </label>
        <button className="primary-button" type="submit" disabled={submitting}>
          {submitting ? 'Sending order…' : 'Place order'}
          <span aria-hidden="true">→</span>
        </button>
      </form>
      {message && <p className={`form-message ${message.type}`} role="status">{message.text}</p>}
      <p className="form-note"><span aria-hidden="true">●</span> Each order is published to the Kafka orders topic.</p>
    </section>
  );
}
