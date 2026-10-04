const money = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  maximumFractionDigits: 2,
});

export default function OrderTable({ orders }) {
  return (
    <section className="panel table-panel">
      <div className="section-heading table-heading">
        <div>
          <p className="eyebrow">Live activity</p>
          <h2>Recent orders</h2>
        </div>
        <span className="live-indicator"><span /> Consumer synced</span>
      </div>
      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Order ID</th>
              <th>Product</th>
              <th>Qty</th>
              <th>Amount</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {orders.length === 0 ? (
              <tr>
                <td className="empty-state" colSpan="5">No orders processed yet. Place an order to get started.</td>
              </tr>
            ) : orders.map((order) => (
              <tr key={order.order_id}>
                <td className="order-id">{order.order_id}</td>
                <td className="product-cell">{order.product}</td>
                <td>{order.quantity}</td>
                <td>{money.format(order.amount)}</td>
                <td><span className="status-pill"><span />Processed</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="table-footer">Showing latest {orders.length} processed {orders.length === 1 ? 'order' : 'orders'}</div>
    </section>
  );
}
