import requests
from bs4 import BeautifulSoup
import re
import yfinance as yf
import datetime
from isyatirimhisse import fetch_financials

# --- AYARLAR ---
url = "https://www.kap.org.tr/tr/Bildirim/1655998"
hisse_kodu = "CWENE" # İleride bot KAP sayfasından bunu da kendi bulacak
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

print("1. KAP sitesine bağlanılıyor...")
response = requests.get(url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")
    tum_metin = soup.get_text(separator=" ", strip=True)
    
    if "ABD Doları" in tum_metin:
        arama_kalibi = r"([\d\.,]+)\s+([A-Za-zÇĞİÖŞÜçğıöşü\s]+)\s*\(([A-Za-zÇĞİÖŞÜçğıöşü]+)\)"
        sonuc = re.search(arama_kalibi, tum_metin)
        
        if sonuc:
            print("✅ BÜYÜK İHALE YAKALANDI!")
            ham_tutar = sonuc.group(1)
            temiz_tutar = ham_tutar.replace(".", "").replace(",", ".")
            is_hacmi_dolar = float(temiz_tutar)
            
            print("2. Canlı Dolar kuru çekiliyor (Yahoo Finance)...")
            kur_verisi = yf.Ticker("USDTRY=X")
            anlik_kuru = kur_verisi.history(period="1d")['Close'].iloc[-1]
            toplam_tl_degeri = is_hacmi_dolar * anlik_kuru
            print(f"--> İhalenin Toplam TL Karşılığı: {toplam_tl_degeri:,.2f} TL")
            
            print(f"\n3. {hisse_kodu} Bilanço Bilgisi Çekiliyor (İş Yatırım)...")
            su_anki_yil = datetime.datetime.now().year 
            
            try:
                df = fetch_financials(
                    symbols=hisse_kodu, 
                    start_year=su_anki_yil - 1, 
                    end_year=su_anki_yil, 
                    exchange="TRY", 
                    financial_group='1' 
                )
                
                sutunlar = df.columns.tolist()
                isim_sutunu = 'FINANCIAL_ITEM_NAME_TR'
                ozkaynak_satiri = df[df[isim_sutunu].str.strip().str.upper() == "TOPLAM ÖZKAYNAKLAR"]
                
                if ozkaynak_satiri.empty:
                    ozkaynak_satiri = df[df[isim_sutunu].str.contains("Ana Ortaklığa Ait Özkaynaklar", case=False, na=False)]
                    
                if not ozkaynak_satiri.empty:
                    donem_sutunlari = [col for col in sutunlar if '/' in col]
                    donem_sutunlari.sort(reverse=True)
                    
                    sirket_ozsermayesi = 0
                    
                    for donem in donem_sutunlari:
                        ham_deger = ozkaynak_satiri.iloc[0][donem]
                        try:
                            sayisal_deger = float(str(ham_deger).replace(",", ""))
                            if sayisal_deger > 0:
                                sirket_ozsermayesi = sayisal_deger
                                break
                        except:
                            continue
                    
                    print(f"--> Güncel Özsermaye: {sirket_ozsermayesi:,.2f} TL")
                    
                    # --- TERAZİ (KARAR ANI) ---
                    print("\n⚖️ HESAPLAMA VE KARAR AŞAMASI ⚖️")
                    if toplam_tl_degeri > sirket_ozsermayesi:
                        print("🚨 HEDEF VURULDU! İhale bedeli, şirketin özsermayesinden BÜYÜK!")
                        print("Telegram'a 'AL' sinyali gönderilecek (Bir sonraki aşama).")
                    else:
                        oran = (toplam_tl_degeri / sirket_ozsermayesi) * 100
                        print(f"İhale devasa ama özsermayeyi geçemedi. (Özsermayenin %{oran:.1f}'i kadar)")
                        print("Telegram sessiz kalacak. Tarama devam ediyor...")
                else:
                    print("Özkaynak tablodan çekilemedi.")
            except Exception as e:
                print(f"Bilanço çekilirken hata oluştu: {e}")
        else:
            print("Rakamlar sayfada var ama Regex formülü eşleşmedi.")
    else:
        print("KAP metninde 'ABD Doları' bulunamadı.")
else:
    print(f"KAP sayfasına ulaşılamadı. Hata Kodu: {response.status_code}")