<script lang="ts">
	import { onMount } from 'svelte';

	const API = 'http://localhost:8000';
	function getToken() {
		return localStorage.getItem('access_token') ?? '';
	}
	function authHeaders() {
		return { 'Content-Type': 'application/json', Authorization: `Bearer ${getToken()}` };
	}
	function peso(v: number) {
		return `₱${Number(v).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
	}

	let loading = true;
	let error = '';
	let report: any = null;
	let billingHistory: any[] = [];
	let filteredHistory: any[] = [];

	let activePeriod: 'ALL' | 'TODAY' | 'THIS WEEK' | 'MONTH' | 'CUSTOM' = 'ALL';
	let searchQuery = '';
	let customFrom = '';
	let customTo = '';

	onMount(async () => {
		await loadAll();
	});

	async function loadAll() {
		loading = true;
		try {
			const [reportRes, historyRes] = await Promise.all([
				fetch(`${API}/reports/financial`, { headers: authHeaders() }),
				fetch(`${API}/reports/billing-history`, { headers: authHeaders() })
			]);
			if (reportRes.ok) report = await reportRes.json();
			else error = 'Failed to load report.';
			if (historyRes.ok) {
				billingHistory = await historyRes.json();
				applyFilters();
			}
		} catch (e) {
			error = 'Could not connect to server.';
		} finally {
			loading = false;
		}
	}

	function applyFilters() {
		const now = new Date();
		let from: Date | null = null;
		let to: Date | null = null;

		if (activePeriod === 'ALL') {
			filteredHistory = billingHistory.filter((b) => {
				const q = searchQuery.toLowerCase();
				return (
					!q ||
					b.id?.toString().includes(q) ||
					b.CONSULTATIONS?.PATIENTS?.Name?.toLowerCase().includes(q) ||
					(b.CONSULTATIONS?.OWNERS?.FirstName + ' ' + b.CONSULTATIONS?.OWNERS?.LastName)
						.toLowerCase()
						.includes(q)
				);
			});
			return;
		}

		if (activePeriod === 'TODAY') {
			from = new Date(now.getFullYear(), now.getMonth(), now.getDate());
			to = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59);
		} else if (activePeriod === 'THIS WEEK') {
			const day = now.getDay();
			from = new Date(now);
			from.setDate(now.getDate() - day);
			to = new Date(now);
			to.setDate(now.getDate() + (6 - day));
		} else if (activePeriod === 'MONTH') {
			from = new Date(now.getFullYear(), now.getMonth(), 1);
			to = new Date(now.getFullYear(), now.getMonth() + 1, 0, 23, 59, 59);
		} else if (activePeriod === 'CUSTOM' && customFrom && customTo) {
			from = new Date(customFrom);
			to = new Date(customTo + 'T23:59:59');
		}

		filteredHistory = billingHistory.filter((b) => {
			const date = new Date(b.created_at);
			const inPeriod = !from || !to || (date >= from && date <= to);
			const q = searchQuery.toLowerCase();
			const matchSearch =
				!q ||
				b.id?.toString().includes(q) ||
				b.CONSULTATIONS?.PATIENTS?.Name?.toLowerCase().includes(q) ||
				(b.CONSULTATIONS?.OWNERS?.FirstName + ' ' + b.CONSULTATIONS?.OWNERS?.LastName)
					.toLowerCase()
					.includes(q);
			return inPeriod && matchSearch;
		});
	}

	$: filteredRevenue  = filteredHistory.reduce((a, b) => a + parseFloat(b.TotalAmount || 0), 0);
	$: filteredTx       = filteredHistory.length;
	$: filteredAvg      = filteredTx > 0 ? filteredRevenue / filteredTx : 0;
	$: filteredVat      = filteredHistory.reduce((a, b) => a + parseFloat(b.VAT || 0), 0);
	$: officialReceipts = filteredHistory.filter((b) => b.ReceiptNo).length;
	$: serviceTotal     = filteredHistory.reduce((a, b) => a + parseFloat(b.ServiceFee || 0), 0);
	$: medicineTotal    = filteredHistory.reduce((a, b) => a + parseFloat(b.MedicineFee || 0), 0);
	$: grandTotal       = serviceTotal + medicineTotal;
	$: servicePct       = grandTotal > 0 ? (serviceTotal / grandTotal) * 100 : 50;
	$: medicinePct      = grandTotal > 0 ? (medicineTotal / grandTotal) * 100 : 50;

	function setPeriod(p: typeof activePeriod) {
		activePeriod = p;
		applyFilters();
	}

	function formatDate(d: string) {
		if (!d) return '—';
		return new Date(d).toLocaleDateString('en-PH', { month: 'short', day: '2-digit', year: 'numeric' });
	}

	function exportPDF() {
		window.print();
	}

	// Shared input class
	const inputCls = 'px-[0.6rem] py-[0.35rem] border-[1.5px] border-gray-200 rounded-md text-[0.78rem] outline-none focus:border-[#2d6a4f] transition-colors duration-150';
</script>

<svelte:head>
	<link
		href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&display=swap"
		rel="stylesheet"
	/>
	<style>
		@media print {
			body * { visibility: hidden; }
			.print-area, .print-area * { visibility: visible; }
			.print-area {
				position: fixed; inset: 0;
				background: white; padding: 2rem; z-index: 9999;
			}
		}
	</style>
</svelte:head>

<div class="flex flex-col gap-5 print-area">

	{#if loading}
		<div class="py-12 text-center text-gray-500">Loading financial data…</div>
	{:else if error}
		<div class="py-8 text-center text-red-700">{error}</div>
	{:else}

		<!-- ── Filter Bar ── -->
		<div class="flex items-center gap-3 flex-wrap bg-white border border-gray-200 rounded-[10px] px-4 py-3">

			<!-- Period tabs -->
			<div class="flex gap-1">
				{#each ['ALL', 'TODAY', 'THIS WEEK', 'MONTH', 'CUSTOM'] as p}
					<button
						on:click={() => setPeriod(p as typeof activePeriod)}
						class="px-[0.85rem] py-[0.35rem] rounded-md border-none text-[0.78rem] font-semibold cursor-pointer transition-colors duration-150
							{activePeriod === p
								? 'bg-[#2d6a4f] text-white'
								: 'bg-gray-100 text-gray-500 hover:bg-gray-200'}"
						style="font-family: inherit;"
					>{p}</button>
				{/each}
			</div>

			<!-- Custom date range -->
			{#if activePeriod === 'CUSTOM'}
				<div class="flex items-center gap-2 text-[0.82rem] text-gray-500">
					<input type="date" bind:value={customFrom} on:change={applyFilters} class={inputCls} style="font-family: inherit;"/>
					<span>to</span>
					<input type="date" bind:value={customTo} on:change={applyFilters} class={inputCls} style="font-family: inherit;"/>
				</div>
			{/if}

			<!-- Search -->
			<div class="relative flex-1 min-w-[200px]">
				<svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14"
					class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none">
					<path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z"/>
				</svg>
				<input
					type="text"
					placeholder="Search by Billing ID, Patient name, or owner..."
					bind:value={searchQuery}
					on:input={applyFilters}
					class="w-full pl-[2.1rem] pr-3 py-2 border-[1.5px] border-gray-200 rounded-lg text-[0.82rem] outline-none focus:border-[#2d6a4f] transition-colors duration-150"
					style="font-family: inherit;"
				/>
			</div>

			<!-- Export -->
			<button
				on:click={exportPDF}
				class="px-4 py-2 bg-white border-[1.5px] border-[#2d6a4f] text-[#2d6a4f] rounded-lg text-[0.82rem] font-semibold cursor-pointer whitespace-nowrap hover:bg-[#f0fdf4] transition-colors duration-150"
				style="font-family: inherit;"
			>⬇ Export PDF</button>
		</div>

		<!-- ── Stat Cards ── -->
		<div class="grid grid-cols-4 gap-4">

			<div class="bg-white border border-gray-200 rounded-[10px] px-5 py-4">
				<div class="flex justify-between items-center mb-2">
					<span class="text-[0.75rem] text-gray-500 font-medium">Total Revenue</span>
					<span class="text-base px-[0.4rem] py-[0.3rem] rounded-md bg-green-100">₱</span>
				</div>
				<p class="text-[1.35rem] font-bold text-gray-900 m-0">{peso(filteredRevenue)}</p>
			</div>

			<div class="bg-white border border-gray-200 rounded-[10px] px-5 py-4">
				<div class="flex justify-between items-center mb-2">
					<span class="text-[0.75rem] text-gray-500 font-medium">Transactions</span>
					<span class="text-base px-[0.4rem] py-[0.3rem] rounded-md bg-blue-100">📋</span>
				</div>
				<p class="text-[1.35rem] font-bold text-gray-900 m-0">{filteredTx}</p>
			</div>

			<div class="bg-white border border-gray-200 rounded-[10px] px-5 py-4">
				<div class="flex justify-between items-center mb-2">
					<span class="text-[0.75rem] text-gray-500 font-medium">Avg Transaction</span>
					<span class="text-base px-[0.4rem] py-[0.3rem] rounded-md bg-orange-100">📊</span>
				</div>
				<p class="text-[1.35rem] font-bold text-gray-900 m-0">{peso(filteredAvg)}</p>
			</div>

			<div class="bg-white border border-gray-200 rounded-[10px] px-5 py-4">
				<div class="flex justify-between items-center mb-2">
					<span class="text-[0.75rem] text-gray-500 font-medium">Total VAT Collected</span>
					<span class="text-base px-[0.4rem] py-[0.3rem] rounded-md bg-purple-100">🧾</span>
				</div>
				<p class="text-[1.35rem] font-bold text-gray-900 m-0">{peso(filteredVat)}</p>
			</div>
		</div>

		<!-- ── Revenue by Category + Quick Stats ── -->
		<div class="grid grid-cols-2 gap-4">

			<!-- Revenue by Category -->
			<div class="bg-white border border-gray-200 rounded-[10px] p-5 flex flex-col gap-4">
				<h3 class="text-[0.9rem] font-bold text-gray-900 m-0">Revenue by Category</h3>

				<div class="flex flex-col gap-1.5">
					<div class="flex justify-between text-[0.83rem] text-gray-700 font-medium">
						<span>Services</span>
						<span class="font-bold text-gray-900">{peso(serviceTotal)}</span>
					</div>
					<div class="h-2 bg-gray-100 rounded-full overflow-hidden">
						<div class="h-full bg-[#2d6a4f] rounded-full transition-[width] duration-500" style="width:{Math.round(servicePct)}%"></div>
					</div>
					<p class="text-[0.7rem] text-gray-400 m-0">{Math.round(servicePct)}% of total revenue</p>
				</div>

				<div class="flex flex-col gap-1.5">
					<div class="flex justify-between text-[0.83rem] text-gray-700 font-medium">
						<span>Medicines</span>
						<span class="font-bold text-gray-900">{peso(medicineTotal)}</span>
					</div>
					<div class="h-2 bg-gray-100 rounded-full overflow-hidden">
						<div class="h-full bg-[#52b788] rounded-full transition-[width] duration-500" style="width:{Math.round(medicinePct)}%"></div>
					</div>
					<p class="text-[0.7rem] text-gray-400 m-0">{Math.round(medicinePct)}% of total revenue</p>
				</div>
			</div>

			<!-- Quick Stats -->
			<div class="bg-white border border-gray-200 rounded-[10px] p-5 flex flex-col gap-4">
				<h3 class="text-[0.9rem] font-bold text-gray-900 m-0">Quick Stats</h3>

				<div class="flex justify-between items-center px-4 py-[0.65rem] rounded-lg bg-green-100 text-[0.83rem] text-gray-700">
					<span>Total Billing Records</span>
					<span class="font-bold text-gray-900">{filteredTx}</span>
				</div>

				<div class="flex justify-between items-center px-4 py-[0.65rem] rounded-lg bg-blue-100 text-[0.83rem] text-gray-700">
					<span>Official Receipts Issued</span>
					<span class="font-bold text-gray-900">{officialReceipts}</span>
				</div>

				<div class="flex justify-between items-center px-4 py-[0.65rem] rounded-lg bg-purple-100 text-[0.83rem] text-gray-700">
					<span>Period Selected</span>
					<span class="bg-[#2d6a4f] text-white px-[0.6rem] py-[0.2rem] rounded-full text-[0.72rem] font-bold">
						{activePeriod}
					</span>
				</div>
			</div>
		</div>

		<!-- ── Billing History Table ── -->
		<div class="bg-white border border-gray-200 rounded-[10px] overflow-hidden">
			<h3 class="text-[0.9rem] font-bold text-gray-900 px-5 py-4 border-b border-gray-200 bg-gray-50 m-0">
				Billing History
			</h3>

			{#if filteredHistory.length === 0}
				<div class="flex flex-col items-center gap-2 py-12 text-gray-400 text-[0.85rem]">
					<span class="text-4xl">📋</span>
					<p class="m-0">No billing records found for the selected period.</p>
				</div>
			{:else}
				<div class="overflow-x-auto">
					<table class="w-full border-collapse text-[0.8rem]">
						<thead>
							<tr class="bg-gray-50">
								<th class="px-4 py-[0.6rem] text-left font-semibold text-gray-500 border-b border-gray-200 whitespace-nowrap">Date</th>
								<th class="px-4 py-[0.6rem] text-left font-semibold text-gray-500 border-b border-gray-200 whitespace-nowrap">Billing ID</th>
								<th class="px-4 py-[0.6rem] text-left font-semibold text-gray-500 border-b border-gray-200 whitespace-nowrap">Patient</th>
								<th class="px-4 py-[0.6rem] text-left font-semibold text-gray-500 border-b border-gray-200 whitespace-nowrap">Owner</th>
								<th class="px-4 py-[0.6rem] text-left font-semibold text-gray-500 border-b border-gray-200 whitespace-nowrap">Services</th>
								<th class="px-4 py-[0.6rem] text-left font-semibold text-gray-500 border-b border-gray-200 whitespace-nowrap">Medicines</th>
								<th class="px-4 py-[0.6rem] text-left font-semibold text-gray-500 border-b border-gray-200 whitespace-nowrap">VAT</th>
								<th class="px-4 py-[0.6rem] text-left font-semibold text-gray-500 border-b border-gray-200 whitespace-nowrap">Total</th>
								<th class="px-4 py-[0.6rem] text-left font-semibold text-gray-500 border-b border-gray-200 whitespace-nowrap">Receipt</th>
							</tr>
						</thead>
						<tbody>
							{#each filteredHistory as b}
								<tr class="border-b border-gray-100 hover:bg-gray-50 last:border-0">
									<td class="px-4 py-[0.65rem] text-gray-700 align-middle whitespace-nowrap">{formatDate(b.created_at)}</td>
									<td class="px-4 py-[0.65rem] text-gray-500 align-middle font-mono text-[0.78rem]">#{b.id}</td>
									<td class="px-4 py-[0.65rem] align-middle">
										<p class="font-semibold text-gray-900 m-0">{b.CONSULTATIONS?.PATIENTS?.Name ?? '—'}</p>
										<p class="text-[0.72rem] text-gray-400 mt-[1px] m-0">{b.CONSULTATIONS?.PATIENTS?.Species} {b.CONSULTATIONS?.PATIENTS?.Breed}</p>
									</td>
									<td class="px-4 py-[0.65rem] text-gray-700 align-middle">{b.CONSULTATIONS?.OWNERS?.FirstName} {b.CONSULTATIONS?.OWNERS?.LastName}</td>
									<td class="px-4 py-[0.65rem] text-gray-700 align-middle">{peso(b.ServiceFee ?? 0)}</td>
									<td class="px-4 py-[0.65rem] text-gray-700 align-middle">{peso(b.MedicineFee ?? 0)}</td>
									<td class="px-4 py-[0.65rem] text-gray-700 align-middle">{peso(b.VAT ?? 0)}</td>
									<td class="px-4 py-[0.65rem] align-middle font-semibold text-[#2d6a4f]">{peso(b.TotalAmount ?? 0)}</td>
									<td class="px-4 py-[0.65rem] align-middle">
										{#if b.ReceiptNo}
											<span class="bg-green-100 text-green-800 px-2 py-[0.2rem] rounded-full text-[0.72rem] font-semibold">
												#{b.ReceiptNo}
											</span>
										{:else}
											<span class="text-gray-300">—</span>
										{/if}
									</td>
								</tr>
							{/each}
						</tbody>
						<tfoot>
							<tr class="bg-[#f0fdf4] border-t-2 border-green-200">
								<td class="px-4 py-[0.65rem] font-bold text-gray-900" colspan="4">TOTAL</td>
								<td class="px-4 py-[0.65rem] font-bold text-gray-900">{peso(serviceTotal)}</td>
								<td class="px-4 py-[0.65rem] font-bold text-gray-900">{peso(medicineTotal)}</td>
								<td class="px-4 py-[0.65rem] font-bold text-gray-900">{peso(filteredVat)}</td>
								<td class="px-4 py-[0.65rem] font-bold text-gray-900">{peso(filteredRevenue)}</td>
								<td></td>
							</tr>
						</tfoot>
					</table>
				</div>
			{/if}
		</div>
	{/if}
</div>