# 💼 Ishxona Hisob-Kitob Telegram Boti

Ishxonada kunlik daromad, xarajatlar va olingan avanslarni hisoblab borish, kunlik va 1 oylik to'liq statistika hamda Excel (.xlsx) hisobot tayyorlab beruvchi qulay Telegram bot.

---

## 🌟 Imkoniyatlar

1. 💰 **Kunlik daromadlarni kiritish** (kunlik ish haqi, bonuslar, qo'shimcha ish tushumlari).
2. 💸 **Kunlik xarajatlarni kiritish** (tushlik, yo'l kira, choy-chaqa, ish qurollari va boshqalar).
3. 🤝 **Ishxonadan olingan avanslarni kiritish** (naqd yoki plastik karta orqali olingan avanslar).
4. 📊 **Bugungi hisobot:**
   - Jami daromad, jami xarajat, jami olingan avans
   - Kunlik sof qoldiq
   - Bugungi barcha amallar ro'yxati
5. 📈 **Oylik statistika & hisob-kitob:**
   - 1 oylik jami daromad, xarajat va avanslar
   - Sof foyda va ishxonadan olinishi kerak bo'lgan qoldiq maosh
   - Xarajatlar toifalari bo'yicha foizli tahlil
   - Kunlar kesimidagi faollik
6. 📥 **Excel (.xlsx) hisobot:**
   - Bir tugma orqali oylik to'liq hisobotni chiroyli formatlangan Excel fayl ko'rinishida yuklab olish.
7. ⚡️ **Tezkor matnli kiritish:**
   - `+ 150000 ish haqi`
   - `- 35000 osh tushlik`
   - `avans 500000 kassa`
8. ❌ **Xatoliklarni bekor qilish:** Oxirgi kiritilgan amalni 1 tugma bilan bekor qilish va o'chirish.

---

## 🚀 Mahalliydan ishga tushirish (Local Run)

1. Kutubxonalarni o'rnatish:
```bash
pip install -r requirements.txt
```

2. `.env` faylida token to'g'riligini tekshirish:
```env
BOT_TOKEN=8994052815:AAHt_peOECP0DbZ0SFWz2o4sUMEbp0YaykQ
DB_NAME=finance.db
CURRENCY=so'm
```

3. Botni ishga tushirish:
```bash
python bot.py
```

---

## 🐙 GitHub'ga yuklash (Push to GitHub)

1. GitHub.com saytida yangi bo'sh repository yarating (masalan: `workplace-finance-bot`).
2. Terminalda bot papkasiga kiring va quyidagi buyruqlarni bajaring:

```bash
git init
git add .
git commit -m "Initial commit: Ishxona hisob-kitob boti"
git branch -M main
git remote add origin https://github.com/SIZNING_GITHUB_USERNAME/workplace-finance-bot.git
git push -u origin main
```

*(Eslatma: `.env` fayli va ma'lumotlar bazasi `.gitignore` qilingan, bot tokeni GitHub'da ochiq ko'rinmaydi).*

---

## 🚂 Railway.app platformasiga bepul deploy qilish

1. [Railway.app](https://railway.app/) saytiga kiring va GitHub akkauntingiz orqali kiring.
2. **"New Project"** -> **"Deploy from GitHub repo"** ni tanlang.
3. Yangi yaratgan repository'ingizni (`workplace-finance-bot`) tanlang.
4. Loyiha sozlamalarida **"Variables"** bo'limiga o'ting va quyidagi o'zgaruvchilarni qo'shing:
   - `BOT_TOKEN` = `8994052815:AAHt_peOECP0DbZ0SFWz2o4sUMEbp0YaykQ`
   - `DB_NAME` = `finance.db`
   - `CURRENCY` = `so'm`
5. Railway avtomatik ravishda `Dockerfile` yoki `Procfile` orqali botni yig'adi va 24/7 rejimda ishga tushiradi!
