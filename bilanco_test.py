from isyatirimhisse import fetch_financials
import datetime

class BilancoOkuyucu:
    def ozsermaye_getir(self, hisse_kodu):
        su_anki_yil = datetime.datetime.now().year 
        print(f"\n📊 [BILANCO_TEST.PY] {hisse_kodu} için en güncel bilanço İş Yatırım'dan aranıyor...")

        try:
            df = fetch_financials(
                symbols=hisse_kodu, 
                start_year=su_anki_yil - 1, 
                end_year=su_anki_yil, 
                exchange="TRY", 
                financial_group='1' 
            )
            
            sutunlar = df.columns.tolist()
            isim_sutunu = 'FINANCIAL_ITEM_NAME_TR'
            
            ozkaynak_satiri = df[df[isim_sutunu].str.strip().str.upper() == "TOPLAM ÖZKAYNAKLAR"]
            
            if ozkaynak_satiri.empty:
                ozkaynak_satiri = df[df[isim_sutunu].str.contains("Ana Ortaklığa Ait Özkaynaklar", case=False, na=False)]
                
            if not ozkaynak_satiri.empty:
                donem_sutunlari = [col for col in sutunlar if '/' in col]
                donem_sutunlari.sort(reverse=True)
                
                ozsermaye = 0
                gecerli_donem = ""
                
                for donem in donem_sutunlari:
                    ham_deger = ozkaynak_satiri.iloc[0][donem]
                    try:
                        sayisal_deger = float(str(ham_deger).replace(",", ""))
                        if sayisal_deger > 0: 
                            ozsermaye = sayisal_deger
                            gecerli_donem = donem
                            break 
                    except:
                        continue
                        
                if ozsermaye > 0:
                    print("✅ BAŞARILI! NOKTA ATIŞI VERİ ÇEKİLDİ")
                    print(f"Bilanço Dönemi: {gecerli_donem}")
                    print(f"Özsermaye: {ozsermaye:,.2f} TL")
                    return ozsermaye # RAKAMI KAZIYICIYA GERİ GÖNDERİYOR
                else:
                    print("⚠️ Uyarı: Satır bulundu ama tüm dönemlerdeki veriler 0 görünüyor.")
                    return 0
            else:
                print("⚠️ Özkaynak kalemi tabloda bulunamadı.")
                return 0
                
        except Exception as e:
            print(f"❌ [BILANCO_TEST.PY] Hata: {e}")
            return 0