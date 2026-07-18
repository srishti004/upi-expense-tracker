import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const STEPS = [
  {
    number: '01',
    title: 'Copy your SMS',
    description: 'Open any UPI transaction message from your bank — HDFC, Axis, SBI, Kotak, any bank works.',
  },
  {
    number: '02',
    title: 'Paste and parse',
    description: 'Paste it into UPI Tracker. It instantly extracts the amount, merchant, and date.',
  },
  {
    number: '03',
    title: 'See your spending',
    description: 'Your dashboard updates immediately with charts, category breakdowns, and budget alerts.',
  },
]

const FEATURES = [
  {
    icon: '⚡',
    title: 'Instant parsing',
    description: 'Paste one SMS or a hundred at once. Each one is parsed and categorized in under a second.',
  },
  {
    icon: '📊',
    title: 'Spending analytics',
    description: 'See exactly where your money goes — Food, Travel, Shopping, Bills — broken down by month.',
  },
  {
    icon: '🎯',
    title: 'Budget alerts',
    description: 'Set monthly limits per category. Get warned before you overspend, not after.',
  },
  {
    icon: '🏦',
    title: 'All banks supported',
    description: 'Works with every major Indian bank — HDFC, Axis, SBI, ICICI, Kotak, PNB, BOB and more.',
  },
  {
    icon: '🔒',
    title: 'Your data stays yours',
    description: 'Each account is fully isolated. No one else can see your transactions.',
  },
  {
    icon: '✏️',
    title: 'Fix wrong categories',
    description: "If the auto-category is wrong, click it and change it. Your correction is remembered.",
  },
]

export default function LandingPage() {
  const navigate = useNavigate()
  const { user, loading } = useAuth()

  useEffect(() => {
    if (!loading && user) {
      navigate('/parse', { replace: true })
    }
  }, [user, loading])

  if (loading) return null

  return (
    <div style={styles.page}>
      {/* Nav */}
      <nav style={styles.nav}>
        <div style={styles.navLogo}>₹ UPI Tracker</div>
        <div style={styles.navLinks}>
          <button onClick={() => navigate('/login')} style={styles.navLogin}>
            Sign in
          </button>
          <button onClick={() => navigate('/signup')} style={styles.navSignup}>
            Get started free
          </button>
        </div>
      </nav>

      {/* Hero */}
      <section style={styles.hero}>
        <div style={styles.heroBadge}>Built for India 🇮🇳</div>
        <h1 style={styles.heroTitle}>
          Turn your UPI SMS<br />
          into a spending report
        </h1>
        <p style={styles.heroSubtitle}>
          Paste any bank transaction SMS. UPI Tracker extracts the amount,
          merchant, and date — then shows you exactly where your money goes.
          No app permissions. No bank login. Just paste and see.
        </p>
        <div style={styles.heroActions}>
          <button onClick={() => navigate('/signup')} style={styles.heroCta}>
            Start tracking free →
          </button>
          <button onClick={() => navigate('/login')} style={styles.heroSecondary}>
            I have an account
          </button>
        </div>

        {/* SMS demo card */}
        <div style={styles.demoWrapper}>
          <div style={styles.demoCard}>
            <div style={styles.demoLabel}>You paste this SMS</div>
            <div style={styles.smsBubble}>
              <span style={styles.smsText}>
                Rs.450 debited from A/c XX1234 for UPI txn to Zomato on 04-Jun. Ref 123456789. Available balance Rs.12,340.
              </span>
            </div>
          </div>

          <div style={styles.demoArrow}>↓</div>

          <div style={styles.demoCard}>
            <div style={styles.demoLabel}>UPI Tracker extracts this</div>
            <div style={styles.parsedResult}>
              {[
                { label: 'Amount',   value: '₹450.00',  color: 'var(--color-debit)' },
                { label: 'Type',     value: 'Debit',    color: 'var(--color-debit)' },
                { label: 'Merchant', value: 'Zomato',   color: 'var(--color-text)' },
                { label: 'Category', value: 'Food',     color: 'var(--color-accent-light)' },
                { label: 'Date',     value: '04 Jun 2026', color: 'var(--color-text)' },
              ].map(({ label, value, color }) => (
                <div key={label} style={styles.parsedRow}>
                  <span style={styles.parsedLabel}>{label}</span>
                  <span style={{ ...styles.parsedValue, color }}>{value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section style={styles.section}>
        <div style={styles.sectionInner}>
          <p style={styles.eyebrow}>How it works</p>
          <h2 style={styles.sectionTitle}>Three steps to know your spending</h2>
          <div style={styles.stepsGrid}>
            {STEPS.map((step) => (
              <div key={step.number} style={styles.stepCard}>
                <div style={styles.stepNumber}>{step.number}</div>
                <h3 style={styles.stepTitle}>{step.title}</h3>
                <p style={styles.stepDesc}>{step.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section style={{ ...styles.section, background: 'var(--color-surface)' }}>
        <div style={styles.sectionInner}>
          <p style={styles.eyebrow}>Features</p>
          <h2 style={styles.sectionTitle}>Everything you need, nothing you don't</h2>
          <div style={styles.featuresGrid}>
            {FEATURES.map((f) => (
              <div key={f.title} style={styles.featureCard}>
                <div style={styles.featureIcon}>{f.icon}</div>
                <h3 style={styles.featureTitle}>{f.title}</h3>
                <p style={styles.featureDesc}>{f.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section style={styles.ctaSection}>
        <div style={styles.sectionInner}>
          <h2 style={styles.ctaTitle}>Start understanding your spending today</h2>
          <p style={styles.ctaSubtitle}>
            Free to use. No credit card. No bank login required.
          </p>
          <button onClick={() => navigate('/signup')} style={styles.heroCta}>
            Create free account →
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer style={styles.footer}>
        <span style={styles.footerLogo}>₹ UPI Tracker</span>
        <span style={styles.footerNote}>Built for Indian UPI users</span>
      </footer>
    </div>
  )
}

const styles = {
  page: {
    minHeight: '100vh',
    background: 'var(--color-bg)',
    color: 'var(--color-text)',
    fontFamily: "'Inter', system-ui, sans-serif",
  },

  // Nav
  nav: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '20px 48px',
    borderBottom: '1px solid var(--color-border)',
    position: 'sticky',
    top: 0,
    background: 'rgba(15,17,23,0.92)',
    backdropFilter: 'blur(12px)',
    zIndex: 100,
  },
  navLogo: {
    fontSize: 18,
    fontWeight: 700,
    color: 'var(--color-accent-light)',
    letterSpacing: '-0.5px',
  },
  navLinks: {
    display: 'flex',
    gap: 12,
    alignItems: 'center',
  },
  navLogin: {
    padding: '8px 16px',
    background: 'transparent',
    border: '1px solid var(--color-border)',
    borderRadius: 6,
    color: 'var(--color-muted)',
    fontSize: 14,
    cursor: 'pointer',
  },
  navSignup: {
    padding: '8px 16px',
    background: 'var(--color-accent)',
    border: 'none',
    borderRadius: 6,
    color: '#fff',
    fontSize: 14,
    fontWeight: 600,
    cursor: 'pointer',
  },

  // Hero
  hero: {
    textAlign: 'center',
    padding: '80px 24px 64px',
    maxWidth: 800,
    margin: '0 auto',
  },
  heroBadge: {
    display: 'inline-block',
    padding: '4px 14px',
    background: 'rgba(108,99,255,0.15)',
    border: '1px solid rgba(108,99,255,0.3)',
    borderRadius: 20,
    fontSize: 13,
    color: 'var(--color-accent-light)',
    marginBottom: 24,
  },
  heroTitle: {
    fontSize: 52,
    fontWeight: 800,
    lineHeight: 1.15,
    letterSpacing: '-1.5px',
    margin: '0 0 20px',
    background: 'linear-gradient(135deg, #fff 60%, var(--color-accent-light))',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
  },
  heroSubtitle: {
    fontSize: 17,
    color: 'var(--color-muted)',
    lineHeight: 1.7,
    margin: '0 auto 32px',
    maxWidth: 560,
  },
  heroActions: {
    display: 'flex',
    gap: 12,
    justifyContent: 'center',
    marginBottom: 56,
    flexWrap: 'wrap',
  },
  heroCta: {
    padding: '13px 28px',
    background: 'var(--color-accent)',
    border: 'none',
    borderRadius: 8,
    color: '#fff',
    fontSize: 15,
    fontWeight: 700,
    cursor: 'pointer',
    letterSpacing: '-0.2px',
  },
  heroSecondary: {
    padding: '13px 28px',
    background: 'transparent',
    border: '1px solid var(--color-border)',
    borderRadius: 8,
    color: 'var(--color-muted)',
    fontSize: 15,
    cursor: 'pointer',
  },

  // Demo card
  demoWrapper: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: 12,
    maxWidth: 480,
    margin: '0 auto',
  },
  demoCard: {
    width: '100%',
    background: 'var(--color-surface)',
    border: '1px solid var(--color-border)',
    borderRadius: 12,
    padding: 20,
    textAlign: 'left',
  },
  demoLabel: {
    fontSize: 11,
    color: 'var(--color-muted)',
    textTransform: 'uppercase',
    letterSpacing: '0.8px',
    marginBottom: 12,
  },
  smsBubble: {
    background: 'var(--color-surface-2)',
    borderRadius: 8,
    padding: '12px 14px',
  },
  smsText: {
    fontSize: 13,
    color: 'var(--color-muted)',
    lineHeight: 1.6,
    fontFamily: 'monospace',
  },
  parsedResult: {
    display: 'flex',
    flexDirection: 'column',
    gap: 8,
  },
  parsedRow: {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: 14,
    paddingBottom: 8,
    borderBottom: '1px solid var(--color-border)',
  },
  parsedLabel: {
    color: 'var(--color-muted)',
  },
  parsedValue: {
    fontWeight: 600,
  },
  demoArrow: {
    fontSize: 20,
    color: 'var(--color-accent)',
  },

  // Sections
  section: {
    padding: '80px 24px',
  },
  sectionInner: {
    maxWidth: 960,
    margin: '0 auto',
  },
  eyebrow: {
    fontSize: 12,
    textTransform: 'uppercase',
    letterSpacing: '1.5px',
    color: 'var(--color-accent-light)',
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 32,
    fontWeight: 700,
    letterSpacing: '-0.5px',
    margin: '0 0 48px',
  },

  // Steps
  stepsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
    gap: 32,
  },
  stepCard: {
    padding: '0',
  },
  stepNumber: {
    fontSize: 13,
    fontWeight: 700,
    color: 'var(--color-accent)',
    marginBottom: 12,
    fontFamily: 'monospace',
  },
  stepTitle: {
    fontSize: 18,
    fontWeight: 700,
    margin: '0 0 8px',
  },
  stepDesc: {
    fontSize: 14,
    color: 'var(--color-muted)',
    lineHeight: 1.7,
    margin: 0,
  },

  // Features
  featuresGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
    gap: 24,
  },
  featureCard: {
    padding: '24px',
    background: 'var(--color-surface-2)',
    border: '1px solid var(--color-border)',
    borderRadius: 10,
  },
  featureIcon: {
    fontSize: 24,
    marginBottom: 12,
  },
  featureTitle: {
    fontSize: 15,
    fontWeight: 700,
    margin: '0 0 8px',
  },
  featureDesc: {
    fontSize: 13,
    color: 'var(--color-muted)',
    lineHeight: 1.7,
    margin: 0,
  },

  // CTA section
  ctaSection: {
    padding: '80px 24px',
    textAlign: 'center',
    borderTop: '1px solid var(--color-border)',
  },
  ctaTitle: {
    fontSize: 32,
    fontWeight: 700,
    letterSpacing: '-0.5px',
    margin: '0 0 12px',
  },
  ctaSubtitle: {
    fontSize: 15,
    color: 'var(--color-muted)',
    margin: '0 0 32px',
  },

  // Footer
  footer: {
    padding: '24px 48px',
    borderTop: '1px solid var(--color-border)',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  footerLogo: {
    fontSize: 15,
    fontWeight: 700,
    color: 'var(--color-accent-light)',
  },
  footerNote: {
    fontSize: 13,
    color: 'var(--color-muted)',
  },
}