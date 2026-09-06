from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time

# MODÜLLERİMİZİ İÇERİ AKTARIYORUZ
from suzgec import KapSuzgeci 
from filtre import KapFiltreci

KAP_ANA_SAYFA = "https://www.kap.org.tr/tr/"

def kap_radar_avci_modu():
    print("🌐 Chrome başlatılıyor (TAM OTOMATİK RADAR MODU)...")
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_experimental_option("detach", True) 
    options.page_load_strategy = 'eager'
    
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument("--disable-renderer-backgrounding")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Yardımcılarımızı başlatıyoruz
    suzgec = KapSuzgeci()   # Süzgecin hafızası burada başlar ve asla silinmez!
    filtreci = KapFiltreci()
    
    tur_sayaci = 0 
    
    try:
        driver.get(KAP_ANA_SAYFA)
        
        # SİSTEM İLK AÇILDIĞINDA FİLTREYİ KUR
        filtreci.filtreleri_kur(driver)
        
        js_tarih_bul = """
            let elements = Array.from(document.querySelectorAll('div, th, span'));
            return elements.find(e => e.innerText.trim() === 'Tarih');
        """
        
        print("🚀 Radar aktif! Ava çıkılıyor...")
        
        while True:
            try:
                tur_sayaci += 1
                
                # 🔥 ANTİ-DONMA KORUMASI: 15 Turda bir sayfayı yenile ve filtreyi baştan kur
                if tur_sayaci >= 15:
                    print("\n🧹 KAP SİTESİ ŞİŞMESİN DİYE HAFIZA TEMİZLENİYOR (F5)...")
                    driver.refresh()
                    time.sleep(5) 
                    print("🔄 Sayfa yenilendi, filtreler silindi.")
                    
                    # Filtreciye haber ver, filtreleri tekrar kursun
                    filtreci.filtreleri_kur(driver)
                    
                    tur_sayaci = 0
                    continue 
                
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
                    time.sleep(0.5)
                    ActionChains(driver).send_keys(Keys.TAB).perform()
                    time.sleep(0.5)
                    guncel_buyutec = driver.switch_to.active_element
                    driver.execute_script("arguments[0].style.outline = '4px solid #00ff00';", guncel_buyutec)
                    
                    ActionChains(driver).send_keys(Keys.ENTER).perform()
                    print(f"\n🔄 [{zaman}] Büyütece basıldı. Radar tarıyor... (Tur: {tur_sayaci}/15)")
                
                time.sleep(5) 
                
                tarih_element = driver.execute_script(js_tarih_bul)
                
                if tarih_element:
                    driver.execute_script("arguments[0].style.outline = '4px solid #00ff00';", tarih_element)
                    
                    PIKSELLER = [50, 120, 190] 
                    
                    for i, piksel in enumerate(PIKSELLER, 1):
                        ActionChains(driver) \
                            .move_to_element(tarih_element) \
                            .move_by_offset(0, piksel) \
                            .key_down(Keys.CONTROL) \
                            .click() \
                            .key_up(Keys.CONTROL) \
                            .perform()
                        
                        time.sleep(0.5) 
                        driver.switch_to.window(driver.window_handles[-1])
                        time.sleep(0.5) 
                        
                        okunan_link = driver.current_url
                        
                        if "Bildirim" in okunan_link:
                            # 🔥 SÜZGEÇ DEVREDE: Aynı link daha önce okunduysa 'False' döner ve reddedilir
                            if suzgec.link_ekle(okunan_link):
                                print(f"🌟 YENİ İLAN KUYRUĞA ALINDI: {okunan_link.split('/')[-1]}")
                            else:
                                print(f"➖ Eski ilan atlandı: {okunan_link.split('/')[-1]}")
                        
                        if len(driver.window_handles) > 1:
                            driver.close()
                            driver.switch_to.window(driver.window_handles[0])
                        elif "Bildirim" in okunan_link:
                            driver.back()
                        
                        time.sleep(0.5) 
                        
                    print(f"📦 KUYRUKTAKİ BEKLEYEN İLAN SAYISI: {suzgec.kuyruk_durumu()}")
                    print("-" * 50)
                else:
                    print("⚠️ Ekranda 'Tarih' referansı bulunamadı!")
                            
            except Exception as e:
                print(f"⚠️ DÖNGÜ HATASI: {e}")
            
            # Kuyruktaki ilanları işleme süresi
            suzgec.kuyrugu_isle(driver=driver, sure_limiti=25)

    except Exception as e:
        print(f"❌ SİSTEM HATASI: {e}")

if __name__ == "__main__":
    kap_radar_avci_modu()