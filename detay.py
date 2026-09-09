import time
from selenium.webdriver.common.by import By

class OzelDurumDetayci:
    def ozet_cek(self, driver, url):
        print(f"\n🔎 [DETAY.PY] Özel Durum ilanı inceleniyor: {url.split('/')[-1]}")
        
        # 🔥 Kendi sekmesini kendisi açıyor
        driver.execute_script(f"window.open('{url}', '_blank');")
        driver.switch_to.window(driver.window_handles[-1])
        
        try:
            print("⏳ Detay için sayfa yükleniyor... 4 saniye bekleniyor...")
            time.sleep(4) 
            
            tum_sayfa_yazisi = driver.find_element(By.TAG_NAME, "body").text
            satirlar = [satir.strip() for satir in tum_sayfa_yazisi.split('\n') if satir.strip()]
            
            ozet_icerik = "Özet Bilgi Bulunamadı!"
            
            for i in range(len(satirlar)):
                if "özet bilgi" in satirlar[i].lower():
                    if i + 1 < len(satirlar):
                        ozet_icerik = satirlar[i+1]
                    break
            
            print("📝 BULUNAN ÖZET BİLGİ İÇERİĞİ:")
            print(f"👉 {ozet_icerik}\n")
            
            return ozet_icerik

        except Exception as e:
            print(f"⚠️ [DETAY.PY] Okuma yapılamadı! Detay: {e}")
            return None
            
        finally:
            # 🔥 İşi bitince kendi açtığı sekmeyi temizliyor
            if len(driver.window_handles) > 1:
                print("🧹 [DETAY.PY] İşlem tamam, sekme kapatıldı.")
                driver.close()
                driver.switch_to.window(driver.window_handles[0])