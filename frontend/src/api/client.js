import axios from 'axios'

const client = axios.create({
  baseURL: '/',
  
})

// Attach JWT on every request
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Redirect to login on 401
client.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      const token = localStorage.getItem('token')
      if (token) {
        // token exists but server rejected it — expired token
        localStorage.removeItem('token')
        window.location.href = '/'
      }
      // if no token, user logged out intentionally — do nothing
    }
    return Promise.reject(err)
  }
)

export default client