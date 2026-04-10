const ACCESS_KEY = 'access_token'
const REFRESH_KEY = 'refresh_token'

export const authClient = {
  setTokens(access: string, refresh: string) {
    if (typeof window === 'undefined') return
    localStorage.setItem(ACCESS_KEY, access)
    localStorage.setItem(REFRESH_KEY, refresh)
  },
  getAccess(): string | null {
    if (typeof window === 'undefined') return null
    return localStorage.getItem(ACCESS_KEY)
  },
  getRefresh(): string | null {
    if (typeof window === 'undefined') return null
    return localStorage.getItem(REFRESH_KEY)
  },
  clear() {
    if (typeof window === 'undefined') return
    localStorage.removeItem(ACCESS_KEY)
    localStorage.removeItem(REFRESH_KEY)
  },
}
