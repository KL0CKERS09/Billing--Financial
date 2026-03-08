<script lang="ts">
	import { onMount } from 'svelte';

	const API = 'http://localhost:8000';
	function getToken() { return localStorage.getItem('access_token') ?? ''; }
	function authHeaders() {
		return { 'Content-Type': 'application/json', Authorization: `Bearer ${getToken()}` };
	}
	function peso(v: number) {
		return `₱${Number(v).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
	}

	let consultations: any[] = [];
	let loading = true;
	let searchQuery = '';
	let filterStatus = 'All';

	let wizardOpen = false;
	let step = 1;
	let selectedConsultation: any = null;

	let activeTab: 'Service' | 'Prescription' | 'OTC' | 'PetSupply' = 'Service';
	let catalogSearch = '';
	let catalogItems: any[] = [];
	let catalogLoading = false;

	let cart: { id: number; name: string; category: string; unit: string; price: number; qty: number; }[] = [];

	let receiptNo = '';
	let saving = false;
	let saved = false;
	let billingError = '';

	$: filtered = consultations.filter((c) => {
		const q = searchQuery.toLowerCase();
		const matchSearch =
			!q ||
			c.ConsultationNumber?.toLowerCase().includes(q) ||
			c.PATIENTS?.Name?.toLowerCase().includes(q) ||
			(c.OWNERS?.FirstName + ' ' + c.OWNERS?.LastName).toLowerCase().includes(q);
		const matchStatus = filterStatus === 'All' || c.Status === filterStatus;
		return matchSearch && matchStatus;
	});

	$: serviceItems    = cart.filter((i) => i.category === 'Service');
	$: medicineItems   = cart.filter((i) => i.category !== 'Service');
	$: servicesSubtotal = serviceItems.reduce((a, i) => a + i.price * i.qty, 0);
	$: medicinesSubtotal = medicineItems.reduce((a, i) => a + i.price * i.qty, 0);
	$: cartSubtotal    = servicesSubtotal + medicinesSubtotal;
	$: vat             = Math.round(cartSubtotal * 0.12 * 100) / 100;
	$: grandTotal      = cartSubtotal + vat;
	$: cartCount       = cart.reduce((a, i) => a + i.qty, 0);
	$: filteredCatalog = catalogItems.filter(
		(i) => !catalogSearch || i.Name?.toLowerCase().includes(catalogSearch.toLowerCase())
	);

	const stepLabels = ['Patient & EMR', 'Services & Products', 'Computation', 'Summary', 'Generate'];

	onMount(async () => {
		await loadConsultations();
		loading = false;
	});

	async function loadConsultations() {
		try {
			const r = await fetch(`${API}/billing/consultations`, { headers: authHeaders() });
			if (r.ok) consultations = await r.json();
		} catch (e) { console.error(e); }
	}

	async function loadCatalog(category: string) {
		catalogLoading = true;
		catalogItems = [];
		try {
			const r = await fetch(`${API}/billing/inventory?category=${category}`, { headers: authHeaders() });
			if (r.ok) { catalogItems = await r.json(); }
			else {
				const r2 = await fetch(`${API}/billing/inventory`, { headers: authHeaders() });
				if (r2.ok) { const all = await r2.json(); catalogItems = all.filter((i: any) => i.Category === category); }
			}
		} catch (e) { console.error(e); }
		catalogLoading = false;
	}

	async function switchTab(tab: typeof activeTab) {
		activeTab = tab;
		catalogSearch = '';
		await loadCatalog(tab);
	}

	function openBilling(c: any) {
		if (c.Status === 'Billed') {
			alert('This consultation has already been billed. Billing cannot be done twice for the same consultation.');
			return;
		}
		billingError = '';
		selectedConsultation = c;
		step = 1;
		cart = [];
		catalogItems = [];
		activeTab = 'Service';
		catalogSearch = '';
		saved = false;
		receiptNo = String(Math.floor(Math.random() * 9000) + 1000).padStart(4, '0');
		wizardOpen = true;
	}

	function goToStep2() {
		step = 2;
		loadCatalog('Service');
	}

	function addToCart(item: any) {
		const existing = cart.find((c) => c.id === item.id);
		if (existing) {
			cart = cart.map((c) => (c.id === item.id ? { ...c, qty: c.qty + 1 } : c));
		} else {
			cart = [...cart, { id: item.id, name: item.Name, category: item.Category ?? 'Service', unit: item.Unit ?? 'piece', price: Number(item.UnitPrice), qty: 1 }];
		}
	}

	function changeQty(id: number, delta: number) {
		cart = cart.map((c) => (c.id === id ? { ...c, qty: Math.max(1, c.qty + delta) } : c)).filter((c) => c.qty > 0);
	}

	function removeFromCart(id: number) { cart = cart.filter((c) => c.id !== id); }
	function cartQty(id: number) { return cart.find((c) => c.id === id)?.qty ?? 0; }

	async function saveBilling() {
		saving = true;
		billingError = '';
		try {
			const body = {
				consultation_id: selectedConsultation.id,
				service_items: serviceItems.map((s) => ({ name: s.name, price: s.price * s.qty })),
				medicine_items: medicineItems.map((m) => ({ inventory_id: m.id, name: m.name, qty: m.qty, unit_price: m.price })),
				service_fee: servicesSubtotal,
				medicine_fee: medicinesSubtotal,
				other_fees: 0,
				receipt_no: receiptNo
			};
			const r = await fetch(`${API}/billing/create`, { method: 'POST', headers: authHeaders(), body: JSON.stringify(body) });
			if (r.status === 409) {
				const err = await r.json();
				billingError = err.detail || 'A billing record already exists for this consultation.';
				saving = false;
				return;
			}
			if (r.ok) {
				saved = true;
				await loadConsultations();
				step = 5;
			} else {
				const err = await r.json();
				billingError = err.detail || 'Failed to save billing. Please try again.';
			}
		} catch (e) {
			console.error(e);
			billingError = 'Network error. Please try again.';
		}
		saving = false;
	}

	function categoryLabel(cat: string) {
		if (cat === 'Service') return 'Service';
		if (cat === 'Prescription') return 'Prescription';
		if (cat === 'OTC') return 'OTC';
		if (cat === 'PetSupply') return 'Pet Supply';
		return cat;
	}

	function statusBadgeClass(status: string) {
		switch ((status || '').toLowerCase()) {
			case 'billed':  return 'bg-[#f0fff0] text-green-800';
			case 'pending': return 'bg-yellow-100 text-yellow-800';
			default:        return 'bg-gray-100 text-gray-600';
		}
	}

	function numberToWords(amount: number): string {
		const n = Math.floor(amount);
		const cents = Math.round((amount - n) * 100);
		const ones = ['','ONE','TWO','THREE','FOUR','FIVE','SIX','SEVEN','EIGHT','NINE','TEN','ELEVEN','TWELVE','THIRTEEN','FOURTEEN','FIFTEEN','SIXTEEN','SEVENTEEN','EIGHTEEN','NINETEEN'];
		const tens = ['','','TWENTY','THIRTY','FORTY','FIFTY','SIXTY','SEVENTY','EIGHTY','NINETY'];
		function toWords(n: number): string {
			if (n === 0) return '';
			if (n < 20) return ones[n] + ' ';
			if (n < 100) return tens[Math.floor(n / 10)] + (n % 10 ? ' ' + ones[n % 10] : '') + ' ';
			if (n < 1000) return ones[Math.floor(n / 100)] + ' HUNDRED ' + toWords(n % 100);
			if (n < 1000000) return toWords(Math.floor(n / 1000)) + 'THOUSAND ' + toWords(n % 1000);
			return toWords(Math.floor(n / 1000000)) + 'MILLION ' + toWords(n % 1000000);
		}
		return `${toWords(n).trim()} PESOS AND ${cents.toString().padStart(2, '0')}/100 (₱${amount.toLocaleString('en-PH', { minimumFractionDigits: 2 })})`;
	}

	// Shared classes
	const wCardHeader = 'bg-[#6e9c87] text-white px-5 py-3 text-[0.88rem] font-semibold flex items-center gap-2';
	const wCardBody   = 'p-5 flex-1 flex flex-col gap-3 bg-white overflow-y-auto';
	const wCardFooter = 'px-5 py-4 border-t border-gray-100 flex items-center bg-white';
	const btnContinue = 'px-8 py-[0.65rem] bg-[#0a4f29] text-white border-none rounded-lg text-[0.85rem] font-semibold cursor-pointer ml-auto disabled:opacity-50 disabled:cursor-not-allowed';
	const btnCancel   = 'px-6 py-[0.6rem] border-[1.5px] border-gray-200 bg-white rounded-lg text-[0.85rem] text-gray-600 cursor-pointer hover:bg-gray-50';
</script>

<svelte:head>
	<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet"/>
	<style>
		@media print {
			body * { visibility: hidden; }
			.receipt-area, .receipt-area * { visibility: visible; }
			.receipt-area { position: fixed; inset: 0; background: white; z-index: 9999; padding: 2rem; }
		}
	</style>
</svelte:head>

<!-- ══ MAIN LIST ══ -->
{#if !wizardOpen}
<div class="flex flex-col gap-5">
	<h1 class="text-[1.6rem] font-bold text-white m-0">Billing</h1>

	<!-- Stats -->
	<div class="grid grid-cols-3 gap-4">
		{#each [
			{ label: 'Total Consultations', val: consultations.length, icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2' },
			{ label: 'Pending Billing',     val: consultations.filter((c) => c.Status === 'Pending').length, icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z' },
			{ label: 'Completed Billing',   val: consultations.filter((c) => c.Status === 'Billed').length,  icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z' }
		] as s}
			<div class="bg-white border border-gray-200 rounded-[10px] px-6 py-5 flex justify-between items-center">
				<div>
					<p class="text-[0.78rem] text-gray-500 font-medium m-0">{s.label}</p>
					<p class="text-[2rem] font-bold text-gray-900 mt-1 m-0">{s.val}</p>
				</div>
				<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="32" height="32" opacity="0.25">
					<path d={s.icon}/>
				</svg>
			</div>
		{/each}
	</div>

	<!-- Toolbar -->
	<div class="flex items-center gap-3 bg-white px-4 py-2.5 rounded-lg">
		<div class="relative flex-1">
			<svg class="absolute left-[0.85rem] top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" viewBox="0 0 20 20" fill="currentColor" width="15" height="15">
				<path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z"/>
			</svg>
			<input
				type="text"
				placeholder="Search by patient name, owner, or Consultation ID..."
				bind:value={searchQuery}
				class="w-full pl-10 pr-3 py-[0.65rem] border-[1.5px] border-gray-200 rounded-lg text-[0.85rem] outline-none bg-white focus:border-[#0a4f29] transition-colors"
				style="font-family: inherit;"
			/>
		</div>
		<div class="flex gap-1.5">
			{#each ['All', 'Pending', 'Billed'] as f}
				<button
					on:click={() => (filterStatus = f)}
					class="px-4 py-[0.45rem] rounded-md border-[1.5px] text-[0.8rem] cursor-pointer transition-colors duration-150
						{filterStatus === f ? 'bg-[#0a4f29] text-white border-[#0a4f29]' : 'bg-white border-gray-200 text-gray-700 hover:border-gray-300'}"
					style="font-family: inherit;"
				>{f}</button>
			{/each}
		</div>
	</div>

	<!-- Table -->
	<div class="bg-white border border-gray-200 rounded-[10px] p-5">
		<h2 class="text-[1rem] font-semibold text-gray-900 mb-4 mt-0">Recent Consultation</h2>
		{#if loading}
			<div class="py-8 text-center text-gray-400 text-[0.85rem]">Loading…</div>
		{:else if filtered.length === 0}
			<div class="py-8 text-center text-gray-400 text-[0.85rem]">No consultations found.</div>
		{:else}
			<div class="overflow-x-auto">
				<table class="w-full border-collapse text-[0.82rem]">
					<thead>
						<tr class="bg-[#f0fff0]">
							{#each ['Consultations ID','Patient','Owner','Date','Diagnosis','Status','Action'] as h}
								<th class="px-4 py-[0.7rem] text-left font-semibold text-gray-700 border-b border-gray-200 whitespace-nowrap">{h}</th>
							{/each}
						</tr>
					</thead>
					<tbody>
						{#each filtered as c}
							<tr class="border-b border-gray-100 hover:bg-gray-50 last:border-0">
								<td class="px-4 py-3 text-gray-700 align-middle">{c.ConsultationNumber}</td>
								<td class="px-4 py-3 align-middle">
									<p class="font-semibold text-gray-900 m-0">{c.PATIENTS?.Name ?? '—'}</p>
									<p class="text-[0.73rem] text-gray-400 mt-[1px] m-0">{c.PATIENTS?.Species} {c.PATIENTS?.Breed}</p>
								</td>
								<td class="px-4 py-3 align-middle">
									<p class="text-gray-700 m-0">{c.OWNERS?.FirstName} {c.OWNERS?.LastName}</p>
									<p class="text-[0.73rem] text-gray-400 mt-[1px] m-0">{c.OWNERS?.PhoneNumber}</p>
								</td>
								<td class="px-4 py-3 text-gray-700 align-middle whitespace-nowrap">
									{new Date(c.Date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
								</td>
								<td class="px-4 py-3 text-gray-700 align-middle text-[0.8rem]" style="max-width:180px">{c.Diagnosis ?? '—'}</td>
								<td class="px-4 py-3 align-middle">
									<span class="inline-block px-3 py-[0.28rem] rounded-full text-[0.73rem] font-semibold {statusBadgeClass(c.Status)}">{c.Status}</span>
								</td>
								<td class="px-4 py-3 align-middle">
									{#if c.Status === 'Billed'}
										<div class="flex items-center gap-1.5 text-[0.78rem] text-gray-400">
											<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="13" height="13">
												<rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/>
											</svg>
											<span>Billed</span>
										</div>
									{:else}
										<button
											on:click={() => openBilling(c)}
											class="px-4 py-[0.4rem] bg-[#0a4f29] text-white border-none rounded-md text-[0.8rem] font-semibold cursor-pointer hover:bg-[#0d6334] transition-colors"
											style="font-family: inherit;"
										>Start Billing</button>
									{/if}
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{/if}
	</div>
</div>

<!-- ══ WIZARD ══ -->
{:else}
<div class="flex flex-col gap-0 min-h-[80vh]">

	<!-- Step bar -->
	<div class="grid border-b-[3px] border-[#0a4f29]" style="grid-template-columns: repeat(5, 1fr); background: #0a4f29;">
		{#each stepLabels as label, i}
			<div class="flex flex-col items-center px-2 py-[0.85rem] gap-1.5">
				<div class="w-full h-[3px] rounded-full
					{step === i + 1 ? 'bg-white' : step > i + 1 ? 'bg-[#a7cdbb]' : 'bg-white/20'}">
				</div>
				<span class="text-[0.72rem] font-medium text-center
					{step === i + 1 ? 'text-white font-semibold' : step > i + 1 ? 'text-[#95d5b2]' : 'text-white/60'}">
					{label}
				</span>
			</div>
		{/each}
	</div>

	<!-- Wizard body wrapper -->
	<div class="flex-1 p-6 flex flex-col gap-4 bg-[#f0fff0] rounded-[20px]">

		<!-- ── STEP 1 ── -->
		{#if step === 1}
			<div class="grid grid-cols-2 gap-4" style="height: 70vh;">

				<!-- Patient card -->
				<div class="border border-gray-200 rounded-xl overflow-hidden flex flex-col">
					<div class={wCardHeader}>
						<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="18" height="18">
							<path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/>
						</svg>
						Patient Information
					</div>
					<div class={wCardBody}>
						<p class="text-[1.15rem] font-bold text-gray-900 m-0">{selectedConsultation?.PATIENTS?.Name}</p>
						<p class="text-[0.78rem] text-gray-500 m-0">{selectedConsultation?.PATIENTS?.Species} • {selectedConsultation?.PATIENTS?.Breed} • {selectedConsultation?.PATIENTS?.Age ?? '?'} years old</p>
						<p class="text-[0.78rem] text-gray-500 m-0">Patient ID: pat-{String(selectedConsultation?.patient_id).padStart(3, '0')}</p>
						<hr class="border-none border-t border-gray-100"/>
						{#each [
							{ icon: 'M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2 M12 7a4 4 0 100-8 4 4 0 000 8', label: 'OWNER NAME', val: `${selectedConsultation?.OWNERS?.FirstName} ${selectedConsultation?.OWNERS?.LastName}` },
							{ icon: 'M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z', label: 'CONTACT', val: selectedConsultation?.OWNERS?.PhoneNumber },
							{ icon: 'M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z M15 11a3 3 0 11-6 0 3 3 0 016 0z', label: 'ADDRESS', val: selectedConsultation?.OWNERS?.Address ?? '—' }
						] as f}
							<div class="flex flex-col gap-1">
								<div class="flex items-center gap-1.5 text-[0.7rem] text-gray-400 font-semibold tracking-[0.04em]">
									<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="13" height="13"><path d={f.icon}/></svg>
									{f.label}
								</div>
								<p class="text-[0.88rem] text-gray-900 font-medium pl-5 m-0">{f.val}</p>
							</div>
						{/each}
					</div>
					<div class={wCardFooter}>
						<button on:click={() => (wizardOpen = false)} class={btnCancel} style="font-family: inherit;">Cancel & Return</button>
					</div>
				</div>

				<!-- EMR card -->
				<div class="border border-gray-200 rounded-xl overflow-hidden flex flex-col">
					<div class={wCardHeader}>
						<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="18" height="18">
							<path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2"/>
						</svg>
						Electronic Medical Record
					</div>
					<div class={wCardBody}>
						<div class="flex items-start gap-3">
							<span class="text-base">📅</span>
							<div>
								<p class="text-[0.68rem] text-gray-400 font-semibold tracking-[0.05em] mb-1 m-0">CONSULTATION DATE</p>
								<p class="text-[0.9rem] text-gray-900 font-semibold m-0">
									{new Date(selectedConsultation?.Date).toLocaleDateString('en-US', { month: 'long', day: '2-digit', year: 'numeric' })}
								</p>
							</div>
						</div>
						<hr class="border-none border-t border-gray-100"/>
						<div class="flex items-start gap-3">
							<span class="text-base">🩺</span>
							<div>
								<p class="text-[0.68rem] text-gray-400 font-semibold tracking-[0.05em] mb-1 m-0">ATTENDING VETERINARIAN</p>
								<p class="text-[0.9rem] text-gray-900 font-semibold m-0">Dr. Maria Rosario</p>
								<p class="text-[0.72rem] text-gray-400 m-0">PRC-VET-2015-001234</p>
							</div>
						</div>
						<hr class="border-none border-t border-gray-100"/>
						<div>
							<p class="text-[0.68rem] text-gray-400 font-semibold tracking-[0.05em] mb-1 m-0">DIAGNOSIS</p>
							<p class="text-[0.9rem] text-gray-900 font-semibold mt-1 m-0">{selectedConsultation?.Diagnosis ?? '—'}</p>
						</div>
						<hr class="border-none border-t border-gray-100"/>
						<div>
							<p class="text-[0.68rem] text-gray-400 font-semibold tracking-[0.05em] mb-1 m-0">CLINICAL NOTES</p>
							<p class="text-[0.85rem] text-gray-700 leading-relaxed mt-1 m-0">{selectedConsultation?.Notes ?? '—'}</p>
						</div>
					</div>
					<div class="{wCardFooter} justify-end">
						<button on:click={goToStep2} class={btnContinue} style="font-family: inherit;">Continue to Medicine Usage →</button>
					</div>
				</div>
			</div>

		<!-- ── STEP 2 ── -->
		{:else if step === 2}
			<div class="flex gap-4 flex-1" style="min-height: 65vh;">

				<!-- Catalog panel -->
				<div class="flex flex-col gap-3 flex-1 min-w-0">
					<!-- Category tabs -->
					<div class="flex gap-0 border-b-2 border-gray-200">
						{#each [
							{ key: 'Service', label: 'Service', icon: '🔧' },
							{ key: 'Prescription', label: 'Prescription Meds', icon: '💊' },
							{ key: 'OTC', label: 'OTC Meds', icon: '🧴' },
							{ key: 'PetSupply', label: 'Pet Supplies', icon: '🛒' }
						] as tab}
							<button
								on:click={() => switchTab(tab.key as typeof activeTab)}
								class="flex items-center gap-1.5 px-4 py-[0.6rem] border-none border-b-2 -mb-[2px] text-[0.8rem] cursor-pointer bg-transparent transition-colors
									{activeTab === tab.key ? 'text-[#0a4f29] border-b-[#0a4f29] font-semibold' : 'text-gray-500 border-b-transparent hover:text-gray-700'}"
								style="font-family: inherit;"
							><span>{tab.icon}</span>{tab.label}</button>
						{/each}
					</div>

					<input
						type="text"
						placeholder="Search here..."
						bind:value={catalogSearch}
						class="w-full px-[0.85rem] py-[0.6rem] border-[1.5px] border-gray-200 rounded-lg text-[0.85rem] outline-none focus:border-[#0a4f29] transition-colors"
						style="font-family: inherit;"
					/>

					{#if catalogLoading}
						<div class="py-8 text-center text-gray-400">Loading…</div>
					{:else}
						<div class="grid gap-[0.65rem] overflow-y-auto" style="grid-template-columns: repeat(3, 1fr); max-height: 50vh;">
							{#each filteredCatalog as item}
								<div class="border-[1.5px] border-gray-200 rounded-lg p-[0.85rem] flex flex-col gap-1.5 bg-white hover:border-[#a7cdbb] transition-colors">
									<div class="flex justify-between items-start">
										<p class="text-[0.82rem] font-semibold text-gray-900 leading-snug flex-1 m-0">{item.Name}</p>
										<button
											on:click={() => addToCart(item)}
											class="w-[22px] h-[22px] rounded-full bg-gray-100 border-none text-lg cursor-pointer flex-shrink-0 flex items-center justify-center text-gray-700 hover:bg-[#0a4f29] hover:text-white transition-colors leading-none"
										>+</button>
									</div>
									<p class="text-[0.7rem] text-gray-400 m-0">
										{#if item.Category !== 'Service'}Stock: {item.Stock} {item.Unit}{:else}{categoryLabel(item.Category)}{/if}
									</p>
									<div class="flex items-baseline gap-1.5 mt-1">
										<p class="text-[0.92rem] font-bold text-gray-900 m-0">₱{Number(item.UnitPrice).toFixed(2)}</p>
										{#if item.Category !== 'Service'}<span class="text-[0.68rem] text-gray-400">per {item.Unit}</span>{/if}
									</div>
								</div>
							{/each}
						</div>
					{/if}
				</div>

				<!-- Cart panel -->
				<div class="border-[1.5px] border-gray-200 rounded-[10px] flex flex-col bg-white overflow-hidden" style="width: 280px; flex-shrink: 0;">
					<div class="px-4 py-[0.85rem] text-[0.88rem] font-semibold text-gray-900 border-b border-gray-100">🛒 Cart</div>

					<div class="flex-1 overflow-y-auto p-3" style="max-height: 50vh;">
						{#if cart.length === 0}
							<div class="flex flex-col items-center justify-center h-full gap-1.5 text-gray-400 py-8">
								<span class="text-[2.5rem] opacity-30">🛒</span>
								<p class="text-[0.82rem] font-medium m-0">Cart is empty</p>
								<p class="text-[0.72rem] text-center m-0">Add Services or Products to get started</p>
							</div>
						{:else}
							<div class="flex flex-col gap-2">
								{#each cart as item}
									<div class="border border-gray-100 rounded-lg p-[0.65rem]">
										<div class="mb-1.5">
											<p class="text-[0.82rem] font-semibold text-gray-900 m-0">{item.name}</p>
											<p class="text-[0.7rem] text-gray-400 m-0">{categoryLabel(item.category)}</p>
										</div>
										<div class="flex justify-between items-center">
											<div class="flex items-center gap-1.5">
												<button on:click={() => changeQty(item.id, -1)} class="w-[22px] h-[22px] rounded border-[1.5px] border-gray-200 bg-white text-[0.9rem] cursor-pointer flex items-center justify-center text-gray-700 hover:bg-[#f0fff0] hover:border-[#0a4f29]" style="font-family: inherit;">-</button>
												<span class="text-[0.85rem] font-semibold text-gray-900 min-w-[20px] text-center">{item.qty}</span>
												<button on:click={() => changeQty(item.id, 1)}  class="w-[22px] h-[22px] rounded border-[1.5px] border-gray-200 bg-white text-[0.9rem] cursor-pointer flex items-center justify-center text-gray-700 hover:bg-[#f0fff0] hover:border-[#0a4f29]" style="font-family: inherit;">+</button>
											</div>
											<div class="text-right">
												<p class="text-[0.68rem] text-gray-400 m-0">₱{item.price.toFixed(2)} / {item.unit}</p>
												<p class="text-[0.82rem] font-bold text-[#0a4f29] m-0">{peso(item.price * item.qty)}</p>
											</div>
										</div>
									</div>
								{/each}
							</div>
						{/if}
					</div>

					<div class="border-t border-gray-100 p-[0.85rem] flex flex-col gap-2 bg-gray-50">
						<div class="flex flex-col gap-1 pb-2">
							<div class="flex justify-between text-[0.82rem] text-gray-600">
								<span>Subtotal:</span><span>{cart.length > 0 ? peso(cartSubtotal) : ''}</span>
							</div>
							<div class="flex justify-between text-[0.88rem] font-bold text-gray-900">
								<span>Total:</span><span>{cart.length > 0 ? peso(cartSubtotal) : ''}</span>
							</div>
						</div>
						<button on:click={() => (step = 3)} disabled={cart.length === 0}
							class="w-full py-[0.65rem] bg-[#0a4f29] text-white border-none rounded-lg text-[0.85rem] font-semibold cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
							style="font-family: inherit;">Continue to Billing</button>
						<button on:click={() => (step = 1)}
							class="w-full py-[0.55rem] bg-gray-200 text-gray-700 border-none rounded-lg text-[0.82rem] cursor-pointer"
							style="font-family: inherit;">Back</button>
					</div>
				</div>
			</div>

		<!-- ── STEP 3 ── -->
		{:else if step === 3}
			<div class="grid grid-cols-2 gap-4">
				<!-- Services -->
				<div class="border border-gray-200 rounded-xl overflow-hidden flex flex-col">
					<div class={wCardHeader}>
						<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="16" height="16"><path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2"/></svg>
						Service Fee
					</div>
					<div class={wCardBody}>
						{#each serviceItems as item}
							<div class="flex items-center gap-2.5 bg-[#f0fff0] rounded-lg px-[0.85rem] py-[0.6rem]">
								<div class="w-5 h-5 bg-[#0a4f29] text-white rounded-full flex items-center justify-center text-[0.65rem] flex-shrink-0">✓</div>
								<span class="flex-1 text-[0.83rem] text-gray-700">{item.name}</span>
								<span class="text-[0.85rem] font-semibold text-gray-900">{peso(item.price * item.qty)}</span>
							</div>
						{/each}
						{#if serviceItems.length === 0}<p class="text-[0.82rem] text-gray-400">No services added.</p>{/if}
					</div>
					<div class="flex justify-between px-5 py-3 border-t border-gray-200 text-[0.85rem] font-semibold text-gray-900 bg-gray-50">
						<span>Services Subtotal</span><span>{peso(servicesSubtotal)}</span>
					</div>
				</div>

				<!-- Cart items -->
				<div class="border border-gray-200 rounded-xl overflow-hidden flex flex-col">
					<div class={wCardHeader}>🛒 Cart</div>
					<div class={wCardBody}>
						{#if medicineItems.length > 0}
							<div class="grid text-[0.7rem] text-gray-400 font-semibold py-1 border-b border-gray-100 mb-1" style="grid-template-columns: 2fr 0.5fr 1fr 1fr;">
								<span></span><span>Qty</span><span>Unit Price</span><span>Subtotal</span>
							</div>
							{#each medicineItems as item}
								<div class="grid text-[0.82rem] text-gray-700 py-1.5 border-b border-gray-50" style="grid-template-columns: 2fr 0.5fr 1fr 1fr;">
									<span>{item.name}</span><span>{item.qty}</span><span>₱{item.price}</span><span>{peso(item.price * item.qty)}</span>
								</div>
							{/each}
						{:else}<p class="text-[0.82rem] text-gray-400">No medicines or supplies added.</p>{/if}
					</div>
					<div class="flex justify-between px-5 py-3 border-t border-gray-200 text-[0.85rem] font-semibold text-gray-900 bg-gray-50">
						<span>Subtotal</span><span>{peso(medicinesSubtotal)}</span>
					</div>
				</div>
			</div>

			<!-- Final computation -->
			<div class="border-[1.5px] border-gray-200 rounded-[10px] p-5 bg-white">
				<h3 class="text-[0.92rem] font-bold text-gray-900 mb-3 mt-0">Final Computation</h3>
				{#each [['Services Total', servicesSubtotal], ['Cart Total', medicinesSubtotal]] as [label, val]}
					<div class="flex justify-between text-[0.83rem] text-gray-700 py-[0.22rem]">
						<span>{label}</span><span>{peso(val as number)}</span>
					</div>
				{/each}
				<hr class="border-none border-t border-gray-200 my-1.5"/>
				<div class="flex justify-between text-[0.83rem] text-gray-700 py-[0.22rem]"><span>Subtotal</span><span>{peso(cartSubtotal)}</span></div>
				<div class="flex justify-between text-[0.83rem] text-gray-700 py-[0.22rem]"><span>VAT (12%)</span><span>{peso(vat)}</span></div>
				<hr class="border-none border-t border-gray-200 my-1.5"/>
				<div class="flex justify-between text-[0.95rem] font-bold text-gray-900 pt-1.5"><span>Grand Total</span><span>{peso(grandTotal)}</span></div>
			</div>

			<div class="flex justify-between items-center pt-2 mt-auto gap-2">
				<button on:click={() => (step = 2)} class={btnCancel} style="font-family: inherit;">Back</button>
				<button on:click={() => (step = 4)} class={btnContinue} style="font-family: inherit;">Continue</button>
			</div>

		<!-- ── STEP 4 ── -->
		{:else if step === 4}
			<div class="grid grid-cols-2 gap-4">
				<!-- Services -->
				<div class="border border-gray-200 rounded-xl overflow-hidden flex flex-col">
					<div class={wCardHeader}>
						<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="16" height="16"><path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2"/></svg>
						Service Fee
					</div>
					<div class={wCardBody}>
						{#each serviceItems as item}
							<div class="flex items-center gap-2.5 bg-[#f0fff0] rounded-lg px-[0.85rem] py-[0.6rem]">
								<div class="w-5 h-5 bg-[#0a4f29] text-white rounded-full flex items-center justify-center text-[0.65rem] flex-shrink-0">✓</div>
								<span class="flex-1 text-[0.83rem] text-gray-700">{item.name}</span>
								<span class="text-[0.85rem] font-semibold text-gray-900">{peso(item.price * item.qty)}</span>
							</div>
						{/each}
					</div>
					<div class="flex justify-between px-5 py-3 border-t border-gray-200 text-[0.85rem] font-semibold text-gray-900 bg-gray-50">
						<span>Services Subtotal</span><span>{peso(servicesSubtotal)}</span>
					</div>
				</div>

				<!-- Cart -->
				<div class="border border-gray-200 rounded-xl overflow-hidden flex flex-col">
					<div class={wCardHeader}>🛒 Cart</div>
					<div class={wCardBody}>
						<div class="grid text-[0.7rem] text-gray-400 font-semibold py-1 border-b border-gray-100 mb-1" style="grid-template-columns: 2fr 0.5fr 1fr 1fr;">
							<span></span><span>Qty</span><span>Unit Price</span><span>Subtotal</span>
						</div>
						{#each medicineItems as item}
							<div class="grid text-[0.82rem] text-gray-700 py-1.5 border-b border-gray-50" style="grid-template-columns: 2fr 0.5fr 1fr 1fr;">
								<span>{item.name}</span><span>{item.qty}</span><span>₱{item.price}</span><span>{peso(item.price * item.qty)}</span>
							</div>
						{/each}
					</div>
					<div class="flex justify-between px-5 py-3 border-t border-gray-200 text-[0.85rem] font-semibold text-gray-900 bg-gray-50">
						<span>Subtotal</span><span>{peso(medicinesSubtotal)}</span>
					</div>
				</div>
			</div>

			<div class="grid grid-cols-2 gap-4 mt-1">
				<!-- Final computation -->
				<div class="border-[1.5px] border-gray-200 rounded-[10px] p-5 bg-white">
					<h3 class="text-[0.92rem] font-bold text-gray-900 mb-3 mt-0">Final Computation</h3>
					{#each [['Services Total', servicesSubtotal], ['Cart Total', medicinesSubtotal]] as [label, val]}
						<div class="flex justify-between text-[0.83rem] text-gray-700 py-[0.22rem]">
							<span>{label}</span><span>{peso(val as number)}</span>
						</div>
					{/each}
					<hr class="border-none border-t border-gray-200 my-1.5"/>
					<div class="flex justify-between text-[0.83rem] text-gray-700 py-[0.22rem]"><span>Subtotal</span><span>{peso(cartSubtotal)}</span></div>
					<div class="flex justify-between text-[0.83rem] text-gray-700 py-[0.22rem]"><span>VAT (12%)</span><span>{peso(vat)}</span></div>
					<hr class="border-none border-t border-gray-200 my-1.5"/>
					<div class="flex justify-between text-[0.95rem] font-bold text-gray-900 pt-1.5"><span>Grand Total</span><span>{peso(grandTotal)}</span></div>
				</div>

				<!-- Consultation details -->
				<div class="border-[1.5px] border-gray-200 rounded-[10px] p-5 bg-white">
					<h3 class="text-[0.92rem] font-bold text-gray-900 mb-3 mt-0">Consultation Details</h3>
					<div class="grid grid-cols-2 gap-4">
						{#each [
							{ icon: '🐾', label: 'Patient', val: selectedConsultation?.PATIENTS?.Name, sub: `${selectedConsultation?.PATIENTS?.Species} • ${selectedConsultation?.PATIENTS?.Breed}` },
							{ icon: '👤', label: 'Owner', val: `${selectedConsultation?.OWNERS?.FirstName} ${selectedConsultation?.OWNERS?.LastName}`, sub: selectedConsultation?.OWNERS?.PhoneNumber },
							{ icon: '📅', label: 'Date', val: new Date(selectedConsultation?.Date).toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' }), sub: null },
							{ icon: '🩺', label: 'Veterinarian', val: 'Dr. Maria Rosario', sub: null }
						] as d}
							<div>
								<p class="text-[0.7rem] text-gray-400 font-semibold mb-1 m-0">{d.icon} {d.label}</p>
								<p class="text-[0.85rem] font-semibold text-gray-900 m-0">{d.val}</p>
								{#if d.sub}<p class="text-[0.72rem] text-gray-400 m-0">{d.sub}</p>{/if}
							</div>
						{/each}
					</div>
				</div>
			</div>

			<!-- Billing error -->
			{#if billingError}
				<div class="flex items-center gap-2.5 bg-red-50 border border-red-200 rounded-[10px] px-[1.1rem] py-3 text-red-700 text-[0.82rem] font-medium">
					<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="16" height="16">
						<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
					</svg>
					{billingError}
				</div>
			{/if}

			<div class="flex justify-between items-center pt-2 mt-auto gap-2">
				<button on:click={() => (step = 3)} class={btnCancel} style="font-family: inherit;">Back</button>
				<button on:click={saveBilling} disabled={saving} class={btnContinue} style="font-family: inherit;">
					{saving ? 'Saving…' : 'Confirm & Generate Receipt'}
				</button>
			</div>

		<!-- ── STEP 5: Receipt ── -->
		{:else if step === 5}
			<div class="flex flex-col gap-4 receipt-area">
				<!-- Receipt -->
				<div class="border-[1.5px] border-gray-300 rounded-lg p-8 bg-white text-[0.82rem]">
					<p class="text-center text-[0.88rem] font-bold uppercase tracking-[0.03em] mb-5 text-gray-900">
						OFFICIAL RECEIPT / SERVICE INVOICE (BIR COMPLIANT)
					</p>

					<div class="flex justify-between items-start pb-4 border-b-[1.5px] border-gray-200 mb-4">
						<div>
							<p class="font-bold text-[0.92rem] text-gray-900 m-0">Dr. Rosario Veterinary Clinic And Pet Grooming Center</p>
							<p class="text-[0.75rem] text-gray-500 mt-1 m-0">123 Vetcare Street, Quezon City</p>
						</div>
						<div class="text-right">
							<p class="text-[0.72rem] text-gray-500 m-0">Official Receipt No.</p>
							<p class="text-[1.3rem] font-bold text-red-500 m-0">{receiptNo}</p>
							<p class="text-[0.75rem] text-gray-500 m-0">Date: {new Date(selectedConsultation?.Date).toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' })}</p>
						</div>
					</div>

					<div class="grid grid-cols-2 gap-8">
						<!-- Left: Items -->
						<div>
							<p class="text-[0.72rem] font-bold text-gray-500 uppercase tracking-[0.05em] mb-2">IN PAYMENT FOR THE FOLLOWING:</p>
							{#each serviceItems as item}
								<div class="flex justify-between py-[0.18rem] text-gray-700">
									<span>{item.name}</span><span>{peso(item.price * item.qty)}</span>
								</div>
							{/each}
							{#if medicineItems.length > 0}
								<p class="text-[0.72rem] font-bold text-gray-500 uppercase tracking-[0.05em] mt-3 mb-2">
									Medicines <span class="float-right font-normal normal-case">Qty</span>
								</p>
								{#each medicineItems as m}
									<div class="flex justify-between py-[0.18rem] text-gray-700">
										<span>{m.name}</span>
										<span class="mr-8">{m.qty}</span>
										<span>{peso(m.price * m.qty)}</span>
									</div>
								{/each}
							{/if}
							<hr class="border-none border-t border-gray-200 my-2"/>
							<div class="flex justify-between py-[0.18rem] text-gray-700"><span>Gross Sales</span><span>{peso(cartSubtotal)}</span></div>
							<div class="flex justify-between py-[0.18rem] text-gray-700"><span>VAT (12%)</span><span>{peso(vat)}</span></div>
							<hr class="border-none border-t border-gray-200 my-2"/>
							<div class="flex justify-between py-[0.18rem] font-bold text-[0.9rem] text-gray-900">
								<span>TOTAL AMOUNT DUE:</span><span>{peso(grandTotal)}</span>
							</div>
						</div>

						<!-- Right: Recipient -->
						<div>
							<p class="text-[0.72rem] font-bold text-gray-500 uppercase tracking-[0.05em] mb-2">RECEIVED FROM:</p>
							<p class="text-[0.88rem] font-semibold text-gray-900 mb-1 m-0">{selectedConsultation?.OWNERS?.FirstName} {selectedConsultation?.OWNERS?.LastName}</p>
							<p class="text-[0.72rem] text-gray-400 m-0">Address:</p>
							<p class="text-[0.82rem] text-gray-700 mb-2 m-0">{selectedConsultation?.OWNERS?.Address ?? '—'}</p>
							<hr class="border-none border-t border-gray-200 my-2"/>
							<p class="text-[0.82rem] text-gray-700 mb-[0.15rem] m-0"><span class="font-semibold">Patient Name:</span> {selectedConsultation?.PATIENTS?.Name}</p>
							<p class="text-[0.82rem] text-gray-700 mb-[0.15rem] m-0"><span class="font-semibold">Species/Breed:</span> {selectedConsultation?.PATIENTS?.Species} - {selectedConsultation?.PATIENTS?.Breed}</p>
							<hr class="border-none border-t border-gray-200 my-2"/>
							<p class="text-[0.72rem] font-bold text-gray-500 uppercase tracking-[0.05em] mb-1">The Sum of:</p>
							<p class="text-[0.78rem] italic text-gray-700 leading-relaxed">{numberToWords(grandTotal)}</p>
							<div class="mt-8 pt-3 border-t border-gray-200">
								<p class="text-[0.88rem] font-semibold text-gray-900 m-0">Dr. Maria Rosario</p>
								<p class="text-[0.72rem] text-gray-400 m-0">PRC-VET-2015-001234</p>
								<p class="text-[0.72rem] text-gray-400 m-0">Attending Veterinarian</p>
							</div>
						</div>
					</div>
				</div>

				<div class="flex justify-between items-center pt-2 gap-2">
					<button on:click={() => (wizardOpen = false)} class={btnCancel} style="font-family: inherit;">Close</button>
					<div class="flex gap-2 ml-auto">
						<button on:click={() => window.print()}
							class="px-6 py-[0.65rem] border-[1.5px] border-[#0a4f29] bg-white text-[#0a4f29] rounded-lg text-[0.85rem] font-semibold cursor-pointer hover:bg-[#f0fff0]"
							style="font-family: inherit;">🖨 Print</button>
						<button on:click={() => window.print()} class={btnContinue} style="font-family: inherit; margin-left: 0;">⬇ Download PDF</button>
					</div>
				</div>
			</div>
		{/if}
	</div>
</div>
{/if}