"""
Ürün, Müşteri ve Mevsim Modelleri (final_generate2.py)
-----------------------------------------------------
Bu modül, ürün verileri, müşteri demografikleri, lokasyon bilgileri,
ve mevsimsel modelleri içerir.

İçerik:
- CustomerModel: Müşteri demografik bilgileri
- LocationModel: Konum ve iklim verileri
- SeasonModel: Mevsimsel modeller ve tarih ilişkileri
- ProductModel: Ürün kategorileri ve özellikleri
"""

import random
from datetime import datetime
from typing import Dict, List, Tuple, Any, Union, Optional, NamedTuple

# İlk modüldeki gerekli sınıfları içe aktarma
from final_generate1 import Constants, DataTypes, DateTimeUtils


class CustomerModel:
    """Müşteri demografik bilgileri işlemleri."""
    
    @staticmethod
    def get_age_group(age: int) -> str:
        """Yaş değerine göre yaş grubunu döndürür."""
        for (lower, upper), group in Constants.AGE_GROUPS.items():
            if lower <= age <= upper:
                return group
        return '18-26'  # Varsayılan grup
    
    @staticmethod
    def get_real_age_from_group(age_group: str) -> int:
        """Yaş grubundan rastgele gerçek yaş değeri üretir."""
        if age_group == '18-26':
            return random.randint(18, 26)
        elif age_group == '27-35':
            return random.randint(27, 35)
        elif age_group == '36-44':
            return random.randint(36, 44)
        elif age_group == '45-53':
            return random.randint(45, 53)
        elif age_group == '54-62':
            return random.randint(54, 62)
        elif age_group == '63-70':
            return random.randint(63, 70)
        else:
            return random.randint(30, 50)  # Varsayılan


class LocationModel:
    """Lokasyon ve iklim ile ilgili veri ve fonksiyonlar."""
    
    @staticmethod
    def create_location_data(location_data_initial: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Lokasyon verilerinden nüfusa dayalı ağırlık değerlerini hesaplar.
        
        Bu fonksiyon, eyaletlerin nüfus değerlerini kullanarak ağırlık değerleri hesaplar.
        Ağırlık hesaplaması doğrusal nüfus oranlarına dayanır, böylece yüksek nüfuslu 
        eyaletler veri setinde daha fazla temsil edilir.
        """
        # Doğrudan nüfus değerlerini alma
        populations = {state: data['population'] for state, data in location_data_initial.items()}
        
        # Utils sınıfını kullanarak nüfus ağırlıklarını normalize et
        from final_generate1 import Utils
        normalized_weights = Utils.normalize_weights(populations)
        
        # Weight değerlerini doğrudan nüfus oranlarına göre hesaplama
        location_data = {}
        for state, data in location_data_initial.items():
            # Normalize edilmiş ağırlığı kullan
            weight = normalized_weights[state]
            location_data[state] = {
                'climate': data['climate'], 
                'population': data['population'], 
                'weight': weight
            }
        
        return location_data
    
    @staticmethod
    def define_location_data() -> Dict[str, Dict[str, Any]]:
        """Lokasyon bilgilerini tanımlar."""
        # Lokasyon bilgileri - iklim karakteristikleri ve nüfus bilgileri
        location_data_initial = {
            # Soğuk iklimli bölgeler
            'Alaska': {'climate': 'cold', 'population': 700000},
            'Maine': {'climate': 'cold', 'population': 1400000},
            'Minnesota': {'climate': 'cold', 'population': 5700000},
            'Montana': {'climate': 'cold', 'population': 1100000},
            'North Dakota': {'climate': 'cold', 'population': 800000},
            'South Dakota': {'climate': 'cold', 'population': 900000},
            'Vermont': {'climate': 'cold', 'population': 650000},
            'Wyoming': {'climate': 'cold', 'population': 580000},
            'Wisconsin': {'climate': 'cold', 'population': 5900000},
            'Michigan': {'climate': 'cold', 'population': 10000000},
            'Idaho': {'climate': 'cold', 'population': 1900000},
                    
            # Ilıman iklimli bölgeler
            'Illinois': {'climate': 'temperate', 'population': 12500000},
            'New York': {'climate': 'temperate', 'population': 19500000},
            'Pennsylvania': {'climate': 'temperate', 'population': 13000000},
            'Ohio': {'climate': 'temperate', 'population': 11800000},
            'Colorado': {'climate': 'temperate', 'population': 5900000},
            'Washington': {'climate': 'temperate', 'population': 7900000},
            'Oregon': {'climate': 'temperate', 'population': 4300000},
            'Utah': {'climate': 'temperate', 'population': 3400000},
            'Iowa': {'climate': 'temperate', 'population': 3200000},
            'Kansas': {'climate': 'temperate', 'population': 2900000},
            'Missouri': {'climate': 'temperate', 'population': 6200000},
            'Nebraska': {'climate': 'temperate', 'population': 2000000},
            'Oklahoma': {'climate': 'temperate', 'population': 4000000},
            'Connecticut': {'climate': 'temperate', 'population': 3600000},
            'Massachusetts': {'climate': 'temperate', 'population': 7000000},
            'Rhode Island': {'climate': 'temperate', 'population': 1100000},
            'New Hampshire': {'climate': 'temperate', 'population': 1400000},
            'New Jersey': {'climate': 'temperate', 'population': 9300000},
            'Indiana': {'climate': 'temperate', 'population': 6800000},
            'Kentucky': {'climate': 'temperate', 'population': 4500000},
            'West Virginia': {'climate': 'temperate', 'population': 1800000},
            'Virginia': {'climate': 'temperate', 'population': 8700000},
            'Maryland': {'climate': 'temperate', 'population': 6200000},
            'Delaware': {'climate': 'temperate', 'population': 1000000},
            'Tennessee': {'climate': 'temperate', 'population': 7000000},
            'North Carolina': {'climate': 'temperate', 'population': 10700000},
            'Arkansas': {'climate': 'temperate', 'population': 3000000},
                    
            # Sıcak iklimli bölgeler
            'California': {'climate': 'varied', 'population': 39000000},
            'Arizona': {'climate': 'hot', 'population': 7400000},
            'New Mexico': {'climate': 'hot', 'population': 2100000},
            'Texas': {'climate': 'hot', 'population': 30000000},
            'Florida': {'climate': 'hot', 'population': 22000000},
            'Georgia': {'climate': 'hot', 'population': 11000000},
            'South Carolina': {'climate': 'hot', 'population': 5300000},
            'Alabama': {'climate': 'hot', 'population': 5100000},
            'Mississippi': {'climate': 'hot', 'population': 2900000},
            'Louisiana': {'climate': 'hot', 'population': 4600000},
            'Nevada': {'climate': 'hot', 'population': 3200000},
            'Hawaii': {'climate': 'tropical', 'population': 1400000}
        }
        
        return LocationModel.create_location_data(location_data_initial)
    
    @staticmethod
    def define_climate_product_multipliers() -> Dict[str, Dict[str, float]]:
        """İklim bazlı ürün ağırlık çarpanlarını tanımlar."""
        return {
            'cold': {
                'summer_items': 0.2,  # Soğuk iklimde yazlık ürünlerin alınma olasılığı düşük
                'winter_items': 5.0   # Soğuk iklimde kışlık ürünlerin alınma olasılığı yüksek
            },
            'temperate': {
                'summer_items': 1.0,  # Ilıman iklimde normal dağılım
                'winter_items': 1.0
            },
            'hot': {
                'summer_items': 5.0,  # Sıcak iklimde yazlık ürünlerin alınma olasılığı yüksek
                'winter_items': 0.2   # Sıcak iklimde kışlık ürünlerin alınma olasılığı düşük
            },
            'tropical': {
                'summer_items': 8.0,  # Tropikal iklimde yazlık ürünlerin alınma olasılığı çok yüksek
                'winter_items': 0.1   # Tropikal iklimde kışlık ürünlerin alınma olasılığı çok düşük
            },
            'varied': {
                'summer_items': 1.2,  # Kaliforniya gibi karışık iklimlerde hafif ağırlıklandırma
                'winter_items': 0.8
            }
        }
    
    @staticmethod
    def get_climate_multipliers(location: str, product_data: Dict[str, Any]) -> Dict[str, float]:
        """Lokasyon için iklim çarpanlarını döndürür."""
        if location and location in product_data['location_data']:
            climate = product_data['location_data'][location]['climate']
            return product_data['climate_product_multipliers'][climate]
        else:
            # Varsayılan olarak ılıman iklim
            return product_data['climate_product_multipliers']['temperate']


class SeasonModel:
    """Mevsim ve tarih ilişkileri için veri ve fonksiyonlar."""
    
    @staticmethod
    def define_season_months() -> Dict[str, List[int]]:
        """Mevsimlerin aylarını tanımlar."""
        return {
            'Winter': [12, 1, 2],    # Aralık, Ocak, Şubat
            'Spring': [3, 4, 5],     # Mart, Nisan, Mayıs
            'Summer': [6, 7, 8],     # Haziran, Temmuz, Ağustos
            'Fall': [9, 10, 11]      # Eylül, Ekim, Kasım
        }
    
    @staticmethod
    def define_holidays() -> Dict[Tuple[int, int], Dict[str, Any]]:
        """Tatil günlerini ve ağırlıklarını tanımlar (gerçekçi ağırlıklarla)."""
        return {
            # Yeni Yıl
            (1, 1): {'weight': 1.2, 'name': 'New Year\'s Day'},
            
            # Başkanlar Günü (Şubat'ın üçüncü pazartesi günü - tahmini)
            (2, 15): {'weight': 1.4, 'name': 'President\'s Day'},
            
            # Sevgililer Günü
            (2, 14): {'weight': 1.7, 'name': 'Valentine\'s Day'},
            
            # Paskalya (tahmini - değişken tarih)
            (4, 4): {'weight': 1.6, 'name': 'Easter'},
            
            # Anneler Günü (Mayıs'ın ikinci pazar günü - tahmini)
            (5, 9): {'weight': 2.3, 'name': 'Mother\'s Day'},
            
            # Anma Günü (Mayıs'ın son pazartesi günü - tahmini)
            (5, 31): {'weight': 1.6, 'name': 'Memorial Day'},
            
            # Babalar Günü (Haziran'ın üçüncü pazar günü - tahmini)
            (6, 20): {'weight': 1.6, 'name': 'Father\'s Day'},
            
            # Juneteenth (19 Haziran)
            (6, 19): {'weight': 1.3, 'name': 'Juneteenth'},
            
            # Bağımsızlık Günü (4 Temmuz)
            (7, 4): {'weight': 1.8, 'name': 'Independence Day'},
            
            # İşçi Bayramı (Eylül'ün ilk pazartesi günü - tahmini)
            (9, 6): {'weight': 1.7, 'name': 'Labor Day'},
            
            # Gaziler Günü (11 Kasım)
            (11, 11): {'weight': 1.4, 'name': 'Veterans Day'},
            
            # Cadılar Bayramı (31 Ekim)
            (10, 31): {'weight': 1.5, 'name': 'Halloween'},
            
            # Black Friday (Kasım'ın dördüncü perşembe günü sonrası - tahmini)
            (11, 26): {'weight': 3.0, 'name': 'Black Friday'},
            
            # Siber Pazartesi (Black Friday'den sonraki pazartesi - tahmini)
            (11, 29): {'weight': 2.7, 'name': 'Cyber Monday'},
            
            # Okula Dönüş Sezonu (Ağustos sonu - Eylül başı)
            (8, 15): {'weight': 2.0, 'name': 'Back to School'},
            (8, 22): {'weight': 2.0, 'name': 'Back to School'},
            (8, 29): {'weight': 2.0, 'name': 'Back to School'},
            (9, 5): {'weight': 2.0, 'name': 'Back to School'},
            
            # Noel öncesi alışveriş
            (12, 1): {'weight': 1.8, 'name': 'Pre-Christmas Shopping'},
            (12, 5): {'weight': 1.9, 'name': 'Pre-Christmas Shopping'},
            (12, 10): {'weight': 2.0, 'name': 'Pre-Christmas Shopping'},
            (12, 15): {'weight': 2.1, 'name': 'Pre-Christmas Shopping'},
            (12, 18): {'weight': 2.2, 'name': 'Pre-Christmas Shopping'},
            (12, 20): {'weight': 2.3, 'name': 'Pre-Christmas Shopping'},
            (12, 22): {'weight': 2.4, 'name': 'Pre-Christmas Shopping'},
            
            # Noel
            (12, 24): {'weight': 2.5, 'name': 'Christmas Eve'},
            (12, 25): {'weight': 2.5, 'name': 'Christmas'},
            
            # Noel sonrası indirimler
            (12, 26): {'weight': 2.2, 'name': 'After Christmas Sale'},
            (12, 27): {'weight': 2.0, 'name': 'After Christmas Sale'},
            (12, 28): {'weight': 1.8, 'name': 'After Christmas Sale'},
            (12, 29): {'weight': 1.7, 'name': 'After Christmas Sale'},
            (12, 30): {'weight': 1.6, 'name': 'After Christmas Sale'},
            
            # Yılbaşı
            (12, 31): {'weight': 1.5, 'name': 'New Year\'s Eve'},
        }
    
    @staticmethod
    def define_category_season_weights() -> Dict[str, Dict[str, float]]:
        """Mevsimlere göre kategori ağırlıklarını tanımlar."""
        return {
            'Winter': {
                'Clothing': 0.35,
                'Footwear': 0.20,
                'Outerwear': 0.35,
                'Accessories': 0.10
            },
            'Spring': {
                'Clothing': 0.40,
                'Footwear': 0.25,
                'Outerwear': 0.15,
                'Accessories': 0.20
            },
            'Summer': {
                'Clothing': 0.45,
                'Footwear': 0.30,
                'Outerwear': 0.05,
                'Accessories': 0.20
            },
            'Fall': {
                'Clothing': 0.35,
                'Footwear': 0.20,
                'Outerwear': 0.25,
                'Accessories': 0.20
            }
        }
    
    @staticmethod
    def define_season_color_preferences() -> Dict[str, Dict[str, float]]:
        """Mevsimlere göre renk tercihlerini tanımlar."""
        return {
            'Winter': {
                'Black': 0.18, 'White': 0.12, 'Gray': 0.12, 'Navy': 0.1, 'Charcoal': 0.08, 
                'Blue': 0.08, 'Red': 0.08, 'Maroon': 0.06, 'Brown': 0.06, 'Beige': 0.04,
                'Purple': 0.03, 'Green': 0.02, 'Silver': 0.01, 'Pink': 0.01, 'Turquoise': 0.005, 
                'Yellow': 0.005, 'Orange': 0.005, 'Olive': 0.005
            },
            'Spring': {
                'Pink': 0.15, 'Blue': 0.12, 'White': 0.1, 'Green': 0.1, 'Yellow': 0.08,
                'Purple': 0.08, 'Beige': 0.07, 'Gray': 0.06, 'Turquoise': 0.05, 'Red': 0.05,
                'Black': 0.04, 'Navy': 0.03, 'Orange': 0.03, 'Brown': 0.02, 'Olive': 0.01,
                'Charcoal': 0.005, 'Maroon': 0.005, 'Silver': 0.005
            },
            'Summer': {
                'White': 0.15, 'Blue': 0.15, 'Pink': 0.1, 'Yellow': 0.1, 'Green': 0.08,
                'Red': 0.07, 'Turquoise': 0.07, 'Beige': 0.06, 'Orange': 0.05, 'Purple': 0.05,
                'Black': 0.04, 'Navy': 0.03, 'Gray': 0.02, 'Brown': 0.01, 'Silver': 0.01,
                'Olive': 0.005, 'Charcoal': 0.005, 'Maroon': 0.005
            },
            'Fall': {
                'Brown': 0.15, 'Orange': 0.12, 'Red': 0.1, 'Maroon': 0.1, 'Olive': 0.09,
                'Navy': 0.08, 'Black': 0.08, 'Beige': 0.07, 'Gray': 0.06, 'Green': 0.05,
                'Yellow': 0.04, 'Blue': 0.03, 'Charcoal': 0.015, 'White': 0.01, 'Purple': 0.01,
                'Pink': 0.005, 'Turquoise': 0.005, 'Silver': 0.005
            }
        }
    
    @staticmethod
    def define_seasonal_items() -> Dict[str, List[str]]:
        """Mevsimsel ürün sınıflandırmalarını tanımlar."""
        return {
            'summer_items': [
                'Shorts', 'T-Shirt', 'Sandals', 'Flip Flops', 'Dress', 'Sunglasses',
                'Skirt', 'Tank Top', 'Swimming Trunks', 'Bikini'
            ],
            'winter_items': [
                'Coat', 'Parka', 'Sweater', 'Boots', 'Gloves', 'Scarf',
                'Hoodie', 'Cardigan', 'Winter Hat', 'Thermal Underwear', 'Earmuffs'
            ]
        }


class ProductModel:
    """Ürün verileri ve ilişkili fonksiyonlar."""
    
    @staticmethod
    def define_category_items() -> Dict[str, Dict[str, Dict[str, Any]]]:
        """Kategori-öğe ilişkilerini tanımlar."""
        # Bu fonksiyon veri yükü açısından çok büyük olduğu için
        # burada sadece bir kısım gösterilmiştir - gerçek implementasyonda
        # bu veriler ayrı veri dosyalarından yüklenebilir.
        return {
            'Clothing': {
                'Blouse': {
                    'Winter': 0.1, 'Spring': 0.3, 'Summer': 0.4, 'Fall': 0.2,
                    'Gender': {'Female': 0.95, 'Male': 0.05},
                    'Age': {'18-26': 0.3, '27-35': 0.3, '36-44': 0.2, '45-53': 0.1, '54-62': 0.06, '63-70': 0.04},
                    'Popularity': 0.6  # Orta-yüksek popülerlik
                },
                'Sweater': {
                    'Winter': 0.5, 'Spring': 0.2, 'Summer': 0.05, 'Fall': 0.25,
                    'Gender': {'Female': 0.6, 'Male': 0.4},
                    'Age': {'18-26': 0.25, '27-35': 0.25, '36-44': 0.20, '45-53': 0.15, '54-62': 0.10, '63-70': 0.05},
                    'Popularity': 0.7  # Yüksek popülerlik (mevsimsel)
                },
                # ... daha fazla giyim öğesi ...
            },
            'Footwear': {
                'Sandals': {
                    'Winter': 0.05, 'Spring': 0.2, 'Summer': 0.7, 'Fall': 0.05,
                    'Gender': {'Female': 0.7, 'Male': 0.3},
                    'Age': {'18-26': 0.3, '27-35': 0.3, '36-44': 0.2, '45-53': 0.1, '54-62': 0.06, '63-70': 0.04},
                    'Popularity': 0.6  # Orta-yüksek popülerlik (mevsimsel)
                },
                'Sneakers': {
                    'Winter': 0.2, 'Spring': 0.3, 'Summer': 0.3, 'Fall': 0.2,
                    'Gender': {'Female': 0.5, 'Male': 0.5},
                    'Age': {'18-26': 0.4, '27-35': 0.3, '36-44': 0.15, '45-53': 0.08, '54-62': 0.05, '63-70': 0.02},
                    'Popularity': 0.9  # Çok yüksek popülerlik
                },
                # ... daha fazla ayakkabı öğesi ...
            },
            'Outerwear': {
                'Coat': {
                    'Winter': 0.7, 'Spring': 0.1, 'Summer': 0.0, 'Fall': 0.2,
                    'Gender': {'Female': 0.55, 'Male': 0.45},
                    'Age': {'18-26': 0.15, '27-35': 0.25, '36-44': 0.25, '45-53': 0.15, '54-62': 0.12, '63-70': 0.08},
                    'Popularity': 0.65  # Orta-yüksek popülerlik (mevsimsel)
                },
                'Jacket': {
                    'Winter': 0.4, 'Spring': 0.2, 'Summer': 0.05, 'Fall': 0.35,
                    'Gender': {'Female': 0.45, 'Male': 0.55},
                    'Age': {'18-26': 0.25, '27-35': 0.3, '36-44': 0.20, '45-53': 0.12, '54-62': 0.08, '63-70': 0.05},
                    'Popularity': 0.8  # Yüksek popülerlik
                },
                # ... daha fazla dış giyim öğesi ...
            },
            'Accessories': {
                'Handbag': {
                    'Winter': 0.2, 'Spring': 0.3, 'Summer': 0.3, 'Fall': 0.2,
                    'Gender': {'Female': 0.95, 'Male': 0.05},
                    'Age': {'18-26': 0.25, '27-35': 0.3, '36-44': 0.25, '45-53': 0.10, '54-62': 0.07, '63-70': 0.03},
                    'Popularity': 0.7  # Yüksek popülerlik
                },
                'Belt': {
                    'Winter': 0.25, 'Spring': 0.25, 'Summer': 0.25, 'Fall': 0.25,
                    'Gender': {'Female': 0.45, 'Male': 0.55},
                    'Age': {'18-26': 0.2, '27-35': 0.3, '36-44': 0.25, '45-53': 0.12, '54-62': 0.08, '63-70': 0.05},
                    'Popularity': 0.55  # Orta popülerlik
                },
                # ... daha fazla aksesuar öğesi ...
            }
        }
    
    @staticmethod
    def define_category_weights() -> Dict[str, Dict[str, Any]]:
        """Kategori popülerlik ağırlıklarını tanımlar."""
        return {
            'Overall': {
                'Clothing': 0.4,
                'Footwear': 0.25,
                'Outerwear': 0.15,
                'Accessories': 0.2
            },
            'Gender': {
                'Female': {
                    'Clothing': 0.42,
                    'Footwear': 0.25,
                    'Outerwear': 0.13,
                    'Accessories': 0.2
                },
                'Male': {
                    'Clothing': 0.38,
                    'Footwear': 0.25,
                    'Outerwear': 0.17,
                    'Accessories': 0.2
                }
            },
            'Age': {
                '18-26': {
                    'Clothing': 0.45,
                    'Footwear': 0.25,
                    'Outerwear': 0.12,
                    'Accessories': 0.18
                },
                '27-35': {
                    'Clothing': 0.4,
                    'Footwear': 0.25,
                    'Outerwear': 0.15,
                    'Accessories': 0.2
                },
                '36-44': {
                    'Clothing': 0.38,
                    'Footwear': 0.25,
                    'Outerwear': 0.17,
                    'Accessories': 0.2
                },
                '45-53': {
                    'Clothing': 0.36,
                    'Footwear': 0.24,
                    'Outerwear': 0.18,
                    'Accessories': 0.22
                },
                '54-62': {
                    'Clothing': 0.34,
                    'Footwear': 0.23,
                    'Outerwear': 0.20,
                    'Accessories': 0.23
                },
                '63-70': {
                    'Clothing': 0.32,
                    'Footwear': 0.22,
                    'Outerwear': 0.22,
                    'Accessories': 0.24
                }
            }
        }
    
    @staticmethod
    def define_color_data() -> Tuple[List[str], Dict[str, float]]:
        """Renk verilerini ve ağırlıklarını tanımlar."""
        color_weights = {
            'Black': 0.15, 'Blue': 0.12, 'White': 0.1, 'Gray': 0.09, 'Red': 0.08,
            'Navy': 0.07, 'Pink': 0.07, 'Green': 0.06, 'Brown': 0.06, 'Beige': 0.05,
            'Purple': 0.03, 'Yellow': 0.03, 'Orange': 0.02, 'Charcoal': 0.02,  
            'Turquoise': 0.01, 'Maroon': 0.02, 'Olive': 0.01, 'Silver': 0.01
        }
        
        return list(color_weights.keys()), color_weights
    
    @staticmethod
    def define_shipping_data() -> Tuple[List[str], Dict[str, float]]:
        """Gönderim türlerini ve ağırlıklarını tanımlar."""
        shipping_weights = {
            'Standard': 0.45,
            'Free Shipping': 0.3,
            'Express': 0.15,
            '2-Day Shipping': 0.08,
            'Next Day Air': 0.02
        }
        
        return list(shipping_weights.keys()), shipping_weights
    
    @staticmethod
    def define_payment_data() -> Tuple[List[str], Dict[str, float]]:
        """Ödeme yöntemlerini ve ağırlıklarını tanımlar."""
        payment_weights = {
            'Credit Card': 0.35,
            'Debit Card': 0.25,
            'PayPal': 0.2,
            'Apple Pay': 0.07,
            'Google Pay': 0.05,
            'Bank Transfer': 0.04,
            'Cash': 0.03,
            'Venmo': 0.01
        }
        
        return list(payment_weights.keys()), payment_weights
    
    @staticmethod
    def define_item_stats() -> Dict[str, Dict[str, float]]:
        """Ürün istatistiklerini tanımlar."""
        # Yine, veri yükü açısından çok büyük olduğu için burada kısaltılmıştır
        return {
            # Clothing
            'Blouse': {'mean': 45.50, 'std_dev': 15.25, 'min': 25.00, 'max': 80.00},
            'Sweater': {'mean': 65.75, 'std_dev': 20.50, 'min': 30.00, 'max': 95.00},
            'Jeans': {'mean': 70.20, 'std_dev': 18.75, 'min': 35.00, 'max': 90.00},
            # ... daha fazla giyim öğesi ...
            
            # Footwear
            'Sandals': {'mean': 45.20, 'std_dev': 14.75, 'min': 22.00, 'max': 80.00},
            'Sneakers': {'mean': 78.50, 'std_dev': 22.30, 'min': 40.00, 'max': 95.00},
            'Boots': {'mean': 88.75, 'std_dev': 24.50, 'min': 45.00, 'max': 95.00},
            # ... daha fazla ayakkabı öğesi ...
            
            # Outerwear
            'Coat': {'mean': 95.30, 'std_dev': 25.75, 'min': 50.00, 'max': 95.00},
            'Jacket': {'mean': 85.75, 'std_dev': 24.50, 'min': 45.00, 'max': 95.00},
            # ... daha fazla dış giyim öğesi ...
            
            # Accessories
            'Handbag': {'mean': 75.80, 'std_dev': 22.50, 'min': 38.00, 'max': 95.00},
            'Belt': {'mean': 48.25, 'std_dev': 15.75, 'min': 24.00, 'max': 82.00},
            # ... daha fazla aksesuar öğesi ...
        }
    
    @staticmethod
    def define_product_data() -> Dict[str, Any]:
        """Ürün kategorileri ve ilgili verileri tanımlar."""
        # Sabitler tanımlama
        seasons = ['Winter', 'Spring', 'Summer', 'Fall']
        
        # Alt bileşenleri tanımlama
        location_data = LocationModel.define_location_data()
        climate_product_multipliers = LocationModel.define_climate_product_multipliers()
        seasonal_items = SeasonModel.define_seasonal_items()
        category_items = ProductModel.define_category_items()
        category_weights = ProductModel.define_category_weights()
        colors, color_weights = ProductModel.define_color_data()
        shipping_types, shipping_weights = ProductModel.define_shipping_data()
        payment_methods, payment_weights = ProductModel.define_payment_data()
        season_months = SeasonModel.define_season_months()
        holidays = SeasonModel.define_holidays()
        
        # Ana veri yapısını oluşturma
        return {
            'category_items': category_items,
            'category_weights': category_weights,
            'colors': colors,
            'color_weights': color_weights,
            'seasons': seasons,
            'shipping_types': shipping_types,
            'shipping_weights': shipping_weights,
            'payment_methods': payment_methods,
            'payment_weights': payment_weights,
            'season_months': season_months,
            'holidays': holidays,
            'location_data': location_data,
            'seasonal_items': seasonal_items,
            'climate_product_multipliers': climate_product_multipliers
        }
    
    @staticmethod
    def calculate_category_weights(
        season: str, 
        gender: Optional[str], 
        age: Optional[str], 
        category_season_weights: Dict[str, Dict[str, float]], 
        category_weights: Dict[str, Dict[str, Any]]
    ) -> Dict[str, float]:
        """Kategori seçimi için ağırlıkları hesaplar."""
        if gender in ['Male', 'Female'] and age:
            # Cinsiyet ve yaşa özgü kategori ağırlıkları
            weights = {}
            for k in category_season_weights[season]:
                base_weight = category_season_weights[season][k]
                gender_weight = category_weights['Gender'][gender][k]
                age_weight = category_weights['Age'][age][k]
                weights[k] = base_weight * gender_weight * age_weight
            
            # StatisticalUtils'i kullanarak ağırlıkları normalize et
            from final_generate3 import StatisticalUtils
            return StatisticalUtils.normalize_weights(weights)
        else:
            # Cinsiyet veya yaş bilgisi yoksa sadece mevsime göre seç
            return category_season_weights[season]
    
    @staticmethod
    def calculate_item_weights(
        items_in_category: List[str], 
        category: str, 
        season: str, 
        gender: Optional[str],
        age: Optional[str], 
        climate_multipliers: Dict[str, float],
        product_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """Ürün seçimi için ağırlıkları hesaplar."""
        item_weights = {}
        for item in items_in_category:
            # Temel mevsim ağırlığı
            base_weight = product_data['category_items'][category][item][season]
            
            # Cinsiyet ve yaş faktörlerini ekleme
            if gender in ['Male', 'Female']:
                gender_factor = product_data['category_items'][category][item]['Gender'].get(gender, 0.5)
                base_weight *= gender_factor
            
            if age:
                age_factor = product_data['category_items'][category][item]['Age'].get(age, 0.25)
                base_weight *= age_factor
            
            # İklim faktörünü ekleme - mevsimsel ürünlere özel ağırlıklandırma
            if item in product_data['seasonal_items']['summer_items']:
                base_weight *= climate_multipliers['summer_items']
            elif item in product_data['seasonal_items']['winter_items']:
                base_weight *= climate_multipliers['winter_items']
            
            # Ürün popülerlik faktörünü ekleme
            popularity_factor = product_data['category_items'][category][item].get('Popularity', 0.5)
            base_weight *= popularity_factor
            
            item_weights[item] = base_weight
        
        # StatisticalUtils'i kullanarak ağırlıkları normalize et
        from final_generate3 import StatisticalUtils
        return StatisticalUtils.normalize_weights(item_weights)
