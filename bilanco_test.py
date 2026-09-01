from isyatirimhisse import fetch_financials
import datetime

hisse_kodu = "CWENE"
su_anki_yil = datetime.datetime.now().year 

print(f"{hisse_kodu} için en güncel bilanço İş Yatırım'dan aranıyor...\n")

try:
    df = fetch_financials(
        symbols=hisse_kodu, 
        start_year=su_anki_yil - 1, 
        end_year=su_anki_yil, 
        exchange="TRY", 
        financial_group='1' 
    )
    
    # Sütun isimleri listesi
    sutunlar = df.columns.tolist()
    isim_sutunu = 'FINANCIAL_ITEM_NAME_TR'
    
    # Nokta atışı 'TOPLAM ÖZKAYNAKLAR' satırını arıyoruz
    ozkaynak_satiri = df[df[isim_sutunu].str.strip().str.upper() == "TOPLAM ÖZKAYNAKLAR"]
    
    # Eğer bulamazsa, alternatif resmi adını arıyoruz
    if ozkaynak_satiri.empty:
        ozkaynak_satiri = df[df[isim_sutunu].str.contains("Ana Ortaklığa Ait Özkaynaklar", case=False, na=False)]
        
    if not ozkaynak_satiri.empty:
        # Tarih içeren sütunları (içinde '/' olanlar) ayırıp sondan başa doğru sıralıyoruz
        donem_sutunlari = [col for col in sutunlar if '/' in col]
        donem_sutunlari.sort(reverse=True)
        
        ozsermaye = 0
        gecerli_donem = ""
        
        # En güncel dönemden geriye doğru sıfır OLMAYAN ilk rakamı arıyoruz
        for donem in donem_sutunlari:
            ham_deger = ozkaynak_satiri.iloc[0][donem]
            
            try:
                # Metni sayıya çevir
                sayisal_deger = float(str(ham_deger).replace(",", ""))
                if sayisal_deger > 0: # Eğer rakam 0'dan büyükse, doğru veriyi bulduk demektir!
                    ozsermaye = sayisal_deger
                    gecerli_donem = donem
                    break # Bulduğumuz an aramayı durdur
            except:
                continue
                
        if ozsermaye > 0:
            print("✅ BAŞARILI! NOKTA ATIŞI VERİ ÇEKİLDİ")
            print(f"Şirket: {hisse_kodu}")
            print(f"Bilanço Dönemi: {gecerli_donem}")
            print(f"Özsermaye: {ozsermaye:,.2f} TL")
        else:
            print("Uyarı: Satır bulundu ama tüm dönemlerdeki veriler 0 görünüyor.")
    else:
        print("Özkaynak kalemi tabloda bulunamadı.")
        
except Exception as e:
    print(f"Hata: {e}")