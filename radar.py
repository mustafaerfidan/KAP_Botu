from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import subprocess
import sys

KAP_URL = "https://www.kap.org.tr/tr/"

def standart_metne_cevir(metin):
    if not metin:
        return ""
    metin = metin.replace("İ", "I").replace("i", "I").replace("ı", "I")
    metin = metin.upper()
    harfler = {"Ş": "S", "Ç": "C", "Ğ": "G", "Ü": "U", "Ö": "O"}
    for tr, eng in harfler.items():
        metin = metin.replace(tr, eng)
    return metin

def kap_tam_isabet_avcisi():
    print("🌐 Chrome başlatılıyor...")
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_experimental_option("detach", True) 

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        driver.get(KAP_URL)
        print("\n" + "="*70)
        print("🚨 SİSTEM HAZIR!")
        print("1. Filtrelerini ayarla (BİST, ÖDA).")
        print("2. Listeyi aşağı kaydır (Ekranda ilanlar görünsün).")
        print("="*70 + "\n")
        
        input("Hazır olduğunda ENTER'a bas! (Fareyle tıklama simülasyonu başlıyor)...\n")
        
        eski_idler = set()
        
        while True:
            # 1. YENİ BİLDİRİM BUTONU KONTROLÜ
            try:
                butonlar = driver.find_elements(By.XPATH, "//*[contains(text(), 'eni bildirim') or contains(text(), 'bildirimler var')]")
                for btn in butonlar:
                    if btn.is_displayed():
                        driver.execute_script("arguments[0].click();", btn)
                        time.sleep(3) 
                        break 
            except:
                pass

            # 2. TABLODAKİ TÜM LİNKLERİ ÇEK
            link_elementleri = driver.find_elements(By.XPATH, "//a[contains(@href, '/tr/Bildirim/')]")
            
            anlik_ilanlar = {} # Aynı ilanın tüm sütunlarını burada birleştireceğiz
            
            for link in link_elementleri:
                try:
                    # Sitenin en tepesindeki (Y<200) kayan reklam bandını tamamen yoksay (EBEBEK belası burada çözüldü)
                    if link.location['y'] < 200:
                        continue
                        
                    url = link.get_attribute("href")
                    bid = url.split("/")[-1]
                    if not bid: continue
                    
                    # Sadece o hücrenin metnini al
                    ham_metin = link.get_attribute("textContent").strip()
                    
                    # Aynı ID'ye sahip yazıları yan yana ekle (TKNSA + Yeni İş İlişkisi + Özet...)
                    if bid not in anlik_ilanlar:
                        anlik_ilanlar[bid] = {
                            'element': link, # Tıklamak için bir tane linki elimizde tutuyoruz
                            'metin': ham_metin
                        }
                    else:
                        anlik_ilanlar[bid]['metin'] += " | " + ham_metin
                        
                except:
                    continue
                    
            # 3. ŞİMDİ TOPLADIĞIMIZ İLANLARI DEĞERLENDİRELİM
            for bid, veri in anlik_ilanlar.items():
                if bid not in eski_idler:
                    eski_idler.add(bid) # Artık bu ilanın TÜM satırını okuduk, eskilere atabiliriz
                    
                    orijinal_metin = veri['metin']
                    
                    # Eğer satırda hiç yazı yoksa pas geç
                    if len(orijinal_metin) < 5:
                        continue

                    # Kırmızı kutuyu çiz (Nereye baktığını gör)
                    hedef_link = veri['element']
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", hedef_link)
                    driver.execute_script("arguments[0].style.border='3px solid red'", hedef_link)
                    time.sleep(0.3)
                    
                    print(f"👀 İlan Okundu: {orijinal_metin[:120]}...")
                    driver.execute_script("arguments[0].style.border=''", hedef_link)
                    
                    metin = standart_metne_cevir(orijinal_metin)
                    
                    # --- HEDEF KONTROLÜ (Senin 3 Altın Kuralın) ---
                    hedef_bulundu = False
                    if "YENI IS ILISKISI" in metin or "IHALE" in metin or "OZEL DURUM ACIKLAMASI" in metin or "SOZLESME" in metin or "SIPARIS" in metin:
                        hedef_bulundu = True

                    if hedef_bulundu:
                        print("\n" + "*"*60)
                        print(f"🎯 HEDEF BULUNDU! Yeni sekmede açılıyor...")
                        
                        # 4. YENİ SEKMEDE AÇ VE ADRESİ KOPYALA
                        driver.execute_script("window.open(arguments[0].href, '_blank');", hedef_link)
                        time.sleep(2)
                        
                        driver.switch_to.window(driver.window_handles[-1])
                        adres_cubugu_url = driver.current_url
                        final_id = adres_cubugu_url.split("/")[-1]
                        
                        print(f"🔗 URL Alındı: {adres_cubugu_url}")
                        print(f"🚀 KAP Kazıyıcı ({final_id}) tetikleniyor...")
                        
                        # 5. KAZIYICIYI ÇALIŞTIR
                        subprocess.Popen([sys.executable, "kap_kaziyici.py", final_id])
                        
                        # Sekmeyi kapat ve ana listeye dön
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        
                        print("*"*60 + "\n")
                        time.sleep(1)
            
            time.sleep(15)

    except Exception as e:
        print(f"❌ HATA: {e}")

kap_tam_isabet_avcisi()