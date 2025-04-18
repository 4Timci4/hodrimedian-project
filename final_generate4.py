"""
Veri Veri İşleme ve Ana Program Akışı (final_generate4.py)
---------------------------------------------------------
Bu modül, veri işleme işlemlerini ve ana program akışını içerir.

İçerik:
- DataIO: Veri okuma ve yazma işlemleri
- HolidayAdjuster: Tatil etkisi ve özel dönem ayarlamaları
- Main: Ana program akışı
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Union, Optional

# Diğer modüllerden gerekli sınıfları içe aktarma
from final_generate1 import Constants, DataTypes, DateTimeUtils
from final_generate2 import ProductModel, SeasonModel
from final_generate3 import PurchaseGenerator, StatisticalUtils
# Satış verilerini bir kez içe aktarma
from sales_data import SPECIAL_DAY_WEIGHTS


class DataIO:
    """Veri okuma ve yazma işlemleri."""
    
    @staticmethod
    def load_data(file_path: str) -> pd.DataFrame:
        """Veri dosyasını yükler."""
        return pd.read_csv(file_path)
    
    @staticmethod
    def filter_columns(df: pd.DataFrame) -> pd.DataFrame:
        """'Discount Applied' ve 'Frequency of Purchases' sütunlarını filtreler. 'Previous Purchases' sütunu korunur."""
        return df.drop(['Discount Applied', 'Frequency of Purchases'], axis=1)
    
    @staticmethod
    def write_to_csv(data: List[List[Any]], output_file: str) -> None:
        """Verileri CSV dosyasına yazar."""
        # Başlık ve veri satırlarını ayırma
        header = data[0]
        rows = data[1:]
        
        # DataFrame oluşturma
        df = pd.DataFrame(rows, columns=header)
        
        # CSV'ye yazma
        df.to_csv(output_file, index=False)
        
        print(f"Veri {output_file} dosyasına başarıyla yazıldı.")
        print(f"Toplam {len(rows)} satır veri oluşturuldu.")
    
    @staticmethod
    def create_previous_purchases_data(df: pd.DataFrame, product_data: Dict[str, Any]) -> List[List[Any]]:
        """Geçmiş ve gelecek alışveriş verilerini oluşturur."""
        # İstenmeyen sütunları kaldırma
        filtered_df = DataIO.filter_columns(df)
        
        # Çıktı verilerini hazırlama
        header = filtered_df.columns.tolist()
        header.append('Purchase Date')
        
        # Geçmiş alışveriş kayıtlarını oluşturma
        print("Geçmiş alışveriş kayıtları oluşturuluyor...")
        past_purchases = PurchaseGenerator.process_past_purchases(df, product_data)
        
        # Gelecek alışveriş kayıtlarını oluşturma
        print("Gelecek alışveriş tahminleri oluşturuluyor...")
        future_purchases = PurchaseGenerator.process_future_purchases(df, product_data)
        
        # Tüm satırları birleştirme
        all_rows = past_purchases + future_purchases
        
        # Son alışveriş tarihlerini istenen oranlara göre düzenle
        print("Son alışveriş tarihleri düzenleniyor...")
        print("- Son alışverişi 2022'de olan müşteriler: %5")
        print("- Son alışverişi 2023'de olan müşteriler: %11")
        
        # Customer ID ve Purchase Date sütunlarının indekslerini bul
        customer_id_index = header.index('Customer ID')
        date_index = len(header) - 1  # Son sütun Purchase Date
        
        # PurchaseGenerator sınıfındaki adjust_last_purchase_dates metodunu kullan
        adjusted_rows = PurchaseGenerator.adjust_last_purchase_dates(all_rows, customer_id_index, date_index)
        
        # Başlığı ve satırları birleştirme
        output_data = [header] + adjusted_rows
        
        return output_data


class HolidayAdjuster:
    """Tatil etkisi ve mevsimsel ayarlamalar."""
    
    @staticmethod
    def convert_holidays_to_list(year: int) -> List[Tuple[datetime, str, float]]:
        """SeasonModel.define_holidays() tarafından tanımlanan tatil günlerini liste formatına dönüştürür."""
        holidays_dict = SeasonModel.define_holidays()
        holidays_list = []
        
        # Sabit tarihli tatiller
        for (month, day), holiday_info in holidays_dict.items():
            try:
                date = datetime(year, month, day)
                holidays_list.append((date, holiday_info['name'], holiday_info['weight']))
            except ValueError:
                # Geçersiz tarih durumunda atla (örn. 29 Şubat artık yıl değilse)
                continue
        
        # Değişken tarihli tatiller (Thanksgiving, Easter vb.) için özel hesaplamalar
        # Thanksgiving (Kasım ayının dördüncü Perşembe günü)
        thanksgiving = DateTimeUtils.calculate_holiday_date(year, 11, 3, 4)  # 3=Perşembe
        holidays_list.append((thanksgiving, "Thanksgiving", 2.2))
        
        # Black Friday (Thanksgiving'in ertesi günü)
        black_friday = thanksgiving + timedelta(days=1)
        holidays_list.append((black_friday, "Black Friday", 3.0))
        
        # Cyber Monday (Thanksgiving'den sonraki Pazartesi)
        cyber_monday = thanksgiving + timedelta(days=(7 - thanksgiving.weekday() + 0) % 7)
        holidays_list.append((cyber_monday, "Cyber Monday", 2.5))
        
        # Anneler Günü (Mayıs'ın 2. Pazar günü)
        mothers_day = DateTimeUtils.calculate_holiday_date(year, 5, 6, 2)  # 6=Pazar
        holidays_list.append((mothers_day, "Mother's Day", 2.0))
        
        # Babalar Günü (Haziran'ın 3. Pazar günü)
        fathers_day = DateTimeUtils.calculate_holiday_date(year, 6, 6, 3)  # 6=Pazar
        holidays_list.append((fathers_day, "Father's Day", 1.8))
        
        # Paskalya (basitleştirilmiş hesaplama)
        easter_dates = {2022: datetime(2022, 4, 17), 2023: datetime(2023, 4, 9), 2024: datetime(2024, 3, 31)}
        easter = easter_dates.get(year)
        if easter:
            holidays_list.append((easter, "Easter", 1.8))
        
        return holidays_list
    
    @staticmethod
    def apply_holiday_effect(df: pd.DataFrame, holidays: List[Tuple[datetime, str, float]]) -> pd.DataFrame:
        """Tüm tatiller için satış artışı etkisi uygular, toplam satır sayısını değiştirmeden.
        
        Args:
            df: Müşteri verileri DataFrame'i
            holidays: (tarih, isim, ağırlık) şeklinde tatil listesi
        
        Returns:
            Tatil etkisi uygulanmış DataFrame
        """
        # Tarih sütununu datetime formatına çevir
        df = df.copy()  # DataFrame'in kopyasını oluştur
        df['Purchase Date'] = pd.to_datetime(df['Purchase Date'])
        
        # Kasım ve Aralık ayları için özel ağırlıklar
        black_friday_weight = SPECIAL_DAY_WEIGHTS['black_friday']
        christmas_weight = SPECIAL_DAY_WEIGHTS['christmas']
        
        # Tatil günlerine yakın tarihlerde yapılan alışverişlerin ağırlıklarını artır
        for index, row in df.iterrows():
            purchase_date = row['Purchase Date']
            
            # Kasım ayı için özel işlem
            if purchase_date.month == 11:
                # Black Friday etkisi (Kasım ayının son haftası)
                if purchase_date.day >= 20:
                    # Satın alma miktarını artır - en az %30, en fazla %60 artış
                    price_adjustment = 1.3 + (np.random.random() * 0.3 * black_friday_weight)  # 1.3 ile 1.6 arasında
                    df.at[index, 'Purchase Amount (USD)'] = min(row['Purchase Amount (USD)'] * price_adjustment, 100.0)
            
            # Aralık ayı için özel işlem
            elif purchase_date.month == 12:
                # Yılbaşı alışverişleri etkisi (Aralık ayının son 10 günü)
                if purchase_date.day >= 20:
                    # Satın alma miktarını artır - en az %30, en fazla %60 artış
                    price_adjustment = 1.3 + (np.random.random() * 0.3 * christmas_weight)  # 1.3 ile 1.6 arasında
                    df.at[index, 'Purchase Amount (USD)'] = min(row['Purchase Amount (USD)'] * price_adjustment, 100.0)
            
            # Diğer tatil günleri için normal işlem
            for holiday_date, holiday_name, weight in holidays:
                # Satın alma tarihi ile tatil arasındaki fark
                date_diff = abs((purchase_date - holiday_date).days)
                
                # Eğer satın alma, tatilden önceki veya sonraki 3 gün içinde gerçekleştiyse
                if date_diff <= 3:
                    # Tatile yakınlık faktörü: tatil günü=1.0, ±1 gün=0.7, ±2 gün=0.5, ±3 gün=0.3
                    proximity_factor = 1.0 if date_diff == 0 else (0.7 if date_diff == 1 else (0.5 if date_diff == 2 else 0.3))
                    
                    # Satın alma miktarını artırma olasılığı: ağırlık * yakınlık faktörü / 10
                    probability = (weight * proximity_factor) / 10
                    
                    # Belirli olasılıkla satın alma miktarını artır
                    if np.random.random() < probability:
                        # Satın alma miktarını artır - en az %30, en fazla %60 artış
                        price_adjustment = 1.3 + (np.random.random() * 0.3)  # 1.3 ile 1.6 arasında
                        df.at[index, 'Purchase Amount (USD)'] = min(row['Purchase Amount (USD)'] * price_adjustment, 100.0)
        
        return df
    
    @staticmethod
    def apply_covid_effect(df: pd.DataFrame) -> pd.DataFrame:
        """2022 yılı için COVID-19 etkisini uygular, toplam satır sayısını değiştirmeden.
        
        Not: Bu fonksiyon sadece 2022 yılı için COVID-19 etkisini uygular çünkü
        pandemi etkisi 2022 yılında daha belirgindi. 2023 ve 2024 yıllarında
        alışveriş davranışları normale dönmeye başladı.
        
        Args:
            df: Müşteri verileri DataFrame'i
        
        Returns:
            COVID etkisi uygulanmış DataFrame
        """
        # DataFrame'in kopyasını oluştur (tarih sütunu zaten apply_holiday_effect'te datetime'a çevrildi)
        df = df.copy()
        
        # 2022 yılındaki satırları belirle
        mask_2022 = df['Purchase Date'].dt.year == 2022
        indices_2022 = df.index[mask_2022].tolist()
        
        if not indices_2022:  # Eğer 2022 yılında satır yoksa, değişiklik yapma
            return df
        
        # Rastgele %15 oranında 2022 satırlarının satın alma miktarlarını azalt (mağaza içi alışveriş azalması)
        indices_to_reduce = np.random.choice(indices_2022, size=int(len(indices_2022) * 0.15), replace=False)
        for idx in indices_to_reduce:
            # Satın alma miktarını azalt
            reduction_factor = 0.7 + np.random.random() * 0.2  # 0.7 ile 0.9 arasında
            df.at[idx, 'Purchase Amount (USD)'] = df.at[idx, 'Purchase Amount (USD)'] * reduction_factor
        
        # 2022 satırlarının %25'inin nakliye türünü ve ödeme yöntemini değiştir (online alışveriş artışı)
        indices_to_modify = np.random.choice(indices_2022, size=int(len(indices_2022) * 0.25), replace=False)
        for idx in indices_to_modify:
            # Nakliye türünü değiştir - online alışveriş için express seçenekler
            df.at[idx, 'Shipping Type'] = np.random.choice(['Express', '2-Day Shipping', 'Next Day Air'], p=[0.5, 0.3, 0.2])
            
            # Ödeme yöntemini online seçeneklere ayarla
            df.at[idx, 'Payment Method'] = np.random.choice(['Credit Card', 'PayPal', 'Apple Pay', 'Google Pay'], p=[0.5, 0.3, 0.1, 0.1])
            
            # Satın alma miktarını biraz artır (online alışveriş teşvikleri nedeniyle)
            increase_factor = 1.05 + np.random.random() * 0.1  # 1.05 ile 1.15 arasında
            df.at[idx, 'Purchase Amount (USD)'] = min(df.at[idx, 'Purchase Amount (USD)'] * increase_factor, 100.0)
        
        return df
    
    @staticmethod
    def redistribute_sales_by_target(df: pd.DataFrame) -> pd.DataFrame:
        """Satış sayılarını hedef değerlere göre yeniden dağıtır.
        
        Bu fonksiyon, ay bazında satış sayılarını hedef değerlere daha yakın hale getirir.
        Özellikle, Ocak 2024'teki fazla satışları azaltıp, Kasım ve Aralık 2024'teki satışları artırır.
        
        Args:
            df: Müşteri verileri DataFrame'i
            
        Returns:
            Yeniden dağıtılmış DataFrame
        """
        print("Satış sayıları hedef değerlere göre yeniden dağıtılıyor...")
        
        # Satış verilerini içe aktar
        from sales_data import SALES_DATA
        
        # DataFrame'in kopyasını oluştur
        df = df.copy()
        
        # Tarih sütununu datetime formatına çevir
        df['Purchase Date'] = pd.to_datetime(df['Purchase Date'])
        
        # 2024 yılı için hedef satış rakamları
        target_sales_2024 = SALES_DATA[2024]
        
        # 2024 yılı verilerini filtrele
        df_2024 = df[df['Purchase Date'].dt.year == 2024].copy()
        
        # Ay bazında satış sayılarını hesapla
        month_counts = df_2024.groupby(df_2024['Purchase Date'].dt.month).size()
        
        # Toplam satış sayısı
        total_sales = len(df_2024)
        
        # Hedef satış oranlarını hesapla - Utils sınıfını kullanarak normalize et
        from final_generate1 import Utils
        target_ratios = Utils.normalize_weights(target_sales_2024)
        
        # Ay bazında hedef satış sayılarını hesapla
        target_counts = {month: int(ratio * total_sales) for month, ratio in target_ratios.items()}
        
        # Ay bazında fazla/eksik satış sayılarını hesapla
        diff_counts = {}
        for month in range(1, 13):
            current = month_counts.get(month, 0)
            target = target_counts.get(month, 0)
            diff_counts[month] = current - target
        
        # Ocak ayındaki fazla satışları Kasım ve Aralık aylarına taşı
        if diff_counts[1] > 0:  # Ocak ayında fazla satış varsa
            # Kasım ve Aralık aylarına taşınacak satış sayısı
            to_move = min(diff_counts[1], 2000)  # En fazla 2000 satış taşı
            
            # Kasım ve Aralık aylarına eşit olarak dağıt
            to_november = to_move // 2
            to_december = to_move - to_november
            
            print(f"Ocak ayından {to_november} satış Kasım ayına, {to_december} satış Aralık ayına taşınıyor...")
            
            # Ocak ayından rastgele satırları seç
            january_indices = df_2024[df_2024['Purchase Date'].dt.month == 1].index.tolist()
            if len(january_indices) > to_move:
                indices_to_move = np.random.choice(january_indices, size=to_move, replace=False)
                
                # Kasım ayına taşınacak satırlar
                november_indices = indices_to_move[:to_november]
                
                # Aralık ayına taşınacak satırlar
                december_indices = indices_to_move[to_november:]
                
                # Kasım ayına taşı
                for idx in november_indices:
                    # Rastgele bir gün seç (Black Friday etkisi için son 10 gün ağırlıklı)
                    # Olasılık değerlerini oluştur
                    nov_probs_dict = {d: 0.02 if d < 20 else 0.05 for d in range(1, 31)}
                    # Utils sınıfını kullanarak normalize et
                    from final_generate1 import Utils
                    nov_probs_dict = Utils.normalize_weights(nov_probs_dict)
                    nov_probs = [nov_probs_dict[d] for d in range(1, 31)]
                    
                    day = np.random.choice(
                        range(1, 31),
                        p=nov_probs  # 20-30 Kasım için daha yüksek olasılık
                    )
                    new_date = datetime(2024, 11, day)
                    df.at[idx, 'Purchase Date'] = new_date
                
                # Aralık ayına taşı
                for idx in december_indices:
                    # Rastgele bir gün seç (Yılbaşı etkisi için son 10 gün ağırlıklı)
                    # Olasılık değerlerini oluştur
                    dec_probs_dict = {d: 0.02 if d < 20 else 0.05 for d in range(1, 32)}
                    # Utils sınıfını kullanarak normalize et
                    from final_generate1 import Utils
                    dec_probs_dict = Utils.normalize_weights(dec_probs_dict)
                    dec_probs = [dec_probs_dict[d] for d in range(1, 32)]
                    
                    day = np.random.choice(
                        range(1, 32),
                        p=dec_probs  # 20-31 Aralık için daha yüksek olasılık
                    )
                    new_date = datetime(2024, 12, day)
                    df.at[idx, 'Purchase Date'] = new_date
        
        # Diğer aylar için de benzer işlemleri yapabiliriz, ancak şimdilik sadece Ocak-Kasım-Aralık düzeltmesi yeterli
        
        # Yeniden dağıtım sonrası satış sayılarını hesapla
        df_2024_new = df[df['Purchase Date'].dt.year == 2024]
        new_month_counts = df_2024_new.groupby(df_2024_new['Purchase Date'].dt.month).size()
        
        print("Yeniden dağıtım sonrası 2024 yılı ay bazında satış sayıları:")
        for month in range(1, 13):
            old_count = month_counts.get(month, 0)
            new_count = new_month_counts.get(month, 0)
            target = target_counts.get(month, 0)
            print(f"Ay {month}: Önceki: {old_count}, Yeni: {new_count}, Hedef: {target}")
        
        return df
    
    @staticmethod
    def apply_promo_codes(df: pd.DataFrame) -> pd.DataFrame:
        """Müşteri bazında promosyon kodu kullanımını uygular.
        
        Subscription Status 1 (üyelik durumu aktif) olan müşterilerin %35'inin alışverişlerinde,
        Subscription Status 0 (üye olmayan) müşterilerin %15'inin alışverişlerinde promosyon kodu
        kullanıldığını belirten yeni bir sütun ekler. Promosyon kodu kullanımı tek bir müşterinin
        tüm alışverişlerine değil, farklı müşterilerin alışverişlerine dağıtılır.
        
        Args:
            df: Müşteri alışveriş verileri DataFrame'i
            
        Returns:
            Promosyon kodu sütunu eklenmiş DataFrame
        """
        print("Promosyon kodu kullanımı uygulanıyor...")
        
        # DataFrame'in kopyasını oluştur
        df = df.copy()
        
        # Promosyon kodu sütununu ekle, varsayılan olarak 0 (kullanılmadı)
        df['Promo Code Used'] = 0
        
        # Müşteri kimliklerine göre verileri grupla
        customer_groups = df.groupby('Customer ID')
        
        # Her müşteri için ayrı ayrı işlem yap
        for customer_id, customer_df in customer_groups:
            # Müşterinin abonelik durumunu belirle
            subscription_status = customer_df['Subscription Status'].iloc[0]
            
            # Hedef promosyon kodu kullanım oranını belirle
            if subscription_status == 1:
                target_promo_ratio = 0.35  # Aboneliği olan müşteriler için %35
            else:
                target_promo_ratio = 0.15  # Aboneliği olmayan müşteriler için %15
            
            # Müşterinin kaç alışverişinde promosyon kodu kullanılacağını hesapla
            num_purchases = len(customer_df)
            num_promo_uses = int(num_purchases * target_promo_ratio)
            
            if num_promo_uses > 0:
                # Rastgele alışveriş indekslerini seç
                indices_to_apply = np.random.choice(
                    customer_df.index.tolist(), 
                    size=num_promo_uses, 
                    replace=False
                )
                
                # Seçilen alışverişlere promosyon kodu kullanımını uygula
                df.loc[indices_to_apply, 'Promo Code Used'] = 1
        
        # Promosyon kodu kullanım istatistiklerini göster
        sub_status_1_count = len(df[df['Subscription Status'] == 1])
        sub_status_0_count = len(df[df['Subscription Status'] == 0])
        
        promo_used_sub_1 = len(df[(df['Subscription Status'] == 1) & (df['Promo Code Used'] == 1)])
        promo_used_sub_0 = len(df[(df['Subscription Status'] == 0) & (df['Promo Code Used'] == 1)])
        
        # Sıfıra bölme hatalarını önlemek için kontrol ekliyoruz
        if sub_status_1_count > 0:
            promo_percent_1 = (promo_used_sub_1 / sub_status_1_count) * 100
            print(f"Subscription Status 1 (Üyeler): Toplam {sub_status_1_count} alışveriş, "
                  f"{promo_used_sub_1} alışverişte promosyon kodu kullanıldı ({promo_percent_1:.2f}%)")
        else:
            print(f"Subscription Status 1 (Üyeler): Veri yok")
        
        if sub_status_0_count > 0:
            promo_percent_0 = (promo_used_sub_0 / sub_status_0_count) * 100
            print(f"Subscription Status 0 (Üye olmayanlar): Toplam {sub_status_0_count} alışveriş, "
                  f"{promo_used_sub_0} alışverişte promosyon kodu kullanıldı ({promo_percent_0:.2f}%)")
        else:
            print(f"Subscription Status 0 (Üye olmayanlar): Veri yok")
        
        return df
    
    @staticmethod
    def apply_adjustments(df: pd.DataFrame) -> pd.DataFrame:
        """Tatil etkisi ve COVID-19 etkisi gibi çeşitli ayarlamaları uygular."""
        print("Veri ayarlamaları uygulanıyor...")
        
        # 2022, 2023 ve 2024 için tatil günlerini al
        all_holidays = []
        for year in range(2022, 2025):
            holidays = HolidayAdjuster.convert_holidays_to_list(year)
            all_holidays.extend(holidays)
        
        # Tatil etkisini uygula
        print("Tatil günü etkisi uygulanıyor...")
        holiday_adjusted_df = HolidayAdjuster.apply_holiday_effect(df, all_holidays)
        
        # Covid etkisini uygula
        print("COVID-19 etkisi 2022 yılı için uygulanıyor...")
        covid_adjusted_df = HolidayAdjuster.apply_covid_effect(holiday_adjusted_df)
        
        # Satış sayılarını hedef değerlere göre yeniden dağıt
        print("Satış sayıları hedef değerlere göre yeniden dağıtılıyor...")
        sales_adjusted_df = HolidayAdjuster.redistribute_sales_by_target(covid_adjusted_df)
        
        # Promosyon kodu kullanımını uygula
        promo_adjusted_df = HolidayAdjuster.apply_promo_codes(sales_adjusted_df)
        
        # Haftanın günü bilgisini ekle
        print("Haftanın günü bilgisi ekleniyor...")
        # Tarih sütununun datetime formatında olduğundan emin ol
        promo_adjusted_df['Purchase Date'] = pd.to_datetime(promo_adjusted_df['Purchase Date'])
        
        # Haftanın günü numarasını ekle (1: Pazartesi, 2: Salı, ..., 7: Pazar)
        promo_adjusted_df['WeekdayNum'] = promo_adjusted_df['Purchase Date'].dt.dayofweek + 1
        
        # Haftanın günü ismini ekle (İngilizce)
        day_names = {
            1: 'Monday',
            2: 'Tuesday',
            3: 'Wednesday',
            4: 'Thursday',
            5: 'Friday',
            6: 'Saturday',
            7: 'Sunday'
        }
        promo_adjusted_df['Weekday'] = promo_adjusted_df['WeekdayNum'].map(day_names)
        
        # Hafta içi/sonu bilgisini ekle (0: Hafta içi, 1: Hafta sonu)
        promo_adjusted_df['Weekend'] = promo_adjusted_df['WeekdayNum'].apply(lambda x: 1 if x >= 6 else 0)
        
        print(f"Özet:")
        print(f"Orijinal satın alma sayısı: {len(df)}")
        print(f"Düzeltilmiş satın alma sayısı: {len(promo_adjusted_df)}")
        print(f"Fark: {len(promo_adjusted_df) - len(df)} ({(len(promo_adjusted_df) - len(df)) / len(df) * 100:.2f}%)")
        
        # 2022 yılı karşılaştırması
        orig_2022 = len(df[pd.to_datetime(df['Purchase Date']).dt.year == 2022])
        adj_2022 = len(promo_adjusted_df[pd.to_datetime(promo_adjusted_df['Purchase Date']).dt.year == 2022])
        print(f"\n2022 satın alma sayısı (orijinal): {orig_2022}")
        print(f"2022 satın alma sayısı (düzeltilmiş): {adj_2022}")
        print(f"2022 değişim: {adj_2022 - orig_2022} ({(adj_2022 - orig_2022) / orig_2022 * 100:.2f}%)")
        
        # Haftanın günlerine göre satış dağılımı
        weekday_counts = promo_adjusted_df['Weekday'].value_counts().sort_index()
        total_count = len(promo_adjusted_df)
        
        print("\nHaftanın Günlerine Göre Satış Dağılımı:")
        for day, count in weekday_counts.items():
            percentage = (count / total_count) * 100
            print(f"{day}: {count} satış ({percentage:.1f}%)")
        
        return promo_adjusted_df


def main():
    """Ana program akışı."""
    # Rastgele sayı üreteci için sabit başlangıç değeri
    print("Program başlatılıyor...")
    random.seed(Constants.RANDOM_SEED)
    np.random.seed(Constants.RANDOM_SEED)
    
    # Veri yükleme
    print(f"{Constants.INPUT_FILE} dosyası yükleniyor...")
    df = DataIO.load_data(Constants.INPUT_FILE)
    
    # Ürün verilerini tanımlama
    print("Ürün verileri tanımlanıyor...")
    product_data = ProductModel.define_product_data()
    
    # Geçmiş alışveriş verilerini oluşturma
    print("Alışveriş verileri oluşturuluyor...")
    output_data = DataIO.create_previous_purchases_data(df, product_data)
    
    # Verileri doğrudan DataFrame'e dönüştür
    header = output_data[0]
    rows = output_data[1:]
    temp_df = pd.DataFrame(rows, columns=header)
    
    # Tatil etkisi ve COVID etkisi uygula
    adjusted_df = HolidayAdjuster.apply_adjustments(temp_df)
    
    # Son dosyayı kaydet
    adjusted_df.to_csv(Constants.OUTPUT_FILE, index=False)
    print(f"Düzeltilmiş veri {Constants.OUTPUT_FILE} dosyasına kaydedildi.")
    
    print("Program başarıyla tamamlandı!")


if __name__ == "__main__":
    main()
