// Telegram WebApp Integration
const tg = window.Telegram?.WebApp || null;

if (tg) {
  tg.ready();
  tg.expand();
  if (tg.enableClosingConfirmation) {
    tg.enableClosingConfirmation();
  }
}

// User state
let currentUserId = 123456789; // Default fallback for local testing
let currentUserName = "Mehmon";

if (tg && tg.initDataUnsafe && tg.initDataUnsafe.user) {
  currentUserId = tg.initDataUnsafe.user.id;
  currentUserName = tg.initDataUnsafe.user.first_name || "Foydalanuvchi";
}

const MONTH_NAMES = [
  "Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
  "Iyul", "Avgust", "Sentyabr", "Oktyabr", "Noyabr", "Dekabr"
];

const now = new Date();
let currentYear = now.getFullYear();
let currentMonth = now.getMonth() + 1; // 1-indexed

const CATEGORIES = {
  income: ["💼 Kunlik ish haqi", "🎁 Bonus", "⚡️ Qo'shimcha ish", "💵 Boshqa"],
  expense: ["🍱 Tushlik/Ovqat", "🚖 Yo'l kira", "☕️ Choy-chaqa", "🛠 Ish uchun", "📱 Aloqa", "📦 Boshqa"],
  advance: ["🤝 Naqd avans", "💳 Plastik avans", "🏢 Rahbariyatdan"]
};

let selectedCategory = "";

function formatMoney(amount) {
  return Math.round(amount || 0).toLocaleString('uz-UZ').replace(/,/g, ' ') + " so'm";
}

// Haptic feedback helper
function haptic(type = 'light') {
  if (tg && tg.HapticFeedback) {
    if (type === 'success' || type === 'error') {
      tg.HapticFeedback.notificationOccurred(type);
    } else {
      tg.HapticFeedback.impactOccurred(type);
    }
  }
}

// Init UI
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("userName").textContent = currentUserName;
  document.getElementById("userAvatar").textContent = currentUserName.charAt(0).toUpperCase();

  const formattedDate = now.toLocaleDateString("uz-UZ", { day: "numeric", month: "long" });
  document.getElementById("currentDateBadge").textContent = formattedDate;

  setupTabs();
  setupMonthSelector();
  setupExportSelect();
  loadTodayData();
  loadMonthlyData();

  document.getElementById("refreshBtn").addEventListener("click", () => {
    haptic('light');
    loadTodayData();
    loadMonthlyData();
  });
});

// Setup Tabs
function setupTabs() {
  const tabs = document.querySelectorAll(".tab-btn");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      haptic('light');
      tabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");

      const targetId = tab.dataset.tab;
      document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
      document.getElementById(targetId).classList.add("active");
    });
  });
}

// Setup Month Selector
function setupMonthSelector() {
  updateMonthHeader();

  document.getElementById("prevMonthBtn").addEventListener("click", () => {
    haptic('light');
    currentMonth -= 1;
    if (currentMonth <= 0) {
      currentMonth = 12;
      currentYear -= 1;
    }
    updateMonthHeader();
    loadMonthlyData();
  });

  document.getElementById("nextMonthBtn").addEventListener("click", () => {
    haptic('light');
    currentMonth += 1;
    if (currentMonth > 12) {
      currentMonth = 1;
      currentYear += 1;
    }
    updateMonthHeader();
    loadMonthlyData();
  });
}

function updateMonthHeader() {
  document.getElementById("selectedMonthTitle").textContent = `${MONTH_NAMES[currentMonth - 1]} ${currentYear}`;
}

// Load Today's Data
async function loadTodayData() {
  try {
    const res = await fetch(`/api/summary?user_id=${currentUserId}`);
    if (!res.ok) throw new Error("Yuklab bo'lmadi");
    const data = await res.json();

    document.getElementById("todayNet").textContent = formatMoney(data.net);
    document.getElementById("todayIncome").textContent = formatMoney(data.total_income);
    document.getElementById("todayExpense").textContent = formatMoney(data.total_expense);
    document.getElementById("todayAdvance").textContent = formatMoney(data.total_advance);
    document.getElementById("todayTxCount").textContent = `${data.count || 0} ta`;

    renderTransactions(data.items || []);
  } catch (err) {
    console.error(err);
  }
}

// Render Transactions
function renderTransactions(items) {
  const list = document.getElementById("todayTxList");
  if (!items || items.length === 0) {
    list.innerHTML = '<div class="empty-state">Bugun hali hech qanday amal kiritilmadi.</div>';
    return;
  }

  list.innerHTML = "";
  items.slice().reverse().forEach(item => {
    const isIncome = item.type === 'income';
    const isExpense = item.type === 'expense';
    const icon = isIncome ? '💰' : (isExpense ? '💸' : '🤝');
    const typeClass = item.type;
    const prefix = isIncome ? '+' : (isExpense ? '-' : '🤝');

    const div = document.createElement("div");
    div.className = "tx-item";
    div.innerHTML = `
      <div class="tx-left">
        <div class="tx-icon-box ${typeClass}">${icon}</div>
        <div class="tx-info">
          <h4>${escapeHtml(item.category || (isIncome ? 'Daromad' : 'Xarajat'))}</h4>
          <p>${escapeHtml(item.description || '-')}</p>
        </div>
      </div>
      <div class="tx-right">
        <span class="tx-amount ${typeClass}">${prefix} ${formatMoney(item.amount)}</span>
        <button class="delete-btn" onclick="deleteTx(${item.id})" title="O'chirish">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
        </button>
      </div>
    `;
    list.appendChild(div);
  });
}

// Delete Transaction
async function deleteTx(id) {
  if (!confirm("Haqiqatan ham ushbu amalni o'chirmoqchimisiz?")) return;
  haptic('error');
  try {
    const res = await fetch(`/api/transaction/${id}?user_id=${currentUserId}`, { method: "DELETE" });
    if (res.ok) {
      loadTodayData();
      loadMonthlyData();
    }
  } catch (err) {
    console.error(err);
  }
}

// Load Monthly Data
async function loadMonthlyData() {
  try {
    const res = await fetch(`/api/monthly?user_id=${currentUserId}&year=${currentYear}&month=${currentMonth}`);
    if (!res.ok) throw new Error("Yuklab bo'lmadi");
    const data = await res.json();

    document.getElementById("monthNetSalary").textContent = formatMoney(data.net_with_advance);
    document.getElementById("monthTotalIncome").textContent = formatMoney(data.total_income);
    document.getElementById("monthTotalExpense").textContent = formatMoney(data.total_expense);
    document.getElementById("monthTotalAdvance").textContent = formatMoney(data.total_advance);
    document.getElementById("monthNetProfit").textContent = formatMoney(data.net);

    // Categories
    const catList = document.getElementById("categoriesList");
    if (!data.expense_by_cat || data.expense_by_cat.length === 0) {
      catList.innerHTML = '<div class="empty-state">Bu oyda xarajatlar mavjud emas.</div>';
    } else {
      catList.innerHTML = "";
      const totalExp = data.total_expense || 1;
      data.expense_by_cat.forEach(cat => {
        const pct = Math.round((cat.cat_sum / totalExp) * 100);
        const row = document.createElement("div");
        row.className = "category-row";
        row.innerHTML = `
          <div class="cat-top">
            <strong>${escapeHtml(cat.category || 'Boshqa')}</strong>
            <span>${formatMoney(cat.cat_sum)} (${pct}%)</span>
          </div>
          <div class="progress-bar-bg">
            <div class="progress-bar-fill" style="width: ${pct}%"></div>
          </div>
        `;
        catList.appendChild(row);
      });
    }

    // Daily breakdown
    const dailyList = document.getElementById("dailyBreakdownList");
    if (!data.daily_breakdown || data.daily_breakdown.length === 0) {
      dailyList.innerHTML = '<div class="empty-state">Kunlik amallar yo\\'q.</div>';
    } else {
      dailyList.innerHTML = "";
      data.daily_breakdown.slice(-7).reverse().forEach(day => {
        const item = document.createElement("div");
        item.className = "tx-item";
        item.innerHTML = `
          <div class="tx-info">
            <h4>🗓 ${day.date}</h4>
            <p>Daromad: +${formatMoney(day.day_income)} | Avans: ${formatMoney(day.day_advance)}</p>
          </div>
          <div class="tx-amount expense">-${formatMoney(day.day_expense)}</div>
        `;
        dailyList.appendChild(item);
      });
    }
  } catch (err) {
    console.error(err);
  }
}

// Modal handling
function openAddModal(type) {
  haptic('medium');
  document.getElementById("txType").value = type;
  document.getElementById("txAmount").value = "";
  document.getElementById("txDesc").value = "";
  document.getElementById("customCategory").value = "";

  const title = type === 'income' ? '💰 Daromad qo\'shish' : (type === 'expense' ? '💸 Xarajat qo\'shish' : '🤝 Avans qo\'shish');
  document.getElementById("modalTitle").textContent = title;

  // Render Category Tags
  const tagsContainer = document.getElementById("categoryTags");
  tagsContainer.innerHTML = "";
  selectedCategory = "";

  const list = CATEGORIES[type] || [];
  list.forEach((cat, idx) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "tag-btn" + (idx === 0 ? " active" : "");
    btn.textContent = cat;
    if (idx === 0) selectedCategory = cat;

    btn.addEventListener("click", () => {
      haptic('light');
      document.querySelectorAll(".tag-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      selectedCategory = cat;
    });
    tagsContainer.appendChild(btn);
  });

  document.getElementById("addModal").classList.add("open");
  setTimeout(() => document.getElementById("txAmount").focus(), 100);
}

function closeModal() {
  document.getElementById("addModal").classList.remove("open");
}

function setQuickAmount(addVal) {
  haptic('light');
  const input = document.getElementById("txAmount");
  let current = parseAmount(input.value) || 0;
  input.value = (current + addVal).toLocaleString('uz-UZ').replace(/,/g, ' ');
}

function parseAmount(text) {
  if (!text) return 0;
  let cleaned = text.toString().toLowerCase().replace(/\s/g, '').replace(/,/g, '.');
  let mult = 1;
  if (cleaned.endsWith('k') || cleaned.endsWith('к')) {
    mult = 1000;
    cleaned = cleaned.slice(0, -1);
  } else if (cleaned.endsWith('m') || cleaned.endsWith('mln')) {
    mult = 1000000;
    cleaned = cleaned.replace('mln', '').replace('m', '');
  }
  const val = parseFloat(cleaned);
  return isNaN(val) ? 0 : val * mult;
}

async function handleFormSubmit(e) {
  e.preventDefault();
  const type = document.getElementById("txType").value;
  const amount = parseAmount(document.getElementById("txAmount").value);
  const customCat = document.getElementById("customCategory").value.trim();
  const category = customCat || selectedCategory || "Umumiy";
  const desc = document.getElementById("txDesc").value.trim();

  if (!amount || amount <= 0) {
    alert("Iltimos, to'g'ri summa kiriting!");
    return;
  }

  const submitBtn = document.getElementById("submitBtn");
  submitBtn.disabled = true;

  try {
    const res = await fetch("/api/transaction", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: currentUserId,
        type: type,
        amount: amount,
        category: category,
        description: desc
      })
    });

    if (res.ok) {
      haptic('success');
      closeModal();
      loadTodayData();
      loadMonthlyData();
    } else {
      alert("Xatolik yuz berdi.");
    }
  } catch (err) {
    console.error(err);
    alert("Server bilan aloqa uzildi.");
  } finally {
    submitBtn.disabled = false;
  }
}

// Setup Export Select & Download
function setupExportSelect() {
  const select = document.getElementById("exportMonthSelect");
  select.innerHTML = "";
  for (let offset = 0; offset < 6; offset++) {
    let m = currentMonth - offset;
    let y = currentYear;
    if (m <= 0) {
      m += 12;
      y -= 1;
    }
    const opt = document.createElement("option");
    opt.value = `${y}-${m}`;
    opt.textContent = `${MONTH_NAMES[m - 1]} ${y}`;
    select.appendChild(opt);
  }

  document.getElementById("downloadExcelBtn").addEventListener("click", () => {
    haptic('medium');
    const [y, m] = select.value.split("-");
    window.location.href = `/api/export?user_id=${currentUserId}&year=${y}&month=${m}`;
  });
}

function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
