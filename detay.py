import time
from selenium.webdriver.common.by import By

class OzelDurumDetayci:
    def ozet_cek(self, driver, url):
        print(f"\n🔎 [DETAY.PY] Özel Durum ilanı inceleniyor: {url.split('/')[-1]}")
        
        driver.get(url)
        
        try:
            print("⏳ Sayfa yükleniyor... 4 saniye bekleniyor...")
            time.sleep(4) 
            
            # Sayfanın gövdesindeki (body) tüm metni tek seferde çek
            tum_sayfa_yazisi = driver.find_element(By.TAG_NAME, "body").text
            
            # Yazıyı satırlara böl ve boş satırları temizle
            satirlar = [satir.strip() for satir in tum_sayfa_yazisi.split('\n') if satir.strip()]
            
            ozet_icerik = "Özet Bilgi Bulunamadı!"
            
            # 🔥 ÇAPA MANTIĞI: "Özet Bilgi" yazısını bul ve hemen altındaki satırı yakala!
            for i in range(len(satirlar)):
                if "özet bilgi" in satirlar[i].lower():
                    if i + 1 < len(satirlar):
                        ozet_icerik = satirlar[i+1]
                    break
            
            print("\n" + "="*80)
            print("📝 BULUNAN ÖZET BİLGİ İÇERİĞİ:")
            print(f"👉 {ozet_icerik}")
            print("="*80 + "\n")
            
            return ozet_icerik

        except Exception as e:
            print(f"⚠️ [DETAY.PY] Okuma yapılamadı! Detay: {e}")
            return None
            
        finally:
            # 🔥 İŞTE BURASI: İlan okunduktan sonra sekmeyi kapatır
            if len(driver.window_handles) > 1:
                print("🧹 İlan okundu, sekme kapatılıyor ve ana radara dönülüyor...")
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            else:
                # Test modunda tek sekme varsa direkt Chrome'u kapatır
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
    
    # Chrome açıldığında boş bir sayfa ile başla
    test_driver.get("about:blank")
    time.sleep(1)
    
    # Test etmek istediğin herhangi bir Özel Durum Açıklaması linki
    TEST_LINKI = "https://www.kap.org.tr/tr/Bildirim/1659576" 
    
    detayci = OzelDurumDetayci()
    detayci.ozet_cek(test_driver, TEST_LINKI)