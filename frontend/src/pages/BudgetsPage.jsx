import { useState, useEffect } from 'react'
import { getBudgetSummary, upsertBudget } from '../api'

const CATEGORIES = [
  'Food', 'Transport', 'Shopping', 'Entertainment', 'Bills',
  'Health', 'Groceries', 'Education', 'Travel', 'Transfers',
  'Subscriptions', 'Uncategorized'
]

export default function BudgetsPage() {
  const [budgets, setBudgets] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Form state
  const [category, setCategory] = useState('Food')
  const [limit, setLimit] = useState('')
  const [formError, setFormError] = useState('')
  const [formLoading, setFormLoading] = useState(false)
  const [formSuccess, setFormSuccess] = useState('')

  const fetchBudgets = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await getBudgetSummary()
      setBudgets(data)
    } catch (err) {
      setError('Failed to load budgets')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchBudgets()
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setFormError('')
    setFormSuccess('')
    setFormLoading(true)
    try {
      await upsertBudget({ category, monthly_limit: Number(limit) })
      setFormSuccess(`Budget for ${category} saved successfully`)
      setLimit('')
      fetchBudgets()   // refresh list
    } catch (err) {
      setFormError(err.response?.data?.detail || 'Failed to save budget')
    } finally {
      setFormLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 680 }}>
      {/* Header */}
      <h2 style={{ margin: '0 0 4px', fontSize: 22, fontWeight: 700 }}>Budgets</h2>
      <p style={{ margin: '0 0 28px', color: 'var(--color-muted)', fontSize: 14 }}>
        Set monthly limits and track your spending
      </p>

      {/* Add / Update budget form */}
      <div style={{
        padding: 20,
        background: 'var(--color-surface)',
        border: '1px solid var(--color-border)',
        borderRadius: 10,
        marginBottom: 28,
      }}>
        <h3 style={{ margin: '0 0 16px', fontSize: 15, fontWeight: 600 }}>
          Set Budget
        </h3>

        {formError && (
          <div style={{ marginBottom: 12, padding: '8px 12px', background: 'rgba(255,107,107,0.1)', border: '1px solid rgba(255,107,107,0.3)', borderRadius: 6, color: 'var(--color-debit)', fontSize: 13 }}>
            {formError}
          </div>
        )}

        {formSuccess && (
          <div style={{ marginBottom: 12, padding: '8px 12px', background: 'rgba(81,207,102,0.1)', border: '1px solid rgba(81,207,102,0.3)', borderRadius: 6, color: 'var(--color-credit)', fontSize: 13 }}>
            {formSuccess}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', gap: 12, alignItems: 'flex-end', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6, flex: 1, minWidth: 160 }}>
            <label style={{ fontSize: 12, color: 'var(--color-muted)' }}>Category</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              style={inputStyle}
            >
              {CATEGORIES.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 6, flex: 1, minWidth: 140 }}>
            <label style={{ fontSize: 12, color: 'var(--color-muted)' }}>Monthly Limit (₹)</label>
            <input
              type="number"
              value={limit}
              onChange={(e) => setLimit(e.target.value)}
              placeholder="e.g. 2000"
              required
              min={1}
              style={inputStyle}
            />
          </div>

          <button
            type="submit"
            disabled={formLoading}
            style={{
              padding: '10px 20px',
              background: 'var(--color-accent)',
              color: '#fff',
              border: 'none',
              borderRadius: 6,
              fontSize: 14,
              fontWeight: 600,
              cursor: formLoading ? 'not-allowed' : 'pointer',
              opacity: formLoading ? 0.7 : 1,
              height: 40,
            }}
          >
            {formLoading ? 'Saving…' : 'Save Budget'}
          </button>
        </form>
      </div>

      {/* Error */}
      {error && (
        <div style={{ padding: '10px 14px', background: 'rgba(255,107,107,0.1)', border: '1px solid rgba(255,107,107,0.3)', borderRadius: 6, color: 'var(--color-debit)', fontSize: 14, marginBottom: 16 }}>
          {error}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div style={{ color: 'var(--color-muted)', fontSize: 14 }}>Loading budgets…</div>
      )}

      {/* Empty state */}
      {!loading && budgets.length === 0 && (
        <div style={{ textAlign: 'center', padding: '40px 0', color: 'var(--color-muted)' }}>
          <div style={{ fontSize: 32, marginBottom: 12 }}>💰</div>
          <p style={{ fontSize: 15, marginBottom: 4 }}>No budgets set yet</p>
          <p style={{ fontSize: 13 }}>Use the form above to set your first monthly budget</p>
        </div>
      )}

      {/* Budget list */}
      {!loading && budgets.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {budgets.map((budget) => {
            const spent = Number(budget.spent || 0)
            const budgetLimit = Number(budget.monthly_limit)
            const percentage = budgetLimit > 0 ? spent / budgetLimit : 0
            const isOver = percentage >= 1
            const isWarning = percentage >= 0.8 && !isOver

            const barColor = isOver
              ? 'var(--color-debit)'
              : isWarning
              ? '#ffd43b'
              : 'var(--color-credit)'

            return (
              <div
                key={budget.category}
                style={{
                  padding: '16px 20px',
                  background: 'var(--color-surface)',
                  border: `1px solid ${isOver ? 'rgba(255,107,107,0.3)' : isWarning ? 'rgba(255,212,59,0.3)' : 'var(--color-border)'}`,
                  borderRadius: 10,
                }}
              >
                {/* Top row */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
                  <div>
                    <span style={{ fontSize: 15, fontWeight: 600 }}>{budget.category}</span>
                    {isOver && (
                      <span style={{ marginLeft: 8, fontSize: 11, color: 'var(--color-debit)', background: 'rgba(255,107,107,0.1)', padding: '2px 8px', borderRadius: 20 }}>
                        Over budget
                      </span>
                    )}
                    {isWarning && (
                      <span style={{ marginLeft: 8, fontSize: 11, color: '#ffd43b', background: 'rgba(255,212,59,0.1)', padding: '2px 8px', borderRadius: 20 }}>
                        Near limit
                      </span>
                    )}
                  </div>
                  <div style={{ fontSize: 13, color: 'var(--color-muted)' }}>
                    <span style={{ color: isOver ? 'var(--color-debit)' : 'var(--color-text)', fontWeight: 600 }}>
                      ₹{spent.toLocaleString('en-IN')}
                    </span>
                    {' / '}
                    ₹{budgetLimit.toLocaleString('en-IN')}
                  </div>
                </div>

                {/* Progress bar */}
                <div style={{
                  height: 6,
                  background: 'var(--color-surface-2)',
                  borderRadius: 3,
                  overflow: 'hidden',
                }}>
                  <div style={{
                    height: '100%',
                    width: `${Math.min(percentage * 100, 100)}%`,
                    background: barColor,
                    borderRadius: 3,
                    transition: 'width 0.4s ease',
                  }} />
                </div>

                {/* Bottom row */}
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8, fontSize: 12, color: 'var(--color-muted)' }}>
                  <span>{Math.round(percentage * 100)}% used</span>
                  <span>
                    {isOver
                      ? `₹${(spent - budgetLimit).toLocaleString('en-IN')} over`
                      : `₹${(budgetLimit - spent).toLocaleString('en-IN')} remaining`
                    }
                  </span>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

const inputStyle = {
  padding: '8px 12px',
  background: 'var(--color-surface-2)',
  border: '1px solid var(--color-border)',
  borderRadius: 6,
  color: 'var(--color-text)',
  fontSize: 14,
  outline: 'none',
  height: 40,
}
