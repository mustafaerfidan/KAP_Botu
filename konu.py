import time
from selenium.webdriver.common.by import By
from detay import OzelDurumDetayci
from kap_kaziyici import KapKaziyici

class KonuIsleyici:
    def __init__(self):
        self.mesgul = False 
        self.detayci = OzelDurumDetayci()
        self.kaziyici = KapKaziyici()

    def isleme_basla(self, driver, url, yeni_sekme=True):
        self.mesgul = True 
        print(f"\n⚙️ [KONU.PY] Görev alındı! Link işleniyor: {url.split('/')[-1]}")
        
        okunan_konu_basligi = "BULUNAMADI"
        
        # --- 1. AŞAMA: SEKME AÇ VE SADECE BAŞLIĞI OKU ---
        if yeni_sekme:
            driver.execute_script(f"window.open('{url}', '_blank');")
            driver.switch_to.window(driver.window_handles[-1])
        else:
            driver.get(url)
        
        try:
            print("⏳ Konu tespiti için sayfa yükleniyor... 4 saniye bekleniyor...")
            time.sleep(4) 
            
            tum_sayfa_yazisi = driver.find_element(By.TAG_NAME, "body").text
            satirlar = [satir.strip() for satir in tum_sayfa_yazisi.split('\n') if satir.strip()]
            
            for i in range(len(satirlar)):
                if satirlar[i] == "A+" and i > 0:
                    okunan_konu_basligi = satirlar[i-1]
                    break
        except Exception as e:
            print(f"⚠️ [HATA] Okuma yapılamadı! Detay: {e}")
        finally:
            # 🔥 KONU.PY BAŞLIĞI ALIR ALMAZ KENDİ SEKMESİNİ KAPATIR VE ANA RADARA DÖNER!
            if yeni_sekme and len(driver.window_handles) > 1:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                print("🧹 [KONU.PY] Başlık alındı, konu sekmesi kapatıldı.")

        # --- 2. AŞAMA: KARAR VE YÖNLENDİRME (Sekme kapalıyken yapılır) ---
        aranan_kelimeler = ["Özel Durum Açıklaması (Genel)", "İhale Süreci / Sonucu", "Yeni İş İlişkisi"] 
        kucuk_harfli_baslik = okunan_konu_basligi.replace('İ', 'i').replace('I', 'ı').lower()
        
        eslesen_kelime = None
        for kelime in aranan_kelimeler:
            aranan_kucuk = kelime.replace('İ', 'i').replace('I', 'ı').lower()
            if aranan_kucuk in kucuk_harfli_baslik:
                eslesen_kelime = kelime
                break 
        
        print("\n" + "="*80)
        if eslesen_kelime:
            print(f"🟢 BULUNAN CÜMLE : '{okunan_konu_basligi}'")
            print(f"🎯 DURUM         : ARANAN KELİME İÇERİYOR ---> ({eslesen_kelime.upper()})")
            print("="*80)
            
            # YÖNLENDİRİCİ: İlgili modül çağrılır, o modül kendi sekmesini kendisi açacaktır!
            if eslesen_kelime == "Özel Durum Açıklaması (Genel)":
                print("🔄 YÖNLENDİRME: İlan 'detay.py' modülüne aktarılıyor...")
                self.detayci.ozet_cek(driver, url)
                
            elif eslesen_kelime in ["İhale Süreci / Sonucu", "Yeni İş İlişkisi"]:
                print("🔄 YÖNLENDİRME: İlan 'kap_kaziyici.py' modülüne aktarılıyor...")
                self.kaziyici.veri_cek(driver, url)

        else:
            print(f"🔴 BULUNAN CÜMLE : '{okunan_konu_basligi}'")
            print(f"🗑️ DURUM         : ARANMAYAN KELİME (ÇÖP)")
            print("="*80 + "\n")
        
        self.mesgul = False
        print(f"✅ [KONU.PY] Tüm işlemler bitti. Meşguliyet kalktı.\n")