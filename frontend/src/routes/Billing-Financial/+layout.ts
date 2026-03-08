import { redirect } from '@sveltejs/kit';
import type { LayoutLoad } from './$types';

export const load: LayoutLoad = async ({ url }) => {
	// This runs client-side — check localStorage for token
	if (typeof localStorage === 'undefined') return { user: null };

	const token = localStorage.getItem('access_token');
	if (!token) {
		throw redirect(302, '/login');
	}

	// Decode JWT payload (no verify needed client-side, server verifies)
	try {
		const payload = JSON.parse(atob(token.split('.')[1]));
		// Check expiry
		if (payload.exp * 1000 < Date.now()) {
			localStorage.removeItem('access_token');
			throw redirect(302, '/login');
		}
		return {
			user: {
				id: payload.sub,
				email: payload.email,
				role: payload.role,
				full_name: payload.full_name
			}
		};
	} catch {
		throw redirect(302, '/login');
	}
};
