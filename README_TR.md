# E-Ticaret Veri Üretme Sistemi

Bu belge, gerçekçi e-ticaret satın alma verileri oluşturmak için kullanılan veri üretme sistemini açıklamaktadır. Sistem, gerçekçi desenler ve korelasyonlar içeren kapsamlı bir veri seti oluşturmak için birlikte çalışan birden fazla Python modülünden oluşmaktadır.

## Sistem Genel Bakışı

Veri üretme sistemi 5 ana modülden oluşmaktadır:

1. **final_generate1.py**: Temel veri yapıları, sabitler ve yardımcı fonksiyonlar
2. **final_generate2.py**: Ürün, müşteri, konum ve mevsimsel modeller
3. **final_generate3.py**: İstatistiksel yardımcı fonksiyonlar ve satın alma verisi üretimi
4. **final_generate4.py**: Veri işleme ve ana program akışı
5. **sales_data.py**: Satış verileri ve ağırlık hesaplamaları

Sistem, temel müşteri bilgilerini `shopping_behavior.csv` dosyasından okur ve detaylı satın alma kayıtları oluşturarak bunları `final_data.csv` dosyasına kaydeder.

## Veri Üretim Süreci

### 1. Başlatma

Süreç, `final_generate4.py` içindeki `main()` fonksiyonu ile başlar:

```python
def main():
    # Tekrarlanabilirlik için rastgele sayı üretecini sabit değerle başlat
    random.seed(Constants.RANDOM_SEED)
    np.random.seed(Constants.RANDOM_SEED)
    
    # Giriş verisini yükle
    df = DataIO.load_data(Constants.INPUT_FILE)  # shopping_behavior.csv
    
    # Ürün verilerini tanımla
    product_data = ProductModel.define_product_data()
    
    # Satın alma verilerini oluştur
    output_data = DataIO.create_previous_purchases_data(df, product_data)
    
    # DataFrame'e dönüştür
    header = output_data[0]
    rows = output_data[1:]
    temp_df = pd.DataFrame(rows, columns=header)
    
    # Ayarlamaları uygula (tatil etkileri, COVID etkileri, vb.)
    adjusted_df = HolidayAdjuster.apply_adjustments(temp_df)
    
    # Çıkış dosyasına kaydet
    adjusted_df.to_csv(Constants.OUTPUT_FILE, index=False)  # final_data.csv
```

### 2. Veri Modellerinin Tanımlanması

Veri üretmeden önce, sistem çeşitli modelleri ve parametreleri tanımlar:

#### Ürün Modeli (`final_generate2.py`)
- Kategoriler (Giyim, Ayakkabı, Dış Giyim, Aksesuarlar)
- Her kategorideki ürünler
- Cinsiyet ve yaşa göre kategori ağırlıkları
- Renk verileri ve tercihleri
- Kargo ve ödeme yöntemleri

#### Konum Modeli (`final_generate2.py`)
- Nüfus ve iklim verileriyle ABD eyaletleri
- İklim bazlı ürün tercihleri

#### Mevsim Modeli (`final_generate2.py`)
- Mevsim tanımları ve ay eşleştirmeleri
- Tatil günleri ve ağırlıkları
- Mevsimsel renk tercihleri

### 3. Satın Alma Verisi Üretimi

Temel veri üretimi, `final_generate3.py` içindeki iki ana fonksiyon aracılığıyla gerçekleşir:

#### Geçmiş Satın Alma Üretimi
```python
def process_past_purchases(df, product_data):
    # Müşterilere nüfus dağılımına göre konum ata
    customer_locations = assign_customer_locations(df, product_data)
    
    # Her müşteri için
    for customer:
        # Müşteri tercihlerine göre rastgele mevsimler oluştur
        seasons = generate_random_seasons(product_data['seasons'], previous_purchases)
        
        # Frekans, mevsimler ve tatillere göre tarihler oluştur
        dates = generate_dates(frequency, previous_purchases, customer_id, seasons, 
                              season_months, holidays)
        
        # Her satın alma tarihi için
        for date, season:
            # Mevsim, cinsiyet, yaş, konuma göre satın alma detayları oluştur
            purchase_details = generate_purchase_details_for_season(
                season, product_data, gender, age_group, location)
            
            # Satın alma kaydı oluştur
            # Çıktı satırlarına ekle
```

#### Gelecek Satın Alma Üretimi
```python
def process_future_purchases(df, product_data):
    # Geçmiş satın almalara benzer, ancak 2024 yılına odaklanır
    # sales_data.py'dan hedef satış oranlarını kullanır
    # Müşterileri satış hedeflerine göre aylara dağıtır
    # Her müşteri için satın alma detayları oluşturur
```

### 4. Gerçekçi Ayarlamalar

Temel veri üretiminden sonra, `final_generate4.py` içinde çeşitli ayarlamalar uygulanır:

#### Tatil Etkileri
```python
def apply_holiday_effect(df, holidays):
    # Her satın alma için
    for purchase:
        # Black Friday veya Noel yakınındaysa, satın alma tutarını artır
        # Diğer tatillerin yakınındaysa, tatil ağırlığı ve yakınlığa bağlı olarak
        # olasılıksal olarak satın alma tutarını artır
```

#### COVID-19 Etkileri (2022 için)
```python
def apply_covid_effect(df):
    # 2022 satın almaları için:
    # - Kayıtların %15'i için satın alma tutarlarını azalt (mağaza alışverişi azalması)
    # - Kayıtların %25'i için kargo ve ödeme yöntemlerini değiştir (online alışveriş artışı)
    # - Online alışveriş için satın alma tutarlarını hafifçe artır (teşvikler)
```

#### Satış Yeniden Dağıtımı
```python
def redistribute_sales_by_target(df):
    # 2024 satış dağılımını hedef oranlara uyacak şekilde ayarla
    # Ocak ayındaki fazla satışları Kasım ve Aralık aylarına taşı
```

#### Ek Özellikler
```python
# Abonelik durumuna göre promosyon kodu kullanımı ekle
# Haftanın günü bilgisini ekle (gün numarası, adı, hafta sonu bayrağı)
```

### 5. İstatistiksel Yardımcı Fonksiyonlar

Sistem, gerçekçi veriler sağlamak için `final_generate3.py` içinde çeşitli istatistiksel yöntemler kullanır:

- Ağırlıklı rastgele seçim
- Fiyatlar için çarpık normal dağılımlar
- İnceleme puanları için J-eğrisi dağılımı
- Değişkenler arasında korelasyon (örn. yaş fiyatı etkiler)

## Üretilen Verinin Temel Özellikleri

Üretilen veri seti şu gerçekçi özellikleri içerir:

1. **Demografik Korelasyonlar**: Yaş ve cinsiyet, ürün tercihlerini ve fiyatları etkiler
2. **Mevsimsel Desenler**: Ürün ve renk tercihleri mevsime göre değişir
3. **Coğrafi Etkiler**: İklim, ürün seçimlerini etkiler
4. **Tatil Etkileri**: Tatil günleri yakınında satın alma tutarları artar
5. **Zamansal Desenler**: Haftanın günü dağılımı, aylık trendler
6. **Ekonomik Faktörler**: Abonelik durumu promosyon kodu kullanımını etkiler
7. **COVID-19 Etkisi**: 2022 alışveriş davranışlarında değişiklikler

## Giriş ve Çıkış Dosyaları

### Giriş: `shopping_behavior.csv`
Temel müşteri bilgilerini içerir:
- Müşteri Kimliği
- Yaş
- Cinsiyet
- Önceki Satın Alma sayısı
- Satın Alma Sıklığı
- Abonelik Durumu
- İndirim Uygulandı

### Çıkış: `final_data.csv`
Detaylı satın alma kayıtlarını içerir:
- Tüm giriş alanları (İndirim Uygulandı ve Sıklık hariç)
- Satın Alınan Ürün
- Kategori
- Satın Alma Tutarı (USD)
- Renk
- Boyut
- Mevsim
- İnceleme Puanı
- Kargo Tipi
- Ödeme Yöntemi
- Satın Alma Tarihi
- Haftanın Günü Numarası
- Haftanın Günü
- Hafta Sonu
- Promosyon Kodu Kullanıldı
- Churn (müşteri kaybı durumu)

## Sistemi Çalıştırma

Veri üretmek için, basitçe şunu çalıştırın:

```python
python final_generate4.py
```

Sistem şunları yapacaktır:
1. Müşteri verilerini `shopping_behavior.csv` dosyasından yükle
2. Satın alma kayıtları oluştur
3. Gerçekçi ayarlamaları uygula
4. Sonucu `final_data.csv` dosyasına kaydet

## Özelleştirme

Sistem şunları değiştirerek özelleştirilebilir:

- `final_generate1.py` içindeki sabitler (örn. RANDOM_SEED, tarih aralıkları)
- `final_generate2.py` içindeki ürün ve kategori tanımları
- `sales_data.py` içindeki satış hedefleri
- `final_generate3.py` içindeki istatistiksel parametreler
