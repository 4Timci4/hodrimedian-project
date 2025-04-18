"""
Satış Verileri ve Ağırlık Hesaplamaları
---------------------------------------
Bu modül, kullanıcının verdiği satış rakamlarını içerir ve
bu verilere göre ağırlık hesaplamaları yapar.
"""

# Kullanıcının verdiği satış rakamları
SALES_DATA = {
    2022: {
        1: 2143,  # Ocak
        2: 1987,  # Şubat
        3: 2315,  # Mart
        4: 2427,  # Nisan
        5: 2568,  # Mayıs
        6: 2153,  # Haziran
        7: 2061,  # Temmuz
        8: 2304,  # Ağustos
        9: 2412,  # Eylül
        10: 2638,  # Ekim
        11: 3745,  # Kasım
        12: 3862,  # Aralık
    },
    2023: {
        1: 2573,  # Ocak
        2: 2418,  # Şubat
        3: 2739,  # Mart
        4: 2863,  # Nisan
        5: 2992,  # Mayıs
        6: 2637,  # Haziran
        7: 2502,  # Temmuz
        8: 2748,  # Ağustos
        9: 2821,  # Eylül
        10: 3097,  # Ekim
        11: 4319,  # Kasım
        12: 4474,  # Aralık
    },
    2024: {
        1: 2889,  # Ocak
        2: 2742,  # Şubat
        3: 3173,  # Mart
        4: 3254,  # Nisan
        5: 3386,  # Mayıs
        6: 2964,  # Haziran
        7: 2913,  # Temmuz
        8: 3157,  # Ağustos
        9: 3209,  # Eylül
        10: 3433,  # Ekim
        11: 5048,  # Kasım
        12: 5304,  # Aralık
    }
}

def calculate_year_weights():
    """Yıl ağırlıklarını hesaplar."""
    # Yıl bazında toplam satış adetleri
    year_totals = {year: sum(months.values()) for year, months in SALES_DATA.items()}
    total_sales = sum(year_totals.values())
    
    # Yıl ağırlıkları
    year_weights = {year: total / total_sales for year, total in year_totals.items()}
    
    return year_weights

def calculate_month_weights():
    """Ay ağırlıklarını hesaplar."""
    # Ay bazında ortalama satış adetleri
    month_totals = {}
    for month in range(1, 13):
        month_sum = sum(SALES_DATA[year][month] for year in SALES_DATA.keys())
        month_totals[month] = month_sum / len(SALES_DATA)
    
    total_monthly_avg = sum(month_totals.values())
    
    # Ay ağırlıkları
    month_weights = {month: total / total_monthly_avg for month, total in month_totals.items()}
    
    return month_weights

def calculate_special_day_weights():
    """Özel günler için ağırlıkları hesaplar."""
    # Ay ağırlıkları
    month_weights = calculate_month_weights()
    
    # Kasım ve Aralık ayları için ağırlıklar
    november_weight = month_weights[11]  # Kasım
    december_weight = month_weights[12]  # Aralık
    
    # Diğer ayların ortalaması
    other_months_avg = sum(month_weights[m] for m in range(1, 11)) / 10
    
    # Black Friday ve yılbaşı alışverişleri için ağırlık faktörleri
    black_friday_factor = november_weight / other_months_avg
    christmas_factor = december_weight / other_months_avg
    
    # Diğer özel günler için ağırlık faktörleri
    valentines_factor = month_weights[2] / other_months_avg  # Şubat (Sevgililer Günü)
    mothers_day_factor = month_weights[5] / other_months_avg  # Mayıs (Anneler Günü)
    back_to_school_factor = (month_weights[8] + month_weights[9]) / (2 * other_months_avg)  # Ağustos-Eylül (Okul dönemi)
    
    return {
        'black_friday': black_friday_factor,
        'christmas': christmas_factor,
        'valentines': valentines_factor,
        'mothers_day': mothers_day_factor,
        'back_to_school': back_to_school_factor
    }

# Ağırlıkları hesapla
YEAR_WEIGHTS = calculate_year_weights()
MONTH_WEIGHTS = calculate_month_weights()
SPECIAL_DAY_WEIGHTS = calculate_special_day_weights()

# Sonuçları yazdır
if __name__ == "__main__":
    print("Yıl Ağırlıkları:")
    for year, weight in YEAR_WEIGHTS.items():
        print(f"{year}: {weight:.3f}")
    
    print("\nAy Ağırlıkları:")
    for month, weight in MONTH_WEIGHTS.items():
        print(f"{month}: {weight:.3f}")
    
    print("\nÖzel Gün Ağırlıkları:")
    for day, weight in SPECIAL_DAY_WEIGHTS.items():
        print(f"{day}: {weight:.3f}")
