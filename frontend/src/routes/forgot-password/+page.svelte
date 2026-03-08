<script lang="ts">
  import { goto } from '$app/navigation';

  // ✅ Fully self-contained — no $lib/config import needed
  // Change this one line when you deploy to production
  const API = 'http://localhost:8000';

  const BG_IMAGE = '/Store-Front.png';

  let step = 1;
  let email = '';
  let code = '';
  let newPassword = '';
  let confirmPassword = '';
  let loading = false;
  let error = '';
  let success = '';
  let resetToken = '';

  async function sendCode() {
    error = '';
    loading = true;
    try {
      const res = await fetch(`${API}/auth/forgot-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to send code');
      step = 2;
      success = `A 6-digit code was sent to ${email}`;
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  async function verifyCode() {
    error = '';
    loading = true;
    try {
      const res = await fetch(`${API}/auth/verify-reset-code`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, code })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Invalid or expired code');
      resetToken = data.reset_token;
      step = 3;
      success = '';
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  async function resetPassword() {
    error = '';
    if (newPassword !== confirmPassword) { error = 'Passwords do not match'; return; }
    if (newPassword.length < 6) { error = 'Password must be at least 6 characters'; return; }
    loading = true;
    try {
      const res = await fetch(`${API}/auth/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reset_token: resetToken, new_password: newPassword })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to reset password');
      success = 'Password reset successfully! Redirecting to login…';
      setTimeout(() => goto('/login'), 2000);
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  const stepTitles = ['Forgot Password', 'Enter Code', 'New Password'];
  const stepSubs = [
    "Enter your email and we'll send a reset code",
    'Check your email for the 6-digit code',
    'Create your new password'
  ];

  // Strength meter
  $: strengthLevel = newPassword.length === 0 ? 0 : newPassword.length < 6 ? 1 : newPassword.length < 10 ? 2 : 3;
  $: strengthLabel = ['Enter password', 'Too short', 'Good', 'Strong ✓'][strengthLevel];
  $: strengthBarColor = ['bg-gray-200', 'bg-red-500', 'bg-yellow-400', 'bg-[#0A4F29]'][strengthLevel];

  // Shared input class — fully self-contained, no app.css dependency
  const inputCls = [
    'w-full px-[0.9rem] py-[0.65rem]',
    'border-[1.5px] border-gray-200 rounded-[9px]',
    'text-[0.9rem] bg-[#fafafa] text-gray-900',
    'outline-none box-border',
    'transition-[border-color,box-shadow] duration-[180ms]',
    'focus:border-[#0A4F29] focus:bg-white focus:shadow-[0_0_0_3px_rgba(10,79,41,0.12)]',
    'placeholder:text-gray-400'
  ].join(' ');
</script>

<svelte:head>
  <title>Forgot Password — Dr. Rosario Veterinary</title>
  <link
    href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=DM+Sans:wght@300;400;500&display=swap"
    rel="stylesheet"
  />
</svelte:head>

<!-- Page wrapper -->
<div
  class="min-h-screen flex items-center justify-center relative p-6 box-border"
  style="--bg: url('{BG_IMAGE}')"
>
  <!-- Blurred BG -->
  <div
    class="fixed inset-0 z-0 opacity-60"
    style="background: var(--bg) center/cover no-repeat; filter: blur(5px);"
  ></div>

  <!-- Dark overlay -->
  <div
    class="fixed inset-0 z-[1]"
    style="background: rgba(10,30,15,0.55); backdrop-filter: blur(2px);"
  ></div>

  <!-- Card -->
  <div
    class="relative z-10 w-full max-w-[440px] rounded-[18px] overflow-hidden bg-white"
    style="box-shadow: 0 32px 80px rgba(0,0,0,0.45), 0 0 0 1px rgba(255,255,255,0.08);"
  >
    <!-- Header -->
    <div
      class="flex items-center gap-4 px-7 py-5"
      style="background: linear-gradient(135deg, #0A4F29 0%, #1a6b3c 100%)"
    >
      <div class="w-[52px] h-[52px] rounded-full bg-white flex items-center justify-center flex-shrink-0">
        <img src="/Clinic-Image.png" alt="Logo" class="w-full h-full rounded-full" />
      </div>
      <div class="flex flex-col leading-tight">
        <span
          class="text-white text-[0.9rem] font-bold tracking-[0.04em]"
          style="font-family: 'Cormorant Garamond', serif;"
        >DR. ROSARIO VETERINARY CLINIC</span>
        <span class="text-white/70 text-[0.7rem] tracking-[0.05em] uppercase mt-[2px]">
          AND PET GROOMING CENTER
        </span>
      </div>
    </div>

    <!-- Step indicator -->
    <div class="flex items-center justify-center px-8 pt-5 gap-2">
      {#each [1, 2, 3] as s}
        <div
          class="w-8 h-8 rounded-full border-2 flex items-center justify-center text-xs font-bold flex-shrink-0 transition-all duration-200
            {step > s
              ? 'border-[#0A4F29] bg-[#0A4F29] text-white'
              : step === s
              ? 'border-[#0A4F29] bg-[#F0FFF0] text-[#0A4F29]'
              : 'border-gray-200 bg-white text-gray-400'}"
        >
          {#if step > s}✓{:else}{s}{/if}
        </div>
        {#if s < 3}
          <div
            class="flex-1 h-0.5 rounded-full transition-colors duration-300
              {step > s ? 'bg-[#0A4F29]' : 'bg-gray-200'}"
          ></div>
        {/if}
      {/each}
    </div>

    <!-- Body -->
    <div class="px-8 py-6 pb-8">
      <h1
        class="text-[2rem] font-semibold text-gray-900 mb-1 mt-0"
        style="font-family: 'Cormorant Garamond', serif;"
      >{stepTitles[step - 1]}</h1>
      <p class="text-xs text-gray-500 mb-5">{stepSubs[step - 1]}</p>

      <!-- Error -->
      {#if error}
        <div class="px-4 py-2.5 rounded-lg text-sm mb-4 bg-red-50 text-red-700 border border-red-200">
          {error}
        </div>
      {/if}

      <!-- Success (steps 1 & 2) -->
      {#if success && step <= 2}
        <div class="px-4 py-2.5 rounded-lg text-sm mb-4 bg-[#F0FFF0] text-[#0A4F29] border border-[#A7CDBB]">
          {success}
        </div>
      {/if}

      <!-- ── STEP 1: Email ── -->
      {#if step === 1}
        <form on:submit|preventDefault={sendCode} class="flex flex-col gap-4">
          <div class="flex flex-col gap-1.5">
            <label class="text-xs font-medium text-gray-600" for="email">Email Address</label>
            <div class="relative">
              <svg
                class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"
                viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="15" height="15"
              >
                <path d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
              </svg>
              <input
                id="email"
                type="email"
                placeholder="juan@email.com"
                bind:value={email}
                required
                class="{inputCls} pl-9"
                style="font-family: 'DM Sans', sans-serif;"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            class="w-full py-3 text-white rounded-[10px] text-[0.95rem] font-medium tracking-[0.03em] border-none cursor-pointer transition-[opacity,transform] duration-[180ms] hover:opacity-90 hover:-translate-y-px disabled:opacity-60 disabled:cursor-not-allowed"
            style="background: linear-gradient(135deg, #0A4F29, #1a6b3c); font-family: 'DM Sans', sans-serif;"
          >
            {loading ? 'Sending…' : 'Send Reset Code'}
          </button>

          <a
            href="/login"
            class="text-center text-xs text-gray-500 no-underline hover:text-[#0A4F29] transition-colors"
          >← Back to Login</a>
        </form>

      <!-- ── STEP 2: Verify Code ── -->
      {:else if step === 2}
        <form on:submit|preventDefault={verifyCode} class="flex flex-col gap-4">
          <div class="text-center text-xs text-gray-500 bg-gray-50 rounded-lg py-2 px-3">
            Code sent to <strong>{email}</strong>
          </div>

          <div class="flex flex-col gap-1.5">
            <label class="text-xs font-medium text-gray-600" for="code">6-Digit Code</label>
            <input
              id="code"
              type="text"
              inputmode="numeric"
              maxlength="6"
              placeholder="000000"
              bind:value={code}
              required
              class="{inputCls} text-center text-[2rem] font-bold tracking-[0.5rem] py-4 text-[#0A4F29] border-[#A7CDBB]"
              style="font-family: 'DM Sans', sans-serif;"
            />
          </div>

          <button
            type="submit"
            disabled={loading || code.length < 6}
            class="w-full py-3 text-white rounded-[10px] text-[0.95rem] font-medium tracking-[0.03em] border-none cursor-pointer transition-[opacity,transform] duration-[180ms] hover:opacity-90 hover:-translate-y-px disabled:opacity-60 disabled:cursor-not-allowed"
            style="background: linear-gradient(135deg, #0A4F29, #1a6b3c); font-family: 'DM Sans', sans-serif;"
          >
            {loading ? 'Verifying…' : 'Verify Code'}
          </button>

          <button
            type="button"
            on:click={sendCode}
            disabled={loading}
            class="text-center text-xs text-[#0A4F29] underline bg-transparent border-none cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
            style="font-family: inherit;"
          >
            Didn't receive it? Resend code
          </button>

          <button
            type="button"
            on:click={() => { step = 1; error = ''; success = ''; }}
            class="text-center text-xs text-gray-500 bg-transparent border-none cursor-pointer"
            style="font-family: inherit;"
          >
            ← Change email
          </button>
        </form>

      <!-- ── STEP 3: New Password ── -->
      {:else}
        <form on:submit|preventDefault={resetPassword} class="flex flex-col gap-4">
          {#if success}
            <div class="px-4 py-2.5 rounded-lg text-sm bg-[#F0FFF0] text-[#0A4F29] border border-[#A7CDBB]">
              {success}
            </div>
          {/if}

          <!-- New Password -->
          <div class="flex flex-col gap-1.5">
            <label class="text-xs font-medium text-gray-600" for="np">New Password</label>
            <div class="relative">
              <svg
                class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"
                viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="15" height="15"
              >
                <rect x="3" y="11" width="18" height="11" rx="2"/>
                <path d="M7 11V7a5 5 0 0110 0v4"/>
              </svg>
              <input
                id="np"
                type="password"
                placeholder="New password"
                bind:value={newPassword}
                required
                class="{inputCls} pl-9"
                style="font-family: 'DM Sans', sans-serif;"
              />
            </div>
          </div>

          <!-- Confirm Password -->
          <div class="flex flex-col gap-1.5">
            <label class="text-xs font-medium text-gray-600" for="cp">Confirm Password</label>
            <div class="relative">
              <svg
                class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"
                viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="15" height="15"
              >
                <rect x="3" y="11" width="18" height="11" rx="2"/>
                <path d="M7 11V7a5 5 0 0110 0v4"/>
              </svg>
              <input
                id="cp"
                type="password"
                placeholder="Repeat password"
                bind:value={confirmPassword}
                required
                class="{inputCls} pl-9"
                style="font-family: 'DM Sans', sans-serif;"
              />
            </div>
          </div>

          <!-- Strength bar -->
          <div class="flex items-center gap-3">
            <div class="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
              <div
                class="h-full rounded-full transition-all duration-300 {strengthBarColor}"
                style="width: {Math.min(100, newPassword.length * 10)}%"
              ></div>
            </div>
            <span class="text-xs text-gray-500 whitespace-nowrap">{strengthLabel}</span>
          </div>

          <button
            type="submit"
            disabled={loading}
            class="w-full py-3 text-white rounded-[10px] text-[0.95rem] font-medium tracking-[0.03em] border-none cursor-pointer transition-[opacity,transform] duration-[180ms] hover:opacity-90 hover:-translate-y-px disabled:opacity-60 disabled:cursor-not-allowed"
            style="background: linear-gradient(135deg, #0A4F29, #1a6b3c); font-family: 'DM Sans', sans-serif;"
          >
            {loading ? 'Resetting…' : 'Reset Password'}
          </button>
        </form>
      {/if}
    </div>
  </div>
</div>