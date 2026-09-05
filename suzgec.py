from collections import deque
import time

from konu import KonuIsleyici

class KapSuzgeci:
    def __init__(self):
        self.kuyruk = deque()      
        self.hafiza = set()        
        self.konu = KonuIsleyici() 

    def link_ekle(self, url):
        """Radar'dan gelen link yeniyse hafızaya yazar ve kuyruğa dizer."""
        if url in self.hafiza:
            return False 
        else:
            self.hafiza.add(url)   
            self.kuyruk.append(url) 
            return True 

    def kuyruk_durumu(self):
        return len(self.kuyruk)

    def kuyrugu_isle(self, driver, sure_limiti):
        print(f"⏳ [SÜZGEÇ] Kuyruk kontrol ediliyor...")
        baslangic_zamani = time.time()
        
        # 16 saniye boyunca sadece şartlar uygunsa işlem yapar
        while time.time() - baslangic_zamani < sure_limiti:
            
            # ŞART: Kuyrukta link olacak VE konu.py meşgul olmayacak!
            if self.kuyruk and not self.konu.mesgul:
                
                # Sadece 1 tane linki kuyruktan al
                islenen_link = self.kuyruk.popleft()
                print(f"🛠️ [SÜZGEÇ] Link kuyruktan çekildi, konu.py'ye yollanıyor: {islenen_link.split('/')[-1]}")
                
                # konu.py'ye gönder (konu.py kendini meşgul yapacak)
                self.konu.isleme_basla(driver, islenen_link)
                
            else:
                # konu.py meşgulse süzgeç hiçbir şey yapmaz, süresinin bitmesini bekler
                time.sleep(1)