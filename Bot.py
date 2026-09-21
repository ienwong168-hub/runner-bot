import os, requests
BOT = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT = os.getenv("TELEGRAM_CHAT_ID")

def scan():
    tickers = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=15).json()
    runners=[]
    for t in tickers:
        if not t['symbol'].endswith('USDT'): continue
        if float(t['quoteVolume']) < 2000000: continue
        try:
            kl = requests.get(f"https://api.binance.com/api/v3/klines?symbol={t['symbol']}&interval=1h&limit=2", timeout=10).json()
            chg=(float(kl[1][4])-float(kl[0][4]))/float(kl[0][4])*100
            if chg>6 and float(kl[1][5])>300000:
                runners.append((t['symbol'][:-4], chg, float(kl[1][4])))
        except: continue
    runners=sorted(runners, key=lambda x:x[1], reverse=True)[:1]
    if runners:
        coin,chg,price=runners[0]
        stop=price*0.8
        text=f"🚀 {coin} +{chg:.1f}% (1H)\n現價 ${price}\n止蝕 -20% @ ${stop}\n\n撳下面批准"
        kb={"inline_keyboard": [[{"text": f"✅批准追入 {coin}", "callback_data": f"BUY_{coin}_{price}_{stop}"}]]}
        requests.post(f"https://api.telegram.org/bot{BOT}/sendMessage", json={"chat_id": CHAT, "text": text, "reply_markup": kb})

scan()
