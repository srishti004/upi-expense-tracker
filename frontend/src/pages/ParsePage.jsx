import { useState } from 'react'
import { parseSMS, parseBulkSMS } from '../api'

export default function ParsePage() {
  const [sms, setSms] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setResult(null)
    setLoading(true)
    try {
      const messages = sms
        .split('\n\n')
        .map((s) => s.trim())
        .filter((s) => s)

      if (messages.length === 1) {
        const data = await parseSMS(messages[0])
        setResult({ type: 'single', data })
      } else {
        const data = await parseBulkSMS(messages)
        setResult({ type: 'bulk', data })
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to parse SMS')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 640 }}>
      {/* Header */}
      <h2 style={{ margin: '0 0 4px', fontSize: 22, fontWeight: 700 }}>
        Parse UPI SMS
      </h2>
      <p style={{ margin: '0 0 24px', color: 'var(--color-muted)', fontSize: 14 }}>
        Paste one SMS or multiple (separated by a blank line) — detected automatically
      </p>

      {/* Input form */}
      <form onSubmit={handleSubmit}>
        <textarea
          value={sms}
          onChange={(e) => setSms(e.target.value)}
          placeholder={
            'Single SMS:\nRs.450 debited from A/c XX1234 for UPI txn to Zomato on 04-Apr.\n\n' +
            'Or multiple (blank line between each):\nRs.450 debited from A/c XX1234 for UPI txn to Zomato on 04-Apr.\n\n' +
            'INR 200 debited from A/c XX5678 for UPI txn to Swiggy on 05-Apr.'
          }
          required
          rows={6}
          style={{
            width: '100%',
            padding: '12px',
            background: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            borderRadius: 8,
            color: 'var(--color-text)',
            fontSize: 13,
            resize: 'vertical',
            outline: 'none',
            fontFamily: 'inherit',
            lineHeight: 1.6,
          }}
        />

        <button
          type="submit"
          disabled={loading}
          style={{
            marginTop: 12,
            padding: '10px 24px',
            background: 'var(--color-accent)',
            color: '#fff',
            border: 'none',
            borderRadius: 6,
            fontSize: 14,
            fontWeight: 600,
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.7 : 1,
          }}
        >
          {loading ? 'Parsing…' : 'Parse SMS'}
        </button>
      </form>

      {/* Error */}
      {error && (
        <div style={{
          marginTop: 16,
          padding: '10px 14px',
          background: 'rgba(255,107,107,0.1)',
          border: '1px solid rgba(255,107,107,0.3)',
          borderRadius: 6,
          color: 'var(--color-debit)',
          fontSize: 14,
        }}>
          {error}
        </div>
      )}

      {/* Single result */}
      {result && result.type === 'single' && (
        <div style={{
          marginTop: 20,
          padding: 20,
          background: 'var(--color-surface)',
          border: '1px solid var(--color-border)',
          borderRadius: 8,
        }}>
          <h3 style={{ margin: '0 0 16px', fontSize: 15, fontWeight: 600 }}>
            Parsed Result
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {[
              { label: 'Amount',   value: result.data.amount ? `₹${result.data.amount}` : '—' },
              { label: 'Type',     value: result.data.txn_type || '—' },
              { label: 'Merchant', value: result.data.merchant || '—' },
              { label: 'Category', value: result.data.category || '—' },
              { label: 'Account',  value: result.data.account || '—' },
            ].map(({ label, value }) => (
              <div
                key={label}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  fontSize: 14,
                  paddingBottom: 8,
                  borderBottom: '1px solid var(--color-border)',
                }}
              >
                <span style={{ color: 'var(--color-muted)' }}>{label}</span>
                <span style={{
                  color: label === 'Type'
                    ? result.data.txn_type === 'debit'
                      ? 'var(--color-debit)'
                      : 'var(--color-credit)'
                    : 'var(--color-text)',
                  fontWeight: label === 'Amount' ? 600 : 400,
                }}>
                  {value}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Bulk results */}
      {result && result.type === 'bulk' && (
        <div style={{ marginTop: 20 }}>

          {/* Summary bar */}
          <div style={{
            padding: '12px 16px',
            background: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            borderRadius: 8,
            marginBottom: 12,
            fontSize: 14,
            display: 'flex',
            gap: 16,
          }}>
            <span style={{ color: 'var(--color-muted)' }}>
              {result.data.total} messages processed
            </span>
            <span style={{ color: 'var(--color-credit)', fontWeight: 600 }}>
              ✓ {result.data.saved} saved
            </span>
            <span style={{ color: 'var(--color-debit)', fontWeight: 600 }}>
              ✗ {result.data.failed} failed
            </span>
          </div>

          {/* Per message results */}
          {result.data.results.map((item, index) => (
            <div
              key={index}
              style={{
                padding: '12px 16px',
                background: 'var(--color-surface)',
                border: `1px solid ${item.success
                  ? 'rgba(81,207,102,0.25)'
                  : 'rgba(255,107,107,0.25)'}`,
                borderRadius: 8,
                marginBottom: 8,
              }}
            >
              {/* Status + main info */}
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                fontSize: 13,
              }}>
                <span style={{
                  color: item.success ? 'var(--color-credit)' : 'var(--color-debit)',
                  fontWeight: 600,
                  fontSize: 15,
                }}>
                  {item.success ? '✓' : '✗'}
                </span>
                <span style={{ color: item.success ? 'var(--color-text)' : 'var(--color-debit)' }}>
                  {item.success
                    ? `₹${item.transaction.amount} · ${item.transaction.merchant || 'Unknown'} · ${item.transaction.category}`
                    : item.error
                  }
                </span>
              </div>

              {/* Raw SMS preview */}
              <div style={{
                marginTop: 6,
                color: 'var(--color-muted)',
                fontSize: 12,
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}>
                {item.raw_sms}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}