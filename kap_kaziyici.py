import requests
from bs4 import BeautifulSoup
import re
import yfinance as yf

# İhalenin linki
url = "https://www.kap.org.tr/tr/Bildirim/1655998"

# Tarayıcı maskemiz
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

print("KAP sitesine bağlanılıyor...")
response = requests.get(url, headers=headers)

if response.status_code == 200:
    print("Bağlantı Başarılı! Tüm sayfa taranıyor...\n")
    
    # Sayfadaki tüm metni (HTML kodlarından arındırarak) devasa bir yazıya çeviriyoruz
    soup = BeautifulSoup(response.text, "html.parser")
    tum_metin = soup.get_text(separator=" ", strip=True)
    
    # Önce kontrol edelim: Acaba metin gerçekten sayfada var mı?
    if "ABD Doları" in tum_metin:
        print("Harika! KAP metni gizlememiş. Regex pençesi fırlatılıyor...\n")
        
        # Senin kurguladığın o kusursuz formül
        arama_kalibi = r"([\d\.,]+)\s+([A-Za-zÇĞİÖŞÜçğıöşü\s]+)\s*\(([A-Za-zÇĞİÖŞÜçğıöşü]+)\)"
        sonuc = re.search(arama_kalibi, tum_metin)
        
        if sonuc:
            print("🎣 BÜYÜK BALIK YAKALANDI!")
            print("Tutar:", sonuc.group(1))
            print("Birim:", sonuc.group(2).strip())
            print("Okunuşu:", sonuc.group(3))
            
            # 1. ADIM: VERİ TEMİZLİĞİ
            ham_tutar = sonuc.group(1) # "48.045.195,00" değerini alır
            temiz_tutar = ham_tutar.replace(".", "").replace(",", ".")
            is_hacmi_dolar = float(temiz_tutar) # Metni matematiksel sayıya çevir
            
            print(f"\n--- MATEMATİKSEL İŞLEMLER ---")
            print(f"Temizlenmiş Sayı: {is_hacmi_dolar}")
            
            # 2. ADIM: CANLI KURU ÇEKME VE ÇARPMA
            if "Dolar" in sonuc.group(2):
                print("Canlı Dolar kuru çekiliyor (Yahoo Finance)...")
                kur_verisi = yf.Ticker("USDTRY=X")
                anlik_kuru = kur_verisi.history(period="1d")['Close'].iloc[-1]
                
                toplam_tl_degeri = is_hacmi_dolar * anlik_kuru
                
                print(f"Anlık Kur: {anlik_kuru:.2f} TL")
                print(f"İhalenin Toplam TL Karşılığı: {toplam_tl_degeri:,.2f} TL")
                
                # --- YENİ EKLENEN KARAR MEKANİZMASI ---
                # Şimdilik CWENE'nin özsermayesini manuel giriyoruz (İleride bunu da bot kendi bulacak)
                sirket_ozsermayesi = 4500000000.0  # 4.5 Milyar TL
                
                print(f"\n--- KARAR AŞAMASI ---")
                print(f"Şirketin Özsermayesi: {sirket_ozsermayesi:,.2f} TL")
                
                if toplam_tl_degeri > sirket_ozsermayesi:
                    print("🚨 HEDEF VURULDU! İhale bedeli, şirketin özsermayesinden BÜYÜK!")
                    print("Telegram'a 'AL' sinyali gönderiliyor...")
                else:
                    oran = (toplam_tl_degeri / sirket_ozsermayesi) * 100
                    print(f"İhale büyük ama özsermayeyi geçemedi. (Özsermayenin %{oran:.1f}'i kadar)")
                    print("Telegram'a mesaj atılmayacak. Bot sessizce taramaya devam ediyor.")
        else:
            print("Rakamlar sayfada var ama formül tam eşleşmedi.")
    else:
        print("Eyvah! Metin HTML içinde yok. KAP veriyi JavaScript ile (dinamik) yüklüyor.")
else:
    print(f"Hata! Sayfaya ulaşılamadı. Hata Kodu: {response.status_code}")