"""
İstatistik ve Satın Alma Veri Üretimi (final_generate3.py)
---------------------------------------------------------
Bu modül, veri analizi için istatistiksel yardımcı fonksiyonları ve 
satın alma verileri üretimi için gerekli sınıfları içerir.

İçerik:
- StatisticalUtils: İstatistiksel analiz ve veri üretimi için yardımcı sınıf
- PurchaseGenerator: Satın alma verileri oluşturmak için ana sınıf
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime
from typing import Dict, List, Tuple, Any, Union, Optional

# Diğer modüllerden gerekli sınıfları içe aktarma
from final_generate1 import Constants, DataTypes, DateTimeUtils
from final_generate2 import CustomerModel, LocationModel, SeasonModel, ProductModel


# Utils sınıfını içe aktar
from final_generate1 import Utils

class StatisticalUtils:
    """İstatistiksel fonksiyonlar ve veri üretici araçlar."""
    
    @staticmethod
    def weighted_choice(choices: List[Any], weights: Union[List[float], Dict[Any, float]]) -> Any:
        """Ağırlıklı rastgele seçim yapar."""
        if isinstance(weights, dict):
            items = list(weights.keys())
            weights_list = [weights[item] for item in items]
            return random.choices(items, weights=weights_list, k=1)[0]
        else:
            return random.choices(choices, weights=weights, k=1)[0]
    
    @staticmethod
    def normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
        """Ağırlıkları normalleştirir (toplamları 1 olacak şekilde)."""
        # Utils sınıfındaki normalize_weights metodunu kullan
        return Utils.normalize_weights(weights)
    
    @staticmethod
    def generate_skewed_normal(
        mean: float, 
        std_dev: float, 
        min_value: float, 
        max_value: float, 
        alpha: float = 5,
        age: Optional[int] = None, 
        gender: Optional[str] = None
    ) -> float:
        """
        Sağa çarpık normal dağılım oluşturur.
        Yaş ve cinsiyet parametreleri ile korelasyon eklenir.
        """
        # Temel değeri hesaplama
        k = (alpha / std_dev) ** 2  # şekil parametresi
        theta = std_dev ** 2 / alpha  # ölçek parametresi
        
        # Gamma dağılımından değer üretme ve kaydırma
        value = np.random.gamma(k, theta) + (mean - alpha)
        
        # Yaş bazlı etki ekleme (yaşa göre artan fiyat eğilimi)
        if age is not None:
            # Yaş etkisi: 18-70 yaş aralığında
            age_factor = (age - 18) / 52  # Normalize edilmiş yaş faktörü (0-1 arası)
            value += age_factor * 10  # Yaşla birlikte maksimum 10$ artış
        
        # Cinsiyet bazlı etki ekleme (erkekler ortalama 10$ daha fazla)
        if gender == "Male":
            value += 10.0
        
        # Minimum ve maksimum sınırlarını uygulama
        value = max(min_value, min(value, max_value))
        
        # 2 ondalık basamağa yuvarlama
        return round(value, 2)
    
    @staticmethod
    def generate_review_rating(
        category: Optional[str] = None, 
        item: Optional[str] = None,
        purchase_amount: Optional[float] = None, 
        season: Optional[str] = None
    ) -> float:
        """
        Müşteri değerlendirme puanı üretir (gerçekçi J-curve dağılımı ile).
        
        Gerçek dünyada değerlendirmeler genellikle bimodal dağılım gösterir:
        - 5 yıldız (çok memnun müşteriler) 
        - 1 yıldız (hiç memnun olmamış müşteriler)
        - Orta değerler (2-4 yıldız) daha az sıklıkta görülür
        
        Bu fonksiyon ayrıca ürün kategorisi, öğe, fiyat ve sezona dayalı 
        faktörleri de hesaba katar.
        """
        # Temel değerlendirme ağırlıkları
        rating_weights = Constants.REVIEW_BASE_WEIGHTS.copy()
        
        if category and item and purchase_amount is not None:
            # Yüksek fiyatlı ürünler için daha polarize değerlendirmeler
            if purchase_amount > 80:
                rating_weights[5.0] *= 1.1  # Yüksek fiyatlı ürünlerde 5 yıldız oranı artar
                rating_weights[1.0] *= 1.2  # Ancak 1 yıldız oranı daha fazla artar (yüksek beklenti)
                # Orta değerleri azalt
                for rating in [2.0, 2.5, 3.0, 3.5, 4.0]:
                    rating_weights[rating] *= 0.9
            
            # Düşük fiyatlı ürünler genelde daha ılımlı değerlendirmelere sahiptir
            elif purchase_amount < 30:
                # Uç değerleri azalt
                rating_weights[5.0] *= 0.9
                rating_weights[1.0] *= 0.85
                # Orta değerleri artır
                for rating in [2.5, 3.0, 3.5, 4.0]:
                    rating_weights[rating] *= 1.15
                    
            # Kategori bazlı ayarlamalar
            if category == 'Accessories':
                # Aksesuarlar genellikle daha yüksek puanlar alır
                rating_weights[5.0] *= 1.05
                rating_weights[4.5] *= 1.05
                rating_weights[1.0] *= 0.9
            
            elif category == 'Footwear':
                # Ayakkabılar daha çok uç değerlendirmeler alır (ya uyar ya uymaz)
                rating_weights[5.0] *= 1.1
                rating_weights[1.0] *= 1.15
                # Orta değerleri azalt
                for rating in [2.5, 3.0, 3.5]:
                    rating_weights[rating] *= 0.85
            
            # Bazı özel ürünler için ayarlamalar
            if item in ['Suit', 'Dress', 'Heels', 'Boots']:
                # Bu ürünler daha yüksek beklentilerle satın alındığından
                # daha kritik değerlendirmelere tabi olabilir
                rating_weights[1.0] *= 1.2
                rating_weights[1.5] *= 1.1
                rating_weights[5.0] *= 0.95
            
            elif item in ['Socks', 'T-Shirt', 'Gloves']:
                # Basit ürünlerde daha az uç değerlendirme olur
                rating_weights[1.0] *= 0.85
                rating_weights[5.0] *= 0.95
                # Orta değerleri artır
                for rating in [3.0, 3.5, 4.0]:
                    rating_weights[rating] *= 1.1
        
        # Ağırlıkları normalize etme - kendi normalize_weights fonksiyonunu kullan
        normalized_weights = StatisticalUtils.normalize_weights(rating_weights)
        
        # Sonuç değerini döndürme
        return StatisticalUtils.weighted_choice(list(normalized_weights.keys()), normalized_weights)
    
    @staticmethod
    def generate_random_seasons(seasons: List[str], num_purchases: int) -> List[str]:
        """Alışveriş sayısına göre mevsim listesi oluşturur."""
        # Mevsim ağırlıkları (toplum için)
        season_weights = {
            'Winter': 0.25,  # Kış ve yaz hafif daha yüksek, tatil sezonu ve yaz aktiviteleri nedeniyle
            'Spring': 0.20,
            'Summer': 0.30,
            'Fall': 0.25
        }
            
        # Müşteri tercihi - bazı müşteriler belirli mevsimlerde daha aktif olabilir
        preference_factor = random.random()  # 0-1 arası rastgele değer
            
        # Müşteri tercihine göre ağırlıkları ayarlama
        if preference_factor < 0.25:  # Kış alışverişçisi
            season_weights = {
                'Winter': 0.4,
                'Spring': 0.2,
                'Summer': 0.15,
                'Fall': 0.25
            }
        elif preference_factor < 0.5:  # Yaz alışverişçisi
            season_weights = {
                'Winter': 0.15,
                'Spring': 0.25,
                'Summer': 0.45,
                'Fall': 0.15
            }
        elif preference_factor < 0.75:  # İlkbahar alışverişçisi
            season_weights = {
                'Winter': 0.15,
                'Spring': 0.45,
                'Summer': 0.25,
                'Fall': 0.15
            }
        # Diğer durumda orijinal ağırlıkları kullan
            
        # Her alışveriş için ağırlıklara göre mevsim seçimi - kendi weighted_choice fonksiyonunu kullan
        return [StatisticalUtils.weighted_choice(seasons, season_weights) for _ in range(num_purchases)]


class PurchaseGenerator:
    """Satın alma verisi oluşturma işlemleri."""
    
    @staticmethod
    def adjust_last_purchase_dates(all_purchases: List[List[Any]], customer_id_index: int, date_index: int) -> List[List[Any]]:
        """Müşterilerin son alışveriş tarihlerini istenen oranlara göre düzenler.
        
        Bu fonksiyon, müşterilerin belirli bir oranının son alışverişi 2022'de,
        belirli bir oranının son alışverişi 2023'de olacak şekilde tarihleri düzenler.
        
        Args:
            all_purchases: Tüm alışveriş verileri
            customer_id_index: Customer ID'nin bulunduğu sütun indeksi
            date_index: Satın alma tarihinin bulunduğu sütun indeksi
            
        Returns:
            Düzenlenmiş alışveriş verileri
        """
        # Önce müşteri bazında alışverişleri gruplayalım
        customer_purchases = {}
        
        # Tüm satırları dolaşarak her müşteri için alışveriş listesi oluştur
        for purchase in all_purchases:
            customer_id = purchase[customer_id_index]
            if customer_id not in customer_purchases:
                customer_purchases[customer_id] = []
            customer_purchases[customer_id].append(purchase)
        
        # Tüm müşterilerin listesini alalım ve karıştıralım
        customer_ids = list(customer_purchases.keys())
        random.shuffle(customer_ids)
        
        # Son alışverişi 2022'de olacak müşteri sayısı (%5)
        customers_2022_count = int(len(customer_ids) * 0.05)
        
        # Son alışverişi 2023'de olacak müşteri sayısı (%11)
        customers_2023_count = int(len(customer_ids) * 0.11)
        
        # Müşteri gruplarını belirle
        customers_2022 = customer_ids[:customers_2022_count]
        customers_2023 = customer_ids[customers_2022_count:customers_2022_count+customers_2023_count]
        
        # Her müşterinin son alışveriş tarihini düzenle
        for customer_id in customers_2022:
            # Müşterinin alışverişlerini tarihe göre sırala
            purchases = sorted(customer_purchases[customer_id], 
                              key=lambda x: datetime.strptime(x[date_index], Constants.DATE_FORMAT))
            
            # Son alışverişi değiştir - 2022 yılında son alışveriş yapanlar
            last_purchase = purchases[-1]
            purchase_date = datetime.strptime(last_purchase[date_index], Constants.DATE_FORMAT)
            
            # Eğer tarih 2022'den sonra ise, 2022'ye ayarla
            if purchase_date.year > 2022:
                # 2022'de rastgele bir tarih seç (Kasım veya Aralık ayı)
                month = random.choice([11, 12])
                day = random.randint(1, 28 if month == 2 else 30 if month in [4, 6, 9, 11] else 31)
                new_date = datetime(2022, month, day)
                
                # Yeni tarihi güncelle
                last_purchase[date_index] = new_date.strftime(Constants.DATE_FORMAT)
        
        for customer_id in customers_2023:
            # Müşterinin alışverişlerini tarihe göre sırala
            purchases = sorted(customer_purchases[customer_id], 
                              key=lambda x: datetime.strptime(x[date_index], Constants.DATE_FORMAT))
            
            # Son alışverişi değiştir - 2023 yılında son alışveriş yapanlar
            last_purchase = purchases[-1]
            purchase_date = datetime.strptime(last_purchase[date_index], Constants.DATE_FORMAT)
            
            # Eğer tarih 2023'ten önce veya sonra ise, 2023'e ayarla
            if purchase_date.year != 2023:
                # 2023'te rastgele bir tarih seç
                month = random.randint(1, 12)
                day = random.randint(1, 28 if month == 2 else 30 if month in [4, 6, 9, 11] else 31)
                new_date = datetime(2023, month, day)
                
                # Yeni tarihi güncelle
                last_purchase[date_index] = new_date.strftime(Constants.DATE_FORMAT)
        
        # Tüm alışverişleri tek bir liste haline getir
        adjusted_purchases = []
        for purchases in customer_purchases.values():
            adjusted_purchases.extend(purchases)
        
        return adjusted_purchases
    
    @staticmethod
    def generate_purchase_details_for_season(
        season: str, 
        product_data: Dict[str, Any], 
        gender: Optional[str] = None, 
        age: Optional[str] = None, 
        location: Optional[str] = None
    ) -> DataTypes.PurchaseDetails:
        """Belirli bir mevsim için uygun ürün detayları oluşturur."""
        # Kategori ağırlıkları
        category_season_weights = SeasonModel.define_category_season_weights()
        
        # Ürün istatistikleri
        item_stats = ProductModel.define_item_stats()
        
        # Mevsime uygun renk ağırlıkları
        season_color_preferences = SeasonModel.define_season_color_preferences()
        
        # Lokasyon bazlı iklim çarpanlarını belirleme
        climate_multipliers = LocationModel.get_climate_multipliers(location, product_data)
        
        # Kategori seçimi için ağırlıkları hesaplama ve kategori seçimi
        category_weights = ProductModel.calculate_category_weights(
            season, gender, age, category_season_weights, product_data['category_weights']
        )
        category = StatisticalUtils.weighted_choice(list(category_weights.keys()), category_weights)
        
        # Kategoriye özgü ürünler
        items_in_category = list(product_data['category_items'][category].keys())
        
        # Ürün seçimi için ağırlıkları hesaplama ve ürün seçimi
        item_weights = ProductModel.calculate_item_weights(
            items_in_category, category, season, gender, age, climate_multipliers, product_data
        )
        item = StatisticalUtils.weighted_choice(items_in_category, item_weights)
        
        # Seçilen ürüne göre istatistikleri alma
        item_stat = item_stats.get(
            item, {'mean': 59.764, 'std_dev': 23.685, 'min': 20.00, 'max': 100.00}
        )
        
        # Belirtilen fiyat dağılımına göre fiyat üretimi
        # 20-30$ aralığında: %15
        # 31-50$ aralığında: %40
        # 51-65$ aralığında: %25
        # 66-80$ aralığında: %12
        # 81-100$ aralığında: %8
        # Ağırlıkları biraz ayarlayarak istenen dağılıma daha yakın sonuçlar elde edelim
        price_ranges = [
            (20, 30, 0.18),  # Biraz artırıldı
            (31, 50, 0.42),  # Biraz artırıldı
            (51, 65, 0.25),  # Aynı kaldı
            (66, 80, 0.10),  # Biraz azaltıldı
            (81, 100, 0.05)  # Biraz azaltıldı
        ]
        
        # Rastgele bir fiyat aralığı seç
        selected_range = StatisticalUtils.weighted_choice(
            price_ranges, 
            [r[2] for r in price_ranges]
        )
        
        # Seçilen aralıkta rastgele bir fiyat üret
        min_price, max_price, _ = selected_range
        purchase_amount = round(random.uniform(min_price, max_price), 2)
        
        # Mevsimsel faktörler ekleme - kış aylarında daha yüksek fiyatlar
        if season == 'Winter':
            purchase_amount = min(purchase_amount * 1.08, 100.0)  # Kış ürünleri genelde daha pahalı
        elif season == 'Summer':
            purchase_amount = purchase_amount * 0.92  # Yaz ürünleri genelde daha ucuz olabilir (yaz indirimleri)
        
        # 2 ondalık basamağa yuvarlama
        purchase_amount = round(purchase_amount, 2)
        
        # Mevsime uygun renk seçimi
        color = StatisticalUtils.weighted_choice(
            list(season_color_preferences[season].keys()), 
            season_color_preferences[season]
        )
        
        # Cinsiyete göre beden dağılımı
        if gender in ['Male', 'Female']:
            # Cinsiyete göre beden ağırlıkları
            size_weights = Constants.SIZE_DISTRIBUTION.get(gender, {})
            if size_weights:
                size = StatisticalUtils.weighted_choice(Constants.SIZES, size_weights)
            else:
                size = random.choice(Constants.SIZES)
        else:
            # Cinsiyet belirtilmemişse rastgele seçim
            size = random.choice(Constants.SIZES)
        
        # İnceleme puanı, gönderim türü ve ödeme yöntemi
        review_rating = StatisticalUtils.generate_review_rating(category, item, purchase_amount, season)
        shipping_type = StatisticalUtils.weighted_choice(
            product_data['shipping_types'], product_data['shipping_weights']
        )
        payment_method = StatisticalUtils.weighted_choice(
            product_data['payment_methods'], product_data['payment_weights']
        )
        
        return DataTypes.PurchaseDetails(
            category=category,
            item=item,
            purchase_amount=purchase_amount,
            color=color,
            size=size,
            review_rating=review_rating,
            shipping_type=shipping_type,
            payment_method=payment_method
        )
    
    @staticmethod
    def assign_customer_locations(customers_df: pd.DataFrame, product_data: Dict[str, Any]) -> Dict[int, str]:
        """Her müşteriye kalıcı bir konum atar, nüfus dağılımına göre gerçekçi bir şekilde.
        
        Bu fonksiyon her müşteriye (CustomerID) tek bir eyalet atar.
        Eyaletlerin nüfus büyüklüğüne göre müşteri sayıları belirlenir.
        """
        # Customer ID'ler için sabit liste oluştur
        customer_ids = customers_df['Customer ID'].unique()
        total_customers = len(customer_ids)
        
        # Eyaletler ve nüfus değerleri
        locations = list(product_data['location_data'].keys())
        populations = np.array([product_data['location_data'][loc]['population'] for loc in locations])
        
        # Toplam nüfus
        total_population = sum(populations)
        
        # Eyalet başına nüfus yüzdesini hesapla
        population_percentages = populations / total_population
        
        # Her eyalete nüfus yüzdesiyle orantılı müşteri sayısı ata
        customers_per_location = np.round(total_customers * population_percentages).astype(int)
        
        # Atanan toplam müşteri sayısını kontrol et
        total_allocated = np.sum(customers_per_location)
        diff = total_customers - total_allocated
        
        if diff != 0:
            # Eğer yuvarlama hatası nedeniyle eksik/fazla müşteri varsa,
            # en büyük nüfuslu eyalete ekle/çıkar
            max_pop_idx = np.argmax(populations)
            customers_per_location[max_pop_idx] += diff
        
        # Müşterileri eyaletlere ata - her customer ID'yi bir lokasyona eşle
        customer_locations = {}
        customer_idx = 0
        
        for loc_idx, num_customers in enumerate(customers_per_location):
            location = locations[loc_idx]
            for _ in range(num_customers):
                if customer_idx < len(customer_ids):
                    customer_locations[customer_ids[customer_idx]] = location
                    customer_idx += 1
        
        # Son kontrol - tüm müşterilerin bir konumu olduğundan emin ol
        for cid in customer_ids:
            if cid not in customer_locations:
                # Eğer bir müşterinin konumu atanmamışsa, rastgele bir konum ata
                customer_locations[cid] = random.choice(locations)
        
        return customer_locations
    
    @staticmethod
    def process_past_purchases(
        df: pd.DataFrame, 
        product_data: Dict[str, Any]
    ) -> List[List[Any]]:
        """Müşterilerin geçmiş alışveriş kayıtlarını oluşturur."""
        # Performans optimizasyonu için ön hesaplamalar
        print("Müşteri lokasyonları atanıyor...")
        customer_locations = PurchaseGenerator.assign_customer_locations(df, product_data)
        
        # Vektörel işlemler için hazırlık
        customer_ids = df['Customer ID'].values
        frequencies = df['Frequency of Purchases'].values
        previous_purchases_counts = df['Previous Purchases'].values.astype(int)
        genders = df['Gender'].values
        age_vals = df['Age'].values.astype(int)
        
        # Yaş gruplarını önceden hesapla
        age_groups = [CustomerModel.get_age_group(age) for age in age_vals]
        
        # Çıktı için hazırlık
        output_rows = []
        total_rows = sum(previous_purchases_counts)
        
        print(f"Toplam {total_rows} satın alma kaydı oluşturuluyor...")
        
        # Batch işleme için müşteri indekslerini hazırla
        batch_size = 100  # Daha büyük batch'ler daha hızlı işlenir
        customer_indices = list(range(len(df)))
        
        # Batch'ler halinde işle
        for batch_start in range(0, len(df), batch_size):
            batch_end = min(batch_start + batch_size, len(df))
            batch_indices = customer_indices[batch_start:batch_end]
            
            for idx in batch_indices:
                row = df.iloc[idx]
                customer_id = customer_ids[idx]
                previous_purchases = previous_purchases_counts[idx]
                gender = genders[idx]
                age_group = age_groups[idx]
                
                # Müşteri için atanmış konumu al
                location = customer_locations[customer_id]
                
                # Müşteriye özgü sezon tercihi oluşturma
                row_seasons = StatisticalUtils.generate_random_seasons(product_data['seasons'], previous_purchases)
                
                # Müşteriye özgü tarihler oluşturma
                dates = DateTimeUtils.generate_dates(
                    frequencies[idx], previous_purchases, customer_id, row_seasons, 
                    product_data['season_months'], product_data['holidays']
                )
                
                # Temel satır verilerini bir kez kopyala
                base_row = row.drop(['Discount Applied', 'Frequency of Purchases']).copy()
                
                # Her geçmiş alışveriş için bir satır oluşturma
                for i, date in enumerate(dates):
                    # Temel satır verilerini kopyalama
                    purchase_row = base_row.copy()
                    season = row_seasons[i]
                    
                    # Mevsim, cinsiyet, yaş ve lokasyona uygun ürün detayları
                    purchase_details = PurchaseGenerator.generate_purchase_details_for_season(
                        season, product_data, gender, age_group, location
                    )
                    
                    # Satır verilerini güncelleme
                    purchase_row['Item Purchased'] = purchase_details.item
                    purchase_row['Category'] = purchase_details.category
                    purchase_row['Purchase Amount (USD)'] = purchase_details.purchase_amount
                    purchase_row['Color'] = purchase_details.color
                    purchase_row['Size'] = purchase_details.size
                    purchase_row['Season'] = season
                    purchase_row['Review Rating'] = purchase_details.review_rating
                    purchase_row['Shipping Type'] = purchase_details.shipping_type
                    purchase_row['Payment Method'] = purchase_details.payment_method
                    
                    # Satırı liste olarak çevirme ve tarihi ekleme
                    row_as_list = purchase_row.tolist()
                    row_as_list.append(date)
                    
                    # Çıktı listesine ekleme
                    output_rows.append(row_as_list)
        
        return output_rows
    
    @staticmethod
    def process_future_purchases(
        df: pd.DataFrame, 
        product_data: Dict[str, Any]
    ) -> List[List[Any]]:
        """Müşterilerin gelecek alışveriş kayıtlarını oluşturur."""
        print("Gelecek alışveriş tahminleri oluşturuluyor...")
        
        # Satış verilerini içe aktar
        from sales_data import MONTH_WEIGHTS, SALES_DATA
        
        # 2024 yılı için hedef satış rakamları
        target_sales_2024 = SALES_DATA[2024]
        
        # Ay bazında hedef satış oranlarını hesapla - StatisticalUtils'i kullanarak normalize et
        target_month_ratios = StatisticalUtils.normalize_weights(target_sales_2024)
        
        # Müşteri sayısı
        customer_count = len(df)
        print(f"Toplam {customer_count} müşteri için gelecek alışveriş tahminleri oluşturuluyor...")
        
        # Ay bazında müşteri sayılarını hesapla
        customers_per_month = {month: int(ratio * customer_count) for month, ratio in target_month_ratios.items()}
        
        # Toplam müşteri sayısını kontrol et ve gerekirse ayarla
        total_assigned = sum(customers_per_month.values())
        if total_assigned < customer_count:
            # Eksik müşterileri Kasım ve Aralık aylarına ekle (bu aylar genelde daha yoğun)
            remaining = customer_count - total_assigned
            customers_per_month[11] += remaining // 2
            customers_per_month[12] += remaining - (remaining // 2)
        elif total_assigned > customer_count:
            # Fazla müşterileri Ocak ayından çıkar (Ocak ayında zirve var)
            excess = total_assigned - customer_count
            customers_per_month[1] = max(1, customers_per_month[1] - excess)
        
        # Ay bazında müşteri listelerini oluştur
        month_customer_lists = {}
        customer_indices = list(range(customer_count))
        random.shuffle(customer_indices)  # Müşterileri karıştır
        
        # Müşterileri aylara dağıt
        start_idx = 0
        for month in range(1, 13):
            count = customers_per_month[month]
            end_idx = min(start_idx + count, customer_count)
            month_customer_lists[month] = customer_indices[start_idx:end_idx]
            start_idx = end_idx
        
        # Önce her müşteriye gerçekçi bir şekilde konum atama
        print("Müşteri lokasyonları atanıyor...")
        customer_locations = PurchaseGenerator.assign_customer_locations(df, product_data)
        
        # Vektörel işlemler için hazırlık
        customer_ids = df['Customer ID'].values
        genders = df['Gender'].values
        age_vals = df['Age'].values.astype(int)
        
        # Yaş gruplarını önceden hesapla
        age_groups = [CustomerModel.get_age_group(age) for age in age_vals]
        
        # Ay için son günleri önceden hesapla
        last_days = {month: DateTimeUtils.get_last_day_of_month(month, 2024) for month in range(1, 13)}
        
        # Ay-mevsim eşleştirmesini önceden hesapla
        month_to_season = {month: DateTimeUtils.get_season_for_month(month, product_data['season_months']) for month in range(1, 13)}
        
        # Çıktı için hazırlık
        output_rows = []
        
        # Batch işleme için ayları grupla
        batch_size = 3  # Her batch'te 3 ay işle
        for batch_start in range(1, 13, batch_size):
            batch_end = min(batch_start + batch_size, 13)
            batch_months = list(range(batch_start, batch_end))
            
            # Her ay için müşterilere satın alma verisi oluştur
            for month in batch_months:
                print(f"Ay {month} için satın alma verileri oluşturuluyor...")
                month_indices = month_customer_lists[month]
                
                # Ay için son gün
                last_day = last_days[month]
                
                # Ay için mevsim
                season = month_to_season[month]
                
                # Gün ağırlıklarını hesapla
                if month == 11:  # Kasım
                    # Black Friday etkisi (Kasım'ın son haftası)
                    day_weights = np.array([1 if d < 20 else 3 for d in range(1, last_day + 1)])
                    day_weights = day_weights / day_weights.sum()  # Normalize et
                elif month == 12:  # Aralık
                    # Yılbaşı alışverişleri etkisi (Aralık'ın son 10 günü)
                    day_weights = np.array([1 if d < 20 else 4 for d in range(1, last_day + 1)])
                    day_weights = day_weights / day_weights.sum()  # Normalize et
                else:
                    # Normal gün seçimi - eşit ağırlık
                    day_weights = None
                
                # Ay için tüm müşterileri işle
                for idx in month_indices:
                    if idx >= len(df):
                        continue  # Güvenlik kontrolü
                    
                    row = df.iloc[idx]
                    customer_id = customer_ids[idx]
                    gender = genders[idx]
                    age_group = age_groups[idx]
                    
                    # Temel satır verilerini kopyalama
                    purchase_row = row.drop(['Discount Applied', 'Frequency of Purchases']).copy()
                    
                    # Rastgele gün seçimi
                    if day_weights is not None:
                        day = np.random.choice(range(1, last_day + 1), p=day_weights)
                    else:
                        day = random.randint(1, last_day)
                    
                    # Tarihi oluşturma
                    try:
                        future_date_obj = datetime(2024, month, day)
                        future_date = future_date_obj.strftime(Constants.DATE_FORMAT)
                    except ValueError:
                        # Geçersiz tarih durumunda DateTimeUtils'i kullan
                        future_date = DateTimeUtils.generate_random_future_date()
                    
                    # Müşterinin atanmış konumunu al
                    location = customer_locations[customer_id]
                    
                    # Eğer mevsim bulunduysa ürün detaylarını oluşturma
                    if season:
                        # Ürün detaylarını oluşturma
                        purchase_details = PurchaseGenerator.generate_purchase_details_for_season(
                            season, product_data, gender, age_group, location
                        )
                        
                        # Satır verilerini güncelleme
                        purchase_row['Item Purchased'] = purchase_details.item
                        purchase_row['Category'] = purchase_details.category
                        purchase_row['Purchase Amount (USD)'] = purchase_details.purchase_amount
                        purchase_row['Color'] = purchase_details.color
                        purchase_row['Size'] = purchase_details.size
                        purchase_row['Season'] = season
                        purchase_row['Review Rating'] = purchase_details.review_rating
                        purchase_row['Shipping Type'] = purchase_details.shipping_type
                        purchase_row['Payment Method'] = purchase_details.payment_method
                    
                    # Satırı liste olarak çevirme ve tarihi ekleme
                    row_as_list = purchase_row.tolist()
                    row_as_list.append(future_date)
                    
                    # Çıktı listesine ekleme
                    output_rows.append(row_as_list)
        
        return output_rows
