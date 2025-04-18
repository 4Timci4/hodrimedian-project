# E-Commerce Data Generation System

This document explains the data generation system used to create realistic e-commerce purchase data. The system consists of multiple Python modules that work together to generate a comprehensive dataset with realistic patterns and correlations.

## System Overview

The data generation system is composed of 5 main modules:

1. **final_generate1.py**: Core data structures, constants, and utility functions
2. **final_generate2.py**: Product, customer, location, and seasonal models
3. **final_generate3.py**: Statistical utilities and purchase data generation
4. **final_generate4.py**: Data processing and main program flow
5. **sales_data.py**: Sales data and weight calculations

The system reads basic customer information from `shopping_behavior.csv` and generates detailed purchase records, which are saved to `previous_purchases_data.csv`.

## Data Generation Process

### 1. Initialization

The process begins in `final_generate4.py` with the `main()` function:

```python
def main():
    # Set random seed for reproducibility
    random.seed(Constants.RANDOM_SEED)
    np.random.seed(Constants.RANDOM_SEED)
    
    # Load input data
    df = DataIO.load_data(Constants.INPUT_FILE)  # shopping_behavior.csv
    
    # Define product data
    product_data = ProductModel.define_product_data()
    
    # Generate purchase data
    output_data = DataIO.create_previous_purchases_data(df, product_data)
    
    # Convert to DataFrame
    header = output_data[0]
    rows = output_data[1:]
    temp_df = pd.DataFrame(rows, columns=header)
    
    # Apply adjustments (holiday effects, COVID effects, etc.)
    adjusted_df = HolidayAdjuster.apply_adjustments(temp_df)
    
    # Save to output file
    adjusted_df.to_csv(Constants.OUTPUT_FILE, index=False)  # previous_purchases_data.csv
```

### 2. Data Models Definition

Before generating data, the system defines various models and parameters:

#### Product Model (`final_generate2.py`)
- Categories (Clothing, Footwear, Outerwear, Accessories)
- Items within each category
- Category weights by gender and age
- Color data and preferences
- Shipping and payment methods

#### Location Model (`final_generate2.py`)
- US states with population and climate data
- Climate-based product preferences

#### Season Model (`final_generate2.py`)
- Season definitions and month mappings
- Holiday dates and weights
- Seasonal color preferences

### 3. Purchase Data Generation

The core data generation happens in `final_generate3.py` through two main functions:

#### Past Purchases Generation
```python
def process_past_purchases(df, product_data):
    # Assign locations to customers based on population distribution
    customer_locations = assign_customer_locations(df, product_data)
    
    # For each customer
    for customer:
        # Generate random seasons based on customer preferences
        seasons = generate_random_seasons(product_data['seasons'], previous_purchases)
        
        # Generate dates based on frequency, seasons, and holidays
        dates = generate_dates(frequency, previous_purchases, customer_id, seasons, 
                              season_months, holidays)
        
        # For each purchase date
        for date, season:
            # Generate purchase details based on season, gender, age, location
            purchase_details = generate_purchase_details_for_season(
                season, product_data, gender, age_group, location)
            
            # Create purchase record
            # Add to output rows
```

#### Future Purchases Generation
```python
def process_future_purchases(df, product_data):
    # Similar to past purchases, but focused on 2024
    # Uses target sales ratios from sales_data.py
    # Distributes customers across months based on sales targets
    # Generates purchase details for each customer
```

### 4. Realistic Adjustments

After basic data generation, several adjustments are applied in `final_generate4.py`:

#### Holiday Effects
```python
def apply_holiday_effect(df, holidays):
    # For each purchase
    for purchase:
        # If near Black Friday or Christmas, increase purchase amount
        # If near other holidays, probabilistically increase purchase amount
        # based on holiday weight and proximity
```

#### COVID-19 Effects (for 2022)
```python
def apply_covid_effect(df):
    # For 2022 purchases:
    # - Reduce purchase amounts for 15% of records (store shopping decrease)
    # - Change shipping and payment methods for 25% of records (online shopping increase)
    # - Slightly increase purchase amounts for online shopping (incentives)
```

#### Sales Redistribution
```python
def redistribute_sales_by_target(df):
    # Adjust 2024 sales distribution to match target ratios
    # Move excess January sales to November and December
```

#### Additional Features
```python
# Add promo code usage based on subscription status
# Add weekday information (day number, name, weekend flag)
```

### 5. Statistical Utilities

The system uses various statistical methods in `final_generate3.py` to ensure realistic data:

- Weighted random selection
- Skewed normal distributions for prices
- J-curve distribution for review ratings
- Correlation between variables (e.g., age affects price)

## Key Features of Generated Data

The generated dataset includes realistic:

1. **Demographic Correlations**: Age and gender affect product preferences and prices
2. **Seasonal Patterns**: Product and color preferences vary by season
3. **Geographic Effects**: Climate affects product choices
4. **Holiday Effects**: Purchase amounts increase near holidays
5. **Temporal Patterns**: Weekday distribution, monthly trends
6. **Economic Factors**: Subscription status affects promo code usage
7. **COVID-19 Impact**: Changes in 2022 shopping behavior

## Input and Output Files

### Input: `shopping_behavior.csv`
Contains basic customer information:
- Customer ID
- Age
- Gender
- Previous Purchases count
- Frequency of Purchases
- Subscription Status
- Discount Applied

### Output: `previous_purchases_data.csv`
Contains detailed purchase records:
- All input fields (except Discount Applied and Frequency)
- Item Purchased
- Category
- Purchase Amount (USD)
- Color
- Size
- Season
- Review Rating
- Shipping Type
- Payment Method
- Purchase Date
- WeekdayNum
- Weekday
- Weekend
- Promo Code Used
- Churn (customer retention status)

## Running the System

To generate data, simply run:

```python
python final_generate4.py
```

The system will:
1. Load customer data from `shopping_behavior.csv`
2. Generate purchase records
3. Apply realistic adjustments
4. Save the result to `previous_purchases_data.csv`

## Customization

The system can be customized by modifying:

- Constants in `final_generate1.py` (e.g., RANDOM_SEED, date ranges)
- Product and category definitions in `final_generate2.py`
- Sales targets in `sales_data.py`
- Statistical parameters in `final_generate3.py`
