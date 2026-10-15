# Retail Sales Intelligence — Data Analytics with Python

**Project author: Satyajit Mahakud**

An interactive portfolio dashboard that explores retail sales performance with **Python, Pandas, Plotly, and Streamlit**.

> **Dataset note:** `retail_sales.csv` is synthetic sample data created for this demonstration. It does not represent real customers or a real company.

## What the project does

- Cleans and standardizes sales data with Pandas.
- Calculates net revenue and estimated profit after discounts.
- Shows headline KPIs: revenue, profit, order count, units sold, and profit margin.
- Visualizes monthly revenue/profit, category performance, region performance, and sales-channel contribution.
- Lets users filter by date, category, and region.
- Highlights the top-performing category, region, and product based on the active filters.
- Shows a product-performance table and lets users download filtered orders as a CSV.
- Supports uploading a replacement CSV that uses the same required column names.

## Project files

```text
retail_sales_analytics_project/
├── app.py              # Streamlit application and analytics
├── retail_sales.csv    # Synthetic sample dataset
├── requirements.txt    # Python dependencies for deployment
├── README.md           # Project documentation
└── .gitignore
```

## Run it on your computer

1. Install Python 3.10 or later.
2. Open a terminal inside this project folder.
3. Install the libraries:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the dashboard:

   ```bash
   streamlit run app.py
   ```

5. Streamlit will print a local address, usually `http://localhost:8501`, to open in your browser.

## Deploy it and get a public link

### Streamlit Community Cloud

1. Sign in to GitHub and create a new public repository, for example `retail-sales-analytics-python`.
2. Upload **all files in this folder** to the repository root (especially `app.py`, `retail_sales.csv`, and `requirements.txt`).
3. Open [Streamlit Community Cloud](https://share.streamlit.io/) and connect your GitHub account.
4. Choose **Create app**, select your repository, choose `app.py` as the main file, and deploy.
5. After a successful deployment, copy the public app URL. The final public URL is created by Streamlit; it cannot be known before deployment.

## Required columns for an uploaded CSV

The replacement CSV must contain these column names:

`Order_ID`, `Order_Date`, `Product`, `Category`, `Region`, `Quantity`, `Unit_Price`, `Discount_Percent`, `Payment_Method`, `Sales_Channel`, `Customer_Type`, `Profit_Margin_Percent`

`Order_Date` should be parseable as a date. The app calculates `Revenue` and `Profit` from quantity, unit price, discount, and profit margin.

## Skills demonstrated

**Python · Pandas · Data Cleaning · Exploratory Data Analysis · KPI Design · Data Visualization · Plotly · Streamlit · CSV Handling · Dashboard Development**

## Suggested GitHub repository description

Interactive retail sales analytics dashboard built with Python, Pandas, Plotly, and Streamlit. Includes data cleaning, KPIs, interactive filters, charts, and CSV export. Created by Satyajit Mahakud.
