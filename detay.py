import time
from selenium.webdriver.common.by import By

class OzelDurumDetayci:
    def __init__(self):
        # 🎯 BORSADA FİYAT HAREKETLİLİĞİ YARATACAK KİLİT KELİMELER
        self.aranan_kelimeler = [
            "sözleşme", "sipariş", "protokol", "anlaşma", "ihale",
            "yatırım", "kapasite", "teşvik", "ruhsat", "lisans", "izin",
            "ortaklık", "satın alma", "pay devri", "birleşme"
        ]

    def ozet_cek(self, driver, url):
        print(f"\n🔎 [DETAY.PY] Özel Durum ilanı inceleniyor: {url.split('/')[-1]}")
        
        driver.get(url)
        
        try:
            print("⏳ Sayfa yükleniyor... 4 saniye bekleniyor...")
            time.sleep(4) 
            
            tum_sayfa_yazisi = driver.find_element(By.TAG_NAME, "body").text
            satirlar = [satir.strip() for satir in tum_sayfa_yazisi.split('\n') if satir.strip()]
            
            ozet_icerik = None
            
            # 🔥 ÇAPA MANTIĞI: "Özet Bilgi" yazısını bul ve hemen altındaki satırı yakala!
            for i in range(len(satirlar)):
                if "özet bilgi" in satirlar[i].lower():
                    if i + 1 < len(satirlar):
                        ozet_icerik = satirlar[i+1]
                    break
            
            if not ozet_icerik:
                print("⚠️ Özet Bilgi satırı bulunamadı, çöp sayılıyor.")
                return None
                
            print(f"📄 OKUNAN ÖZET: '{ozet_icerik}'")
            
            # =================================================================
            # 🔥 KELİME FİLTRESİ VE KÜÇÜK HARF ÇEVİRİMİ 🔥
            # =================================================================
            kucuk_ozet = ozet_icerik.replace('İ', 'i').replace('I', 'ı').lower()
            
            eslesen_kelime = None
            for kelime in self.aranan_kelimeler:
                aranan_kucuk = kelime.replace('İ', 'i').replace('I', 'ı').lower()
                
                if aranan_kucuk in kucuk_ozet:
                    eslesen_kelime = kelime
                    break
                    
            print("\n" + "="*80)
            if eslesen_kelime:
                print(f"🟢 DURUM         : ARANAN KELİME İÇERİYOR ---> ({eslesen_kelime.upper()})")
                print(f"📝 ALTIN İÇERİK  : {ozet_icerik}")
                print("✅ Eşleşme başarılı! (İçerik merkeze iletilecek)")
                print("="*80 + "\n")
                return ozet_icerik # Altın ilanı yakaladı, metni geri gönderiyor
            else:
                print("🔴 DURUM         : ARANMAYAN KELİME (ÇÖP)")
                print("❌ Eşleşme yok! İlan çöpe atıldı.")
                print("="*80 + "\n")
                return None # Aradığımız kelime yok, None (Hiçbir şey) gönderiyor
            # =================================================================

        except Exception as e:
            print(f"⚠️ [DETAY.PY] Okuma yapılamadı! Detay: {e}")
            return None
            
        finally:
            if len(driver.window_handles) > 1:
                print("🧹 İlan okundu, sekme kapatılıyor ve ana radara dönülüyor...")
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            else:
                print("🧹 İlan okundu, tarayıcı tamamen kapatılıyor...")
                driver.quit()

# =====================================================================
# 🧪 SADECE DETAY.PY'Yİ TEK BAŞINA TEST ETMEK İÇİN
# =====================================================================
if __name__ == "__main__":
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    
    print("🧪 TEST MODU AKTİF: detay.py tek başına çalıştırılıyor...")
    
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_experimental_option("detach", True) 
    options.page_load_strategy = 'eager'
    
    test_driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    test_driver.get("about:blank")
    time.sleep(1)
    
    # İçinde yatırım/kapasite geçen bir KAP linkini veya eski denediğini buraya koyup test edebilirsin
    TEST_LINKI = "https://www.kap.org.tr/tr/Bildirim/1659576" 
    
    detayci = OzelDurumDetayci()
    detayci.ozet_cek(test_driver, TEST_LINKI)