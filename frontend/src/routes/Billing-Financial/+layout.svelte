<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	export let data: { user: any };

	let currentTime = '';
	let currentDate = '';
	let sidebarCollapsed = false;

	function updateTime() {
		const now = new Date();
		currentDate = now.toLocaleDateString('en-US', {
			month: 'long',
			day: 'numeric',
			year: 'numeric'
		});
		currentTime = now.toLocaleTimeString('en-US', {
			hour: '2-digit',
			minute: '2-digit',
			second: '2-digit'
		});
	}

	onMount(() => {
		updateTime();
		const interval = setInterval(updateTime, 1000);
		if (window.innerWidth < 1024) sidebarCollapsed = true;
		return () => clearInterval(interval);
	});

	function logout() {
		localStorage.removeItem('access_token');
		localStorage.removeItem('role');
		localStorage.removeItem('user');
		goto('/login');
	}

	$: role = data?.user?.role ?? '';
	$: fullName = data?.user?.full_name ?? '';
	$: email = data?.user?.email ?? '';

	let receptionistOpen = true;
	let billingOpen = true;
</script>

<svelte:head>
	<link
		href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&display=swap"
		rel="stylesheet"
	/>
	<meta name="viewport" content="width=device-width, initial-scale=1.0" />
</svelte:head>

<div class="layout" class:collapsed={sidebarCollapsed}>
	<aside class="sidebar">
		<button
			class="toggle-btn"
			on:click={() => (sidebarCollapsed = !sidebarCollapsed)}
			title="Toggle sidebar"
		>
			<svg
				viewBox="0 0 24 24"
				fill="none"
				stroke="currentColor"
				stroke-width="2"
				width="18"
				height="18"
			>
				{#if sidebarCollapsed}
					<path d="M9 18l6-6-6-6" />
				{:else}
					<path d="M15 18l-6-6 6-6" />
				{/if}
			</svg>
		</button>
		<div class="profile">
			<div class="avatar">
				<svg viewBox="0 0 24 24" fill="#aaa" width="28" height="28">
					<path
						d="M12 12c2.7 0 4.8-2.1 4.8-4.8S14.7 2.4 12 2.4 7.2 4.5 7.2 7.2 9.3 12 12 12zm0 2.4c-3.2 0-9.6 1.6-9.6 4.8v2.4h19.2v-2.4c0-3.2-6.4-4.8-9.6-4.8z"
					/>
				</svg>
			</div>
			{#if !sidebarCollapsed}
				<p class="name">{fullName}</p>
				<p class="email">{email}</p>
			{/if}
		</div>
		<nav class="nav">
			{#if !sidebarCollapsed}
				<a
					href="/Billing-Financial/admin-dashboard-overview"
					class="nav-top-link"
					class:active={$page.url.pathname === '/Billing-Financial/admin-dashboard-overview'}
				>
					<svg
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="1.5"
						width="15"
						height="15"
						><rect x="3" y="3" width="7" height="7" /><rect
							x="14"
							y="3"
							width="7"
							height="7"
						/><rect x="3" y="14" width="7" height="7" /><rect
							x="14"
							y="14"
							width="7"
							height="7"
						/></svg
					>
					Admin Dashboard Overview
				</a>
			{/if}
			<button class="nav-group" on:click={() => (receptionistOpen = !receptionistOpen)}>
				{#if !sidebarCollapsed}
					<span>Receptionist Dashboard</span>
					<span class="chevron" class:open={receptionistOpen}>›</span>
				{:else}
					<svg
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="1.5"
						width="16"
						height="16"
						><path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg
					>
				{/if}
			</button>
			{#if receptionistOpen && !sidebarCollapsed}
				<div class="nav-children">
					<a
						href="/Billing-Financial/dashboard"
						class="nav-child"
						class:active={$page.url.pathname === '/Billing-Financial/'}>Dashboard</a
					>
					<a
						href="/Billing-Financial/appointments"
						class="nav-child"
						class:active={$page.url.pathname.includes('appointments')}
						>Appointments and Scheduling</a
					>
					<a
						href="/Billing-Financial/emr"
						class="nav-child"
						class:active={$page.url.pathname.includes('emr')}>EMR</a
					>
					<a
						href="/Billing-Financial/inventory"
						class="nav-child"
						class:active={$page.url.pathname.includes('inventory')}>Inventory</a
					>
				</div>
			{/if}
			<button class="nav-group" on:click={() => (billingOpen = !billingOpen)}>
				{#if !sidebarCollapsed}
					<span>Billing and Financial Dashboard</span>
					<span class="chevron" class:open={billingOpen}>›</span>
				{:else}
					<svg
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="1.5"
						width="16"
						height="16"
						><path
							d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2"
						/></svg
					>
				{/if}
			</button>
			{#if billingOpen && !sidebarCollapsed}
				<div class="nav-children">
					<a
						href="/Billing-Financial/dashboard"
						class="nav-child"
						class:active={$page.url.pathname === '/Billing-Financial/dashboard'}>Dashboard</a
					>
					<a
						href="/Billing-Financial/billing"
						class="nav-child"
						class:active={$page.url.pathname.includes('billing')}>Billing</a
					>
					<a
						href="/Billing-Financial/financial-report"
						class="nav-child"
						class:active={$page.url.pathname.includes('financial-report')}>Financial Report</a
					>
				</div>
			{/if}
			<div class="nav-bottom">
				<a
					href="/Billing-Financial/reports"
					class="nav-item"
					class:active={$page.url.pathname.includes('reports')}
					title="Reports"
				>
					<svg
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="1.5"
						width="15"
						height="15"
						><path
							d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
						/></svg
					>
					{#if !sidebarCollapsed}<span>Reports</span>{/if}
				</a>
				<a
					href="/Billing-Financial/settings"
					class="nav-item"
					class:active={$page.url.pathname.includes('settings')}
					title="Settings"
				>
					<svg
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="1.5"
						width="15"
						height="15"
						><path
							d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
						/><circle cx="12" cy="12" r="3" /></svg
					>
					{#if !sidebarCollapsed}<span>Settings</span>{/if}
				</a>
				<button class="nav-logout" on:click={logout} title="Logout">
					<svg
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="1.5"
						width="15"
						height="15"
						><path
							d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
						/></svg
					>
					{#if !sidebarCollapsed}<span>Logout</span>{/if}
				</button>
			</div>
		</nav>
	</aside>
	<div class="main">
		<header class="topbar">
			<div class="brand-left">
				<img src="/Clinic-Image.png" alt="Logo" class="brand-logo" />
				<div class="brand-text">
					<p class="brand-name">Dr. Rosario Veterinary Clinic</p>
					<p class="brand-sub">Pet Grooming Center</p>
				</div>
			</div>
			<p class="datetime">{currentDate} &nbsp;&nbsp; {currentTime}</p>
		</header>

		<div class="content">
			<slot />
		</div>
	</div>
</div>

<style>
	*,
	*::before,
	*::after {
		box-sizing: border-box;
		margin: 0;
		padding: 0;
	}
	:global(html) {
		font-size: clamp(13px, 1.1vw, 16px);
	}
	:global(body) {
		font-family: 'DM Sans', sans-serif;
		background: #f5f7f5;
		overflow: hidden;
	}
	.layout {
		display: flex;
		height: 100vh;
		width: 100vw;
		overflow: hidden;
	}
	.sidebar {
		width: clamp(180px, 16vw, 240px);
		flex-shrink: 0;
		background: #fff;
		border-right: 1px solid #e5e7eb;
		display: flex;
		flex-direction: column;
		overflow-y: auto;
		overflow-x: hidden;
		transition: width 0.25s ease;
		position: relative;
	}
	.layout.collapsed .sidebar {
		width: clamp(48px, 5vw, 64px);
	}
	.toggle-btn {
		position: absolute;
		top: 0.6rem;
		right: 0.5rem;
		z-index: 10;
		background: #f3f4f6;
		border: 1px solid #e5e7eb;
		border-radius: 6px;
		padding: 0.3rem;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		color: #6b7280;
		transition: background 0.15s;
	}
	.toggle-btn:hover {
		background: #e5e7eb;
	}
	.profile {
		padding: clamp(0.75rem, 2vh, 1.5rem) 0.75rem clamp(0.5rem, 1.5vh, 1rem);
		display: flex;
		flex-direction: column;
		align-items: center;
		border-bottom: 1px solid #e5e7eb;
		min-height: 80px;
		padding-top: 2.5rem;
	}
	.avatar {
		width: clamp(40px, 4vw, 56px);
		height: clamp(40px, 4vw, 56px);
		border-radius: 50%;
		background: #e5e7eb;
		display: flex;
		align-items: center;
		justify-content: center;
		margin-bottom: 0.4rem;
		flex-shrink: 0;
	}
	.name {
		font-weight: 600;
		font-size: clamp(0.7rem, 0.85vw, 0.9rem);
		color: #111;
		text-align: center;
		word-break: break-word;
	}
	.email {
		font-size: clamp(0.6rem, 0.7vw, 0.75rem);
		color: #6b7280;
		text-align: center;
		margin-top: 2px;
		word-break: break-all;
	}

	.nav {
		display: flex;
		flex-direction: column;
		padding: 0.5rem 0;
		gap: 2px;
		flex: 1;
	}

	.nav-top-link {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 0.75rem;
		margin: 0.25rem 0.4rem;
		font-size: clamp(0.72rem, 0.8vw, 0.85rem);
		font-weight: 600;
		color: white;
		background: #0a4f29;
		border-radius: 7px;
		text-decoration: none;
		transition: background 0.15s;
	}
	.nav-top-link:hover {
		background: #0d6334;
	}
	.nav-top-link.active {
		background: #0d6334;
	}

	.nav-group {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0.5rem 0.75rem;
		font-size: clamp(0.68rem, 0.75vw, 0.82rem);
		font-weight: 500;
		color: #111;
		background: #f3f4f6;
		border: 1px solid #e5e7eb;
		border-radius: 7px;
		margin: 0.2rem 0.4rem;
		cursor: pointer;
		transition: background 0.15s;
		text-align: left;
		gap: 0.25rem;
	}
	.nav-group:hover {
		background: #e5e7eb;
	}
	.chevron {
		font-size: 1rem;
		transition: transform 0.2s;
		transform: rotate(90deg);
		flex-shrink: 0;
	}
	.chevron.open {
		transform: rotate(270deg);
	}

	.nav-children {
		display: flex;
		flex-direction: column;
		padding-left: 0.4rem;
		gap: 1px;
	}
	.nav-child {
		display: block;
		padding: 0.4rem 0.75rem;
		font-size: clamp(0.65rem, 0.72vw, 0.78rem);
		color: #6b7280;
		text-decoration: none;
		border-radius: 6px;
		margin: 0 0.4rem;
		transition:
			background 0.15s,
			color 0.15s;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}
	.nav-child:hover {
		background: #f0fff0;
		color: #0a4f29;
	}
	.nav-child.active {
		color: #0a4f29;
		font-weight: 600;
		background: #f0fff0;
	}

	.nav-bottom {
		margin-top: auto;
		display: flex;
		flex-direction: column;
		gap: 2px;
		padding: 0.5rem 0;
		border-top: 1px solid #f3f4f6;
	}
	.nav-item {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 0.75rem;
		font-size: clamp(0.68rem, 0.75vw, 0.82rem);
		color: #374151;
		text-decoration: none;
		border-radius: 6px;
		margin: 0 0.4rem;
		transition: background 0.15s;
		white-space: nowrap;
	}
	.nav-item:hover {
		background: #f0fff0;
		color: #0a4f29;
	}
	.nav-item.active {
		background: #f0fff0;
		color: #0a4f29;
		font-weight: 600;
	}

	.nav-logout {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin: 0 0.4rem;
		padding: 0.5rem 0.75rem;
		background: white;
		border: 1.5px solid #e5e7eb;
		border-radius: 7px;
		font-size: clamp(0.68rem, 0.75vw, 0.82rem);
		font-weight: 500;
		cursor: pointer;
		color: #374151;
		transition: background 0.15s;
		font-family: inherit;
		white-space: nowrap;
	}
	.nav-logout:hover {
		background: #fef2f2;
		color: #b91c1c;
		border-color: #fecaca;
	}

	.main {
		flex: 1;
		display: flex;
		flex-direction: column;
		min-width: 0;
		background-color: #0a4f29;
		max-height: 100vh;
		overflow-y: auto;
	}

	.topbar {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: clamp(0.5rem, 1.2vh, 0.85rem) clamp(0.75rem, 2vw, 1.5rem);
		background: white;
		border-bottom: 1px solid #e5e7eb;
		width: 100%;
		position: sticky;
		top: 0;
		z-index: 50;
		flex-shrink: 0;
	}
	.brand-left {
		display: flex;
		align-items: center;
		gap: clamp(0.5rem, 1vw, 0.85rem);
	}
	.brand-logo {
		width: clamp(32px, 3.5vw, 46px);
		height: clamp(32px, 3.5vw, 46px);
		border-radius: 50%;
		flex-shrink: 0;
	}
	.brand-name {
		font-weight: 700;
		font-size: clamp(0.78rem, 1vw, 1rem);
		color: #111;
		white-space: nowrap;
	}
	.brand-sub {
		font-size: clamp(0.62rem, 0.72vw, 0.75rem);
		color: #6b7280;
	}
	.datetime {
		font-size: clamp(0.65rem, 0.78vw, 0.82rem);
		color: #6b7280;
		white-space: nowrap;
		flex-shrink: 0;
	}

	.content {
		padding: clamp(0.75rem, 2vh, 1.5rem) clamp(0.75rem, 2vw, 1.5rem);
		flex: 1;
	}

	@media (max-width: 1280px) {
		:global(html) {
			font-size: 14px;
		}
	}
	@media (max-width: 1024px) {
		.sidebar {
			width: clamp(48px, 5vw, 64px);
		}
		.layout:not(.collapsed) .sidebar {
			width: clamp(180px, 16vw, 220px);
		}
	}
	@media (max-width: 768px) {
		:global(html) {
			font-size: 13px;
		}
		.sidebar {
			position: fixed;
			left: 0;
			top: 0;
			bottom: 0;
			z-index: 100;
			box-shadow: 4px 0 12px rgba(0, 0, 0, 0.15);
		}
		.layout.collapsed .sidebar {
			width: 0;
			overflow: hidden;
		}
		.main {
			margin-left: 0;
		}
		.topbar {
			padding: 0.5rem 0.75rem;
		}
		.content {
			padding: 0.75rem;
		}
	}
	@media (max-width: 480px) {
		:global(html) {
			font-size: 12px;
		}
		.brand-sub {
			display: none;
		}
	}
</style>
