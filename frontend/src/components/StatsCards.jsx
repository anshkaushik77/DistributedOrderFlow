const money = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  maximumFractionDigits: 0,
});

export default function StatsCards({ totalOrders, totalRevenue }) {
  return (
    <section className="stats-grid" aria-label="Order statistics">
      <article className="stat-card">
        <div className="stat-heading">
          <span className="stat-icon orders-icon" aria-hidden="true">↗</span>
          <span className="stat-label">Total orders</span>
        </div>
        <strong className="stat-value">{totalOrders.toLocaleString('en-IN')}</strong>
        <span className="stat-footnote">Orders processed by Kafka</span>
      </article>
      <article className="stat-card">
        <div className="stat-heading">
          <span className="stat-icon revenue-icon" aria-hidden="true">₹</span>
          <span className="stat-label">Total revenue</span>
        </div>
        <strong className="stat-value">{money.format(totalRevenue)}</strong>
        <span className="stat-footnote">Across all processed orders</span>
      </article>
    </section>
  );
}
