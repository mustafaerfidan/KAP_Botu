import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

class KapTiklayici:
    def __init__(self):
        # 🎯 HEDEF AYARLARI (Senin kalibre ettiğin kusursuz pikseller)
        self.X_KAYMA = 130 
        self.Y_PIKSELLER = [110, 170, 250]

    def lazerli_tikla_ve_topla(self, driver, tarih_element, suzgec):
        print("\n🔵 [TIKLAMA.PY] Lazerli vur-kaç sistemi devreye girdi!")
        
        for i, piksel in enumerate(self.Y_PIKSELLER, 1):
            
            eski_sekme_sayisi = len(driver.window_handles)
            
            # ====================================================================
            # 1. AŞAMA: HAYALET MAVİ LAZER EFEKTİNİ ÇİZ 
            # ====================================================================
            driver.execute_script(f"""
                let rect = arguments[0].getBoundingClientRect();
                let x = rect.left + (rect.width / 2) + {self.X_KAYMA};
                let y = rect.top + (rect.height / 2) + {piksel};
                
                let dot = document.createElement('div');
                dot.style.position = 'fixed';
                dot.style.left = (x - 7) + 'px'; 
                dot.style.top = (y - 7) + 'px';
                dot.style.width = '15px';
                dot.style.height = '15px';
                dot.style.backgroundColor = 'blue';
                dot.style.borderRadius = '50%';
                dot.style.zIndex = '999999';
                dot.style.boxShadow = '0 0 15px 5px cyan'; 
                dot.style.pointerEvents = 'none'; 
                document.body.appendChild(dot);
                
                setTimeout(() => dot.remove(), 1500);
            """, tarih_element)
            
            time.sleep(0.5) 
            
            # ====================================================================
            # 2. AŞAMA: LAZERİN OLDUĞU YERE CTRL+TIKLA YAP
            # ====================================================================
            ActionChains(driver) \
                .move_to_element(tarih_element) \
                .move_by_offset(self.X_KAYMA, piksel) \
                .key_down(Keys.CONTROL) \
                .click() \
                .key_up(Keys.CONTROL) \
                .perform()
            
            time.sleep(0.5) 
            
            # ====================================================================
            # 3. AŞAMA: İÇERİĞİ BOŞVER, SADECE LİNKİ AL VE SEKMEYİ ZORLA KAPAT!
            # ====================================================================
            if len(driver.window_handles) > eski_sekme_sayisi:
                try:
                    driver.switch_to.window(driver.window_handles[-1])
                    
                    # 🔥 VUR-KAÇ TAKTİĞİ: Sayfanın içeriği yüklenmeden ZORLA DURDUR!
                    try:
                        driver.execute_script("window.stop();")
                    except:
                        pass
                    
                    # Sayfa durduruldu ama adres çubuğundaki link elimizde!
                    okunan_link = driver.current_url
                    
                    if "Bildirim" in okunan_link:
                        if suzgec.link_ekle(okunan_link):
                            print(f"🌟 YENİ İLAN KUYRUĞA ALINDI: {okunan_link.split('/')[-1]}")
                        else:
                            print(f"➖ Eski ilan atlandı: {okunan_link.split('/')[-1]}")
                
                except Exception as e:
                    print(f"⚠️ [TIKLAMA.PY] Link okunurken pürüz çıktı: {e}")
                
                finally:
                    # Ne olursa olsun o sekmeyi anında kapat ve geri dön!
                    if len(driver.window_handles) > 1:
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
            else:
                print(f"⚠️ X:{self.X_KAYMA} Y:{piksel} noktasına tıklandı ama yeni sekme AÇILMADI!")
            
            time.sleep(0.5) 

# =====================================================================
# 🧪 SADECE TIKLAMA.PY'Yİ TEK BAŞINA TEST ETMEK İÇİN
# =====================================================================
if __name__ == "__main__":
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    
    print("🧪 TIKLAMA.PY TEST MODU AKTİF: Tarayıcı açılıyor...")
    
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_experimental_option("detach", True) 
    # Sayfa yüklenmesini beklemeden işleme geçmek için eager modu ekledik
    options.page_load_strategy = 'eager' 
    
    test_driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    test_driver.get("https://www.kap.org.tr/tr/")
    print("⏳ KAP açıldı, tablonun yüklenmesi için 5 saniye bekleniyor...")
    time.sleep(5)
    
    js_tarih_bul = """
        let elements = Array.from(document.querySelectorAll('div, th, span'));
        return elements.find(e => e.innerText.trim() === 'Tarih');
    """
    hedef_tarih_elementi = test_driver.execute_script(js_tarih_bul)
    
    if hedef_tarih_elementi:
        test_driver.execute_script("arguments[0].style.outline = '4px solid #00ff00';", hedef_tarih_elementi)
        print("✅ Tarih referansı bulundu! Lazer ateşleniyor...")
        
        class SahteSuzgec:
            def link_ekle(self, link): return True
            def kuyruk_durumu(self): return 1
            
        tiklayici = KapTiklayici()
        tiklayici.lazerli_tikla_ve_topla(test_driver, hedef_tarih_elementi, SahteSuzgec())
        
        print("\n🎯 Test Bitti!")
    else:
        print("❌ 'Tarih' referansı bulunamadı.")