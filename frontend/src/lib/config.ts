import { PUBLIC_API_URL } from '$env/static/public';

export const API = PUBLIC_API_URL || 'http://localhost:8000';

export function getToken(): string {
  if (typeof localStorage === 'undefined') return '';
  return localStorage.getItem('access_token') ?? '';
}

export function authHeaders(): Record<string, string> {
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${getToken()}`
  };
}






































































