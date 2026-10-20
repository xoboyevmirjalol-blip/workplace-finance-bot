// Telegram WebApp SDK
const tg = window.Telegram?.WebApp || null;

if (tg) {
  tg.ready();
  tg.expand();
  if (tg.enableClosingConfirmation) {
    tg.enableClosingConfirmation();
  }
}

// User state
let currentUserId = 123456789;
let currentUserName = "Foydalanuvchi";

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
let activeTab = "tab-dashboard";

// Foydalanuvchi bergan maxsus buyumlar katalogi va belgilangan narxlari
const YASALGAN_CATALOG = [
  { name: "Twix", price: 10000 },
  { name: "Twix panarama", price: 12000 },
  { name: "A4", price: 7000 },
  { name: "A4 panarama", price: 10000 },
  { name: "Albom", price: 12000 },
  { name: "Katta karopka", price: 100000 },
  { name: "Kichik karopka", price: 10000 },
  { name: "Plastik 2 list", price: 2000 },
  { name: "Plastik 3 list", price: 3000 },
  { name: "Plastik 4 list", price: 4000 },
  { name: "Plastik 5 list", price: 5000 },
  { name: "Xardcover", price: 10000 }
];

// Montajlar bo'limi uchun maxsus katalog va belgilangan narxlar
const MONTAJ_CATALOG = [
  { name: "Twix", price: 10000 },
  { name: "Twix panarama", price: 10000 },
  { name: "A4", price: 7000 },
  { name: "A4 panarama", price: 7000 },
  { name: "Plastik 2 list", price: 5000 },
  { name: "Plastik 3 list", price: 7000 },
  { name: "Plastik 4 list", price: 8000 },
  { name: "Plastik 5 list", price: 9000 },
  { name: "Albom", price: 40000 },
  { name: "Xardcover 3 list", price: 7000 },
  { name: "Xardcover 4 list", price: 8000 },
  { name: "Xardcover", price: 10000 },
  { name: "Palma albom", price: 25000 }
];

const SECTION_CONFIG = {
  yasalgan: {
    title: "🔨 Yasalgan buyum qo'shish",
    labelAmount: "Jami hisoblangan summa (so'm):",
    labelCategory: "Buyum turini tanlang:",
    labelDescription: "",
    colorClass: "text-yasalgan",
    icon: "🔨"
  },
  montaj: {
    title: "🔧 Montaj ishi qo'shish",
    labelAmount: "Jami hisoblangan summa (so'm):",
    labelCategory: "Montaj turini tanlang:",
    labelDescription: "",
    colorClass: "text-montaj",
    icon: "🔧"
  },
  income: {
    title: "💰 Daromad qo'shish",
    labelAmount: "Daromad summasi (so'mda):",
    labelCategory: "Toifa:",
    labelDescription: "Qo'shimcha izoh:",
    defaultTags: ["Kunlik ish haqi", "Bonus", "Qo'shimcha tushum", "Boshqa"],
    colorClass: "text-income",
    icon: "💰"
  },
  expense: {
    title: "💸 Xarajat qo'shish",
    labelAmount: "Xarajat summasi (so'mda):",
    labelCategory: "Xarajat toifasi:",
    labelDescription: "Izoh (masalan: Tushlik osh, yo'l kira):",
    defaultTags: ["Materiallar", "Asbob-anjom", "Tushlik", "Yo'l kira", "Choy-chaqa", "Boshqa"],
    colorClass: "text-expense",
    icon: "💸"
  },
  advance: {
    title: "🤝 Avans qo'shish",
    labelAmount: "Olingan avans summasi (so'mda):",
    labelCategory: "Qayerdan olindi:",
    labelDescription: "Izoh:",
    defaultTags: ["Naqd kassa", "Plastik karta", "Rahbariyatdan"],
    colorClass: "text-advance",
    icon: "🤝"
  }
};

let activeModalType = "yasalgan";
let selectedTag = "";
let currentUnitPrice = 10000;
let currentQuantity = 1;

function formatMoney(amount) {
  return Math.round(amount || 0).toLocaleString('uz-UZ').replace(/,/g, ' ') + " so'm";
}

function haptic(type = 'light') {
  if (tg && tg.HapticFeedback) {
    if (type === 'success' || type === 'error') {
      tg.HapticFeedback.notificationOccurred(type);
    } else {
      tg.HapticFeedback.impactOccurred(type);
    }
  }
}

// App Initialization
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("userName").textContent = currentUserName;
  document.getElementById("userAvatar").textContent = currentUserName.charAt(0).toUpperCase();
  document.getElementById("currentDateText").textContent = now.toLocaleDateString("uz-UZ", { day: "numeric", month: "long" });
  document.getElementById("entryDate").value = now.toISOString().split("T")[0];

  setupMonthNav();
  setupTabs();
  setupExcelSelect();
  loadAllData();

  document.getElementById("reloadBtn").addEventListener("click", () => {
    haptic('light');
    loadAllData();
  });
});

// Month Nav
function setupMonthNav() {
  updateMonthHeader();

  document.getElementById("prevMonthBtn").addEventListener("click", () => {
    haptic('light');
    currentMonth -= 1;
    if (currentMonth <= 0) {
      currentMonth = 12;
      currentYear -= 1;
    }
    updateMonthHeader();
    loadAllData();
  });

  document.getElementById("nextMonthBtn").addEventListener("click", () => {
    haptic('light');
    currentMonth += 1;
    if (currentMonth > 12) {
      currentMonth = 1;
      currentYear += 1;
    }
    updateMonthHeader();
    loadAllData();
  });
}

function updateMonthHeader() {
  document.getElementById("monthDisplay").textContent = `${MONTH_NAMES[currentMonth - 1]} ${currentYear}`;
}

// Tabs setup
function setupTabs() {
  const tabButtons = document.querySelectorAll(".tab-item");
  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const target = btn.dataset.tab;
      switchTab(target);
    });
  });
}

function switchTab(tabId) {
  haptic('light');
  activeTab = tabId;

  // Buttons
  document.querySelectorAll(".tab-item").forEach(b => {
    if (b.dataset.tab === tabId) {
      b.classList.add("active");
      b.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" });
    } else {
      b.classList.remove("active");
    }
  });

  // Pages
  document.querySelectorAll(".tab-page").forEach(p => p.classList.remove("active"));
  const activePage = document.getElementById(tabId);
  if (activePage) activePage.classList.add("active");

  // Load specific tab data if needed
  if (tabId === "tab-yasalgan") loadSectionList("yasalgan", "yasalganList", "yasalganPageSub");
  else if (tabId === "tab-montaj") loadSectionList("montaj", "montajList", "montajPageSub");
  else if (tabId === "tab-income") loadSectionList("income", "incomeList", "incomePageSub");
  else if (tabId === "tab-expense") loadSectionList("expense", "expenseList", "expensePageSub");
  else if (tabId === "tab-advance") loadSectionList("advance", "advanceList", "advancePageSub");
}

// Load All Data
async function loadAllData() {
  await loadDashboard();
  if (activeTab === "tab-yasalgan") loadSectionList("yasalgan", "yasalganList", "yasalganPageSub");
  else if (activeTab === "tab-montaj") loadSectionList("montaj", "montajList", "montajPageSub");
  else if (activeTab === "tab-income") loadSectionList("income", "incomeList", "incomePageSub");
  else if (activeTab === "tab-expense") loadSectionList("expense", "expenseList", "expensePageSub");
  else if (activeTab === "tab-advance") loadSectionList("advance", "advanceList", "advancePageSub");
}

// Load Dashboard Overview
async function loadDashboard() {
  try {
    const res = await fetch(`/api/overview?user_id=${currentUserId}&year=${currentYear}&month=${currentMonth}`);
    if (!res.ok) throw new Error("Dashboard yuklanmadi");
    const data = await res.json();

    // Badges
    document.getElementById("badgeYasalgan").textContent = data.yasalgan.count || 0;
    document.getElementById("badgeMontaj").textContent = data.montaj.count || 0;
    document.getElementById("badgeIncome").textContent = data.income.count || 0;
    document.getElementById("badgeExpense").textContent = data.expense.count || 0;
    document.getElementById("badgeAdvance").textContent = data.advance.count || 0;

    // Dashboard values
    document.getElementById("dashNetSalary").textContent = formatMoney(data.net_salary);
    document.getElementById("dashTotalYasalgan").textContent = formatMoney(data.yasalgan.total);
    document.getElementById("dashCountYasalgan").textContent = `${data.yasalgan.count} ta buyum`;
    
    document.getElementById("dashTotalMontaj").textContent = formatMoney(data.montaj.total);
    document.getElementById("dashCountMontaj").textContent = `${data.montaj.count} ta ob'yekt`;

    document.getElementById("dashTotalIncome").textContent = formatMoney(data.income.total);
    document.getElementById("dashCountIncome").textContent = `${data.income.count} ta tushum`;

    document.getElementById("dashTotalExpense").textContent = formatMoney(data.expense.total);
    document.getElementById("dashCountExpense").textContent = `${data.expense.count} ta sarf`;

    document.getElementById("dashTotalAdvance").textContent = formatMoney(data.advance.total);
    document.getElementById("dashCountAdvance").textContent = `${data.advance.count} ta avans`;

    document.getElementById("dashNetProfit").textContent = formatMoney(data.net_profit);

    // Monthly Analysis Page Values
    document.getElementById("mNetSalary").textContent = formatMoney(data.net_salary);
    document.getElementById("mTotalYasalgan").textContent = formatMoney(data.yasalgan.total);
    document.getElementById("mTotalMontaj").textContent = formatMoney(data.montaj.total);
    document.getElementById("mTotalIncome").textContent = formatMoney(data.income.total);
    document.getElementById("mTotalExpense").textContent = formatMoney(data.expense.total);
    document.getElementById("mTotalAdvance").textContent = formatMoney(data.advance.total);
    document.getElementById("mNetProfit").textContent = formatMoney(data.net_profit);

    // Expense Categories Breakdown
    renderExpenseCategories(data.expense_by_cat || [], data.expense.total || 0);

    // Recent items feed
    renderRecentFeed(data.recent_items || []);
  } catch (err) {
    console.error(err);
  }
}

// Render Recent Feed on Dashboard
function renderRecentFeed(items) {
  const container = document.getElementById("dashRecentList");
  if (!items || items.length === 0) {
    container.innerHTML = '<div class="empty-hint">Hozircha amallar kiritilmagan.</div>';
    return;
  }

  container.innerHTML = "";
  items.slice(0, 10).forEach(item => {
    container.appendChild(createItemElement(item));
  });
}

// Load Section List (Yasalgan, Montaj, etc.)
async function loadSectionList(type, listId, subId) {
  try {
    const res = await fetch(`/api/items?user_id=${currentUserId}&type=${type}&year=${currentYear}&month=${currentMonth}`);
    if (!res.ok) throw new Error("Yuklanmadi");
    const data = await res.json();

    const subElem = document.getElementById(subId);
    if (subElem) {
      subElem.textContent = `Oylik jami: ${formatMoney(data.total)} (${data.count} ta)`;
    }

    const listElem = document.getElementById(listId);
    if (!listElem) return;

    if (!data.items || data.items.length === 0) {
      listElem.innerHTML = '<div class="empty-hint">Ushbu oyda hech narsa kiritilmagan.</div>';
      return;
    }

    listElem.innerHTML = "";
    data.items.forEach(item => {
      listElem.appendChild(createItemElement(item));
    });
  } catch (err) {
    console.error(err);
  }
}

// Create Item Element for lists
function createItemElement(item) {
  const cfg = SECTION_CONFIG[item.type] || SECTION_CONFIG.income;
  const isMinus = item.type === 'expense';
  const prefix = isMinus ? '-' : '+';
  const sumColorClass = cfg.colorClass;

  const div = document.createElement("div");
  div.className = "feed-item";
  div.innerHTML = `
    <div class="item-left">
      <div class="item-icon">${cfg.icon}</div>
      <div class="item-texts">
        <h4>${escapeHtml(item.category || cfg.title)}</h4>
        <p>${escapeHtml(item.description || '-')} &bull; <small>${item.date}</small></p>
      </div>
    </div>
    <div class="item-right">
      <span class="item-sum ${sumColorClass}">${prefix}${formatMoney(item.amount)}</span>
      <button class="del-btn" onclick="deleteEntry(${item.id})" title="O'chirish">
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
      </button>
    </div>
  `;
  return div;
}

// Delete Entry
async function deleteEntry(id) {
  if (!confirm("Ushbu yozuvni o'chirmoqchimisiz?")) return;
  haptic('error');
  try {
    const res = await fetch(`/api/entry/${id}?user_id=${currentUserId}`, { method: "DELETE" });
    if (res.ok) {
      loadAllData();
    }
  } catch (err) {
    console.error(err);
  }
}

// Render Expense Categories
function renderExpenseCategories(categories, totalExp) {
  const container = document.getElementById("mExpenseCategories");
  if (!categories || categories.length === 0) {
    container.innerHTML = '<div class="empty-hint">Xarajatlar mavjud emas.</div>';
    return;
  }

  container.innerHTML = "";
  const total = totalExp || 1;
  categories.forEach(cat => {
    const pct = Math.round((cat.cat_sum / total) * 100);
    const row = document.createElement("div");
    row.className = "cat-bar-item";
    row.innerHTML = `
      <div class="cat-bar-head">
        <strong>${escapeHtml(cat.category || 'Boshqa')}</strong>
        <span>${formatMoney(cat.cat_sum)} (${pct}%)</span>
      </div>
      <div class="cat-bar-track">
        <div class="cat-bar-progress" style="width: ${pct}%"></div>
      </div>
    `;
    container.appendChild(row);
  });
}

// Open Modal
function openAddModal(type) {
  haptic('medium');
  activeModalType = type;
  const cfg = SECTION_CONFIG[type] || SECTION_CONFIG.income;

  document.getElementById("entryType").value = type;
  document.getElementById("modalHeading").textContent = cfg.title;
  document.getElementById("labelAmount").textContent = cfg.labelAmount;
  document.getElementById("labelCategory").textContent = cfg.labelCategory;

  document.getElementById("entryAmount").value = "";
  document.getElementById("customCatInput").value = "";
  document.getElementById("entryDescription").value = "";
  document.getElementById("entryDate").value = now.toISOString().split("T")[0];

  const fieldQty = document.getElementById("fieldQuantity");
  const fieldDesc = document.getElementById("fieldDescription");
  const calcCard = document.getElementById("calcPreviewCard");
  const quickAmountsRow = document.getElementById("quickAmountsRow");
  const tagsContainer = document.getElementById("categoryTags");
  tagsContainer.innerHTML = "";
  selectedTag = "";

  if (type === 'yasalgan' || type === 'montaj') {
    // YASALGAN va MONTAJ: Soni va avto-hisoblash faol, Izoh olib tashlanadi
    fieldQty.style.display = "block";
    calcCard.style.display = "flex";
    fieldDesc.style.display = "none"; // Izohni olib tashlaymiz
    quickAmountsRow.style.display = "none"; // Summa avtomatik hisoblanadi

    currentQuantity = 1;
    document.getElementById("entryQuantity").value = 1;

    const catalog = (type === 'yasalgan') ? YASALGAN_CATALOG : MONTAJ_CATALOG;

    // Mahsulotlar va narxlari ro'yxati
    catalog.forEach((item, idx) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "tag-pill" + (idx === 0 ? " active" : "");
      btn.innerHTML = `${item.name} <span class="tag-price">${item.price.toLocaleString('uz-UZ')}</span>`;
      
      if (idx === 0) {
        selectedTag = item.name;
        currentUnitPrice = item.price;
      }

      btn.addEventListener("click", () => {
        haptic('light');
        document.querySelectorAll(".tag-pill").forEach(p => p.classList.remove("active"));
        btn.classList.add("active");
        selectedTag = item.name;
        currentUnitPrice = item.price;
        recalculateQuantityPrice();
      });
      tagsContainer.appendChild(btn);
    });

    recalculateQuantityPrice();
  } else {
    // Boshqa bo'limlar (Daromad, Xarajat, Avans)
    fieldQty.style.display = "none";
    calcCard.style.display = "none";
    fieldDesc.style.display = "block";
    quickAmountsRow.style.display = "flex";
    document.getElementById("labelDescription").textContent = cfg.labelDescription;

    (cfg.defaultTags || []).forEach((tag, idx) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "tag-pill" + (idx === 0 ? " active" : "");
      btn.textContent = tag;
      if (idx === 0) selectedTag = tag;

      btn.addEventListener("click", () => {
        haptic('light');
        document.querySelectorAll(".tag-pill").forEach(p => p.classList.remove("active"));
        btn.classList.add("active");
        selectedTag = tag;
      });
      tagsContainer.appendChild(btn);
    });
  }

  document.getElementById("addModal").classList.add("show");
  if (type !== 'yasalgan' && type !== 'montaj') {
    setTimeout(() => document.getElementById("entryAmount").focus(), 120);
  }
}

// Stepper & Quantity Handlers
function stepQty(delta) {
  haptic('light');
  let q = parseInt(document.getElementById("entryQuantity").value) || 1;
  q = Math.max(1, q + delta);
  document.getElementById("entryQuantity").value = q;
  currentQuantity = q;
  recalculateQuantityPrice();
}

function setQty(val) {
  haptic('light');
  document.getElementById("entryQuantity").value = val;
  currentQuantity = val;
  recalculateQuantityPrice();
}

function onQtyChange() {
  let val = parseInt(document.getElementById("entryQuantity").value);
  if (isNaN(val) || val < 1) val = 1;
  currentQuantity = val;
  recalculateQuantityPrice();
}

function recalculateQuantityPrice() {
  if (activeModalType !== 'yasalgan' && activeModalType !== 'montaj') return;
  const total = currentQuantity * currentUnitPrice;
  document.getElementById("calcFormula").textContent = `${currentQuantity} ta × ${currentUnitPrice.toLocaleString('uz-UZ')} so'm`;
  document.getElementById("calcTotal").textContent = `${total.toLocaleString('uz-UZ')} so'm`;
  document.getElementById("entryAmount").value = total.toLocaleString('uz-UZ').replace(/,/g, ' ');
}

function closeModal() {
  document.getElementById("addModal").classList.remove("show");
}

function addAmountVal(val) {
  haptic('light');
  const input = document.getElementById("entryAmount");
  let current = parseNumber(input.value) || 0;
  input.value = (current + val).toLocaleString('uz-UZ').replace(/,/g, ' ');
}

function parseNumber(text) {
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

// Form Submit
async function handleFormSubmit(e) {
  e.preventDefault();
  const type = document.getElementById("entryType").value;
  const amount = parseNumber(document.getElementById("entryAmount").value);
  const customCat = document.getElementById("customCatInput").value.trim();
  const category = customCat || selectedTag || "Umumiy";
  const dateVal = document.getElementById("entryDate").value || now.toISOString().split("T")[0];

  let desc = "";
  if (type === 'yasalgan' || type === 'montaj') {
    desc = `${currentQuantity} dona (${currentUnitPrice.toLocaleString('uz-UZ')} so'm)`;
  } else {
    desc = document.getElementById("entryDescription").value.trim();
  }

  if (!amount || amount <= 0) {
    alert("Iltimos, to'g'ri summa kiriting!");
    return;
  }

  const btn = document.getElementById("saveSubmitBtn");
  btn.disabled = true;

  try {
    const res = await fetch("/api/entry", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: currentUserId,
        type: type,
        amount: amount,
        category: category,
        description: desc,
        date: dateVal
      })
    });

    if (res.ok) {
      haptic('success');
      closeModal();
      loadAllData();
    } else {
      alert("Xatolik yuz berdi.");
    }
  } catch (err) {
    console.error(err);
    alert("Server bilan aloqa uzildi.");
  } finally {
    btn.disabled = false;
  }
}

// Excel Select Setup
function setupExcelSelect() {
  const select = document.getElementById("excelMonthSelect");
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
