<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	const API = 'http://localhost:8000';

	function getToken() {
		return typeof localStorage !== 'undefined' ? localStorage.getItem('access_token') : '';
	}
	function authHeaders() {
		return { 'Content-Type': 'application/json', Authorization: `Bearer ${getToken()}` };
	}

	let stats = {
		totalOwners: 0,
		ownersDiff: 0,
		totalPatients: 0,
		dogCount: 0,
		catCount: 0,
		todayAppointments: 0,
		confirmed: 0,
		waiting: 0,
		cancelled: 0,
		lowStock: 0,
		expiringMeds: 0,
		todayRevenue: 0,
		revenueDiff: 0
	};

	let auditLogs: any[] = [];
	let expenses: any[] = [];
	let totalDeductions = 0;
	let loading = true;

	const peso = (n: number) =>
		'₱' + n.toLocaleString('en-PH', { minimumFractionDigits: 0, maximumFractionDigits: 0 });

	function formatDateTime(dateStr: string) {
		const d = new Date(dateStr);
		return (
			d.toLocaleDateString('en-PH', { year: 'numeric', month: '2-digit', day: '2-digit' }) +
			' ' +
			d.toLocaleTimeString('en-PH', { hour: '2-digit', minute: '2-digit', hour12: false })
		);
	}

	function actionIcon(icon: string) {
		switch (icon) {
			case 'add': return '+';
			case 'edit': return '✎';
			case 'bill': return '₱';
			case 'cancel': return '✕';
			case 'check': return '✓';
			case 'delete': return '🗑';
			case 'warning': return '⚠';
			default: return '•';
		}
	}

	function actionColor(icon: string) {
		switch (icon) {
			case 'add': return '#0A4F29';
			case 'edit': return '#2563eb';
			case 'bill': return '#7c3aed';
			case 'cancel': return '#dc2626';
			case 'check': return '#16a34a';
			case 'delete': return '#dc2626';
			case 'warning': return '#d97706';
			default: return '#6b7280';
		}
	}

	function expenseIcon(cat: string) {
		switch (cat) {
			case 'Medical Supplies': return '💊';
			case 'Staff Salaries': return '👤';
			case 'Utilities': return '⚡';
			case 'Rent': return '🏠';
			case 'Equipment': return '🔧';
			default: return '📋';
		}
	}

	async function fetchAll() {
		loading = true;
		try {
			const res = await fetch(`${API}/dashboard/admin-stats`, { headers: authHeaders() });
			if (res.ok) {
				const d = await res.json();
				stats = { ...stats, ...d.stats };
				auditLogs = d.audit_logs || [];
				expenses = d.expenses || [];
				totalDeductions = expenses.reduce((s: number, e: any) => s + (e.Amount || 0), 0);
			}
		} catch (e) {
			console.error(e);
		} finally {
			loading = false;
		}
	}

	onMount(fetchAll);
</script>

<div class="flex flex-col gap-6">

	<!-- Page Header -->
	<div class="flex items-start justify-between">
		<div>
			<h1 class="text-[clamp(1.3rem,2.5vw,1.8rem)] font-bold text-white m-0">Dashboard Overview</h1>
			<p class="text-[0.8rem] text-white/60 mt-[2px] mb-0">Real-time clinic metrics and performance</p>
		</div>
		<button
			on:click={fetchAll}
			class="flex items-center gap-1.5 bg-white/10 border border-white/20 text-white rounded-lg px-[0.9rem] py-2 text-[0.8rem] cursor-pointer transition-colors duration-150 hover:bg-white/20"
			style="font-family: inherit;"
		>
			<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
				<path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
			</svg>
			Refresh
		</button>
	</div>

	{#if loading}
		<!-- Loading -->
		<div class="flex flex-col items-center gap-4 py-16 text-white">
			<div class="w-9 h-9 border-[3px] border-white/20 border-t-white rounded-full animate-spin"></div>
			<p class="m-0 text-sm">Loading dashboard…</p>
		</div>
	{:else}

		<!-- Stat Cards Grid -->
		<div class="grid grid-cols-3 gap-4 max-[1200px]:grid-cols-2 max-[600px]:grid-cols-1">

			<!-- Total Owners -->
			<div class="bg-white rounded-[14px] p-5 flex flex-col gap-1.5 shadow-[0_2px_8px_rgba(0,0,0,0.08)]">
				<div class="flex justify-between items-start">
					<span class="text-[0.78rem] text-gray-500 font-medium leading-snug max-w-[140px]">Total Registered Pet Owners</span>
					<div class="w-9 h-9 rounded-[10px] flex items-center justify-center flex-shrink-0 bg-blue-50 text-blue-600">
						<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="20" height="20">
							<path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/>
							<path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75"/>
						</svg>
					</div>
				</div>
				<div class="text-[clamp(1.6rem,2.5vw,2.2rem)] font-bold text-gray-900 leading-none">{stats.totalOwners.toLocaleString()}</div>
				<div class="text-[0.72rem] {stats.ownersDiff >= 0 ? 'text-green-600' : 'text-red-600'}">
					{stats.ownersDiff >= 0 ? '+' : ''}{stats.ownersDiff} from last month
				</div>
			</div>

			<!-- Total Patients -->
			<div class="bg-white rounded-[14px] p-5 flex flex-col gap-1.5 shadow-[0_2px_8px_rgba(0,0,0,0.08)]">
				<div class="flex justify-between items-start">
					<span class="text-[0.78rem] text-gray-500 font-medium leading-snug max-w-[140px]">Total Active Patients</span>
					<div class="w-9 h-9 rounded-[10px] flex items-center justify-center flex-shrink-0 bg-pink-50 text-pink-600">
						<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="20" height="20">
							<path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z"/>
						</svg>
					</div>
				</div>
				<div class="text-[clamp(1.6rem,2.5vw,2.2rem)] font-bold text-gray-900 leading-none">{stats.totalPatients.toLocaleString()}</div>
				<div class="text-[0.72rem] text-gray-500">{stats.dogCount} Dogs, {stats.catCount} Cats</div>
			</div>

			<!-- Today's Appointments -->
			<div class="bg-white rounded-[14px] p-5 flex flex-col gap-1.5 shadow-[0_2px_8px_rgba(0,0,0,0.08)]">
				<div class="flex justify-between items-start">
					<span class="text-[0.78rem] text-gray-500 font-medium leading-snug max-w-[140px]">Today's Appointment</span>
					<div class="w-9 h-9 rounded-[10px] flex items-center justify-center flex-shrink-0 bg-[#f0fff0] text-[#0a4f29]">
						<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="20" height="20">
							<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>
						</svg>
					</div>
				</div>
				<div class="text-[clamp(1.6rem,2.5vw,2.2rem)] font-bold text-gray-900 leading-none">{stats.todayAppointments}</div>
				<div class="text-[0.72rem] text-gray-500 flex items-center gap-1.5 flex-wrap">
					<span class="bg-green-100 text-green-800 px-1.5 py-px rounded-full text-[0.68rem]">{stats.confirmed} Confirmed</span>
					<span class="bg-yellow-100 text-yellow-800 px-1.5 py-px rounded-full text-[0.68rem]">{stats.waiting} Waiting</span>
					<span class="bg-red-100 text-red-800 px-1.5 py-px rounded-full text-[0.68rem]">{stats.cancelled} Cancelled</span>
				</div>
			</div>

			<!-- Low Stock -->
			<div class="bg-white rounded-[14px] p-5 flex flex-col gap-1.5 shadow-[0_2px_8px_rgba(0,0,0,0.08)]">
				<div class="flex justify-between items-start">
					<span class="text-[0.78rem] text-gray-500 font-medium leading-snug max-w-[140px]">Low Stock Items</span>
					<div class="w-9 h-9 rounded-[10px] flex items-center justify-center flex-shrink-0 bg-orange-50 text-orange-600">
						<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="20" height="20">
							<path d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
						</svg>
					</div>
				</div>
				<div class="text-[clamp(1.6rem,2.5vw,2.2rem)] font-bold text-gray-900 leading-none">{stats.lowStock}</div>
				<div class="text-[0.72rem] text-amber-600">Requires immediate attention</div>
			</div>

			<!-- Expiring Meds -->
			<div class="bg-white rounded-[14px] p-5 flex flex-col gap-1.5 shadow-[0_2px_8px_rgba(0,0,0,0.08)]">
				<div class="flex justify-between items-start">
					<span class="text-[0.78rem] text-gray-500 font-medium leading-snug max-w-[140px]">Expiring Medicines (7 days)</span>
					<div class="w-9 h-9 rounded-[10px] flex items-center justify-center flex-shrink-0 bg-yellow-50 text-yellow-600">
						<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="20" height="20">
							<path d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
						</svg>
					</div>
				</div>
				<div class="text-[clamp(1.6rem,2.5vw,2.2rem)] font-bold text-gray-900 leading-none">{stats.expiringMeds}</div>
				<div class="text-[0.72rem] text-amber-600">Check inventory details</div>
			</div>

			<!-- Today's Revenue -->
			<div class="bg-white rounded-[14px] p-5 flex flex-col gap-1.5 shadow-[0_2px_8px_rgba(0,0,0,0.08)]">
				<div class="flex justify-between items-start">
					<span class="text-[0.78rem] text-gray-500 font-medium leading-snug max-w-[140px]">Today's Revenue</span>
					<div class="w-9 h-9 rounded-[10px] flex items-center justify-center flex-shrink-0 bg-[#f0fff0] text-[#0a4f29]">
						<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="20" height="20">
							<line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/>
						</svg>
					</div>
				</div>
				<div class="text-[clamp(1.2rem,2vw,1.7rem)] font-bold text-gray-900 leading-none">{peso(stats.todayRevenue)}</div>
				<div class="text-[0.72rem] {stats.revenueDiff >= 0 ? 'text-green-600' : 'text-red-600'}">
					{stats.revenueDiff >= 0 ? '+' : ''}{stats.revenueDiff}% from yesterday
				</div>
			</div>
		</div>

		<!-- Bottom Panels -->
		<div class="grid grid-cols-2 gap-4 max-[900px]:grid-cols-1">

			<!-- Recent Staff Activity -->
			<div class="bg-white rounded-[14px] flex flex-col shadow-[0_2px_8px_rgba(0,0,0,0.08)] overflow-hidden">
				<div class="px-5 pt-[1.1rem] pb-2 border-b border-gray-100">
					<div class="flex items-center gap-2 text-gray-900">
						<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="16" height="16">
							<path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
						</svg>
						<span class="text-[0.9rem] font-semibold">Recent Staff Activity</span>
					</div>
					<p class="text-[0.72rem] text-gray-400 mt-[2px] mb-0">Latest modifications by staff members</p>
				</div>

				<div class="flex-1 overflow-y-auto px-4 py-2 flex flex-col gap-0" style="max-height:340px;">
					{#if auditLogs.length === 0}
						<p class="text-gray-400 text-[0.82rem] text-center py-8">No recent activity</p>
					{:else}
						{#each auditLogs.slice(0, 6) as log}
							<div class="flex gap-3 items-start py-[0.65rem] border-b border-gray-50 last:border-0">
								<div
									class="w-[30px] h-[30px] rounded-lg flex-shrink-0 flex items-center justify-center text-xs font-bold"
									style="background:{actionColor(log.Icon)}15; color:{actionColor(log.Icon)}"
								>
									{actionIcon(log.Icon)}
								</div>
								<div class="flex-1 min-w-0">
									<div class="flex justify-between items-start gap-2">
										<span class="text-[0.8rem] font-semibold text-gray-900">{log.Action}</span>
										<span class="text-[0.68rem] text-gray-400 whitespace-nowrap flex-shrink-0">{formatDateTime(log.created_at)}</span>
									</div>
									{#if log.USERS}
										<div class="text-[0.7rem] text-gray-500 flex items-center gap-1 mt-[2px]">
											<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="11" height="11">
												<path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/>
											</svg>
											{log.USERS.FirstName} {log.USERS.LastName}
										</div>
									{/if}
									<div class="text-[0.72rem] text-gray-500 leading-snug">{log.Details}</div>
								</div>
							</div>
						{/each}
					{/if}
				</div>

				<button
					on:click={() => goto('/Billing-Financial/audit-logs')}
					class="mx-5 mb-4 mt-2 py-2 bg-transparent border-none text-[#0a4f29] text-[0.78rem] font-medium cursor-pointer text-left flex items-center gap-1 hover:underline"
					style="font-family: inherit;"
				>
					View all activity logs →
				</button>
			</div>

			<!-- Recent Financial Deductions -->
			<div class="bg-white rounded-[14px] flex flex-col shadow-[0_2px_8px_rgba(0,0,0,0.08)] overflow-hidden">
				<div class="px-5 pt-[1.1rem] pb-2 border-b border-gray-100">
					<div class="flex items-center gap-2 text-gray-900">
						<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="16" height="16">
							<path d="M9 14l6-6m-5.5.5h.01m4.99 5h.01M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16l3.5-2 3.5 2 3.5-2 3.5 2z"/>
						</svg>
						<span class="text-[0.9rem] font-semibold">Recent Financial Deduction</span>
					</div>
					<p class="text-[0.72rem] text-gray-400 mt-[2px] mb-0">Latest fund deductions and expenses</p>
				</div>

				<!-- Total deductions banner -->
				<div class="mx-5 mt-3 mb-1 flex justify-between items-center bg-red-50 border border-red-200 rounded-[10px] px-4 py-2.5 text-[0.82rem] font-medium text-gray-700">
					<span>Today's Total Deductions</span>
					<span class="font-bold text-red-600 text-base">-{peso(totalDeductions)}</span>
				</div>

				<div class="flex-1 overflow-y-auto px-4 py-2 flex flex-col gap-0" style="max-height:340px;">
					{#if expenses.length === 0}
						<p class="text-gray-400 text-[0.82rem] text-center py-8">No expenses today</p>
					{:else}
						{#each expenses.slice(0, 6) as exp}
							<div class="flex gap-3 items-start py-[0.65rem] border-b border-gray-50 last:border-0">
								<div class="w-[30px] h-[30px] bg-[#f0fff0] rounded-lg flex-shrink-0 flex items-center justify-center text-[0.85rem]">
									{expenseIcon(exp.Category)}
								</div>
								<div class="flex-1 min-w-0">
									<div class="flex justify-between items-start gap-2">
										<span class="text-[0.8rem] font-semibold text-gray-900">{exp.Category}</span>
										<span class="text-[0.85rem] font-bold text-red-600 whitespace-nowrap">-{peso(exp.Amount)}</span>
									</div>
									<div class="text-[0.7rem] text-gray-500 leading-snug my-[2px] whitespace-nowrap overflow-hidden text-ellipsis">{exp.Notes}</div>
									{#if exp.CreatedBy}
										<div class="text-[0.65rem] text-gray-400">By: {exp.CreatedBy} · {formatDateTime(exp.created_at)}</div>
									{/if}
								</div>
							</div>
						{/each}
					{/if}
				</div>

				<button
					on:click={() => goto('/Billing-Financial/audit-logs?tab=expenses')}
					class="mx-5 mb-4 mt-2 py-2 bg-transparent border-none text-[#0a4f29] text-[0.78rem] font-medium cursor-pointer text-left flex items-center gap-1 hover:underline"
					style="font-family: inherit;"
				>
					View all activity logs →
				</button>
			</div>
		</div>
	{/if}
</div>