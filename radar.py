from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time

# YENİ YAZDIĞIMIZ SÜZGEÇ MODÜLÜNÜ İÇERİ AKTARIYORUZ
from suzgec import KapSuzgeci 

KAP_ANA_SAYFA = "https://www.kap.org.tr/tr/"

def kap_saf_piksel_modu_hizli():
    print("🌐 Chrome başlatılıyor (SÜZGEÇ ENTEGRELİ MOD)...")
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_experimental_option("detach", True) 
    options.page_load_strategy = 'eager'
    
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument("--disable-renderer-backgrounding")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # SÜZGECİMİZİ (GÜMRÜK MEMURUNU) GÖREVE BAŞLATIYORUZ
    suzgec = KapSuzgeci()
    
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
        
        print("✅ Sistem hazır! Linkler okunup süzgece gönderilecek.")
        
        while True:
            try:
                zaman = time.strftime('%H:%M:%S')
                
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
                    print(f"\n🔄 [{zaman}] Büyütece basıldı.")
                
                print("⏳ Sayfanın tam oturması için 4 saniye bekleniyor...")
                time.sleep(4) 
                
                tarih_element = driver.execute_script(js_tarih_bul)
                
                if tarih_element:
                    driver.execute_script("arguments[0].style.outline = '4px solid #00ff00';", tarih_element)
                    
                    PIKSELLER = [50, 120, 180] 
                    
                    for i, piksel in enumerate(PIKSELLER, 1):
                        ActionChains(driver) \
                            .move_to_element(tarih_element) \
                            .move_by_offset(0, piksel) \
                            .key_down(Keys.CONTROL) \
                            .click() \
                            .key_up(Keys.CONTROL) \
                            .perform()
                        
                        time.sleep(1) 
                        
                        driver.switch_to.window(driver.window_handles[-1])
                        time.sleep(1) 
                        
                        okunan_link = driver.current_url
                        
                        # --- YENİ SÜZGEÇ MANTIĞI BURADA DEVREYE GİRİYOR ---
                        if suzgec.link_ekle(okunan_link):
                            print(f"🌟 YENİ İLAN SÜZGEÇTEN GEÇTİ VE KUYRUĞA ALINDI: {okunan_link}")
                        else:
                            # Terminali çok kirletmesin diye eski linkleri gri gibi sönük yazdırabiliriz veya direkt pass geçebiliriz
                            print(f"➖ Eski ilan atlandı: {okunan_link.split('/')[-1]}")
                        
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        time.sleep(1) 
                        
                    print("-" * 50)
                    print(f"📦 KUYRUKTAKİ BEKLEYEN İLAN SAYISI: {suzgec.kuyruk_durumu()}")
                    print("-" * 50)
                    
                else:
                    print("⚠️ Ekranda 'Tarih' referansı bulunamadı!")
                            
            except Exception as e:
                print(f"⚠️ DÖNGÜ HATASI: {e}")
            
            time.sleep(10) 

    except Exception as e:
        print(f"❌ SİSTEM HATASI: {e}")

kap_saf_piksel_modu_hizli()