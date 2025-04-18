"""
Veri Analizi Yardımcı Sınıflar ve Sabitler (final_generate1.py)
--------------------------------------------------------------
Bu modül, veri analizi için gerekli temel veri yapılarını, sabitleri
ve tarih/zaman işlemleri için yardımcı fonksiyonları içerir.

İçerik:
- Constants: Sabit değerler ve yapılandırma parametreleri
- DataTypes: Veri yapıları ve yardımcı sınıflar
- DateTimeUtils: Tarih ve zaman ile ilgili yardımcı fonksiyonlar
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import calendar
from typing import Dict, List, Tuple, Any, Union, Optional, NamedTuple, TypeVar


class Constants:
    """Uygulamada kullanılan sabit değerler."""
    RANDOM_SEED = 42
    INPUT_FILE = 'shopping_behavior.csv'
    OUTPUT_FILE = 'previous_purchases_data.csv'
    DATE_FORMAT = '%Y-%m-%d'
    YEAR_RANGE = [2022, 2023, 2024]
    
    # Yaş grupları sınırları
    AGE_GROUPS = {
        (18, 26): '18-26',
        (27, 35): '27-35', 
        (36, 44): '36-44',
        (45, 53): '45-53',
        (54, 62): '54-62',
        (63, 70): '63-70'
    }
    
    # Beden dağılımları (yüzde olarak)
    SIZE_DISTRIBUTION = {
        'Male': {
            'S': 15.0,
            'M': 30.0,
            'L': 35.0,
            'XL': 20.0
        },
        'Female': {
            'S': 10.0,
            'M': 25.0,
            'L': 35.0,
            'XL': 30.0
        }
    }
    
    # Tüm beden seçenekleri
    SIZES = ['S', 'M', 'L', 'XL']
    
    # Haftanın günlerine göre alışveriş olasılık ağırlıkları 
    # Talep edilen dağılım:
    # Pazartesi: 8.4%, Salı: 9.5%, Çarşamba: 11.6%, Perşembe: 13.7%
    # Cuma: 18.9%, Cumartesi: 21.1%, Pazar: 16.8%
    WEEKDAY_WEIGHTS = {
        0: 0.084,  # Pazartesi
        1: 0.095,  # Salı
        2: 0.116,  # Çarşamba
        3: 0.137,  # Perşembe
        4: 0.189,  # Cuma
        5: 0.211,  # Cumartesi
        6: 0.168   # Pazar
    }
    
    # Değerlendirme ağırlıkları - Gerçek dünya verilerine dayalı daha belirgin J-curve/bimodal dağılımı
    # Kaynak: E-ticaret platformlarındaki gerçek yıldız dağılımları
    REVIEW_BASE_WEIGHTS = {
        5.0: 0.48,  # 5 yıldız - Çok daha belirgin, müşteriler memnun olduğunda yorum yapar
        4.5: 0.11,  # 4.5 yıldız
        4.0: 0.09,  # 4 yıldız
        3.5: 0.05,  # 3.5 yıldız - Orta değerler çok daha az (müşteriler kararsız değilse yorum yazmaz)
        3.0: 0.04,  # 3 yıldız
        2.5: 0.02,  # 2.5 yıldız
        2.0: 0.03,  # 2 yıldız
        1.5: 0.03,  # 1.5 yıldız
        1.0: 0.15   # 1 yıldız - Belirgin ikinci zirve (memnuniyetsiz müşteriler aktif yorum yapar)
    }
    
    # Popüler alışveriş günleri ve özel dönemler - gerçek takvim etkisi
    SHOPPING_SEASONS = {
        # Tatil sezonu
        (11, 15, 12, 31): 'Holiday Season',  # 15 Kasım - 31 Aralık
        # Yaz sezonu
        (6, 1, 8, 31): 'Summer Season',      # 1 Haziran - 31 Ağustos
        # Okul dönemi başlangıcı
        (8, 15, 9, 15): 'Back to School',    # 15 Ağustos - 15 Eylül
        # Bahar sezonu
        (3, 1, 5, 31): 'Spring Season',      # 1 Mart - 31 Mayıs
    }
    
    # Özel günler ve önemi - alışveriş davranışlarında artış faktörü
    # Satış verilerinden hesaplanan ağırlıkları içe aktar
    from sales_data import SPECIAL_DAY_WEIGHTS
    
    SPECIAL_DAYS = {
        # Black Friday ve çevresi (Kasım ayının son haftası)
        (11, 20, 11, 30): SPECIAL_DAY_WEIGHTS['black_friday'],
        # Yılbaşı alışverişleri (Aralık ayının son haftası)
        (12, 20, 12, 31): SPECIAL_DAY_WEIGHTS['christmas'],
        # Sevgililer Günü sezonu (1-14 Şubat)
        (2, 1, 2, 14): SPECIAL_DAY_WEIGHTS['valentines'],
        # Anneler Günü sezonu (Mayıs başı)
        (5, 1, 5, 15): SPECIAL_DAY_WEIGHTS['mothers_day'],
        # Okulların açılış dönemi (Ağustos sonu - Eylül başı)
        (8, 20, 9, 10): SPECIAL_DAY_WEIGHTS['back_to_school']
    }
    
    # Gelecek tarih aralığı - daha dengeli bir dağılım için tüm yılı kapsayacak şekilde değiştirildi
    FUTURE_DATE_START = datetime(2024, 1, 1)
    FUTURE_DATE_END = datetime(2024, 12, 31)


class DataTypes:
    """Veri tipleri ve yardımcı sınıflar."""
    
    class PurchaseDetails(NamedTuple):
        """Satın alma detayları için veri yapısı."""
        category: str
        item: str
        purchase_amount: float
        color: str
        size: str
        review_rating: float
        shipping_type: str
        payment_method: str


class Utils:
    """Genel yardımcı fonksiyonlar."""
    
    @staticmethod
    def normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
        """Ağırlıkları normalleştirir (toplamları 1 olacak şekilde)."""
        total_weight = sum(weights.values())
        if total_weight > 0:
            return {k: v/total_weight for k, v in weights.items()}
        else:
            # Eğer tüm ağırlıklar sıfırsa, eşit dağılım kullan
            return {k: 1.0/len(weights) for k in weights}


class DateTimeUtils:
    """Tarih ve zaman ile ilgili yardımcı fonksiyonlar."""
    
    @staticmethod
    def get_last_day_of_month(month: int, year: int) -> int:
        """Belirtilen ay ve yıl için ayın son gününü döndürür."""
        if month == 2:
            if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):  # Artık yıl kontrolü
                return 29
            else:
                return 28
        elif month in [4, 6, 9, 11]:  # 30 gün olan aylar
            return 30
        else:  # 31 gün olan aylar
            return 31
    
    @staticmethod
    def get_holiday_weight(date: datetime, holidays: Dict) -> float:
        """Belirli bir tarih için tatil, özel dönem ve gün ağırlığını döndürür."""
        # Özel günlerin kontrolü
        month_day = (date.month, date.day)
        if month_day in holidays:
            return holidays[month_day]['weight']
        
        # Özel dönemlerin kontrolü (tarih aralıkları - örn. tatil sezonu)
        for (start_month, start_day, end_month, end_day), weight in Constants.SPECIAL_DAYS.items():
            # Başlangıç ve bitiş tarihlerini oluştur
            start_date = datetime(date.year, start_month, start_day)
            # Yılı aşma durumu (örn. Kasım-Ocak)
            if end_month < start_month:
                end_date = datetime(date.year + 1, end_month, end_day)
            else:
                end_date = datetime(date.year, end_month, end_day)
            
            # Tarih aralığında mı kontrol et
            if start_date <= date <= end_date:
                # Aralık içinde tarihe yaklaştıkça ağırlığı artır (örn. Black Friday'e yaklaşırken)
                days_to_end = (end_date - date).days
                if days_to_end <= 3:  # Son 3 gün
                    return weight * 1.2  # %20 daha fazla alışveriş
                return weight
        
        # Özel bir durum yoksa haftanın gününe göre ağırlığı döndür
        weekday = date.weekday()  # 0: Pazartesi, 1: Salı, ..., 6: Pazar
        return Constants.WEEKDAY_WEIGHTS.get(weekday, 1.0)
    
    @staticmethod
    def generate_date_for_season(
        season: str, 
        year: int, 
        customer_id: int, 
        season_months: Dict[str, List[int]], 
        holidays: Dict[Tuple[int, int], Dict[str, Any]]
    ) -> datetime:
        """Belirli bir mevsim için uygun tarih oluşturur."""
        # Tutarlı rastgele sayı üretimi için
        random.seed(customer_id + hash(season) + year)
            
        # Mevsim için uygun ay seçimi
        month = random.choice(season_months[season])
            
        # Ay için son gün hesaplama
        last_day = DateTimeUtils.get_last_day_of_month(month, year)
            
        # Günler için ağırlıklar hesaplama (tatil günleri daha yüksek olasılıklı)
        day_weights = []
        for day in range(1, last_day + 1):
            try:
                date = datetime(year, month, day)
                weight = DateTimeUtils.get_holiday_weight(date, holidays)
                day_weights.append(weight)
            except ValueError:
                day_weights.append(0)  # Geçersiz tarih
            
        # Ağırlıklı olarak gün seçimi
        if sum(day_weights) > 0:  # Eğer en az bir geçerli gün varsa
            day = random.choices(range(1, last_day + 1), weights=day_weights, k=1)[0]
        else:
            day = random.randint(1, last_day)  # Tüm günler geçersizse rastgele seç
            
        # Tarihi oluşturma ve doğrulama
        try:
            date = datetime(year, month, day)
            return date
        except ValueError:
            # Geçersiz tarih durumunda başka bir gün seç
            day = random.randint(1, last_day - 1)
            date = datetime(year, month, day)
            return date
    
    @staticmethod
    def generate_random_future_date() -> str:
        """1 Ocak 2024 ile 31 Aralık 2024 arasında rastgele bir tarih üretir."""
        date_range = (Constants.FUTURE_DATE_END - Constants.FUTURE_DATE_START).days
        
        # Hafta içi günlere daha yüksek ağırlık verme
        weights = []
        current_date = Constants.FUTURE_DATE_START
        for _ in range(date_range + 1):
            # 0: Pazartesi, ..., 6: Pazar
            weekday = current_date.weekday()
            weights.append(Constants.WEEKDAY_WEIGHTS.get(weekday, 1.0))  # Hafta içi/sonu ağırlıklarını kullan
            current_date += timedelta(days=1)
        
        # Ağırlıklı rastgele gün seçimi
        day_offset = random.choices(range(date_range + 1), weights=weights, k=1)[0]
        
        # Tarih döndürme
        return (Constants.FUTURE_DATE_START + timedelta(days=day_offset)).strftime(Constants.DATE_FORMAT)
    
    @staticmethod
    def generate_dates(
        frequency: str, 
        num_purchases: int, 
        customer_id: int, 
        seasons_list: List[str], 
        season_months: Dict[str, List[int]], 
        holidays: Dict[Tuple[int, int], Dict[str, Any]]
    ) -> List[str]:
        """Müşteri alışveriş frekansına ve sayısına göre tarih dizisi üretir."""
        dates = []
        
        # Satış verilerini içe aktar
        from sales_data import YEAR_WEIGHTS, MONTH_WEIGHTS
        
        # Yıl ağırlıkları - gerçek satış verilerine göre
        year_weights = YEAR_WEIGHTS
        years = list(year_weights.keys())
            
        # Mevsim listesi - her satırdaki mevsim değeri
        season_list = seasons_list * (num_purchases // len(seasons_list) + 1)
        season_list = season_list[:num_purchases]
            
        # Her alışveriş için tarih üretme
        for i in range(num_purchases):
            season = season_list[i]
                    
            # Ağırlıklı yıl seçimi
            year = random.choices(years, weights=[year_weights[y] for y in years], k=1)[0]
            
            # Ay ağırlıklarına göre ay seçimi
            # Önce mevsime uygun ayları belirle
            season_month_list = season_months[season]
            # Mevsim ayları için ağırlıkları al
            month_weights_for_season = {m: MONTH_WEIGHTS[m] for m in season_month_list}
            # Ağırlıkları normalize et
            total_weight = sum(month_weights_for_season.values())
            normalized_weights = {m: w/total_weight for m, w in month_weights_for_season.items()}
            # Ağırlıklı ay seçimi
            month = random.choices(
                list(month_weights_for_season.keys()), 
                weights=[normalized_weights[m] for m in month_weights_for_season.keys()], 
                k=1
            )[0]
            
            # Ay için son gün hesaplama
            last_day = DateTimeUtils.get_last_day_of_month(month, year)
            
            # Günler için ağırlıklar hesaplama (tatil günleri daha yüksek olasılıklı)
            day_weights = []
            for day in range(1, last_day + 1):
                try:
                    date = datetime(year, month, day)
                    weight = DateTimeUtils.get_holiday_weight(date, holidays)
                    day_weights.append(weight)
                except ValueError:
                    day_weights.append(0)  # Geçersiz tarih
            
            # Ağırlıklı olarak gün seçimi
            if sum(day_weights) > 0:  # Eğer en az bir geçerli gün varsa
                day = random.choices(range(1, last_day + 1), weights=day_weights, k=1)[0]
            else:
                day = random.randint(1, last_day)  # Tüm günler geçersizse rastgele seç
            
            # Tarihi oluşturma
            try:
                date = datetime(year, month, day)
            except ValueError:
                # Geçersiz tarih durumunda başka bir gün seç
                day = random.randint(1, last_day - 1)
                date = datetime(year, month, day)
            
            # Haftanın günü ağırlıklarına göre tarih seçimi
            # Önce ay içindeki tüm günleri oluştur
            all_days = []
            all_weights = []
            
            # Ayın ilk gününden başlayarak tüm günleri oluştur
            current_date = datetime(year, month, 1)
            while current_date.month == month:
                # Haftanın günü ağırlığını al
                weekday = current_date.weekday()
                weight = Constants.WEEKDAY_WEIGHTS.get(weekday, 1.0)
                
                # Tatil günü ağırlığını ekle
                holiday_weight = DateTimeUtils.get_holiday_weight(current_date, holidays)
                weight *= holiday_weight
                
                all_days.append(current_date)
                all_weights.append(weight)
                
                current_date += timedelta(days=1)
            
            # Ağırlıklı olarak gün seçimi
            if sum(all_weights) > 0:  # Eğer en az bir geçerli gün varsa
                date = random.choices(all_days, weights=all_weights, k=1)[0]
            else:
                # Tüm günler geçersizse rastgele seç
                date = random.choice(all_days)
            
            # 2022-2024 aralığında kalmasını sağlama
            if date.year < 2022:
                date = date.replace(year=2022)
            elif date.year > 2024:
                date = date.replace(year=2024)
                    
            dates.append(date)
            
        # Tarihleri kronolojik sıralama
        dates.sort()
            
        # String formatında döndürme
        return [d.strftime(Constants.DATE_FORMAT) for d in dates]
    
    @staticmethod
    def get_season_for_month(month: int, season_months: Dict[str, List[int]]) -> Optional[str]:
        """Ay numarasına göre ilgili mevsimi döndürür."""
        for season, months in season_months.items():
            if month in months:
                return season
        return None
    
    @staticmethod
    def calculate_holiday_date(year, month, day_of_week, week_number):
        """Belirli bir ayın belirli haftasındaki belirli gün için tarih hesaplar.
        
        Args:
            year: Yıl
            month: Ay (1-12)
            day_of_week: Haftanın günü (0=Pazartesi, 6=Pazar)
            week_number: Ayın kaçıncı haftası (1, 2, 3, 4, -1=son)
        
        Returns:
            Hesaplanan tarih
        """
        # Ayın ilk gününü al
        first_day = datetime(year, month, 1)
        
        # Ayın ilk gününden sonraki ilk istenilen haftanın günü
        first_day_of_week = first_day + timedelta(days=(day_of_week - first_day.weekday()) % 7)
        
        if week_number > 0:
            # Pozitif hafta numarası (ayın başından itibaren)
            result = first_day_of_week + timedelta(days=7 * (week_number - 1))
        else:
            # Negatif hafta numarası (ayın sonundan itibaren)
            # Ayın son gününü bul
            last_day = datetime(year, month, calendar.monthrange(year, month)[1])
            # Ayın son gününden önceki son istenilen haftanın günü
            last_day_of_week = last_day - timedelta(days=(last_day.weekday() - day_of_week) % 7)
            if last_day_of_week > last_day:
                last_day_of_week -= timedelta(days=7)
            
            # week_number=-1 için son haftadaki gün
            result = last_day_of_week + timedelta(days=7 * (week_number + 1))
        
        return result
