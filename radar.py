from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time
import subprocess
import sys

KAP_ANA_SAYFA = "https://www.kap.org.tr/tr/"

def standart_metne_cevir(metin):
    if not metin:
        return ""
    metin = metin.replace("İ", "I").replace("i", "I").replace("ı", "I")
    metin = metin.upper()
    harfler = {"Ş": "S", "Ç": "C", "Ğ": "G", "Ü": "U", "Ö": "O"}
    for tr, eng in harfler.items():
        metin = metin.replace(tr, eng)
    return metin

def kap_tab_enter_kesin_bot():
    print("🌐 Chrome başlatılıyor...")
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
        print("1. Filtrelerini ayarla (BİST, ÖDA, 50-100-250 vs.)")
        print("2. Tablo ekrana geldiğinde terminalde ENTER'a bas.")
        print("="*70 + "\n")
        
        input("Hazır olduğunda ENTER tuşuna bas...\n")
        
        eski_idler = set()
        
        # Tablo satırlarını çeken JS
        js_veri_cekme_kodu = """
            let data = {};
            document.querySelectorAll('a[href*="/tr/Bildirim/"]').forEach(a => {
                let row = a.closest('tr, [role="row"], div.w-row, div.ng-scope'); 
                let id = a.href.split('/').pop();
                if (row && id && id.length > 3) {
                    let metin = row.innerText;
                    if (metin && metin.length > 30) {
                        data[id] = metin;
                    }
                }
            });
            return data;
        """

        # SADECE ŞİRKET UNVANI KUTUSUNU YAKALAYAN JS
        tablo_inputu = driver.execute_script("""
            let allInputs = Array.from(document.querySelectorAll('input'));
            
            // 1. Placeholder'ında 'kod' veya 'unvan' olan gerçek görünen kutuyu yakala
            let hedef = allInputs.find(inp => {
                let p = (inp.placeholder || '').toLowerCase();
                let gorunur = inp.offsetWidth > 40 && inp.offsetHeight > 15;
                return gorunur && (p.includes('kod') || p.includes('unvan') || p.includes('irket'));
            });

            // 2. Bulamazsa 50-100-250'nin solundaki görünür kutuyu al
            if (!hedef) {
                let gosterim = Array.from(document.querySelectorAll('*')).find(el => {
                    let t = (el.textContent || '').trim();
                    return (t === '50' || t === 'Gösterim') && el.getBoundingClientRect().top > 200;
                });
                if (gosterim) {
                    let satir = gosterim.closest('.row, form, div.w-row') || gosterim.parentElement.parentElement;
                    if (satir) {
                        hedef = Array.from(satir.querySelectorAll('input')).find(i => i.offsetWidth > 40);
                    }
                }
            }

            return hedef;
        """)

        if not tablo_inputu:
            print("❌ Hata: Şirket unvanı kutusu tespit edilemedi!")
            return

        # 1. Kutuya odaklan ve tıkla (Selenium crash vermesin diye JS ile tetikliyoruz)
        print("🎯 Şirket unvanı kutusuna tıklandı...")
        driver.execute_script("""
            arguments[0].scrollIntoView({block: 'center'});
            arguments[0].style.outline = '4px solid #00ff00';
            arguments[0].focus();
            arguments[0].click();
        """, tablo_inputu)
        time.sleep(0.5)

        # 2. Klavyeden TAB tuşuna bas (Bitişiğindeki gri büyütece geçer)
        print("⌨️ TAB tuşuna basıldı...")
        ActionChains(driver).send_keys(Keys.TAB).perform()
        time.sleep(0.5)

        # 3. TAB ile odaklanan büyüteci yeşil yap ve hafızaya al
        buyutec_butonu = driver.switch_to.active_element
        driver.execute_script("arguments[0].style.outline = '4px solid #00ff00';", buyutec_butonu)

        # 4. İlk ENTER tuşunu bas
        print("🚀 İlk ENTER basıldı! Tablo tetiklendi...")
        ActionChains(driver).send_keys(Keys.ENTER).perform()
        time.sleep(2)

        # Mevcut eski ilanları hafızaya al
        baslangic_verileri = driver.execute_script(js_veri_cekme_kodu)
        for bid in baslangic_verileri.keys():
            eski_idler.add(bid)
            
        print(f"\n✅ Başlangıçtaki {len(eski_idler)} adet eski ilan listeye alındı.")
        print("⏳ Radar devrede. Her 15 saniyede bir ENTER basılacak...\n")
        
        while True:
            try:
                zaman = time.strftime('%H:%M:%S')
                
                # Büyütece odaklanıp ENTER bas
                driver.execute_script("arguments[0].focus();", buyutec_butonu)
                ActionChains(driver).send_keys(Keys.ENTER).perform()

                print(f"⌨️ [{zaman}] ENTER basıldı, liste tazelendi.")
                
                # Tablonun güncellenmesi için 3 saniye pay bırak
                time.sleep(3)
                
                # Yeni verileri çek
                guncel_veriler = driver.execute_script(js_veri_cekme_kodu)
                
                for bildirim_id, orijinal_metin in guncel_veriler.items():
                    if bildirim_id not in eski_idler:
                        eski_idler.add(bildirim_id)
                        
                        print("-" * 60)
                        temiz_gosterim = " ".join(orijinal_metin.split())
                        print(f"👀 YENİ İLAN DÜŞTÜ: {temiz_gosterim[:100]}...")
                        
                        metin = standart_metne_cevir(orijinal_metin)
                        
                        # Hedef kelime kontrolü
                        hedef_bulundu = False
                        if "YENI IS ILISKISI" in metin or "IHALE" in metin or "OZEL DURUM ACIKLAMASI" in metin or "SOZLESME" in metin or "SIPARIS" in metin:
                            hedef_bulundu = True

                        if hedef_bulundu:
                            print("\n" + "🎯"*10)
                            print(f"✅ HEDEF KELİME BULUNDU!")
                            print(f"🚀 KAP Kazıyıcı ({bildirim_id}) tetikleniyor...")
                            
                            subprocess.Popen([sys.executable, "kap_kaziyici.py", bildirim_id])
                            print("🎯"*10 + "\n")
                            
            except Exception as e:
                pass
            
            # 12 saniye bekleme (toplam 15 saniye)
            time.sleep(12)

    except Exception as e:
        print(f"❌ HATA: {e}")

kap_tab_enter_kesin_bot()