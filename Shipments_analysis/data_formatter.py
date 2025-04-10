import json
from tabulate import tabulate
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import os

def format_company_data(data):
    """
    Format and display ImportYeti company data in a readable way
    """
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            print("Error: Invalid JSON data")
            return
    
    if "data" in data:
        data = data["data"]
    
    # Company Basic Information
    print("=" * 80)
    print(f"COMPANY OVERVIEW: {data.get('title', 'Unknown')}")
    print("=" * 80)
    print(f"Address: {data.get('address', 'N/A')}")
    
    if data.get('also_known_names'):
        print(f"Also known as: {', '.join(data['also_known_names'])}")
    
    print(f"Website: {data.get('website', 'N/A')}")
    print(f"Phone: {data.get('phone_number', 'N/A')}")
    print(f"Total Sea Shipments: {data.get('total_shipments', 'N/A')}")
    print("-" * 80)
    
    # Import Metrics
    if data.get('containers'):
        print("\nCONTAINER METRICS:")
        container_data = []
        for container in data['containers']:
            container_data.append([
                container.get('type', 'N/A'),
                container.get('length', 'N/A'),
                container.get('group', 'N/A'),
                container.get('shipments', 'N/A'),
                f"{container.get('weight', 0):,} kg" if container.get('weight') else 'N/A',
                container.get('count', 'N/A')
            ])
        
        print(tabulate(container_data, 
                       headers=['Type', 'Length', 'Group', 'Shipments', 'Weight', 'Count'],
                       tablefmt='grid'))
    
    # Suppliers Table
    if data.get('suppliers_table'):
        print("\nTOP SUPPLIERS:")
        suppliers_data = []
        for supplier in data['suppliers_table'][:10]:  # Show top 10
            suppliers_data.append([
                supplier.get('supplier_name', 'N/A'),
                supplier.get('supplier_address_country', 'N/A'),
                supplier.get('total_shipments_company', 'N/A'),
                supplier.get('most_recent_shipment', 'N/A')
            ])
        
        print(tabulate(suppliers_data, 
                       headers=['Supplier Name', 'Country', 'Total Shipments', 'Most Recent'],
                       tablefmt='grid'))
    
    # HS Codes
    if data.get('hs_codes'):
        print("\nPRODUCT BREAKDOWN (HS CODES):")
        hs_data = []
        for hs in data['hs_codes'][:10]:  # Show top 10
            hs_data.append([
                hs.get('hs_code', 'N/A'),
                hs.get('description', 'N/A'),
                hs.get('shipments', 'N/A'),
                hs.get('shipments_12m', 'N/A')
            ])
        
        print(tabulate(hs_data, 
                       headers=['HS Code', 'Description', 'Total Shipments', 'Last 12 Months'],
                       tablefmt='grid'))
    
    # Recent Bills of Lading
    if data.get('recent_bols'):
        print("\nRECENT SHIPMENTS:")
        bol_data = []
        for bol in data['recent_bols'][:5]:  # Show top 5
            bol_data.append([
                bol.get('date_formatted', 'N/A'),
                bol.get('Bill_of_Lading', 'N/A'),
                bol.get('Shipper_Name', 'N/A'),
                bol.get('Country', 'N/A'),
                f"{bol.get('Weight_in_KG', 0):,} kg" if bol.get('Weight_in_KG') else 'N/A',
                bol.get('Product_Description', 'N/A')[:40] + '...' if bol.get('Product_Description') and len(bol.get('Product_Description')) > 40 else bol.get('Product_Description', 'N/A')
            ])
        
        print(tabulate(bol_data, 
                       headers=['Date', 'B/L Number', 'Shipper', 'Country', 'Weight', 'Product Description'],
                       tablefmt='grid'))
    
    # Time Series Data - Visualization if available
    if data.get('time_series') and len(data['time_series']) > 1:
        print("\nSHIPMENTS OVER TIME:")
        plot_time_series(data['time_series'])

def plot_time_series(time_series):
    """Plot time series data as a bar chart"""
    dates = []
    shipments = []
    
    # Convert time series to lists for plotting
    for date_str, values in time_series.items():
        try:
            # Parse date in MM/DD/YYYY format
            date_obj = datetime.strptime(date_str, '%d/%m/%Y')
            formatted_date = date_obj.strftime('%b %Y')  # Convert to abbreviated month and year
            dates.append(formatted_date)
            shipments.append(values.get('shipments', 0))
        except ValueError:
            continue
    
    # Create DataFrame for easier handling
    if dates and shipments:
        df = pd.DataFrame({'Date': dates, 'Shipments': shipments})
        
        # If we have more than 12 data points, sample to show about 12 points
        if len(df) > 12:
            step = len(df) // 12
            df = df.iloc[::step, :]
        
        # Create plot
        plt.figure(figsize=(12, 6))
        plt.bar(df['Date'], df['Shipments'], color='skyblue')
        plt.title('Shipments Over Time')
        plt.xlabel('Date')
        plt.ylabel('Number of Shipments')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save the plot to a file
        output_dir = os.path.dirname(os.path.abspath(__file__))
        plt.savefig(os.path.join(output_dir, 'shipments_over_time.png'))
        print(f"Shipments chart saved to 'shipments_over_time.png'")
    else:
        print("Insufficient time series data for plotting")

if __name__ == "__main__":
    # Example usage - can be replaced with actual API call
    with open('sample_data.json', 'r') as f:
        sample_data = json.load(f)
    
    format_company_data(sample_data)