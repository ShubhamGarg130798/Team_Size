import streamlit as st
import pandas as pd
try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="Team Requirement Analyzer",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.markdown('<p class="main-header">📊 Team Requirement Analyzer</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Calculate staffing requirements based on loan disbursement targets</p>', unsafe_allow_html=True)

# Sidebar for inputs
st.sidebar.header("⚙️ Input Parameters")

# Financial Parameters
st.sidebar.subheader("💰 Loan Disbursement Details")
loan_amt_current = st.sidebar.number_input(
    "Loan Amount to be Disbursed (Current Month)",
    min_value=0.0,
    value=10000000.0,
    step=100000.0,
    format="%.0f",
    help="Enter amount in absolute value (e.g., 10000000 for 1 CR)"
)

pf_percentage = st.sidebar.number_input(
    "Processing Fee (PF) %",
    min_value=0.0,
    max_value=100.0,
    value=11.8,
    step=0.1,
    help="Processing fee as percentage of loan amount"
)

roi_per_day = st.sidebar.number_input(
    "ROI per Day (%)",
    min_value=0.0,
    max_value=10.0,
    value=1.0,
    step=0.1,
    help="Daily rate of interest"
)

avg_ticket_size = st.sidebar.number_input(
    "Average Ticket Size",
    min_value=1.0,
    value=30000.0,
    step=1000.0,
    format="%.0f",
    help="Average loan amount per customer"
)

avg_tenure = st.sidebar.number_input(
    "Average Tenure (days)",
    min_value=1,
    value=25,
    step=1,
    help="Average loan tenure in days"
)

no_of_days = st.sidebar.number_input(
    "No of Days in Month",
    min_value=1,
    max_value=31,
    value=30,
    step=1
)

# Historical Data
st.sidebar.subheader("📈 Historical Disbursement Data")
loan_amt_t1 = st.sidebar.number_input(
    "Loan Amount Disbursed (T-1 Month)",
    min_value=0.0,
    value=8000000.0,
    step=100000.0,
    format="%.0f",
    help="Loan amount disbursed in previous month"
)

loan_amt_t2 = st.sidebar.number_input(
    "Loan Amount Disbursed (T-2 Month)",
    min_value=0.0,
    value=5000000.0,
    step=100000.0,
    format="%.0f",
    help="Loan amount disbursed two months ago"
)

# Team Performance Parameters
st.sidebar.subheader("👥 Team Performance Targets")
sanction_sales_target = st.sidebar.number_input(
    "Sanction & Sales Target Per Day Per Person",
    min_value=1.0,
    value=250000.0,
    step=10000.0,
    format="%.0f",
    help="Daily target per sanction/sales person"
)

collection_target = st.sidebar.number_input(
    "Collection Per Month Per Person",
    min_value=1.0,
    value=8000000.0,
    step=100000.0,
    format="%.0f",
    help="Monthly collection target per person"
)

# Calculations
st.header("📋 Key Calculations")

# 1. Amount to be present in bank
pf_amount = (pf_percentage / 100) * loan_amt_current
amt_in_bank = loan_amt_current - pf_amount

# 2. Repayment Amount
repayment_amt = loan_amt_current + (loan_amt_current * (roi_per_day / 100) * avg_tenure)

# 3. Number of Loans
no_of_loans = loan_amt_current / avg_ticket_size

# 4. Number of Sanction and Sales Person Required
no_sanction_sales = (loan_amt_current / no_of_days) / sanction_sales_target

# 5. Interest calculations for collection
interest_current = loan_amt_current * (roi_per_day / 100) * avg_tenure
interest_t1 = loan_amt_t1 * (roi_per_day / 100) * avg_tenure
interest_t2 = loan_amt_t2 * (roi_per_day / 100) * avg_tenure

# Collection components (Principal + Interest)
collection_current = (loan_amt_current + interest_current) * 0.11
collection_t1 = (loan_amt_t1 + interest_t1) * 0.78
collection_t2 = (loan_amt_t2 + interest_t2) * 0.11

# Total collection required
total_collection_required = collection_current + collection_t1 + collection_t2

# Number of Collection Person Required
no_collection = total_collection_required / collection_target

# Display results in columns
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="💵 Amount in Bank",
        value=f"₹{amt_in_bank/100000:.2f}L",
        delta=f"-₹{pf_amount/100000:.2f}L (PF)",
        help=f"Net amount after deducting {pf_percentage}% processing fee"
    )

with col2:
    st.metric(
        label="🔄 Repayment Amount",
        value=f"₹{repayment_amt/100000:.2f}L",
        delta=f"+₹{(repayment_amt-loan_amt_current)/100000:.2f}L (Interest)",
        help="Total amount to be collected including interest"
    )

with col3:
    st.metric(
        label="📝 Number of Loans",
        value=f"{int(no_of_loans)}",
        help=f"Based on avg ticket size of ₹{avg_ticket_size:,.0f}"
    )

with col4:
    st.metric(
        label="👥 Total Staff Required",
        value=f"{int(no_sanction_sales) + (1 if no_sanction_sales % 1 > 0 else 0) + int(no_collection) + (1 if no_collection % 1 > 0 else 0)}",
        help="Total Sanction/Sales + Collection staff"
    )

# Staff breakdown
st.header("👥 Staff Requirement Breakdown")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Sanction & Sales Team")
    st.info(f"""
    **Calculation:**
    - Daily Target: ₹{loan_amt_current/no_of_days:,.0f}
    - Per Person Target: ₹{sanction_sales_target:,.0f}
    - **Exact Staff Needed:** {no_sanction_sales:.2f}
    - **Rounded Up:** {int(no_sanction_sales) + (1 if no_sanction_sales % 1 > 0 else 0)} persons
    """)

with col2:
    st.subheader("Collection Team")
    st.info(f"""
    **Calculation:**
    - Total Collection Target: ₹{total_collection_required:,.0f}
    - Per Person Target: ₹{collection_target:,.0f}
    - **Exact Staff Needed:** {no_collection:.2f}
    - **Rounded Up:** {int(no_collection) + (1 if no_collection % 1 > 0 else 0)} persons
    """)

# Collection breakdown
st.header("💰 Collection Requirement Analysis")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Collection Components")
    
    collection_breakdown = pd.DataFrame({
        'Period': ['Current Month (11%)', 'T-1 Month (78%)', 'T-2 Month (11%)'],
        'Disbursement': [
            f"₹{loan_amt_current/100000:.2f}L",
            f"₹{loan_amt_t1/100000:.2f}L",
            f"₹{loan_amt_t2/100000:.2f}L"
        ],
        'Interest': [
            f"₹{interest_current/100000:.2f}L",
            f"₹{interest_t1/100000:.2f}L",
            f"₹{interest_t2/100000:.2f}L"
        ],
        'Collection': [
            f"₹{collection_current/100000:.2f}L",
            f"₹{collection_t1/100000:.2f}L",
            f"₹{collection_t2/100000:.2f}L"
        ],
        'Percentage': ['10%', '75%', '15%']
    })
    
    st.dataframe(collection_breakdown, use_container_width=True, hide_index=True)
    st.success(f"**Total Collection Required:** ₹{total_collection_required/100000:.2f} Lakhs")

with col2:
    st.subheader("Collection Distribution")
    
    if PLOTLY_AVAILABLE:
        pie_data = pd.DataFrame({
            'Period': ['Current (10%)', 'T-1 (75%)', 'T-2 (15%)'],
            'Amount': [collection_current, collection_t1, collection_t2]
        })
        
        fig_pie = px.pie(
            pie_data,
            values='Amount',
            names='Period',
            title='Collection Split by Period',
            color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1'],
            hole=0.4
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning("Install plotly for visualizations: pip install plotly")
        pie_data = pd.DataFrame({
            'Period': ['Current (10%)', 'T-1 (75%)', 'T-2 (15%)'],
            'Amount': [f"₹{collection_current/100000:.2f}L", f"₹{collection_t1/100000:.2f}L", f"₹{collection_t2/100000:.2f}L"]
        })
        st.dataframe(pie_data, use_container_width=True, hide_index=True)

# Team composition visualization
st.header("📊 Team Composition Visualization")

team_rounded = {
    'Sanction & Sales': int(no_sanction_sales) + (1 if no_sanction_sales % 1 > 0 else 0),
    'Collection': int(no_collection) + (1 if no_collection % 1 > 0 else 0)
}

if PLOTLY_AVAILABLE:
    fig_team = go.Figure(data=[
        go.Bar(
            name='Required Staff',
            x=list(team_rounded.keys()),
            y=list(team_rounded.values()),
            text=list(team_rounded.values()),
            textposition='outside',
            marker_color=['#636EFA', '#EF553B']
        )
    ])

    fig_team.update_layout(
        title='Team Requirement by Role',
        xaxis_title='Role',
        yaxis_title='Number of Staff',
        showlegend=False,
        height=400
    )

    st.plotly_chart(fig_team, use_container_width=True)
else:
    team_df = pd.DataFrame({
        'Role': list(team_rounded.keys()),
        'Required Staff': list(team_rounded.values())
    })
    st.bar_chart(team_df.set_index('Role'))

# Complete summary table
st.header("📋 Complete Summary Report")

summary_data = {
    'Parameter': [
        'Loan Amount to Disburse (Current)',
        'Processing Fee Amount',
        'Amount Required in Bank',
        'Number of Loans',
        'Average Ticket Size',
        'Interest Amount (Current)',
        'Total Repayment Amount (Current)',
        '',
        'Loan Disbursed T-1 Month',
        'Interest Amount T-1',
        'Loan Disbursed T-2 Month',
        'Interest Amount T-2',
        '',
        'Collection from Current (10%)',
        'Collection from T-1 (75%)',
        'Collection from T-2 (15%)',
        'Total Collection Required',
        '',
        'Sanction & Sales Staff (Exact)',
        'Sanction & Sales Staff (Rounded)',
        'Collection Staff (Exact)',
        'Collection Staff (Rounded)',
        'Total Staff Required'
    ],
    'Value': [
        f"₹{loan_amt_current:,.0f}",
        f"₹{pf_amount:,.0f}",
        f"₹{amt_in_bank:,.0f}",
        f"{int(no_of_loans)}",
        f"₹{avg_ticket_size:,.0f}",
        f"₹{interest_current:,.0f}",
        f"₹{repayment_amt:,.0f}",
        '',
        f"₹{loan_amt_t1:,.0f}",
        f"₹{interest_t1:,.0f}",
        f"₹{loan_amt_t2:,.0f}",
        f"₹{interest_t2:,.0f}",
        '',
        f"₹{collection_current:,.0f}",
        f"₹{collection_t1:,.0f}",
        f"₹{collection_t2:,.0f}",
        f"₹{total_collection_required:,.0f}",
        '',
        f"{no_sanction_sales:.2f}",
        f"{team_rounded['Sanction & Sales']}",
        f"{no_collection:.2f}",
        f"{team_rounded['Collection']}",
        f"{sum(team_rounded.values())}"
    ]
}

summary_df = pd.DataFrame(summary_data)
st.dataframe(summary_df, use_container_width=True, hide_index=True)

# Export options
st.header("📥 Export Options")

col1, col2 = st.columns(2)

with col1:
    csv = summary_df.to_csv(index=False)
    st.download_button(
        label="📄 Download Summary as CSV",
        data=csv,
        file_name="team_requirement_analysis.csv",
        mime="text/csv",
        use_container_width=True
    )

with col2:
    # Create detailed report
    detailed_report = f"""
TEAM REQUIREMENT ANALYSIS REPORT
================================
Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

INPUT PARAMETERS:
- Loan Amount (Current): ₹{loan_amt_current:,.0f}
- Processing Fee: {pf_percentage}%
- ROI per Day: {roi_per_day}%
- Average Ticket Size: ₹{avg_ticket_size:,.0f}
- Average Tenure: {avg_tenure} days
- Sanction Target/Day/Person: ₹{sanction_sales_target:,.0f}
- Collection Target/Month/Person: ₹{collection_target:,.0f}

CALCULATED RESULTS:
- Amount in Bank: ₹{amt_in_bank:,.0f}
- Repayment Amount: ₹{repayment_amt:,.0f}
- Number of Loans: {int(no_of_loans)}
- Sanction & Sales Staff: {team_rounded['Sanction & Sales']}
- Collection Staff: {team_rounded['Collection']}
- Total Staff Required: {sum(team_rounded.values())}

COLLECTION BREAKDOWN:
- Current Month (10%): ₹{collection_current:,.0f}
- T-1 Month (75%): ₹{collection_t1:,.0f}
- T-2 Month (15%): ₹{collection_t2:,.0f}
- Total Collection: ₹{total_collection_required:,.0f}
"""
    
    st.download_button(
        label="📝 Download Detailed Report",
        data=detailed_report,
        file_name="detailed_team_analysis.txt",
        mime="text/plain",
        use_container_width=True
    )

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p><strong>Team Requirement Analyzer</strong> | Built with Streamlit</p>
        <p>Designed for efficient loan disbursement and collection team planning</p>
    </div>
""", unsafe_allow_html=True)
