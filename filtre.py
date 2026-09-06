import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

class KapFiltreci:
    def filtreleri_kur(self, driver):
        print("\n⚙️ [FİLTRE.PY] Tek Çapalı Piksel Operasyonu başlıyor...")
        time.sleep(3) 
        
        # 🔥 SİHİRLİ LAZER KODU (Şu an CANLI modda olduğumuz için kapalı, gerekirse açabilirsin)
        lazer_kodu = """
            document.addEventListener('click', function(e) {
                let dot = document.createElement('div');
                dot.style.position = 'fixed';
                dot.style.left = (e.clientX - 5) + 'px';
                dot.style.top = (e.clientY - 5) + 'px';
                dot.style.width = '12px';
                dot.style.height = '12px';
                dot.style.backgroundColor = 'blue';
                dot.style.borderRadius = '50%';
                dot.style.zIndex = '999999';
                dot.style.pointerEvents = 'none';
                document.body.appendChild(dot);
            });
        """
        # driver.execute_script(lazer_kodu) # <--- LAZERİ TEKRAR AÇMAK İÇİN BAŞINDAKİ '#' İŞARETİNİ SİL
        
        try:
            # ==========================================================
            # 🎯 ANA KARARGAH: ŞİRKET TİPİ ÇAPASI
            # ==========================================================
            js_sirket_tipi_bul = """
                let elements = Array.from(document.querySelectorAll('div, span'));
                return elements.find(e => e.innerText.trim() === 'Şirket Tipi' || e.innerText.trim() === 'Tüm Şirketler');
            """
            sirket_capa = driver.execute_script(js_sirket_tipi_bul)
            
            if sirket_capa:
                print("🎯 ANA ÇAPA ('Şirket Tipi') bulundu!")
                # driver.execute_script("arguments[0].style.outline = '3px solid red';", sirket_capa)
                time.sleep(0.5)
                
                # ANA MENÜYÜ AÇ
                ActionChains(driver).move_to_element(sirket_capa).click().perform()
                time.sleep(1) 
                
                # 🔥 1. ATIŞ: BİST Devre Kesici 
                Y_1 = 60      
                X_1 = -55     
                print(f"📏 1. Atış (BİST Devre Kesici): Aşağı {Y_1}, Sola {X_1}...")
                ActionChains(driver).move_to_element(sirket_capa).move_by_offset(X_1, Y_1).click().perform()
                time.sleep(1)
                
                # 🔥 2. ATIŞ: Düzenleyici ve Denetleyici Kurumlar 
                Y_2 = 260      
                X_2 = 25     
                print(f"📏 2. Atış (Düzenleyici Kurumlar): Aşağı {Y_2}, Sola {X_2}...")
                ActionChains(driver).move_to_element(sirket_capa).move_by_offset(X_2, Y_2).click().perform()
                time.sleep(1)
                
                # 🔥 3. ATIŞ: Bildirim Tipi Menüsünü Aç 
                Y_3 = 0       
                X_3 = 300     
                print(f"📏 3. Atış (Bildirim Tipi Menüsünü Açma): Sağa {X_3}...")
                ActionChains(driver).move_to_element(sirket_capa).move_by_offset(X_3, Y_3).click().perform()
                time.sleep(1)

                # 🔥 4. ATIŞ: Özel Durum Açıklamaları 
                Y_4 = 80      
                X_4 = 300     
                print(f"📏 4. Atış (ÖDA): Ana Çapadan Aşağı {Y_4}, Sağa {X_4}...")
                ActionChains(driver).move_to_element(sirket_capa).move_by_offset(X_4, Y_4).click().perform()
                time.sleep(1)
                
                # 🔥 5. ATIŞ (FİNAL): Arama Butonu (Büyüteç)
                print(f"📏 5. Atış (Büyüteç/Arama): Sağa 630...")
                ActionChains(driver).move_to_element(sirket_capa).move_by_offset(630, 0).click().perform()
                
                print("✔️ [FİLTRE.PY] BÜTÜN ATIŞLAR KUSURSUZ TAMAMLANDI! Tablo güncelleniyor...")
                time.sleep(2) # Tablonun yüklenmesi için ufak bir mola (15 saniyeden 2 saniyeye düşürüldü)
            else:
                print("⚠️ ANA ÇAPA bulunamadı!")

        except Exception as e:
            print(f"⚠️ [FİLTRE.PY] Hata detayı: {e}\n")


# =====================================================================
# 🧪 SADECE FILTRE.PY'Yİ TEK BAŞINA TEST ETMEK İÇİN
# =====================================================================
if __name__ == "__main__":
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    
    print("🧪 TEST MODU AKTİF: filtre.py tek başına çalıştırılıyor...")
    
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_experimental_option("detach", True) 
    options.page_load_strategy = 'eager'
    
    test_driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    print("🌐 KAP Ana Sayfası açılıyor...")
    test_driver.get("https://www.kap.org.tr/tr/")
    
    filtreci = KapFiltreci()
    filtreci.filtreleri_kur(test_driver)