<script lang="ts">
	import { goto } from '$app/navigation';

	const BG_IMAGE = '/Store-Front.png';

	let mode: 'login' | 'register' = 'login';

	let username = '';
	let password = '';

	let firstName = '';
	let middleName = '';
	let lastName = '';
	let email = '';
	let regPassword = '';
	let confirmPassword = '';
	let birthday = '';
	let age: number | '' = '';
	let phoneNumber = '';
	let role: 'receptionist' | 'veterinary' = 'receptionist';

	let error = '';
	let success = '';
	let loading = false;

	async function handleLogin() {
		error = '';
		loading = true;
		try {
			const res = await fetch('http://localhost:8000/auth/login', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ username, password })
			});
			const data = await res.json();
			if (!res.ok) throw new Error(data.detail || 'Login failed');
			localStorage.setItem('access_token', data.access_token);
			localStorage.setItem('role', data.role);
			goto('/Billing-Financial/dashboard');
		} catch (e: any) {
			error = e.message;
		} finally {
			loading = false;
		}
	}

	async function handleRegister() {
		error = '';
		success = '';
		if (regPassword !== confirmPassword) {
			error = 'Passwords do not match';
			return;
		}
		loading = true;
		try {
			const res = await fetch('http://localhost:8000/auth/register', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					first_name: firstName,
					middle_name: middleName,
					last_name: lastName,
					username: email,
					password: regPassword,
					role,
					birthday: birthday || null,
					age: age !== '' ? Number(age) : null,
					phone_number: phoneNumber || null
				})
			});
			const data = await res.json();
			if (!res.ok) throw new Error(data.detail || 'Registration failed');
			success = 'Account created! You can now log in.';
			mode = 'login';
			firstName = middleName = lastName = email = regPassword = confirmPassword = birthday = phoneNumber = '';
			age = '';
		} catch (e: any) {
			error = e.message;
		} finally {
			loading = false;
		}
	}

	function switchMode(m: 'login' | 'register') {
		mode = m;
		error = '';
		success = '';
	}

	// Shared input class to avoid repetition
	const inputClass =
		"w-full px-[0.9rem] py-[0.65rem] border-[1.5px] border-gray-200 rounded-[9px] text-[0.9rem] bg-[#fafafa] text-gray-900 outline-none box-border transition-[border-color,box-shadow] duration-[180ms] focus:border-[#2d6a4f] focus:bg-white focus:shadow-[0_0_0_3px_rgba(45,106,79,0.12)] placeholder:text-gray-400";
</script>

<svelte:head>
	<title>{mode === 'login' ? 'Log In' : 'Register'} — Dr. Rosario Veterinary</title>
	<link
		href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=DM+Sans:wght@300;400;500&display=swap"
		rel="stylesheet"
	/>
</svelte:head>

<!-- Page -->
<div
	class="min-h-screen flex items-center justify-center relative p-6 box-border"
	style="--bg: url('{BG_IMAGE}')"
>
	<!-- Blurred BG image -->
	<div
		class="fixed inset-0 z-0 opacity-60"
		style="background: var(--bg) center / cover no-repeat; filter: blur(5px);"
	></div>

	<!-- Dark overlay -->
	<div
		class="fixed inset-0 z-[1]"
		style="background: rgba(10, 30, 15, 0.55); backdrop-filter: blur(2px);"
	></div>

	<!-- Card -->
	<div
		class="relative z-10 w-full rounded-[18px] overflow-hidden bg-white transition-[max-width] duration-[350ms] ease-in-out"
		style="
			max-width: {mode === 'register' ? '660px' : '440px'};
			box-shadow: 0 32px 80px rgba(0,0,0,0.45), 0 0 0 1px rgba(255,255,255,0.08);
		"
	>
		<!-- Header -->
		<div
			class="flex items-center gap-4 px-7 py-5"
			style="background: linear-gradient(135deg, #1a4731 0%, #2d6a4f 100%)"
		>
			<div class="w-[52px] h-[52px] rounded-full bg-white flex items-center justify-center flex-shrink-0">
				<img
					src="/Clinic-Image.png"
					alt="Clinic Logo"
					class="w-full h-full rounded-full"
					style="transform: translateY(1.5px);"
				/>
			</div>
			<div class="flex flex-col leading-tight">
				<span
					class="text-white text-[0.9rem] font-bold tracking-[0.04em]"
					style="font-family: 'Cormorant Garamond', serif;"
				>
					DR. ROSARIO VETERINARY CLINIC
				</span>
				<span class="text-white/70 text-[0.7rem] tracking-[0.05em] uppercase mt-[2px]">
					AND PET GROOMING CENTER
				</span>
			</div>
		</div>

		<!-- Body -->
		<div class="px-8 py-8 pb-9">
			<h1
				class="text-center mb-6 text-gray-900 text-[2.4rem] font-semibold tracking-[-0.01em] m-0"
				style="font-family: 'Cormorant Garamond', serif;"
			>
				{mode === 'login' ? 'Log in' : 'Register'}
			</h1>

			<!-- Alerts -->
			{#if error}
				<div class="px-4 py-2.5 rounded-lg text-[0.85rem] mb-4 bg-red-50 text-red-700 border border-red-200">
					{error}
				</div>
			{/if}
			{#if success}
				<div class="px-4 py-2.5 rounded-lg text-[0.85rem] mb-4 bg-[#f0fdf4] text-green-800 border border-green-200">
					{success}
				</div>
			{/if}

			<!-- ── LOGIN ── -->
			{#if mode === 'login'}
				<form on:submit|preventDefault={handleLogin} class="flex flex-col gap-4">

					<div class="flex flex-col gap-[0.35rem]">
						<label for="username" class="text-[0.8rem] font-medium text-gray-700 tracking-[0.02em]">
							Email / Username
						</label>
						<input
							id="username"
							type="text"
							placeholder="Enter your email"
							bind:value={username}
							required
							autocomplete="username"
							class={inputClass}
							style="font-family: 'DM Sans', sans-serif;"
						/>
					</div>

					<div class="flex flex-col gap-[0.35rem]">
						<label for="password" class="text-[0.8rem] font-medium text-gray-700 tracking-[0.02em]">
							Password
						</label>
						<input
							id="password"
							type="password"
							placeholder="Enter your password"
							bind:value={password}
							required
							autocomplete="current-password"
							class={inputClass}
							style="font-family: 'DM Sans', sans-serif;"
						/>
					</div>

					<a
						href="../forgot-password"
						class="self-end text-[0.8rem] font-medium text-[#2d6a4f] no-underline -mt-1 hover:underline"
					>
						Forgot Password?
					</a>

					<button
						type="submit"
						disabled={loading}
						class="w-full py-[0.8rem] mt-1 text-white rounded-[10px] text-[0.95rem] font-medium tracking-[0.03em] cursor-pointer border-none transition-[opacity,transform] duration-[180ms] hover:opacity-90 hover:-translate-y-px disabled:opacity-60 disabled:cursor-not-allowed"
						style="background: linear-gradient(135deg, #1a4731, #2d6a4f); font-family: 'DM Sans', sans-serif;"
					>
						{loading ? 'Logging in…' : 'Login'}
					</button>

					<p class="text-center text-[0.82rem] text-gray-500 m-0">
						Don't have an account?
						<button
							type="button"
							on:click={() => switchMode('register')}
							class="bg-transparent border-none p-0 text-[#2d6a4f] font-semibold cursor-pointer text-[inherit] hover:underline"
							style="font-family: inherit;"
						>
							Register here
						</button>
					</p>
				</form>

			<!-- ── REGISTER ── -->
			{:else}
				<form on:submit|preventDefault={handleRegister} class="flex flex-col gap-4">

					<!-- First / Middle / Last -->
					<div class="grid gap-3" style="grid-template-columns: 1fr 1fr 1fr;">
						{#each [
							{ id: 'firstName', label: 'First Name', ph: 'Juan', bind: firstName, req: true },
							{ id: 'middleName', label: 'Middle Name', ph: 'Santos', bind: middleName, req: false },
							{ id: 'lastName', label: 'Last Name', ph: 'Dela Cruz', bind: lastName, req: true }
						] as f}
							<div class="flex flex-col gap-[0.35rem]">
								<label for={f.id} class="text-[0.8rem] font-medium text-gray-700 tracking-[0.02em]">
									{f.label}{#if f.req}<span class="text-red-500"> *</span>{/if}
								</label>
								{#if f.id === 'firstName'}
									<input id="firstName" type="text" placeholder={f.ph} bind:value={firstName} required class={inputClass} style="font-family:'DM Sans',sans-serif;"/>
								{:else if f.id === 'middleName'}
									<input id="middleName" type="text" placeholder={f.ph} bind:value={middleName} class={inputClass} style="font-family:'DM Sans',sans-serif;"/>
								{:else}
									<input id="lastName" type="text" placeholder={f.ph} bind:value={lastName} required class={inputClass} style="font-family:'DM Sans',sans-serif;"/>
								{/if}
							</div>
						{/each}
					</div>

					<!-- Email / Phone -->
					<div class="grid grid-cols-2 gap-[0.85rem]">
						<div class="flex flex-col gap-[0.35rem]">
							<label for="reg-email" class="text-[0.8rem] font-medium text-gray-700 tracking-[0.02em]">
								Email <span class="text-red-500">*</span>
							</label>
							<input id="reg-email" type="text" placeholder="juan@email.com" bind:value={email} required autocomplete="username" class={inputClass} style="font-family:'DM Sans',sans-serif;"/>
						</div>
						<div class="flex flex-col gap-[0.35rem]">
							<label for="phone" class="text-[0.8rem] font-medium text-gray-700 tracking-[0.02em]">Phone Number</label>
							<input id="phone" type="tel" placeholder="09XX-XXX-XXXX" bind:value={phoneNumber} class={inputClass} style="font-family:'DM Sans',sans-serif;"/>
						</div>
					</div>

					<!-- Birthday / Age -->
					<div class="grid grid-cols-2 gap-[0.85rem]">
						<div class="flex flex-col gap-[0.35rem]">
							<label for="birthday" class="text-[0.8rem] font-medium text-gray-700 tracking-[0.02em]">Birthday</label>
							<input id="birthday" type="date" bind:value={birthday} class={inputClass} style="font-family:'DM Sans',sans-serif;"/>
						</div>
						<div class="flex flex-col gap-[0.35rem]">
							<label for="age" class="text-[0.8rem] font-medium text-gray-700 tracking-[0.02em]">Age</label>
							<input id="age" type="number" placeholder="e.g. 30" min="1" max="120" bind:value={age} class={inputClass} style="font-family:'DM Sans',sans-serif;"/>
						</div>
					</div>

					<!-- Password / Confirm -->
					<div class="grid grid-cols-2 gap-[0.85rem]">
						<div class="flex flex-col gap-[0.35rem]">
							<label for="reg-password" class="text-[0.8rem] font-medium text-gray-700 tracking-[0.02em]">
								Password <span class="text-red-500">*</span>
							</label>
							<input id="reg-password" type="password" placeholder="Create password" bind:value={regPassword} required autocomplete="new-password" class={inputClass} style="font-family:'DM Sans',sans-serif;"/>
						</div>
						<div class="flex flex-col gap-[0.35rem]">
							<label for="confirm-password" class="text-[0.8rem] font-medium text-gray-700 tracking-[0.02em]">
								Confirm Password <span class="text-red-500">*</span>
							</label>
							<input id="confirm-password" type="password" placeholder="Repeat password" bind:value={confirmPassword} required autocomplete="new-password" class={inputClass} style="font-family:'DM Sans',sans-serif;"/>
						</div>
					</div>

					<!-- Role -->
					<div class="flex flex-col gap-[0.35rem]">
						<label for="role" class="text-[0.8rem] font-medium text-gray-700 tracking-[0.02em]">
							Role <span class="text-red-500">*</span>
						</label>
						<select id="role" bind:value={role} class={inputClass} style="font-family:'DM Sans',sans-serif;">
							<option value="receptionist">Receptionist</option>
							<option value="veterinary">Veterinary</option>
						</select>
					</div>

					<button
						type="submit"
						disabled={loading}
						class="w-full py-[0.8rem] mt-1 text-white rounded-[10px] text-[0.95rem] font-medium tracking-[0.03em] cursor-pointer border-none transition-[opacity,transform] duration-[180ms] hover:opacity-90 hover:-translate-y-px disabled:opacity-60 disabled:cursor-not-allowed"
						style="background: linear-gradient(135deg, #1a4731, #2d6a4f); font-family: 'DM Sans', sans-serif;"
					>
						{loading ? 'Creating account…' : 'Create Account'}
					</button>

					<p class="text-center text-[0.82rem] text-gray-500 m-0">
						Already have an account?
						<button
							type="button"
							on:click={() => switchMode('login')}
							class="bg-transparent border-none p-0 text-[#2d6a4f] font-semibold cursor-pointer text-[inherit] hover:underline"
							style="font-family: inherit;"
						>
							Log in here
						</button>
					</p>
				</form>
			{/if}
		</div>
	</div>
</div>