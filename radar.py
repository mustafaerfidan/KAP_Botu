from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time

KAP_ANA_SAYFA = "https://www.kap.org.tr/tr/"

def kap_saf_piksel_modu():
    print("🌐 Chrome başlatılıyor (ESKİ USUL PİKSEL MODU)...")
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_experimental_option("detach", True) 
    
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument("--disable-renderer-backgrounding")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        driver.get(KAP_ANA_SAYFA)
        print("\n" + "="*70)
        print("🚨 KONTROL SENDE!")
        print("1. Filtrelerini ayarla (BİST, ÖDA vs.)")
        print("2. Tablo ekrana geldiğinde terminalde ENTER'a bas.")
        print("="*70 + "\n")
        
        input("Hazır olduğunda ENTER tuşuna bas...\n")
        
        js_tarih_bul = """
            let elements = Array.from(document.querySelectorAll('div, th, span'));
            return elements.find(e => e.innerText.trim() === 'Tarih');
        """
        
        print("✅ Sistem hazır! Tarih referans alınıp piksellerle aşağı inilecek.")
        
        while True:
            try:
                zaman = time.strftime('%H:%M:%S')
                
                # 1. Büyüteci bul ve yenile
                guncel_input = driver.execute_script("""
                    let allInputs = Array.from(document.querySelectorAll('input'));
                    return allInputs.find(inp => {
                        let p = (inp.placeholder || '').toLowerCase();
                        return inp.offsetWidth > 40 && (p.includes('kod') || p.includes('unvan') || p.includes('irket'));
                    });
                """)

                if guncel_input:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].focus(); arguments[0].click();", guncel_input)
                    time.sleep(0.2)
                    ActionChains(driver).send_keys(Keys.TAB).perform()
                    time.sleep(0.2)
                    guncel_buyutec = driver.switch_to.active_element
                    driver.execute_script("arguments[0].style.outline = '4px solid #00ff00';", guncel_buyutec)
                    
                    ActionChains(driver).send_keys(Keys.ENTER).perform()
                    print(f"🔄 [{zaman}] Büyütece basıldı.")
                
                print("⏳ Sayfanın tam oturması için 6 saniye bekleniyor...")
                time.sleep(3) 
                
                # 2. Tarih yazısını bul
                tarih_element = driver.execute_script(js_tarih_bul)
                
                if tarih_element:
                    driver.execute_script("arguments[0].style.outline = '4px solid #00ff00';", tarih_element)
                    print(f"🎯 Tarih referansı bulundu. Tıklamalar başlıyor...")
                    
                    # 🔥 BURADAKİ SAYILARI KAFANA GÖRE DEĞİŞTİR 🔥
                    # 1. İlan, 2. İlan ve 3. İlan için inilecek pikseller
                    PIKSELLER = [50, 120, 190] 
                    
                    for i, piksel in enumerate(PIKSELLER, 1):
                        # Fareyi BAŞTAN "Tarih" yazısına koyup piksel kadar in
                        ActionChains(driver) \
                            .move_to_element(tarih_element) \
                            .move_by_offset(0, piksel) \
                            .key_down(Keys.CONTROL) \
                            .click() \
                            .key_up(Keys.CONTROL) \
                            .perform()
                        
                        time.sleep(1) # Sekme geçiş payı
                        
                        # Yeni sekmeye geç
                        driver.switch_to.window(driver.window_handles[-1])
                        
                        print(f"⏳ {i}. İlan açıldı (İnilen Piksel: {piksel}), sayfanın yüklenmesi için 5 saniye bekleniyor...")
                        time.sleep(3) 
                        
                        print(f"✅ Okundu: {driver.current_url}")
                        
                        # Kapat ve ana tabloya dön
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        
                        time.sleep(1) # Nefes alma payı
                        
                    print("-" * 50)
                else:
                    print("⚠️ Ekranda 'Tarih' referansı bulunamadı!")
                            
            except Exception as e:
                print(f"⚠️ DÖNGÜ HATASI: {e}")
            
            print("⏳ Bir sonraki yenileme için 25 saniye bekleniyor...")
            time.sleep(20) 

    except Exception as e:
        print(f"❌ SİSTEM HATASI: {e}")

kap_saf_piksel_modu()