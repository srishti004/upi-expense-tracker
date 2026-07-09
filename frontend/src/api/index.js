import client from './client'

// ── Auth ───────────────────────────────────────────────
export const signup = (data) =>
  client.post('/auth/signup', data).then((r) => r.data)

export const login = (email, password) => {
  const formData = new FormData()
  formData.append('username', email)  // OAuth2 spec uses "username" even for email
  formData.append('password', password)
  return client.post('/auth/login', formData).then((r) => r.data)
}
export const getMe = () =>
  client.get('/auth/me').then((r) => r.data)

// ── SMS ────────────────────────────────────────────────
export const parseSMS = (raw_sms) =>
  client.post('/api/sms/parse', { raw_sms }).then((r) => r.data)

export const parseBulkSMS = (messages) =>
  client.post('/api/sms/parse/bulk', { messages }).then((r) => r.data)

// ── Transactions ───────────────────────────────────────
export const getTransactions = (params = {}) =>
  client.get('/api/transactions', { params }).then((r) => r.data)

export const updateCategory = (id, category) =>
  client.put(`/api/transactions/${id}/category`, { category }).then((r) => r.data)

// ── Budgets ────────────────────────────────────────────
export const getBudgets = () =>
  client.get('/api/budgets').then((r) => r.data)

export const upsertBudget = (data) =>
  client.post('/api/budgets', data).then((r) => r.data)

export const updateBudget = (id, data) =>
  client.put(`/api/budgets/${id}`, data).then((r) => r.data)

export const getBudgetSummary = () =>
  client.get('/api/budgets/summary').then((r) => r.data)

// ── Analytics ──────────────────────────────────────────
export const getDashboard = () =>
  client.get('/api/analytics/dashboard').then((r) => r.data)

export const getSpending = (from_date, to_date) =>
  client.get('/api/analytics/spending', { params: { from_date, to_date } }).then((r) => r.data)

export const getMonthlyTrend = (months = 6) =>
  client.get('/api/analytics/monthly-trend', { params: { months } }).then((r) => r.data)

export const getCategoryDrilldown = (name, month, year) =>
  client.get(`/api/analytics/category/${name}`, { params: { month, year } }).then((r) => r.data)