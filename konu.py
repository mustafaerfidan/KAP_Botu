import time
from selenium.webdriver.common.by import By

class KonuIsleyici:
    def __init__(self):
        self.mesgul = False 

    def isleme_basla(self, driver, url, yeni_sekme=True):
        self.mesgul = True 
        print(f"\n⚙️ [KONU.PY] Görev alındı! Link işleniyor: {url.split('/')[-1]}")
        
        if yeni_sekme:
            # Gerçek sistemde Radar bozulmasın diye yeni sekme açılır
            driver.execute_script(f"window.open('{url}', '_blank');")
            driver.switch_to.window(driver.window_handles[-1])
        else:
            # Test modunda direkt linke gidilir
            driver.get(url)
        
        try:
            print("⏳ Sayfa yükleniyor... 4 saniye bekleniyor...")
            time.sleep(4) 
            
            # Sayfanın gövdesindeki (body) tüm metni tek seferde çek
            tum_sayfa_yazisi = driver.find_element(By.TAG_NAME, "body").text
            
            # Yazıyı satırlara böl ve boş satırları temizle
            satirlar = [satir.strip() for satir in tum_sayfa_yazisi.split('\n') if satir.strip()]
            
            okunan_konu_basligi = "BULUNAMADI"
            
            # 🔥 ÇAPA MANTIĞI: Listeyi tara, "A+" yazısını bulduğunda bir önceki satırı al!
            for i in range(len(satirlar)):
                if satirlar[i] == "A+" and i > 0:
                    okunan_konu_basligi = satirlar[i-1]
                    break
            
            # =================================================================
            # 🔥 3 KELİMELİK FİLTRELEME VE RAPORLAMA ALGORİTMASI 🔥
            # =================================================================
            aranan_kelimeler = ["sözleşme", "ihale", "yeni iş"] 
            kucuk_harfli_baslik = okunan_konu_basligi.lower()
            
            eslesen_kelime = None
            for kelime in aranan_kelimeler:
                if kelime in kucuk_harfli_baslik:
                    eslesen_kelime = kelime
                    break 
            
            print("\n" + "="*80)
            if eslesen_kelime:
                print(f"🟢 BULUNAN CÜMLE : '{okunan_konu_basligi}'")
                print(f"🎯 DURUM         : ARANAN KELİME İÇERİYOR ---> ({eslesen_kelime.upper()})")
                print("✅ Eşleşme başarılı! (Sekme planlandığı gibi kapatılacak)")
            else:
                print(f"🔴 BULUNAN CÜMLE : '{okunan_konu_basligi}'")
                print(f"🗑️ DURUM         : ARANMAYAN KELİME (ÇÖP)")
                print("❌ Eşleşme yok! (Sekme planlandığı gibi kapatılacak)")
            print("="*80 + "\n")
            # =================================================================

        except Exception as e:
            print(f"⚠️ [HATA] Okuma yapılamadı! Detay: {e}")
            
        finally:
            # 🔥 İŞTE BURASI: Hata olsa da, kelime bulunsa da, bulunmasa da BURASI KESİN ÇALIŞIR!
            if yeni_sekme and len(driver.window_handles) > 1:
                print("🧹 Sekme kapatılıyor ve ana radara dönülüyor...")
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
        
        self.mesgul = False
        print(f"✅ [KONU.PY] Tarama bitti. Meşguliyet kalktı.\n")


# =====================================================================
# 🧪 SADECE KONU.PY'Yİ TEK BAŞINA TEST ETMEK İÇİN
# =====================================================================
if __name__ == "__main__":
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    
    print("🧪 TEST MODU AKTİF: konu.py tek başına çalıştırılıyor...")
    
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_experimental_option("detach", True) 
    options.page_load_strategy = 'eager'
    
    test_driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    test_driver.get("about:blank")
    time.sleep(1)
    
    TEST_LINKI = "https://www.kap.org.tr/tr/Bildirim/1659252" 
    
    isleyici = KonuIsleyici()
    isleyici.isleme_basla(test_driver, TEST_LINKI, yeni_sekme=False)