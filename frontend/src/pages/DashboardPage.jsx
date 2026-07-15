import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts'
import { getDashboard, getMonthlyTrend } from '../api'

const COLORS = [
  '#6c63ff', '#ff6b6b', '#51cf66', '#ffd43b',
  '#74c0fc', '#f783ac', '#a9e34b', '#ff922b',
  '#66d9e8', '#cc5de8'
]

const fmt = (n) => `₹${Number(n).toLocaleString('en-IN')}`

export default function DashboardPage() {
  const [dashboard, setDashboard] = useState(null)
  const [trend, setTrend] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    const fetchAll = async () => {
      setLoading(true)
      try {
        const [dash, trendData] = await Promise.all([
          getDashboard(),
          getMonthlyTrend(6),
        ])
        setDashboard(dash)
        setTrend(trendData)
      } catch (err) {
        setError('Failed to load dashboard')
      } finally {
        setLoading(false)
      }
    }
    fetchAll()
  }, [])

  if (loading) {
    return (
      <div style={{ color: 'var(--color-muted)', fontSize: 14, padding: '40px 0' }}>
        Loading dashboard…
      </div>
    )
  }

  if (error) {
    return (
      <div style={{ padding: '10px 14px', background: 'rgba(255,107,107,0.1)', border: '1px solid rgba(255,107,107,0.3)', borderRadius: 6, color: 'var(--color-debit)', fontSize: 14 }}>
        {error}
      </div>
    )
  }

  // Empty state — no transactions yet
  if (!dashboard || dashboard.total_transactions === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '80px 0' }}>
        <div style={{ fontSize: 48, marginBottom: 16 }}>📊</div>
        <h2 style={{ margin: '0 0 8px', fontSize: 20, fontWeight: 700 }}>No data yet</h2>
        <p style={{ color: 'var(--color-muted)', fontSize: 14, marginBottom: 24 }}>
          Parse some UPI SMS messages to see your spending analytics
        </p>
        <button
          onClick={() => navigate('/parse')}
          style={{ padding: '10px 24px', background: 'var(--color-accent)', color: '#fff', border: 'none', borderRadius: 6, fontSize: 14, fontWeight: 600, cursor: 'pointer' }}
        >
          Add SMS →
        </button>
      </div>
    )
  }

  const pieData = (dashboard.spending_by_category || []).map((c) => ({
  name: c.category,
  value: Number(c.spent),    // ✅ correct
}))

  const barData = trend.map((t) => ({
  name: t.month,
  Debit: Number(t.spent),      // ✅ matches API
  Credit: Number(t.credited),  // ✅ matches API
}))

  return (
    <div>
      {/* Header */}
      <h2 style={{ margin: '0 0 4px', fontSize: 22, fontWeight: 700 }}>Dashboard</h2>
      <p style={{ margin: '0 0 28px', color: 'var(--color-muted)', fontSize: 14 }}>
        Your spending overview
      </p>

      {/* Stat cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 16, marginBottom: 32 }}>
        <StatCard
  label="This Month"
  value={fmt(dashboard.total_spent_this_month || 0)}
  color="var(--color-debit)"
/>
<StatCard
  label="Last Month"
  value={fmt(dashboard.total_spent_last_month || 0)}
  color="var(--color-text)"
/>
<StatCard
  label="Month Change"
  value={`${dashboard.month_over_month_change > 0 ? '+' : ''}${dashboard.month_over_month_change}%`}
  color={dashboard.month_over_month_change <= 0 ? 'var(--color-credit)' : 'var(--color-debit)'}
/>
<StatCard
  label="Categories"
  value={dashboard.spending_by_category?.length || 0}
  color="var(--color-accent-light)"
/>
      </div>

      {/* Charts row */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 32 }}>

        {/* Pie chart — spending by category */}
        {pieData.length > 0 && (
          <div style={cardStyle}>
            <h3 style={chartTitle}>Spending by Category</h3>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={85}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {pieData.map((_, index) => (
                    <Cell key={index} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value) => fmt(value)}
                  contentStyle={{ background: 'var(--color-surface-2)', border: '1px solid var(--color-border)', borderRadius: 6, fontSize: 12 }}
                  labelStyle={{ color: 'var(--color-text)' }}
                />
              </PieChart>
            </ResponsiveContainer>
            {/* Legend */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px 14px', marginTop: 8 }}>
              {pieData.map((entry, index) => (
                <div key={entry.name} style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12 }}>
                  <div style={{ width: 8, height: 8, borderRadius: '50%', background: COLORS[index % COLORS.length], flexShrink: 0 }} />
                  <span style={{ color: 'var(--color-muted)' }}>{entry.name}</span>
                  <span style={{ color: 'var(--color-text)', fontWeight: 600 }}>{fmt(entry.value)}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Bar chart — monthly trend */}
        {barData.length > 0 && (
          <div style={cardStyle}>
            <h3 style={chartTitle}>Monthly Trend</h3>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={barData} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                <XAxis dataKey="name" tick={{ fontSize: 11, fill: 'var(--color-muted)' }} />
                <YAxis tick={{ fontSize: 11, fill: 'var(--color-muted)' }} tickFormatter={(v) => `₹${v/1000}k`} />
                <Tooltip
                  formatter={(value) => fmt(value)}
                  contentStyle={{ background: 'var(--color-surface-2)', border: '1px solid var(--color-border)', borderRadius: 6, fontSize: 12 }}
                />
                <Bar dataKey="Debit" fill="var(--color-debit)" radius={[3, 3, 0, 0]} opacity={0.85} />
                <Bar dataKey="Credit" fill="var(--color-credit)" radius={[3, 3, 0, 0]} opacity={0.85} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Budget alerts */}
      {dashboard.budget_alerts && dashboard.budget_alerts.length > 0 && (
        <div style={{ marginBottom: 32 }}>
          <h3 style={{ margin: '0 0 12px', fontSize: 15, fontWeight: 600 }}>Budget Alerts</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {dashboard.budget_alerts.map((alert) => (
              <div key={alert.category} style={{
                padding: '12px 16px',
                background: 'var(--color-surface)',
                border: `1px solid ${alert.percentage >= 1 ? 'rgba(255,107,107,0.4)' : 'rgba(255,180,0,0.3)'}`,
                borderRadius: 8,
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}>
                <div>
                  <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 4 }}>{alert.category}</div>
                  <div style={{ fontSize: 12, color: 'var(--color-muted)' }}>
                    {fmt(alert.spent)} of {fmt(alert.limit)} budget
                  </div>
                </div>
                <div style={{
                  fontSize: 14,
                  fontWeight: 700,
                  color: alert.percentage >= 1 ? 'var(--color-debit)' : '#ffd43b',
                }}>
                  {Math.round(alert.percentage * 100)}%
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent transactions */}
      {dashboard.recent_transactions && dashboard.recent_transactions.length > 0 && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <h3 style={{ margin: 0, fontSize: 15, fontWeight: 600 }}>Recent Transactions</h3>
            <span
              onClick={() => navigate('/transactions')}
              style={{ fontSize: 13, color: 'var(--color-accent-light)', cursor: 'pointer' }}
            >
              View all →
            </span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {dashboard.recent_transactions.map((txn) => (
              <div key={txn.id} style={{
                padding: '12px 16px',
                background: 'var(--color-surface)',
                border: '1px solid var(--color-border)',
                borderRadius: 8,
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}>
                <div>
                  <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 2 }}>
                    {txn.merchant || 'Unknown'}
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--color-muted)' }}>
                    {txn.category} · {txn.txn_date}
                  </div>
                </div>
                <div style={{
                  fontWeight: 700,
                  fontSize: 15,
                  color: txn.txn_type === 'debit' ? 'var(--color-debit)' : 'var(--color-credit)',
                }}>
                  {txn.txn_type === 'debit' ? '−' : '+'}₹{txn.amount}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function StatCard({ label, value, color }) {
  return (
    <div style={{
      padding: '20px',
      background: 'var(--color-surface)',
      border: '1px solid var(--color-border)',
      borderRadius: 10,
    }}>
      <div style={{ fontSize: 12, color: 'var(--color-muted)', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
        {label}
      </div>
      <div style={{ fontSize: 22, fontWeight: 700, color }}>
        {value}
      </div>
    </div>
  )
}

const cardStyle = {
  padding: 20,
  background: 'var(--color-surface)',
  border: '1px solid var(--color-border)',
  borderRadius: 10,
}

const chartTitle = {
  margin: '0 0 16px',
  fontSize: 14,
  fontWeight: 600,
  color: 'var(--color-text)',
}