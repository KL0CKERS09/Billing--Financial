<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';

	const API = 'http://localhost:8000';
	function getToken() {
		return typeof localStorage !== 'undefined' ? localStorage.getItem('access_token') : '';
	}
	function authHeaders() {
		return { 'Content-Type': 'application/json', Authorization: `Bearer ${getToken()}` };
	}

	let activeTab: 'activity' | 'expenses' = 'activity';

	// ── Audit logs state ──
	let logs: any[] = [];
	let filteredLogs: any[] = [];
	let logsLoading = true;
	let logsSearch = '';
	let logsModule = 'All';
	let logsDateFrom = '';
	let logsDateTo = '';
	const modules = ['All', 'Patients', 'Inventory', 'Billing', 'EMR', 'Owners', 'Appointments'];

	// ── Expenses state ──
	let expenses: any[] = [];
	let filteredExpenses: any[] = [];
	let expLoading = true;
	let expSearch = '';
	let expCategory = 'All';
	let expDateFrom = '';
	let expDateTo = '';
	const expCategories = [
		'All', 'Medical Supplies', 'Staff Salaries', 'Utilities', 'Rent', 'Equipment', 'Miscellaneous'
	];

	const peso = (n: number) => '₱' + Number(n).toLocaleString('en-PH', { minimumFractionDigits: 2 });

	function formatDT(dateStr: string) {
		if (!dateStr) return '—';
		const d = new Date(dateStr);
		return (
			d.toLocaleDateString('en-PH', { year: 'numeric', month: 'short', day: 'numeric' }) +
			' ' +
			d.toLocaleTimeString('en-PH', { hour: '2-digit', minute: '2-digit', hour12: false })
		);
	}

	function actionColor(icon: string) {
		const map: Record<string, string> = {
			add: '#0A4F29', edit: '#2563eb', bill: '#7c3aed',
			cancel: '#dc2626', check: '#16a34a', delete: '#dc2626', warning: '#d97706'
		};
		return map[icon] || '#6b7280';
	}
	function actionIcon(icon: string) {
		const map: Record<string, string> = {
			add: '+', edit: '✎', bill: '₱', cancel: '✕', check: '✓', delete: '🗑', warning: '⚠'
		};
		return map[icon] || '•';
	}
	function expenseIcon(cat: string) {
		const map: Record<string, string> = {
			'Medical Supplies': '💊', 'Staff Salaries': '👤',
			Utilities: '⚡', Rent: '🏠', Equipment: '🔧'
		};
		return map[cat] || '📋';
	}

	function moduleBadgeClass(mod: string) {
		const m = (mod || '').toLowerCase();
		const map: Record<string, string> = {
			patients:     'bg-pink-50 text-pink-600',
			inventory:    'bg-orange-50 text-orange-600',
			billing:      'bg-purple-50 text-purple-700',
			emr:          'bg-blue-50 text-blue-600',
			owners:       'bg-[#f0fff0] text-[#0a4f29]',
			appointments: 'bg-yellow-50 text-yellow-800'
		};
		return map[m] || 'bg-gray-100 text-gray-600';
	}

	async function fetchLogs() {
		logsLoading = true;
		try {
			const res = await fetch(`${API}/dashboard/audit-logs`, { headers: authHeaders() });
			if (res.ok) { logs = await res.json(); applyLogsFilter(); }
		} finally { logsLoading = false; }
	}

	async function fetchExpenses() {
		expLoading = true;
		try {
			const res = await fetch(`${API}/dashboard/all-expenses`, { headers: authHeaders() });
			if (res.ok) { expenses = await res.json(); applyExpFilter(); }
		} finally { expLoading = false; }
	}

	function applyLogsFilter() {
		filteredLogs = logs.filter((l) => {
			const s = logsSearch.toLowerCase();
			const matchSearch = !s ||
				(l.Action || '').toLowerCase().includes(s) ||
				(l.Details || '').toLowerCase().includes(s) ||
				(l.Module || '').toLowerCase().includes(s) ||
				(l.USERS ? `${l.USERS.FirstName} ${l.USERS.LastName}`.toLowerCase().includes(s) : false);
			const matchModule = logsModule === 'All' || l.Module === logsModule;
			const matchFrom = !logsDateFrom || new Date(l.created_at) >= new Date(logsDateFrom);
			const matchTo = !logsDateTo || new Date(l.created_at) <= new Date(logsDateTo + 'T23:59:59');
			return matchSearch && matchModule && matchFrom && matchTo;
		});
	}

	function applyExpFilter() {
		filteredExpenses = expenses.filter((e) => {
			const s = expSearch.toLowerCase();
			const matchSearch = !s ||
				(e.Category || '').toLowerCase().includes(s) ||
				(e.Notes || '').toLowerCase().includes(s) ||
				(e.CreatedBy || '').toLowerCase().includes(s);
			const matchCat = expCategory === 'All' || e.Category === expCategory;
			const matchFrom = !expDateFrom || new Date(e.created_at) >= new Date(expDateFrom);
			const matchTo = !expDateTo || new Date(e.created_at) <= new Date(expDateTo + 'T23:59:59');
			return matchSearch && matchCat && matchFrom && matchTo;
		});
	}

	function clearLogsFilter() { logsSearch = ''; logsModule = 'All'; logsDateFrom = ''; logsDateTo = ''; applyLogsFilter(); }
	function clearExpFilter()  { expSearch = '';  expCategory = 'All'; expDateFrom = ''; expDateTo = '';  applyExpFilter(); }

	$: (logsSearch, logsModule, logsDateFrom, logsDateTo, applyLogsFilter());
	$: (expSearch, expCategory, expDateFrom, expDateTo, applyExpFilter());
	$: totalFiltered = filteredExpenses.reduce((s, e) => s + Number(e.Amount || 0), 0);

	onMount(() => {
		const tab = $page.url.searchParams.get('tab');
		if (tab === 'expenses') activeTab = 'expenses';
		fetchLogs();
		fetchExpenses();
	});

	// Shared classes
	const filterInputCls = 'px-3 py-2 border-[1.5px] border-gray-200 rounded-lg text-[0.82rem] outline-none bg-[#fafafa] text-gray-700 focus:border-[#0a4f29] transition-colors duration-150';
	const ghostBtnCls = 'flex items-center gap-1.5 bg-white/10 border border-white/20 text-white rounded-lg px-[0.85rem] py-[0.45rem] text-[0.78rem] cursor-pointer whitespace-nowrap transition-colors duration-150 hover:bg-white/20';
</script>

<div class="flex flex-col gap-5">

	<!-- Header -->
	<div class="flex items-start justify-between gap-4">
		<div class="flex items-center gap-4">
			<button
				on:click={() => goto('/Billing-Financial/admin-dashboard-overview')}
				class={ghostBtnCls}
				style="font-family: inherit;"
			>
				<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
					<path d="M19 12H5M12 5l-7 7 7 7"/>
				</svg>
				Back
			</button>
			<div>
				<h1 class="text-[clamp(1.2rem,2.2vw,1.6rem)] font-bold text-white m-0">Activity & Audit Logs</h1>
				<p class="text-[0.78rem] text-white/60 mt-[2px] mb-0">Complete history of staff actions and financial deductions</p>
			</div>
		</div>
		<button
			on:click={() => { fetchLogs(); fetchExpenses(); }}
			class={ghostBtnCls}
			style="font-family: inherit;"
		>
			<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15">
				<path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
			</svg>
			Refresh
		</button>
	</div>

	<!-- Tabs -->
	<div class="flex gap-2">
		<button
			on:click={() => (activeTab = 'activity')}
			class="flex items-center gap-2 px-[1.1rem] py-[0.6rem] rounded-[10px] text-[0.82rem] font-medium cursor-pointer border transition-all duration-150
				{activeTab === 'activity'
					? 'bg-white text-[#0a4f29] border-white font-semibold'
					: 'bg-white/10 border-white/15 text-white/70 hover:bg-white/18 hover:text-white'}"
			style="font-family: inherit;"
		>
			<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="15" height="15">
				<path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
			</svg>
			Staff Activity
			<span class="bg-[#0a4f29] text-white rounded-full px-[7px] py-px text-[0.68rem] font-bold">
				{filteredLogs.length}
			</span>
		</button>
		<button
			on:click={() => (activeTab = 'expenses')}
			class="flex items-center gap-2 px-[1.1rem] py-[0.6rem] rounded-[10px] text-[0.82rem] font-medium cursor-pointer border transition-all duration-150
				{activeTab === 'expenses'
					? 'bg-white text-[#0a4f29] border-white font-semibold'
					: 'bg-white/10 border-white/15 text-white/70 hover:bg-white/18 hover:text-white'}"
			style="font-family: inherit;"
		>
			<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="15" height="15">
				<path d="M9 14l6-6m-5.5.5h.01m4.99 5h.01M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16l3.5-2 3.5 2 3.5-2 3.5 2z"/>
			</svg>
			Financial Deductions
			<span class="bg-[#0a4f29] text-white rounded-full px-[7px] py-px text-[0.68rem] font-bold">
				{filteredExpenses.length}
			</span>
		</button>
	</div>

	<!-- ══ ACTIVITY TAB ══ -->
	{#if activeTab === 'activity'}
		<!-- Filter bar -->
		<div class="flex gap-2.5 items-center flex-wrap bg-white rounded-xl px-4 py-3 shadow-[0_2px_8px_rgba(0,0,0,0.06)]">
			<div class="relative flex-1 min-w-[200px]">
				<svg class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="15" height="15">
					<circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
				</svg>
				<input
					type="text"
					placeholder="Search action, details, staff…"
					bind:value={logsSearch}
					class="{filterInputCls} w-full pl-9"
					style="font-family: inherit;"
				/>
			</div>
			<select bind:value={logsModule} class={filterInputCls} style="font-family: inherit;">
				{#each modules as m}<option value={m}>{m}</option>{/each}
			</select>
			<input type="date" bind:value={logsDateFrom} title="From date" class={filterInputCls} style="font-family: inherit;"/>
			<input type="date" bind:value={logsDateTo}   title="To date"   class={filterInputCls} style="font-family: inherit;"/>
			<button
				on:click={clearLogsFilter}
				class="px-[0.9rem] py-2 bg-gray-100 border border-gray-200 rounded-lg text-[0.78rem] text-gray-500 cursor-pointer transition-colors duration-150 hover:bg-red-50 hover:text-red-600 hover:border-red-200"
				style="font-family: inherit;"
			>Clear</button>
		</div>

		<!-- Table card -->
		<div class="bg-white rounded-[14px] overflow-hidden shadow-[0_2px_8px_rgba(0,0,0,0.07)]">
			{#if logsLoading}
				<div class="flex items-center gap-3 px-5 py-8 text-gray-500 text-[0.82rem]">
					<div class="w-5 h-5 border-2 border-gray-200 border-t-[#0a4f29] rounded-full animate-spin flex-shrink-0"></div>
					Loading logs…
				</div>
			{:else if filteredLogs.length === 0}
				<div class="flex flex-col items-center gap-3 p-12 text-gray-400 text-[0.85rem]">
					<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="40" height="40" class="opacity-30">
						<path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
					</svg>
					<p class="m-0">No activity logs found</p>
				</div>
			{:else}
				<div class="px-5 py-[0.65rem] text-[0.75rem] text-gray-400 border-b border-gray-100">
					{filteredLogs.length} record{filteredLogs.length !== 1 ? 's' : ''} found
				</div>
				<div class="overflow-x-auto">
					<table class="w-full border-collapse">
						<thead>
							<tr class="bg-[#f0fff0]">
								<th class="px-4 py-[0.7rem] text-left text-[0.75rem] font-semibold text-[#0a4f29] whitespace-nowrap">Action</th>
								<th class="px-4 py-[0.7rem] text-left text-[0.75rem] font-semibold text-[#0a4f29] whitespace-nowrap">Module</th>
								<th class="px-4 py-[0.7rem] text-left text-[0.75rem] font-semibold text-[#0a4f29] whitespace-nowrap">Staff</th>
								<th class="px-4 py-[0.7rem] text-left text-[0.75rem] font-semibold text-[#0a4f29] whitespace-nowrap">Details</th>
								<th class="px-4 py-[0.7rem] text-left text-[0.75rem] font-semibold text-[#0a4f29] whitespace-nowrap">Date & Time</th>
							</tr>
						</thead>
						<tbody>
							{#each filteredLogs as log}
								<tr class="border-b border-gray-50 hover:bg-gray-50 last:border-0">
									<td class="px-4 py-[0.7rem] text-[0.78rem] text-gray-700 align-top">
										<div class="flex items-center gap-2">
											<span
												class="w-6 h-6 rounded-md flex items-center justify-center text-[0.7rem] font-bold flex-shrink-0"
												style="background:{actionColor(log.Icon)}15; color:{actionColor(log.Icon)}"
											>{actionIcon(log.Icon)}</span>
											<span class="font-medium text-gray-900 text-[0.78rem]">{log.Action}</span>
										</div>
									</td>
									<td class="px-4 py-[0.7rem] text-[0.78rem] text-gray-700 align-top">
										<span class="inline-block px-2 py-px rounded-full text-[0.68rem] font-semibold whitespace-nowrap {moduleBadgeClass(log.Module)}">
											{log.Module || '—'}
										</span>
									</td>
									<td class="px-4 py-[0.7rem] text-[0.75rem] text-gray-700 align-top whitespace-nowrap">
										{#if log.USERS}{log.USERS.FirstName} {log.USERS.LastName}{:else}<span class="text-gray-400">—</span>{/if}
									</td>
									<td class="px-4 py-[0.7rem] text-[0.74rem] text-gray-500 align-top leading-snug" style="max-width:260px">{log.Details || '—'}</td>
									<td class="px-4 py-[0.7rem] text-[0.72rem] text-gray-400 align-top whitespace-nowrap">{formatDT(log.created_at)}</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			{/if}
		</div>
	{/if}

	<!-- ══ EXPENSES TAB ══ -->
	{#if activeTab === 'expenses'}
		<!-- Filter bar -->
		<div class="flex gap-2.5 items-center flex-wrap bg-white rounded-xl px-4 py-3 shadow-[0_2px_8px_rgba(0,0,0,0.06)]">
			<div class="relative flex-1 min-w-[200px]">
				<svg class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="15" height="15">
					<circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
				</svg>
				<input
					type="text"
					placeholder="Search category, notes, staff…"
					bind:value={expSearch}
					class="{filterInputCls} w-full pl-9"
					style="font-family: inherit;"
				/>
			</div>
			<select bind:value={expCategory} class={filterInputCls} style="font-family: inherit;">
				{#each expCategories as c}<option value={c}>{c}</option>{/each}
			</select>
			<input type="date" bind:value={expDateFrom} title="From date" class={filterInputCls} style="font-family: inherit;"/>
			<input type="date" bind:value={expDateTo}   title="To date"   class={filterInputCls} style="font-family: inherit;"/>
			<button
				on:click={clearExpFilter}
				class="px-[0.9rem] py-2 bg-gray-100 border border-gray-200 rounded-lg text-[0.78rem] text-gray-500 cursor-pointer transition-colors duration-150 hover:bg-red-50 hover:text-red-600 hover:border-red-200"
				style="font-family: inherit;"
			>Clear</button>
		</div>

		<!-- Total banner -->
		<div class="flex justify-between items-center bg-red-50 border border-red-200 rounded-xl px-5 py-3 text-[0.85rem] font-medium text-gray-700">
			<span>Total Deductions ({filteredExpenses.length} records)</span>
			<span class="font-bold text-red-600 text-[1.1rem]">-{peso(totalFiltered)}</span>
		</div>

		<!-- Table card -->
		<div class="bg-white rounded-[14px] overflow-hidden shadow-[0_2px_8px_rgba(0,0,0,0.07)]">
			{#if expLoading}
				<div class="flex items-center gap-3 px-5 py-8 text-gray-500 text-[0.82rem]">
					<div class="w-5 h-5 border-2 border-gray-200 border-t-[#0a4f29] rounded-full animate-spin flex-shrink-0"></div>
					Loading expenses…
				</div>
			{:else if filteredExpenses.length === 0}
				<div class="flex flex-col items-center gap-3 p-12 text-gray-400 text-[0.85rem]">
					<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="40" height="40" class="opacity-30">
						<path d="M9 14l6-6m-5.5.5h.01m4.99 5h.01M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16l3.5-2 3.5 2 3.5-2 3.5 2z"/>
					</svg>
					<p class="m-0">No expense records found</p>
				</div>
			{:else}
				<div class="px-5 py-[0.65rem] text-[0.75rem] text-gray-400 border-b border-gray-100">
					{filteredExpenses.length} record{filteredExpenses.length !== 1 ? 's' : ''} found
				</div>
				<div class="overflow-x-auto">
					<table class="w-full border-collapse">
						<thead>
							<tr class="bg-[#f0fff0]">
								<th class="px-4 py-[0.7rem] text-left text-[0.75rem] font-semibold text-[#0a4f29] whitespace-nowrap">Category</th>
								<th class="px-4 py-[0.7rem] text-left text-[0.75rem] font-semibold text-[#0a4f29] whitespace-nowrap">Amount</th>
								<th class="px-4 py-[0.7rem] text-left text-[0.75rem] font-semibold text-[#0a4f29] whitespace-nowrap">Notes</th>
								<th class="px-4 py-[0.7rem] text-left text-[0.75rem] font-semibold text-[#0a4f29] whitespace-nowrap">Created By</th>
								<th class="px-4 py-[0.7rem] text-left text-[0.75rem] font-semibold text-[#0a4f29] whitespace-nowrap">Approved By</th>
								<th class="px-4 py-[0.7rem] text-left text-[0.75rem] font-semibold text-[#0a4f29] whitespace-nowrap">Date</th>
							</tr>
						</thead>
						<tbody>
							{#each filteredExpenses as exp}
								<tr class="border-b border-gray-50 hover:bg-gray-50 last:border-0">
									<td class="px-4 py-[0.7rem] text-[0.78rem] text-gray-700 align-top">
										<div class="flex items-center gap-2">
											<span class="text-base flex-shrink-0">{expenseIcon(exp.Category)}</span>
											<span class="font-medium text-gray-900">{exp.Category}</span>
										</div>
									</td>
									<td class="px-4 py-[0.7rem] text-[0.78rem] align-top whitespace-nowrap">
										<span class="text-red-600 font-semibold">-{peso(exp.Amount)}</span>
									</td>
									<td class="px-4 py-[0.7rem] text-[0.74rem] text-gray-500 align-top leading-snug" style="max-width:260px">{exp.Notes || '—'}</td>
									<td class="px-4 py-[0.7rem] text-[0.75rem] text-gray-700 align-top whitespace-nowrap">{exp.CreatedBy || '—'}</td>
									<td class="px-4 py-[0.7rem] text-[0.75rem] text-gray-700 align-top whitespace-nowrap">{exp.ApprovedBy || '—'}</td>
									<td class="px-4 py-[0.7rem] text-[0.72rem] text-gray-400 align-top whitespace-nowrap">{formatDT(exp.created_at)}</td>
								</tr>
							{/each}
						</tbody>
						<tfoot>
							<tr class="bg-[#f0fff0] border-t-2 border-[#a7cdbb]">
								<td class="px-4 py-[0.7rem] text-[0.78rem] font-semibold text-gray-900">Total</td>
								<td class="px-4 py-[0.7rem] text-[0.78rem]">
									<span class="text-red-600 font-bold">-{peso(totalFiltered)}</span>
								</td>
								<td colspan="4"></td>
							</tr>
						</tfoot>
					</table>
				</div>
			{/if}
		</div>
	{/if}
</div>