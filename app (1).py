from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# -----------------------------------------------------------------------------
# Retail Sales Analytics Dashboard
# Created by Satyajit Mahakud
# Dataset: synthetic sample data supplied with this project for demonstration.
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="Retail Sales Intelligence | Satyajit Mahakud",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = Path(__file__).parent / "retail_sales.csv"

st.markdown(
    """
    <style>
      /* Keep the dashboard readable regardless of the viewer's Streamlit theme. */
      .stApp, [data-testid="stAppViewContainer"] {
        background: #f6f8fc !important; color: #1f2937 !important;
      }
      [data-testid="stAppViewContainer"] .main .block-container {
        color: #1f2937 !important;
      }
      [data-testid="stSidebar"] { background: #101a2d !important; }
      [data-testid="stSidebar"] * { color: #f3f6fc !important; }
      /* The uploader drop-zone is light, so use dark text inside it. */
      [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
        background: #f8fafc !important; border: 1px dashed #9aa9bd !important;
      }
      [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] * {
        color: #1f2937 !important;
      }
      [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {
        background: #e7eef7 !important; color: #1f2937 !important;
        border: 1px solid #aab8ca !important;
      }
      .hero {
        padding: 1.35rem 1.6rem; border-radius: 18px;
        background: linear-gradient(120deg, #10213d 0%, #174a72 60%, #287f92 100%);
        color: #ffffff; margin-bottom: 1rem;
      }
      .hero h1 { margin: 0 0 .35rem 0; font-size: 2.15rem; }
      .hero p { margin: 0; color: #e1edf7; font-size: 1rem; }
      .author-tag {
        display: inline-block; margin-top: .8rem; padding: .28rem .7rem;
        border: 1px solid rgba(255,255,255,.4); border-radius: 30px;
        font-size: .82rem; color: #ffffff;
      }
      div[data-testid="stMetric"] {
        background: #ffffff !important; border: 1px solid #e4eaf3;
        padding: 14px 16px; border-radius: 14px;
        box-shadow: 0 3px 14px rgba(25,45,75,.04);
      }
      div[data-testid="stMetric"] * { color: #172b4d !important; }
      div[data-testid="stMetricLabel"] { color: #52627a !important; }
      [data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p,
      [data-testid="stMarkdownContainer"] li, [data-testid="stCaptionContainer"],
      [data-testid="stText"] { color: #263445; }
      .section-caption { color: #607087; font-size: .93rem; }
      .footer {
        text-align: center; color: #718096; font-size: .85rem;
        padding: 1.5rem 0 .7rem 0; border-top: 1px solid #e3e9f2;
        margin-top: 2rem;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


def clean_data(frame: pd.DataFrame) -> pd.DataFrame:
    """Standardize columns and clean the included retail sales dataset."""
    df = frame.copy()
    df.columns = [str(c).strip().replace(" ", "_") for c in df.columns]

    required = {
        "Order_ID", "Order_Date", "Product", "Category", "Region",
        "Quantity", "Unit_Price", "Discount_Percent", "Payment_Method",
        "Sales_Channel", "Customer_Type", "Profit_Margin_Percent"
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            "The uploaded CSV is missing these required columns: "
            + ", ".join(sorted(missing))
        )

    df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    df["Unit_Price"] = pd.to_numeric(df["Unit_Price"], errors="coerce")
    df["Discount_Percent"] = pd.to_numeric(df["Discount_Percent"], errors="coerce").fillna(0)
    df["Profit_Margin_Percent"] = pd.to_numeric(
        df["Profit_Margin_Percent"], errors="coerce"
    ).fillna(0)

    # Remove unusable rows and duplicate order IDs, then standardize missing labels.
    df = df.dropna(subset=["Order_ID", "Order_Date", "Quantity", "Unit_Price"])
    df = df.drop_duplicates(subset=["Order_ID"])
    for col in ["Product", "Category", "Region", "Payment_Method", "Sales_Channel", "Customer_Type"]:
        df[col] = df[col].fillna("Unknown").astype(str).str.strip()
        df.loc[df[col].eq(""), col] = "Unknown"

    df = df[(df["Quantity"] > 0) & (df["Unit_Price"] >= 0)]
    df["Discount_Percent"] = df["Discount_Percent"].clip(0, 100)
    df["Gross_Sales"] = df["Quantity"] * df["Unit_Price"]
    df["Revenue"] = df["Gross_Sales"] * (1 - df["Discount_Percent"] / 100)
    df["Profit"] = df["Revenue"] * df["Profit_Margin_Percent"] / 100
    df["Month"] = df["Order_Date"].dt.to_period("M").dt.to_timestamp()
    df["Month_Label"] = df["Month"].dt.strftime("%b %Y")
    return df.sort_values("Order_Date")


def money(value: float) -> str:
    return f"₹{value:,.0f}"


def empty_state(message: str) -> None:
    st.info(message)


st.markdown(
    """
    <div class="hero">
      <h1>📊 Retail Sales Intelligence</h1>
      <p>Explore revenue, profit, product performance, and customer buying patterns.</p>
      <span class="author-tag">Built by Satyajit Mahakud · Data Analytics with Python</span>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## Dashboard controls")
    st.caption("Filter the data to explore different parts of the business.")
    uploaded = st.file_uploader("Upload a replacement CSV", type=["csv"])
    st.markdown("---")
    st.markdown("### About this project")
    st.write("A portfolio project using Python, Pandas, Plotly, and Streamlit.")
    st.caption("The included dataset is synthetic sample data, not real customer or company data.")

try:
    source_df = pd.read_csv(uploaded) if uploaded is not None else pd.read_csv(DATA_FILE)
    df = clean_data(source_df)
except Exception as exc:
    st.error(f"Could not load the data: {exc}")
    st.markdown("See the README for the required CSV columns and setup instructions.")
    st.stop()

if df.empty:
    empty_state("There are no usable rows after cleaning. Please check the input CSV.")
    st.stop()

min_date = df["Order_Date"].min().date()
max_date = df["Order_Date"].max().date()

with st.sidebar:
    date_range = st.date_input(
        "Order date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    categories = sorted(df["Category"].unique().tolist())
    regions = sorted(df["Region"].unique().tolist())
    selected_categories = st.multiselect("Product category", categories, default=categories)
    selected_regions = st.multiselect("Region", regions, default=regions)

filtered = df.copy()
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered = filtered[
        filtered["Order_Date"].dt.date.between(start_date, end_date)
    ]
if selected_categories:
    filtered = filtered[filtered["Category"].isin(selected_categories)]
else:
    filtered = filtered.iloc[0:0]
if selected_regions:
    filtered = filtered[filtered["Region"].isin(selected_regions)]
else:
    filtered = filtered.iloc[0:0]

st.caption(
    f"Showing {len(filtered):,} of {len(df):,} unique orders · "
    f"{df['Order_Date'].min():%d %b %Y} to {df['Order_Date'].max():%d %b %Y}"
)

if filtered.empty:
    empty_state("No orders match these filters. Select a wider date range or more categories/regions.")
    st.stop()

revenue = float(filtered["Revenue"].sum())
profit = float(filtered["Profit"].sum())
orders = int(filtered["Order_ID"].nunique())
units = int(filtered["Quantity"].sum())
avg_order_value = revenue / orders if orders else 0
profit_margin = (profit / revenue * 100) if revenue else 0

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Net revenue", money(revenue))
m2.metric("Estimated profit", money(profit))
m3.metric("Orders", f"{orders:,}")
m4.metric("Units sold", f"{units:,}")
m5.metric("Profit margin", f"{profit_margin:.1f}%")

st.markdown("## Sales overview")
st.markdown('<p class="section-caption">Track monthly performance and compare major contributors.</p>', unsafe_allow_html=True)

monthly = (
    filtered.groupby("Month", as_index=False)
    .agg(Revenue=("Revenue", "sum"), Profit=("Profit", "sum"), Orders=("Order_ID", "nunique"))
    .sort_values("Month")
)
category_sales = (
    filtered.groupby("Category", as_index=False)
    .agg(Revenue=("Revenue", "sum"), Profit=("Profit", "sum"), Units=("Quantity", "sum"))
    .sort_values("Revenue", ascending=False)
)
region_sales = (
    filtered.groupby("Region", as_index=False)
    .agg(Revenue=("Revenue", "sum"), Orders=("Order_ID", "nunique"))
    .sort_values("Revenue", ascending=False)
)

c1, c2 = st.columns([1.55, 1])
with c1:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly["Month"], y=monthly["Revenue"], mode="lines+markers",
        name="Revenue", line=dict(color="#176b87", width=3),
        hovertemplate="%{x|%b %Y}<br>Revenue: ₹%{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=monthly["Month"], y=monthly["Profit"], mode="lines+markers",
        name="Profit", line=dict(color="#e3a33d", width=3),
        hovertemplate="%{x|%b %Y}<br>Profit: ₹%{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        title="Revenue and profit over time", height=370,
        margin=dict(l=10, r=10, t=55, b=10),
        legend=dict(orientation="h", y=1.12),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="white", font_color="#263445",
        yaxis_title="Amount (₹)", xaxis_title="Month",
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#e8edf4")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    fig = px.bar(
        category_sales, x="Revenue", y="Category", orientation="h",
        text=category_sales["Revenue"].map(lambda x: f"₹{x:,.0f}"),
        title="Revenue by category", color="Revenue",
        color_continuous_scale=["#a8d8e5", "#176b87"],
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(
        height=370, margin=dict(l=10, r=35, t=55, b=10),
        coloraxis_showscale=False, paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="white", font_color="#263445", xaxis_title="Revenue (₹)", yaxis_title="",
    )
    fig.update_xaxes(showgrid=True, gridcolor="#e8edf4")
    fig.update_yaxes(showgrid=False, autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)

c3, c4 = st.columns(2)
with c3:
    fig = px.bar(
        region_sales, x="Region", y="Revenue", color="Region",
        title="Revenue by region", text=region_sales["Revenue"].map(lambda x: f"₹{x:,.0f}"),
        color_discrete_sequence=["#176b87", "#4c9aab", "#83c5be", "#e3a33d", "#8b7bb5"],
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(height=330, showlegend=False, margin=dict(l=10, r=20, t=55, b=10),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="white", font_color="#263445",
                      yaxis_title="Revenue (₹)")
    fig.update_yaxes(gridcolor="#e8edf4")
    st.plotly_chart(fig, use_container_width=True)

with c4:
    channel_sales = filtered.groupby("Sales_Channel", as_index=False)["Revenue"].sum()
    fig = px.pie(
        channel_sales, names="Sales_Channel", values="Revenue", hole=0.58,
        title="Revenue by sales channel",
        color_discrete_sequence=["#176b87", "#4c9aab", "#e3a33d", "#8b7bb5"],
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(height=330, margin=dict(l=10, r=10, t=55, b=10),
                      paper_bgcolor="rgba(0,0,0,0)", legend_title_text="", font_color="#263445")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("## Key findings")
top_category = category_sales.iloc[0]
top_region = region_sales.iloc[0]
top_product = (
    filtered.groupby("Product", as_index=False).agg(Revenue=("Revenue", "sum"))
    .sort_values("Revenue", ascending=False).iloc[0]
)
ins1, ins2, ins3 = st.columns(3)
with ins1:
    st.info(f"**Top category**\n\n{top_category['Category']} generated {money(float(top_category['Revenue']))} in revenue.")
with ins2:
    st.info(f"**Leading region**\n\n{top_region['Region']} contributed {money(float(top_region['Revenue']))} in revenue.")
with ins3:
    st.info(f"**Top product**\n\n{top_product['Product']} generated {money(float(top_product['Revenue']))} in revenue.")

st.markdown("## Product performance")
product_summary = (
    filtered.groupby(["Product", "Category"], as_index=False)
    .agg(Units_Sold=("Quantity", "sum"), Orders=("Order_ID", "nunique"),
         Revenue=("Revenue", "sum"), Profit=("Profit", "sum"))
    .sort_values("Revenue", ascending=False)
)
show_n = st.slider("Number of products to display", min_value=5, max_value=25, value=10, step=5)
shown_products = product_summary.head(show_n).copy()
shown_products["Revenue"] = shown_products["Revenue"].round(2)
shown_products["Profit"] = shown_products["Profit"].round(2)
st.dataframe(shown_products, use_container_width=True, hide_index=True)

with st.expander("View filtered order data"):
    display_df = filtered[[
        "Order_ID", "Order_Date", "Product", "Category", "Region", "Quantity",
        "Unit_Price", "Discount_Percent", "Revenue", "Profit", "Payment_Method",
        "Sales_Channel", "Customer_Type"
    ]].copy()
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    csv_bytes = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download filtered data as CSV", data=csv_bytes,
        file_name="satyajit_mahakud_filtered_sales.csv", mime="text/csv",
    )

st.markdown(
    '<div class="footer">Retail Sales Intelligence · Created by <strong>Satyajit Mahakud</strong> · '
    'Python · Pandas · Plotly · Streamlit</div>',
    unsafe_allow_html=True,
)
