import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

class KapTiklayici:
    def __init__(self):
        pass

    def lazerli_tikla_ve_topla(self, driver, suzgec=None):
        print("\n👻 [TIKLAMA.PY] KUTU KIRICI MOD: KAP'ın gizli satırlarına (div) sızılıyor...")
        
        try:
            # ====================================================================
            # 1. AŞAMA: TABLONUN YÜKLENMESİNİ BEKLE
            # ====================================================================
            print("⏳ Tablonun indirilmesi bekleniyor...")
            bekleme_sayaci = 0
            while bekleme_sayaci < 12:
                spinner_var_mi = driver.execute_script("""
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
                
            time.sleep(2) 
            
            # ====================================================================
            # 2. AŞAMA: SİHİRLİ JS İLE SATIR (KUTU) ELEMENTLERİNİ BUL
            # ====================================================================
            js_kutulari_bul = """
                // 1. Tarih başlığını bul
                let elemanlar = Array.from(document.querySelectorAll('div, span, th'));
                let tarih = elemanlar.find(e => e.innerText.trim() === 'Tarih');
                if (!tarih) return [];
                
                // 2. Asıl tablonun çerçevesini bul
                let tablo = tarih.parentElement;
                while (tablo && tablo.innerText.length < 200) {
                    tablo = tablo.parentElement;
                }
                
                // 3. Tablonun içindeki gerçek ilan satırlarını yakala
                let satirlar = Array.from(tablo.querySelectorAll('.list-group-item, .w-table-row, div[role="row"]'));
                
                // Eğer sınıfları (class) değiştirmişlerse "Bugün" veya "Saat" formatı olan kutuları bul
                if (satirlar.length === 0) {
                    let regex = /Bugün|\\d{2}:\\d{2}/;
                    satirlar = Array.from(tablo.children).filter(child => regex.test(child.innerText) && !child.innerText.includes('Tarih'));
                }
                
                // İlk 3 satırı (DOM elementi olarak) geri gönder
                return satirlar.slice(0, 3);
            """
            
            # Bot HTML kutularını fiziksel nesne (WebElement) olarak alıyor!
            bulunan_kutular = driver.execute_script(js_kutulari_bul)
            
            if bulunan_kutular and len(bulunan_kutular) > 0:
                print(f"\n🎯 Ekranda {len(bulunan_kutular)} adet gizli ilan kutusu bulundu! Operasyon başlıyor...")
                print("="*90)
                
                for i, kutu in enumerate(bulunan_kutular, 1):
                    eski_sekme_sayisi = len(driver.window_handles)
                    
                    # Kutunun içindeki yazıyı (Şirket adını vs.) görelim
                    kutu_yazisi = kutu.text.replace('\n', ' ')[:45]
                    print(f"[{i}] VURULAN KUTU: {kutu_yazisi}...")
                    
                    # ================================================================
                    # FİZİKSEL VURUŞ: Fareyle direkt o kutunun kalbine CTRL+TIKLA!
                    # ================================================================
                    ActionChains(driver) \
                        .move_to_element(kutu) \
                        .key_down(Keys.CONTROL) \
                        .click() \
                        .key_up(Keys.CONTROL) \
                        .perform()
                        
                    time.sleep(1.5) # Sekmenin açılmasını bekle
                    
                    # Yeni sekme açıldıysa:
                    if len(driver.window_handles) > eski_sekme_sayisi:
                        driver.switch_to.window(driver.window_handles[-1])
                        
                        try:
                            driver.execute_script("window.stop();") # Vur-Kaç!
                        except:
                            pass
                            
                        okunan_link = driver.current_url
                        print(f"    🔗 YAKALANAN GİZLİ LİNK: {okunan_link.split('/')[-1]}")
                        
                        if suzgec:
                            suzgec.link_ekle(okunan_link)
                            
                        # Sekmeyi kapat ve ana radara dön
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                    
                    # Bazen KAP kendi içinde aynı sekmeyi günceller (CTRL basmamıza rağmen)
                    elif driver.current_url != "https://www.kap.org.tr/tr/":
                        try:
                            driver.execute_script("window.stop();")
                        except:
                            pass
                        okunan_link = driver.current_url
                        print(f"    🔗 AYNI SEKMEYE AÇILDI, LİNK ALINDI: {okunan_link.split('/')[-1]}")
                        if suzgec:
                            suzgec.link_ekle(okunan_link)
                        driver.back() # Anasayfaya geri dön
                        time.sleep(1)
                        
                    else:
                        print("    ⚠️ Kutuya tıklandı ama tepki vermedi! KAP engeli olabilir.")
                    
                    time.sleep(0.5)
                print("="*90)
                
            else:
                print("⚠️ Ekranda tıklanacak ilan kutusu (satır) bulunamadı!")
                
        except Exception as e:
            print(f"❌ [TIKLAMA.PY] Operasyon sırasında hata: {e}")

# =====================================================================
# 🧪 TIKLAMA.PY TEST MODU (Zırhlı Versiyon)
# =====================================================================
if __name__ == "__main__":
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    
    print("🧪 TIKLAMA.PY TEST MODU AKTİF: Zırhlar giyiliyor, tarayıcı açılıyor...")
    
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_experimental_option("detach", True) 
    
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    test_driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    test_driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
              get: () => undefined
            })
        '''
    })
    
    test_driver.get("https://www.kap.org.tr/tr/")
    
    class SahteSuzgec:
        def link_ekle(self, link): return True
        def kuyruk_durumu(self): return 1
        
    tiklayici = KapTiklayici()
    tiklayici.lazerli_tikla_ve_topla(test_driver, SahteSuzgec())
    
    print("\n✅ Test Bitti!")