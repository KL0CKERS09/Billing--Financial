<script lang="ts">
	import { onMount } from 'svelte';

	export let data: { user: any };

	const API = 'http://localhost:8000';

	let stats = {
		total_consultations: 0,
		pending_billing: 0,
		completed_billing: 0,
		total_revenue: 0,
		total_transactions: 0,
		avg_transaction: 0,
		total_vat_collected: 0
	};

	let consultations: any[] = [];
	let loadingStats = true;
	let loadingConsultations = true;

	function getToken() {
		return localStorage.getItem('access_token') ?? '';
	}

	function authHeaders() {
		return {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${getToken()}`
		};
	}

	function peso(val: number) {
		return `₱${val.toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
	}

	function statusBadgeClass(status: string) {
		switch ((status || '').toLowerCase()) {
			case 'billed':    return 'bg-green-100 text-green-800';
			case 'pending':   return 'bg-yellow-100 text-yellow-800';
			case 'completed': return 'bg-blue-100 text-blue-800';
			default:          return 'bg-gray-100 text-gray-600';
		}
	}

	onMount(async () => {
		try {
			const [sRes, cRes] = await Promise.all([
				fetch(`${API}/dashboard/stats`, { headers: authHeaders() }),
				fetch(`${API}/dashboard/consultations?limit=10`, { headers: authHeaders() })
			]);
			if (sRes.ok) stats = await sRes.json();
			if (cRes.ok) consultations = await cRes.json();
		} catch (e) {
			console.error(e);
		} finally {
			loadingStats = false;
			loadingConsultations = false;
		}
	});
</script>

<div class="flex flex-col gap-5">

	<!-- Page title -->
	<h1 class="text-[1.6rem] font-bold text-white m-0">Dashboard</h1>

	<!-- Welcome banner -->
	<div
		class="rounded-[10px] px-5 py-4 border border-green-200"
		style="background: linear-gradient(135deg, #f0fdf4, #dcfce7);"
	>
		<p class="font-semibold text-green-800 text-[0.95rem] m-0">Welcome back to Billing and Financial!</p>
		<p class="text-[0.82rem] text-[#4b7c5e] mt-[2px] mb-0">
			Here's the latest overview of your dashboard — stay updated and keep achieving your goals.
		</p>
	</div>

	{#if loadingStats}
		<div class="px-4 py-3 text-gray-500 text-[0.85rem]">Loading stats…</div>
	{:else}

		<!-- Top 3 stat cards -->
		<div class="grid grid-cols-3 gap-4">

			<!-- Total Consultations -->
			<div class="bg-white rounded-[10px] p-5 border border-gray-200 flex items-center justify-between gap-3">
				<div>
					<p class="text-[0.78rem] text-gray-500 font-medium m-0">Total Consultations</p>
					<p class="text-[2rem] font-bold text-gray-900 mt-1 mb-0">{stats.total_consultations}</p>
				</div>
				<div class="p-2 rounded-lg bg-[#f0fdf4] text-[#2d6a4f] flex-shrink-0">
					<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="36" height="36">
						<path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
					</svg>
				</div>
			</div>

			<!-- Pending Billing -->
			<div class="bg-white rounded-[10px] p-5 border border-gray-200 flex items-center justify-between gap-3">
				<div>
					<p class="text-[0.78rem] text-gray-500 font-medium m-0">Pending Billing</p>
					<p class="text-[2rem] font-bold text-gray-900 mt-1 mb-0">{stats.pending_billing}</p>
				</div>
				<div class="p-2 rounded-lg bg-yellow-50 text-yellow-600 flex-shrink-0">
					<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="36" height="36">
						<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18M9 4v5"/>
					</svg>
				</div>
			</div>

			<!-- Completed Billing -->
			<div class="bg-white rounded-[10px] p-5 border border-gray-200 flex items-center justify-between gap-3">
				<div>
					<p class="text-[0.78rem] text-gray-500 font-medium m-0">Completed Billing</p>
					<p class="text-[2rem] font-bold text-gray-900 mt-1 mb-0">{stats.completed_billing}</p>
				</div>
				<div class="p-2 rounded-lg bg-[#f0fdf4] text-green-600 flex-shrink-0">
					<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="36" height="36">
						<circle cx="12" cy="12" r="9"/><path d="M9 12l2 2 4-4"/>
					</svg>
				</div>
			</div>
		</div>

		<!-- Bottom 4 smaller stat cards -->
		<div class="grid grid-cols-4 gap-4">
			<div class="bg-white rounded-[10px] p-5 border border-gray-200 flex flex-col gap-1">
				<p class="text-[0.78rem] text-gray-500 font-medium m-0">Total Revenue</p>
				<p class="text-[1.4rem] font-bold text-gray-900 m-0">{peso(stats.total_revenue)}</p>
			</div>
			<div class="bg-white rounded-[10px] p-5 border border-gray-200 flex flex-col gap-1">
				<p class="text-[0.78rem] text-gray-500 font-medium m-0">Transaction</p>
				<p class="text-[1.4rem] font-bold text-gray-900 m-0">{stats.total_transactions}</p>
			</div>
			<div class="bg-white rounded-[10px] p-5 border border-gray-200 flex flex-col gap-1">
				<p class="text-[0.78rem] text-gray-500 font-medium m-0">Avg Transaction</p>
				<p class="text-[1.4rem] font-bold text-gray-900 m-0">{peso(stats.avg_transaction)}</p>
			</div>
			<div class="bg-white rounded-[10px] p-5 border border-gray-200 flex flex-col gap-1">
				<p class="text-[0.78rem] text-gray-500 font-medium m-0">Total VAT Collected</p>
				<p class="text-[1.4rem] font-bold text-gray-900 m-0">{peso(stats.total_vat_collected)}</p>
			</div>
		</div>
	{/if}

	<!-- Recent Consultations table -->
	<div class="bg-white rounded-[10px] border border-gray-200 p-5">
		<h2 class="text-[1.05rem] font-semibold text-gray-900 mb-4 mt-0">Recent Consultation</h2>

		{#if loadingConsultations}
			<div class="px-2 py-3 text-gray-500 text-[0.85rem]">Loading consultations…</div>
		{:else if consultations.length === 0}
			<p class="px-2 py-3 text-gray-400 text-[0.85rem] m-0">No consultations found.</p>
		{:else}
			<div class="overflow-x-auto">
				<table class="w-full border-collapse text-[0.82rem]">
					<thead>
						<tr class="bg-gray-50">
							<th class="px-[0.85rem] py-[0.6rem] text-left font-semibold text-gray-500 border-b border-gray-200 whitespace-nowrap">Consultations ID</th>
							<th class="px-[0.85rem] py-[0.6rem] text-left font-semibold text-gray-500 border-b border-gray-200 whitespace-nowrap">Patient</th>
							<th class="px-[0.85rem] py-[0.6rem] text-left font-semibold text-gray-500 border-b border-gray-200 whitespace-nowrap">Owner</th>
							<th class="px-[0.85rem] py-[0.6rem] text-left font-semibold text-gray-500 border-b border-gray-200 whitespace-nowrap">Date</th>
							<th class="px-[0.85rem] py-[0.6rem] text-left font-semibold text-gray-500 border-b border-gray-200 whitespace-nowrap">Diagnosis</th>
							<th class="px-[0.85rem] py-[0.6rem] text-left font-semibold text-gray-500 border-b border-gray-200 whitespace-nowrap">Status</th>
						</tr>
					</thead>
					<tbody>
						{#each consultations as c}
							<tr class="border-b border-gray-100 hover:bg-gray-50 last:border-0">
								<td class="px-[0.85rem] py-3 text-gray-700 align-top">{c.ConsultationNumber}</td>
								<td class="px-[0.85rem] py-3 align-top">
									<p class="font-medium text-gray-900 m-0">{c.PATIENTS?.Name ?? '—'}</p>
									<p class="text-[0.75rem] text-gray-400 mt-[1px] m-0">{c.PATIENTS?.Species ?? ''} {c.PATIENTS?.Breed ?? ''}</p>
								</td>
								<td class="px-[0.85rem] py-3 align-top">
									<p class="text-gray-700 m-0">{c.OWNERS?.FirstName ?? ''} {c.OWNERS?.LastName ?? ''}</p>
									<p class="text-[0.75rem] text-gray-400 mt-[1px] m-0">{c.OWNERS?.PhoneNumber ?? ''}</p>
								</td>
								<td class="px-[0.85rem] py-3 text-gray-700 align-top whitespace-nowrap">
									{new Date(c.Date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
								</td>
								<td class="px-[0.85rem] py-3 text-gray-700 align-top">{c.Diagnosis ?? '—'}</td>
								<td class="px-[0.85rem] py-3 align-top">
									<span class="inline-block px-[0.65rem] py-1 rounded-full text-[0.75rem] font-semibold {statusBadgeClass(c.Status)}">
										{c.Status}
									</span>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{/if}
	</div>
</div>