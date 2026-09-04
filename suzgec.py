from collections import deque

class KapSuzgeci:
    def __init__(self):
        # FIFO (İlk Giren İlk Çıkar) mantığı için kuyruk
        self.kuyruk = deque()      
        # Aynı linki 2 kere kuyruğa almamak için geçmişi tuttuğumuz hafıza
        self.hafiza = set()        

    def link_ekle(self, url):
        """Link yeni ise kuyruğa ekler, eskiyse reddeder."""
        if url in self.hafiza:
            return False # Bu link zaten var, reddedildi.
        else:
            self.hafiza.add(url)   # Linki hafızaya kazı
            self.kuyruk.append(url) # İşlem sırası (kuyruk) için sıraya al
            return True # Yeni link başarıyla eklendi!

    def islenecek_link_al(self):
        """Kuyruktaki en eski (ilk giren) linki verir ve kuyruktan siler."""
        if self.kuyruk:
            return self.kuyruk.popleft() # Sol taraftan (en baştan) al
        return None

    def kuyruk_durumu(self):
        """Kuyrukta bekleyen link sayısını verir."""
        return len(self.kuyruk)