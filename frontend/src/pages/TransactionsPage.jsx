import { useState, useEffect } from 'react'
import { getTransactions, updateCategory } from '../api'
import client from '../api/client'

const CATEGORIES = [
  'Food', 'Transport', 'Shopping', 'Entertainment', 'Bills',
  'Health', 'Groceries', 'Education', 'Travel', 'Transfers',
  'Subscriptions', 'Uncategorized'
]

const MONTHS = [
  { value: 1,  label: 'January' },  { value: 2,  label: 'February' },
  { value: 3,  label: 'March' },    { value: 4,  label: 'April' },
  { value: 5,  label: 'May' },      { value: 6,  label: 'June' },
  { value: 7,  label: 'July' },     { value: 8,  label: 'August' },
  { value: 9,  label: 'September' },{ value: 10, label: 'October' },
  { value: 11, label: 'November' }, { value: 12, label: 'December' },
]

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Filters
  const [month, setMonth] = useState('')
  const [year, setYear] = useState(new Date().getFullYear())
  const [category, setCategory] = useState('')

  // Pagination
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const limit = 20

  // Category edit
  const [editingId, setEditingId] = useState(null)
  const [editingCategory, setEditingCategory] = useState('')

  // Recategorize
  const [recatLoading, setRecatLoading] = useState(false)
  const [recatMsg, setRecatMsg] = useState('')

  const fetchTransactions = async () => {
    setLoading(true)
    setError('')
    try {
      const params = { page, page_size: limit }
      if (month) params.month = month
      if (month) params.year = year
      if (category) params.category = category

      const data = await getTransactions(params)
      setTransactions(data.transactions)
      setTotal(data.total)
    } catch (err) {
      setError('Failed to load transactions')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchTransactions()
  }, [page, month, year, category])

  const handleCategoryUpdate = async (id) => {
    try {
      await updateCategory(id, editingCategory)
      setEditingId(null)
      fetchTransactions()
    } catch (err) {
      alert('Failed to update category')
    }
  }

  const handleRecategorize = async () => {
    setRecatLoading(true)
    setRecatMsg('')
    try {
      const data = await client.post('/api/transactions/recategorize').then(r => r.data)
      setRecatMsg(`✓ ${data.message}`)
      fetchTransactions()
    } catch (err) {
      setRecatMsg('Failed to recategorize')
    } finally {
      setRecatLoading(false)
    }
  }

  const totalPages = Math.ceil(total / limit)

  return (
    <div>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
        <h2 style={{ margin: 0, fontSize: 22, fontWeight: 700 }}>Transactions</h2>
        <button
          onClick={handleRecategorize}
          disabled={recatLoading}
          style={{
            padding: '7px 14px',
            background: 'transparent',
            border: '1px solid var(--color-border)',
            borderRadius: 6,
            color: 'var(--color-muted)',
            fontSize: 13,
            cursor: recatLoading ? 'not-allowed' : 'pointer',
          }}
        >
          {recatLoading ? 'Updating…' : '↻ Fix categories'}
        </button>
      </div>

      <p style={{ margin: '0 0 16px', color: 'var(--color-muted)', fontSize: 14 }}>
        {total} transactions found
      </p>

      {recatMsg && (
        <p style={{ fontSize: 13, color: 'var(--color-credit)', margin: '0 0 16px' }}>
          {recatMsg}
        </p>
      )}

      {/* Filters */}
      <div style={{ display: 'flex', gap: 12, marginBottom: 20, flexWrap: 'wrap' }}>
        <select
          value={month}
          onChange={(e) => { setMonth(e.target.value); setPage(1) }}
          style={selectStyle}
        >
          <option value="">All months</option>
          {MONTHS.map((m) => (
            <option key={m.value} value={m.value}>{m.label}</option>
          ))}
        </select>

        {month && (
          <input
            type="number"
            value={year}
            onChange={(e) => { setYear(e.target.value); setPage(1) }}
            placeholder="Year"
            style={{ ...selectStyle, width: 90 }}
          />
        )}

        <select
          value={category}
          onChange={(e) => { setCategory(e.target.value); setPage(1) }}
          style={selectStyle}
        >
          <option value="">All categories</option>
          {CATEGORIES.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>

        {(month || category) && (
          <button
            onClick={() => { setMonth(''); setCategory(''); setPage(1) }}
            style={clearBtnStyle}
          >
            Clear filters
          </button>
        )}
      </div>

      {/* Error */}
      {error && (
        <div style={{
          padding: '10px 14px',
          background: 'rgba(255,107,107,0.1)',
          border: '1px solid rgba(255,107,107,0.3)',
          borderRadius: 6,
          color: 'var(--color-debit)',
          fontSize: 14,
          marginBottom: 16,
        }}>
          {error}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div style={{ color: 'var(--color-muted)', fontSize: 14, padding: '20px 0' }}>
          Loading transactions…
        </div>
      )}

      {/* Empty state */}
      {!loading && transactions.length === 0 && (
        <div style={{ textAlign: 'center', padding: '48px 0', color: 'var(--color-muted)' }}>
          <div style={{ fontSize: 32, marginBottom: 12 }}>📭</div>
          <p style={{ fontSize: 15, marginBottom: 4 }}>No transactions found</p>
          <p style={{ fontSize: 13 }}>Try changing filters or parse some SMS messages first</p>
        </div>
      )}

      {/* Transactions list */}
      {!loading && transactions.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {transactions.map((txn) => (
            <div
              key={txn.id}
              style={{
                padding: '14px 16px',
                background: 'var(--color-surface)',
                border: '1px solid var(--color-border)',
                borderRadius: 8,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: 12,
              }}
            >
              {/* Left — merchant + date */}
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 4 }}>
                  {txn.merchant || 'Unknown'}
                </div>
                <div style={{ fontSize: 12, color: 'var(--color-muted)' }}>
                  {txn.txn_date} · {txn.account_masked || 'N/A'}
                </div>
              </div>

              {/* Middle — category (editable) */}
              <div style={{ minWidth: 140 }}>
                {editingId === txn.id ? (
                  <div style={{ display: 'flex', gap: 6 }}>
                    <select
                      value={editingCategory}
                      onChange={(e) => setEditingCategory(e.target.value)}
                      style={{ ...selectStyle, fontSize: 12, padding: '4px 8px' }}
                    >
                      {CATEGORIES.map((c) => (
                        <option key={c} value={c}>{c}</option>
                      ))}
                    </select>
                    <button
                      onClick={() => handleCategoryUpdate(txn.id)}
                      style={{
                        padding: '4px 8px',
                        background: 'var(--color-accent)',
                        color: '#fff',
                        border: 'none',
                        borderRadius: 4,
                        fontSize: 12,
                        cursor: 'pointer',
                      }}
                    >
                      Save
                    </button>
                    <button
                      onClick={() => setEditingId(null)}
                      style={{
                        padding: '4px 8px',
                        background: 'transparent',
                        color: 'var(--color-muted)',
                        border: '1px solid var(--color-border)',
                        borderRadius: 4,
                        fontSize: 12,
                        cursor: 'pointer',
                      }}
                    >
                      ✕
                    </button>
                  </div>
                ) : (
                  <span
                    onClick={() => { setEditingId(txn.id); setEditingCategory(txn.category) }}
                    style={{
                      fontSize: 12,
                      padding: '3px 10px',
                      background: 'var(--color-surface-2)',
                      border: '1px solid var(--color-border)',
                      borderRadius: 20,
                      color: 'var(--color-muted)',
                      cursor: 'pointer',
                    }}
                    title="Click to edit category"
                  >
                    {txn.category}
                  </span>
                )}
              </div>

              {/* Right — amount */}
              <div style={{
                fontWeight: 700,
                fontSize: 15,
                color: txn.txn_type === 'debit' ? 'var(--color-debit)' : 'var(--color-credit)',
                whiteSpace: 'nowrap',
              }}>
                {txn.txn_type === 'debit' ? '−' : '+'}₹{txn.amount}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div style={{ display: 'flex', gap: 8, marginTop: 20, alignItems: 'center' }}>
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            style={pageBtnStyle(page === 1)}
          >
            ← Prev
          </button>
          <span style={{ fontSize: 13, color: 'var(--color-muted)' }}>
            Page {page} of {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            style={pageBtnStyle(page === totalPages)}
          >
            Next →
          </button>
        </div>
      )}
    </div>
  )
}

const selectStyle = {
  padding: '8px 12px',
  background: 'var(--color-surface)',
  border: '1px solid var(--color-border)',
  borderRadius: 6,
  color: 'var(--color-text)',
  fontSize: 13,
  cursor: 'pointer',
  outline: 'none',
}

const clearBtnStyle = {
  padding: '8px 12px',
  background: 'transparent',
  border: '1px solid var(--color-border)',
  borderRadius: 6,
  color: 'var(--color-muted)',
  fontSize: 13,
  cursor: 'pointer',
}

const pageBtnStyle = (disabled) => ({
  padding: '8px 14px',
  background: disabled ? 'var(--color-surface)' : 'var(--color-accent)',
  border: '1px solid var(--color-border)',
  borderRadius: 6,
  color: disabled ? 'var(--color-muted)' : '#fff',
  fontSize: 13,
  cursor: disabled ? 'not-allowed' : 'pointer',
  opacity: disabled ? 0.5 : 1,
})