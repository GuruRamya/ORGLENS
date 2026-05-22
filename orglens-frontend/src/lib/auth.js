import axios from 'axios'

const BASE = '/api/auth'

export async function register(email, password, fullName) {
  const { data } = await axios.post(`${BASE}/register`, {
    email, password, full_name: fullName
  })
  localStorage.setItem('token', data.access_token)
  localStorage.setItem('user', JSON.stringify({ id: data.user_id, email: data.email }))
  return data
}

export async function login(email, password) {
  const formData = new URLSearchParams()
  formData.append('username', email)
  formData.append('password', password)
  const { data } = await axios.post(`${BASE}/token`, formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  })
  localStorage.setItem('token', data.access_token)
  localStorage.setItem('user', JSON.stringify({ id: data.user_id, email: data.email }))
  return data
}

export function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  window.location.href = '/login'
}

export function getToken() {
  return localStorage.getItem('token')
}

export function getUser() {
  const raw = localStorage.getItem('user')
  return raw ? JSON.parse(raw) : null
}

export function isAuthenticated() {
  return !!getToken()
}