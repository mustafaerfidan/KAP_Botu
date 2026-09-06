from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time

from suzgec import KapSuzgeci 
from filtre import KapFiltreci

KAP_ANA_SAYFA = "https://www.kap.org.tr/tr/"

def kap_radar_avci_modu():
    print("🛡️ ZIRHLI VE TURBO RADAR SİSTEMİ BAŞLATILIYOR (Hafifletilmiş Dedektör)...")
    
    suzgec = KapSuzgeci()   
    filtreci = KapFiltreci()
    
    genel_tur_sayaci = 0 
    
    while True:
        print("\n🌐 Yeni ve taptaze bir Chrome açılıyor...")
        
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_experimental_option("detach", True) 
        options.page_load_strategy = 'eager'
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")

        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            driver.set_page_load_timeout(45) 
            
            driver.get(KAP_ANA_SAYFA)
            
            filtreci.filtreleri_kur(driver)
            
            js_tarih_bul = """
                let elements = Array.from(document.querySelectorAll('div, th, span'));
                return elements.find(e => e.innerText.trim() === 'Tarih');
            """
            
            print("🚀 Radar aktif! Turbo modda ava çıkılıyor...")
            
            ic_tur_sayaci = 0
            while ic_tur_sayaci < 5:
                ic_tur_sayaci += 1
                genel_tur_sayaci += 1
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
                    print(f"\n🔄 [{zaman}] Büyütece basıldı. Radar tarıyor... (5'lik Tur: {ic_tur_sayaci}/5 | Genel Tur: {genel_tur_sayaci})")
                else:
                    raise Exception("Arama butonu (Input) bulunamadı! Sayfa eksik yüklenmiş.")
                
                # ==============================================================================
                # 🔥 YENİ SİSTEM: HAFİFLETİLMİŞ AKILLI SPINNER DEDEKTÖRÜ (CHROME'U PATLATMAZ)
                # ==============================================================================
                time.sleep(1.5) 
                
                bekleme_sayaci = 0
                while bekleme_sayaci < 12: 
                    spinner_var_mi = driver.execute_script("""
                        // Bütün DOM'u taramak yerine sadece class isminde loading/spinner geçenleri bul (ÇOK HIZLI)
                        let spinners = document.querySelectorAll('[class*="loading" i], [class*="spinner" i], [class*="blockui" i]');
                        for(let i=0; i<spinners.length; i++) {
                            let style = window.getComputedStyle(spinners[i]);
                            if(style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0') {
                                return true;
                            }
                        }
                        return false;
                    """)
                    
                    if not spinner_var_mi:
                        break 
                        
                    time.sleep(1)
                    bekleme_sayaci += 1
                    
                if bekleme_sayaci >= 12:
                    raise Exception("Sonsuz dönen ikon tespit edildi! KAP Tablosu askıda kaldı.")
                
                time.sleep(1.5) 
                # ==============================================================================
                
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
                        
                        time.sleep(0.5) 
                        driver.switch_to.window(driver.window_handles[-1])
                        time.sleep(0.5) 
                        
                        okunan_link = driver.current_url
                        
                        if "Bildirim" in okunan_link:
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
                        
                    bekleyen_sayisi = suzgec.kuyruk_durumu()
                    print(f"📦 KUYRUKTAKİ BEKLEYEN İLAN SAYISI: {bekleyen_sayisi}")
                    print("-" * 50)
                    
                    if bekleyen_sayisi > 0:
                        print("⚡ Süzgeç devreye giriyor...")
                        suzgec.kuyrugu_isle(driver=driver, sure_limiti=25)
                    else:
                        print("⚡ Kuyruk boş, süzgeç atlandı. Doğrudan yeni taramaya geçiliyor.")
                        
                else:
                    raise Exception("Ekranda 'Tarih' referansı bulunamadı!")
                
                print("⏳ Diğer tura geçmeden önce 2 saniye bekleniyor...")
                time.sleep(2)

            print("\n🧹 5 TUR TAMAMLANDI! RAM'i temizlemek için tarayıcı tamamen kapatılıp yeniden açılacak...")
            
        except Exception as e:
            # Buradaki hata mesajını daha okunaklı yaptık
            print(f"\n❌ SİSTEMDE BİR TIKANMA/HATA OLDU:\n{e}")
            print("🔄 Panik yok! Arızalı/Donuk tarayıcı imha edilip yenisi açılacak...")
            
        finally:
            try:
                driver.quit()
                print("💀 Eski Chrome tamamen kapatıldı.")
            except:
                pass
            time.sleep(3) 

if __name__ == "__main__":
    kap_radar_avci_modu()