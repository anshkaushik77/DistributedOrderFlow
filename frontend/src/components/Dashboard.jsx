import { useCallback, useEffect, useState } from 'react';
import axios from 'axios';
import OrderForm from './OrderForm.jsx';
import OrderTable from './OrderTable.jsx';
import StatsCards from './StatsCards.jsx';

export default function Dashboard() {
  const [orders, setOrders] = useState([]);
  const [analytics, setAnalytics] = useState({ total_orders: 0, total_revenue: 0 });
  const [apiAvailable, setApiAvailable] = useState(true);

  const refreshDashboard = useCallback(async () => {
    try {
      const [ordersResponse, analyticsResponse] = await Promise.all([
        axios.get('/orders'),
        axios.get('/analytics'),
      ]);
      setOrders([...ordersResponse.data].reverse());
      setAnalytics(analyticsResponse.data);
      setApiAvailable(true);
    } catch {
      setApiAvailable(false);
    }
  }, []);

  useEffect(() => {
    refreshDashboard();
    const timer = window.setInterval(refreshDashboard, 3000);
    return () => window.clearInterval(timer);
  }, [refreshDashboard]);

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="#top" aria-label="Distributed OrderFlow home">
          <span className="brand-mark" aria-hidden="true"><i /><i /><i /></span>
          <span>Order<span className="brand-light">Flow</span></span>
        </a>
        <div className="topbar-right">
          <span className="system-status"><span className={apiAvailable ? '' : 'offline'} />{apiAvailable ? 'System operational' : 'API unavailable'}</span>
          <span className="avatar" aria-label="Demo workspace">DF</span>
        </div>
      </header>

      <div className="dashboard-content" id="top">
        <section className="welcome-row">
          <div>
            <p className="eyebrow">Distributed systems demo</p>
            <h1>Distributed OrderFlow</h1>
            <p className="welcome-copy">A clear view of every order moving through your event pipeline.</p>
          </div>
          <div className="pipeline-badge"><span className="pipeline-dot" /> Kafka pipeline <span className="pipeline-divider">/</span> <span>orders</span></div>
        </section>

        <StatsCards totalOrders={analytics.total_orders || 0} totalRevenue={analytics.total_revenue || 0} />
        <OrderForm onOrderCreated={refreshDashboard} />
        <OrderTable orders={orders.slice(0, 10)} />
        <footer className="page-footer"><span>Distributed OrderFlow</span><span>Built with Flask, Kafka &amp; React</span></footer>
      </div>
    </main>
  );
}
