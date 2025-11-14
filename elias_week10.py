import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Cloud Resource Tagging Analysis", layout="wide")

# === LOAD DATA ============================================
@st.cache_data
def load_data():
    # Read the file as text first to see what's happening
    with open('cloudmart_multi_account.csv', 'r') as f:
        lines = f.readlines()
    
    # Parse the header
    header_line = lines[0].strip().replace('"', '')
    headers = [h.strip() for h in header_line.split(',')]
    
    # Parse each data row
    data_rows = []
    for line in lines[1:]:
        if line.strip():  # Skip empty lines
            # Remove quotes and split by comma
            clean_line = line.strip().replace('"', '')
            values = [v.strip() for v in clean_line.split(',')]
            
            # Only add if we have the right number of columns
            if len(values) == len(headers):
                data_rows.append(values)
    
    # Create dataframe
    df = pd.DataFrame(data_rows, columns=headers)
    
    # Convert MonthlyCostUSD to numeric
    df['MonthlyCostUSD'] = pd.to_numeric(df['MonthlyCostUSD'], errors='coerce')
    
    # DON'T remove duplicates - keep all resources
    df = df.reset_index(drop=True)
    
    return df

try:
    df = load_data()
    
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.stop()

# === HEADER ============================================
st.title("☁️ CloudMart Resource Tagging & Cost Governance Dashboard")
st.markdown("**Week 10 Activity: Resource Tagging Analysis**")

# Check if required columns exist
required_cols = ['AccountID', 'ResourceID', 'Service', 'Region', 'Department', 'Project', 
                 'Environment', 'Owner', 'CostCenter', 'CreatedBy', 'MonthlyCostUSD', 'Tagged']

missing_cols = [col for col in required_cols if col not in df.columns]

if missing_cols:
    st.error(f"Missing columns: {missing_cols}")
    st.write("**Available columns:**", df.columns.tolist())
    st.write("**First few rows:**")
    st.dataframe(df.head())
    st.stop()

# === SIDEBAR FILTERS ============================================
st.sidebar.header("🎯 Filters")

# Department filter
try:
    dept_unique = df['Department'].dropna().unique().tolist()
    departments = ['All'] + sorted([str(d) for d in dept_unique])
except:
    departments = ['All']

selected_dept = st.sidebar.multiselect(
    "Select Department(s)",
    options=departments,
    default=['All']
)

# Service filter
try:
    service_unique = df['Service'].unique().tolist()
    services = ['All'] + sorted([str(s) for s in service_unique])
except:
    services = ['All']

selected_service = st.sidebar.multiselect(
    "Select Service(s)",
    options=services,
    default=['All']
)

# Region filter
try:
    region_unique = df['Region'].unique().tolist()
    regions = ['All'] + sorted([str(r) for r in region_unique])
except:
    regions = ['All']

selected_region = st.sidebar.multiselect(
    "Select Region(s)",
    options=regions,
    default=['All']
)

# Environment filter
try:
    env_unique = df['Environment'].dropna().unique().tolist()
    environments = ['All'] + sorted([str(e) for e in env_unique])
except:
    environments = ['All']

selected_env = st.sidebar.multiselect(
    "Select Environment(s)",
    options=environments,
    default=['All']
)

# Apply filters
filtered_df = df.copy()

if 'All' not in selected_dept:
    filtered_df = filtered_df[filtered_df['Department'].isin(selected_dept)]

if 'All' not in selected_service:
    filtered_df = filtered_df[filtered_df['Service'].isin(selected_service)]

if 'All' not in selected_region:
    filtered_df = filtered_df[filtered_df['Region'].isin(selected_region)]

if 'All' not in selected_env:
    filtered_df = filtered_df[filtered_df['Environment'].isin(selected_env)]

# === TASK SET 1: DATA EXPLORATION ============================================
st.header("📊 Task Set 1: Data Exploration")

# Task 1.1: Display first 5 rows
st.subheader("Task 1.1: First 5 Rows of Dataset")
st.dataframe(filtered_df.head(), use_container_width=True)

st.markdown("---")

# Task 1.2: Check for missing values
st.subheader("Task 1.2: Missing Values in Dataset")
missing_data = filtered_df.isnull().sum().sort_values(ascending=False)
missing_df = pd.DataFrame({
    'Column': missing_data.index,
    'Missing Count': missing_data.values,
    'Missing %': (missing_data.values / len(filtered_df) * 100).round(2)
})
st.dataframe(missing_df, use_container_width=True, hide_index=True)

st.markdown("---")

# Task 1.3: Columns with most missing values
st.subheader("Task 1.3: Columns with Most Missing Values")
col1, col2 = st.columns([1, 2])
with col1:
    st.dataframe(missing_df.head(5), use_container_width=True, hide_index=True)
with col2:
    fig_missing = px.bar(
        missing_df.head(8),
        x='Column',
        y='Missing Count',
        title='Top Missing Values by Column',
        color='Missing %',
        color_continuous_scale='Reds'
    )
    st.plotly_chart(fig_missing, use_container_width=True)

st.markdown("---")

# Task 1.4: Count tagged vs untagged
st.subheader("Task 1.4: Count Total Resources - Tagged vs Untagged")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Resources", f"{len(filtered_df):,}")
    
with col2:
    tagged_count = len(filtered_df[filtered_df['Tagged'] == 'Yes'])
    st.metric("Tagged Resources", f"{tagged_count:,}")
    
with col3:
    untagged_count = len(filtered_df[filtered_df['Tagged'] == 'No'])
    st.metric("Untagged Resources", f"{untagged_count:,}")
    
with col4:
    st.metric("Tagged %", f"{(tagged_count/len(filtered_df)*100):.1f}%")

tagged_counts = filtered_df['Tagged'].value_counts().reset_index()
tagged_counts.columns = ['Tagged', 'Count']
st.dataframe(tagged_counts, use_container_width=True, hide_index=True)

st.markdown("---")

# Task 1.5: Percentage of untagged
st.subheader("Task 1.5: Percentage of Untagged Resources")
untagged_pct = (untagged_count / len(filtered_df) * 100) if len(filtered_df) > 0 else 0

col1, col2 = st.columns(2)
with col1:
    st.metric("Untagged Percentage", f"{untagged_pct:.2f}%", delta=f"{untagged_count} resources", delta_color="inverse")
with col2:
    fig_pie_task15 = px.pie(
        tagged_counts,
        values='Count',
        names='Tagged',
        title='Resource Tagging Distribution',
        color='Tagged',
        color_discrete_map={'Yes': 'green', 'No': 'red'}
    )
    st.plotly_chart(fig_pie_task15, use_container_width=True)

# === TASK SET 2: COST VISIBILITY ============================================
st.header("💰 Task Set 2: Cost Visibility")

# Task 2.1: Calculate total cost of tagged vs untagged
st.subheader("Task 2.1: Total Cost of Tagged vs Untagged Resources")

total_cost = filtered_df['MonthlyCostUSD'].sum()
tagged_cost = filtered_df[filtered_df['Tagged'] == 'Yes']['MonthlyCostUSD'].sum()
untagged_cost = filtered_df[filtered_df['Tagged'] == 'No']['MonthlyCostUSD'].sum()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Monthly Cost", f"${total_cost:,.2f}")
with col2:
    st.metric("Tagged Cost", f"${tagged_cost:,.2f}")
with col3:
    st.metric("Untagged Cost", f"${untagged_cost:,.2f}")

cost_comparison = pd.DataFrame({
    'Status': ['Tagged', 'Untagged'],
    'Cost (USD)': [tagged_cost, untagged_cost]
})
st.dataframe(cost_comparison, use_container_width=True, hide_index=True)

st.markdown("---")

# Task 2.2: Percentage of untagged cost
st.subheader("Task 2.2: Percentage of Total Cost that is Untagged")
untagged_cost_pct = (untagged_cost / total_cost * 100) if total_cost > 0 else 0

col1, col2 = st.columns(2)
with col1:
    st.metric("Untagged Cost Percentage", f"{untagged_cost_pct:.2f}%")
    st.write(f"**Calculation:** (${untagged_cost:,.2f} / ${total_cost:,.2f}) × 100 = {untagged_cost_pct:.2f}%")
with col2:
    fig_cost_pie = px.pie(
        cost_comparison,
        values='Cost (USD)',
        names='Status',
        title='Cost Distribution by Tagging Status',
        color='Status',
        color_discrete_map={'Tagged': 'green', 'Untagged': 'red'}
    )
    st.plotly_chart(fig_cost_pie, use_container_width=True)

st.markdown("---")

# Task 2.3: Department with most untagged cost
st.subheader("Task 2.3: Which Department Has the Most Untagged Cost?")
dept_untagged = filtered_df[filtered_df['Tagged'] == 'No'].groupby('Department')['MonthlyCostUSD'].sum().reset_index()
dept_untagged = dept_untagged.sort_values('MonthlyCostUSD', ascending=False)

if len(dept_untagged) > 0:
    st.write(f"**Answer:** {dept_untagged.iloc[0]['Department']} with ${dept_untagged.iloc[0]['MonthlyCostUSD']:,.2f} in untagged costs")
    st.dataframe(dept_untagged, use_container_width=True, hide_index=True)
    
    fig_dept_untagged = px.bar(
        dept_untagged,
        x='Department',
        y='MonthlyCostUSD',
        title='Untagged Cost by Department',
        labels={'MonthlyCostUSD': 'Untagged Cost (USD)'},
        color='MonthlyCostUSD',
        color_continuous_scale='Reds'
    )
    st.plotly_chart(fig_dept_untagged, use_container_width=True)
else:
    st.info("No untagged resources in selected filters")

st.markdown("---")

# Task 2.4: Project with most cost overall
st.subheader("Task 2.4: Which Project Consumes the Most Cost Overall?")
project_cost = filtered_df.groupby('Project')['MonthlyCostUSD'].sum().reset_index()
project_cost = project_cost.sort_values('MonthlyCostUSD', ascending=False)

if len(project_cost) > 0:
    st.write(f"**Answer:** {project_cost.iloc[0]['Project']} with ${project_cost.iloc[0]['MonthlyCostUSD']:,.2f} total cost")
    st.dataframe(project_cost.head(10), use_container_width=True, hide_index=True)
    
    fig_project_cost = px.bar(
        project_cost.head(10),
        x='Project',
        y='MonthlyCostUSD',
        title='Top 10 Projects by Total Cost',
        labels={'MonthlyCostUSD': 'Total Cost (USD)'},
        color='MonthlyCostUSD',
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig_project_cost, use_container_width=True)

st.markdown("---")

# Task 2.5: Prod vs Dev comparison
st.subheader("Task 2.5: Compare Prod vs Dev Environments (Cost & Tagging Quality)")
env_comparison = filtered_df.groupby(['Environment', 'Tagged'])['MonthlyCostUSD'].sum().reset_index()

# Create summary table
env_summary = filtered_df.groupby('Environment').agg({
    'MonthlyCostUSD': 'sum',
    'ResourceID': 'count'
}).reset_index()
env_summary.columns = ['Environment', 'Total Cost (USD)', 'Total Resources']

# Add tagging percentage
for env in env_summary['Environment']:
    env_df = filtered_df[filtered_df['Environment'] == env]
    tagged_pct = (len(env_df[env_df['Tagged'] == 'Yes']) / len(env_df) * 100) if len(env_df) > 0 else 0
    env_summary.loc[env_summary['Environment'] == env, 'Tagging %'] = tagged_pct

st.dataframe(env_summary, use_container_width=True, hide_index=True)

fig_env = px.bar(
    env_comparison,
    x='Environment',
    y='MonthlyCostUSD',
    color='Tagged',
    title='Cost Comparison: Prod vs Dev vs Test (by Tagging Status)',
    labels={'MonthlyCostUSD': 'Monthly Cost (USD)'},
    barmode='group',
    color_discrete_map={'Yes': 'green', 'No': 'red'}
)
st.plotly_chart(fig_env, use_container_width=True)

# === TASK SET 3: TAGGING COMPLIANCE ============================================
st.header("✅ Task Set 3: Tagging Compliance")

# Task 3.1: Tag Completeness Score
tag_columns = ['Department', 'Project', 'Environment', 'Owner', 'CostCenter']
filtered_df['TagCompletenessScore'] = filtered_df[tag_columns].notna().sum(axis=1)

col1, col2, col3 = st.columns(3)

with col1:
    avg_completeness = filtered_df['TagCompletenessScore'].mean()
    st.metric("Avg Completeness Score", f"{avg_completeness:.2f}/5")

with col2:
    fully_tagged = len(filtered_df[filtered_df['TagCompletenessScore'] == 5])
    st.metric("Fully Tagged Resources", f"{fully_tagged:,}")

with col3:
    poorly_tagged = len(filtered_df[filtered_df['TagCompletenessScore'] < 3])
    st.metric("Poorly Tagged (<3 tags)", f"{poorly_tagged:,}")

# Task 3.2: Lowest completeness resources
st.subheader("3.2: Resources with Lowest Tag Completeness")
lowest_completeness = filtered_df.nsmallest(10, 'TagCompletenessScore')[
    ['ResourceID', 'Service', 'Department', 'TagCompletenessScore', 'MonthlyCostUSD', 'Tagged']
]
st.dataframe(lowest_completeness, use_container_width=True, hide_index=True)

# Task 3.3: Missing tag fields
col1, col2 = st.columns(2)

with col1:
    st.subheader("3.3: Most Frequently Missing Tags")
    missing_tags = filtered_df[tag_columns].isnull().sum().sort_values(ascending=False)
    missing_tags_df = pd.DataFrame({
        'Tag Field': missing_tags.index,
        'Missing Count': missing_tags.values,
        'Missing %': (missing_tags.values / len(filtered_df) * 100).round(2)
    })
    st.dataframe(missing_tags_df, use_container_width=True, hide_index=True)

with col2:
    fig_missing_tags = px.bar(
        missing_tags_df,
        x='Tag Field',
        y='Missing Count',
        title='Missing Tag Fields',
        color='Missing %',
        color_continuous_scale='Oranges'
    )
    st.plotly_chart(fig_missing_tags, use_container_width=True)

# Task 3.4: List untagged resources
st.subheader("3.4: Untagged Resources Details")
untagged_resources = filtered_df[filtered_df['Tagged'] == 'No'][
    ['ResourceID', 'Service', 'Department', 'Project', 'Environment', 'MonthlyCostUSD', 'Owner']
].sort_values('MonthlyCostUSD', ascending=False)

st.dataframe(untagged_resources.head(20), use_container_width=True, hide_index=True)

# Task 3.5: Export untagged resources
st.subheader("3.5: Export Untagged Resources")
col1, col2 = st.columns([1, 3])
with col1:
    st.download_button(
        label="📥 Download Untagged Resources CSV",
        data=untagged_resources.to_csv(index=False).encode('utf-8'),
        file_name='untagged_resources.csv',
        mime='text/csv'
    )
with col2:
    st.info(f"Total untagged resources: {len(untagged_resources)} | Total cost: ${untagged_resources['MonthlyCostUSD'].sum():,.2f}")

# === TASK SET 4: VISUALIZATION DASHBOARD ============================================
st.header("📈 Task Set 4: Visualization Dashboard")

tab1, tab2, tab3, tab4 = st.tabs(["Tagged vs Untagged", "Department Analysis", "Service Analysis", "Environment Analysis"])

with tab1:
    # Task 4.1: Pie chart
    st.subheader("4.1: Tagged vs Untagged Resources")
    
    col1, col2 = st.columns(2)
    
    with col1:
        tagged_counts = filtered_df['Tagged'].value_counts().reset_index()
        tagged_counts.columns = ['Tagged', 'Count']
        
        fig_pie = px.pie(
            tagged_counts,
            values='Count',
            names='Tagged',
            title='Resource Tagging Status',
            color='Tagged',
            color_discrete_map={'Yes': 'green', 'No': 'red'},
            hole=0.4
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        cost_by_tagged = filtered_df.groupby('Tagged')['MonthlyCostUSD'].sum().reset_index()
        
        fig_cost_pie = px.pie(
            cost_by_tagged,
            values='MonthlyCostUSD',
            names='Tagged',
            title='Cost Distribution by Tagging Status',
            color='Tagged',
            color_discrete_map={'Yes': 'green', 'No': 'red'},
            hole=0.4
        )
        st.plotly_chart(fig_cost_pie, use_container_width=True)

with tab2:
    # Task 4.2: Department analysis
    st.subheader("4.2: Cost per Department by Tagging Status")
    
    dept_tag_cost = filtered_df.groupby(['Department', 'Tagged'])['MonthlyCostUSD'].sum().reset_index()
    
    fig_dept = px.bar(
        dept_tag_cost,
        x='Department',
        y='MonthlyCostUSD',
        color='Tagged',
        title='Department Cost by Tagging Status',
        labels={'MonthlyCostUSD': 'Monthly Cost (USD)'},
        barmode='group',
        color_discrete_map={'Yes': 'green', 'No': 'red'}
    )
    st.plotly_chart(fig_dept, use_container_width=True)

with tab3:
    # Task 4.3: Service analysis
    st.subheader("4.3: Total Cost per Service")
    
    service_cost = filtered_df.groupby('Service')['MonthlyCostUSD'].sum().sort_values().reset_index()
    
    fig_service = px.bar(
        service_cost,
        y='Service',
        x='MonthlyCostUSD',
        orientation='h',
        title='Cost by Cloud Service',
        labels={'MonthlyCostUSD': 'Monthly Cost (USD)'},
        color='MonthlyCostUSD',
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig_service, use_container_width=True)

with tab4:
    # Task 4.4: Environment analysis
    st.subheader("4.4: Cost by Environment")
    
    col1, col2 = st.columns(2)
    
    with col1:
        env_cost = filtered_df.groupby('Environment')['MonthlyCostUSD'].sum().reset_index()
        
        fig_env_bar = px.bar(
            env_cost,
            x='Environment',
            y='MonthlyCostUSD',
            title='Cost by Environment',
            labels={'MonthlyCostUSD': 'Monthly Cost (USD)'},
            color='Environment',
            color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c']
        )
        st.plotly_chart(fig_env_bar, use_container_width=True)
    
    with col2:
        fig_env_pie = px.pie(
            env_cost,
            values='MonthlyCostUSD',
            names='Environment',
            title='Cost Distribution by Environment',
            hole=0.4
        )
        st.plotly_chart(fig_env_pie, use_container_width=True)

# === TASK SET 5: TAG REMEDIATION WORKFLOW ============================================
st.header("🔧 Task Set 5: Tag Remediation Workflow")

st.subheader("5.1 & 5.2: Edit Untagged Resources")
st.info("💡 Tip: Double-click cells to edit. Fill in missing Department, Project, and Owner fields.")

# Create editable dataframe for untagged resources
untagged_editable = filtered_df[filtered_df['Tagged'] == 'No'][
    ['ResourceID', 'Service', 'Department', 'Project', 'Environment', 'Owner', 'CostCenter', 'MonthlyCostUSD']
].copy()

edited_df = st.data_editor(
    untagged_editable,
    use_container_width=True,
    num_rows="dynamic",
    hide_index=True
)

# Task 5.3: Download remediated data
col1, col2, col3 = st.columns(3)

with col1:
    st.download_button(
        label="📥 Download Remediated CSV",
        data=edited_df.to_csv(index=False).encode('utf-8'),
        file_name='remediated_resources.csv',
        mime='text/csv'
    )

with col2:
    st.download_button(
        label="📥 Download Full Dataset",
        data=filtered_df.to_csv(index=False).encode('utf-8'),
        file_name='full_dataset.csv',
        mime='text/csv'
    )

# Task 5.4: Before/After comparison
st.subheader("5.4: Before & After Remediation Comparison")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 BEFORE Remediation")
    st.metric("Untagged Resources", f"{len(untagged_editable):,}")
    st.metric("Untagged Cost", f"${untagged_editable['MonthlyCostUSD'].sum():,.2f}")
    st.metric("Missing Tags", f"{untagged_editable[tag_columns].isnull().sum().sum():,}")

with col2:
    st.markdown("### ✅ AFTER Remediation")
    missing_after = edited_df[tag_columns].isnull().sum().sum()
    improvement = len(untagged_editable) - len(edited_df[edited_df[tag_columns].isnull().any(axis=1)])
    
    st.metric("Resources to Review", f"{len(edited_df):,}")
    st.metric("Remaining Missing Tags", f"{missing_after:,}")
    st.metric("Improvement", f"+{improvement} resources", delta="Good")

# === SUMMARY REPORT ============================================
st.header("📋 Summary Report")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Key Findings")
    st.markdown(f"""
    - **Total Resources**: {len(filtered_df):,}
    - **Untagged Resources**: {untagged_count:,} ({untagged_pct:.1f}%)
    - **Total Monthly Cost**: ${total_cost:,.2f}
    - **Untagged Cost**: ${untagged_cost:,.2f} ({untagged_cost_pct:.1f}%)
    - **Avg Tag Completeness**: {avg_completeness:.2f}/5
    """)

with col2:
    st.subheader("Recommendations")
    st.markdown("""
    1. **Implement Mandatory Tagging Policies**
       - Enforce tags at resource creation
       - Use AWS Config rules or Azure Policy
    
    2. **Automate Tag Remediation**
       - Use Terraform/CloudFormation with default tags
       - Schedule regular tag audits
    
    3. **Cost Center Enforcement**
       - Link tags to billing alerts
       - Generate department-level cost reports
    
    4. **Regular Audits**
       - Weekly tagging compliance checks
       - Monthly cost allocation reviews
    """)

st.success("✅ Analysis complete! Use the sidebar filters to explore different views and download the data for your report.")