import time
import re
import yfinance as yf
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

# 🔥 KENDİ YAZDIĞIN BİLANÇO DOSYASINI İÇERİ AKTARIYORUZ
from bilanco_test import BilancoOkuyucu 

class KapKaziyici:
    def __init__(self):
        # Bilanço uzmanımızı göreve hazır bekletiyoruz
        self.bilanco_motoru = BilancoOkuyucu()

    def veri_cek(self, driver, url):
        print(f"\n💰 [KAP_KAZIYICI.PY] İş/İhale ilanı inceleniyor: {url.split('/')[-1]}")
        
        driver.execute_script(f"window.open('{url}', '_blank');")
        driver.switch_to.window(driver.window_handles[-1])
        
        try:
            print("⏳ 1. KAP sitesine bağlanılıyor... (Sayfa bekleniyor)")
            time.sleep(4)
            
            # --- HİSSE KODUNU OTOMATİK BULMA ---
            try:
                hisse_kodu_element = driver.find_element(By.CSS_SELECTOR, ".type-medium.bi-sky-black")
                hisse_kodu = hisse_kodu_element.text.strip().split(',')[0].strip()
                print(f"🏢 Tespit Edilen Hisse Kodu: {hisse_kodu}")
            except:
                print("⚠️ Hisse kodu sayfada bulunamadı! Halka açık bir şirket olmayabilir.")
                return False

            soup = BeautifulSoup(driver.page_source, "html.parser")
            tum_metin = soup.get_text(separator=" ", strip=True)
            
            if "ABD Doları" in tum_metin:
                arama_kalibi = r"([\d\.,]+)\s+([A-Za-zÇĞİÖŞÜçğıöşü\s]+)\s*\(([A-Za-zÇĞİÖŞÜçğıöşü]+)\)"
                sonuc = re.search(arama_kalibi, tum_metin)
                
                if sonuc:
                    print("✅ BÜYÜK İHALE YAKALANDI!")
                    ham_tutar = sonuc.group(1)
                    temiz_tutar = ham_tutar.replace(".", "").replace(",", ".")
                    is_hacmi_dolar = float(temiz_tutar)
                    
                    print("2. Canlı Dolar kuru çekiliyor (Yahoo Finance)...")
                    kur_verisi = yf.Ticker("USDTRY=X")
                    anlik_kuru = kur_verisi.history(period="1d")['Close'].iloc[-1]
                    toplam_tl_degeri = is_hacmi_dolar * anlik_kuru
                    print(f"--> İhalenin Toplam TL Karşılığı: {toplam_tl_degeri:,.2f} TL")
                    
                    # =========================================================
                    # 🔥 BURADA BİLANÇO DOSYASINA "ŞU HİSSEYİ BUL" DİYORUZ 🔥
                    # =========================================================
                    sirket_ozsermayesi = self.bilanco_motoru.ozsermaye_getir(hisse_kodu)
                    
                    if sirket_ozsermayesi > 0:
                        # --- TERAZİ (KARAR ANI) ---
                        print("\n⚖️ HESAPLAMA VE KARAR AŞAMASI ⚖️")
                        if toplam_tl_degeri > sirket_ozsermayesi:
                            print("🚨 HEDEF VURULDU! İhale bedeli, şirketin özsermayesinden BÜYÜK!")
                            print("Telegram'a 'AL' sinyali gönderilecek (Bir sonraki aşama).")
                        else:
                            oran = (toplam_tl_degeri / sirket_ozsermayesi) * 100
                            print(f"İhale devasa ama özsermayeyi geçemedi. (Özsermayenin %{oran:.1f}'i kadar)")
                            print("Telegram sessiz kalacak. Tarama devam ediyor...")
                    else:
                        print("⚠️ Bilanço çekilemediği için terazi kurulamadı.")
                else:
                    print("Rakamlar sayfada var ama Regex formülü eşleşmedi.")
            else:
                print("KAP metninde 'ABD Doları' bulunamadı.")
            
            return True
            
        except Exception as e:
            print(f"⚠️ [KAP_KAZIYICI.PY] Beklenmeyen Hata: {e}")
            return False
            
        finally:
            if len(driver.window_handles) > 1:
                print("🧹 [KAP_KAZIYICI.PY] İşlem tamam, sekme kapatıldı ve radara dönüldü.\n")
                driver.close()
                driver.switch_to.window(driver.window_handles[0])