
import streamlit as st
import pandas as pd
import plotly.express as px

# Title and Web Page Configurations
st.set_page_config(page_title="Baby Name Analysis aka STRV Case Study",
                   layout = 'wide', 
                   page_icon = "👼🏻")
st.title("""👼🏻 Baby Name Analysis""")

# Load CSV Files
@st.cache_data
def load_data():
    national_names = pd.read_parquet("NationalNames1960.parquet")
    state_names = pd.read_parquet("StateNames1960.parquet")
    top50_unisex_national = pd.read_csv("Top50_Unisex_National.csv")
    top30_unisex_state = pd.read_csv("Top30_Unisex_State.csv")
    return national_names, state_names, top50_unisex_national, top30_unisex_state

national_names, state_names, top50_unisex_national, top30_unisex_state= load_data()

national_names['Year'] = national_names['Year'].astype(int)
state_names['Year'] = state_names['Year'].astype(int)
top50_unisex_national['Year'] = top50_unisex_national['Year'].astype(int)
top30_unisex_state['Year'] = top30_unisex_state['Year'].astype(int)

# --- Line Chart Filters ---
st.subheader("Line Chart Filters")
# Create 4 columns
col1, col2, col3, col4 = st.columns(4)

with col1:
    selected_names = st.multiselect("Select up to 3 names:", state_names["Name"].unique(), default=["Emma"], max_selections=3)

with col2:
    year_range = st.slider("Select Year Range:", int(state_names["Year"].min()), int(state_names["Year"].max()), (2000, 2010))

with col3:
    selected_state = st.selectbox(
        "Select State:", # label
        ["All"] + list(state_names["State"].unique()), # options
        index=(["All"] + list(state_names["State"].unique())).index("CA")  # default = California
    )

with col4:
    selected_gender = st.radio("Select Gender:", ["Both", "Male", "Female"])

# -------------------- LINE CHART --------------------
st.header("Name Popularity Over Time (State Level)")

filtered_data = state_names[
    (state_names["Year"].between(*year_range)) &
    (state_names["Name"].isin(selected_names))
]

# Step 2: Apply Gender Filter or Aggregate if "Both"
if selected_gender == "Both":
    line_data = filtered_data.groupby(["Year", "Name", "State"], as_index=False)["Count"].sum()
    line_data["Gender"] = "Both"  # Ensure consistency
else:
    line_data = filtered_data[filtered_data["Gender"] == ("M" if selected_gender == "Male" else "F")]

# Step 3: Apply State Filter or Aggregate if "All"
if selected_state == "All":
    line_data = line_data.groupby(["Year", "Name", "Gender"], as_index=False)["Count"].sum()
    line_data["State"] = "All"  # Ensure consistency
else:
    line_data = line_data[line_data["State"] == selected_state]

# Plot line chart
if not line_data.empty:
    fig = px.line(line_data, x="Year", y="Count", color="Name", markers=True, title="Popularity Over Years")
    st.plotly_chart(fig)
else:
    st.warning("No data available for selected filters.")

# --- Choropleth Map Filters ---
st.subheader("Map Filters")
# Create 3 columns
col1, col2, col3 = st.columns(3)

with col1:
    map_name = st.selectbox("Select Name:", state_names["Name"].unique())

with col2:
    map_year_range = st.slider("Select Year Range for Map:", int(state_names["Year"].min()), int(state_names["Year"].max()), (2000, 2010))

with col3:
    map_gender = st.radio("Select Gender for Map:", ["Both", "Male", "Female"])

# -------------------- CHOROPLETH MAP --------------------
st.header("Name Popularity by State")

# Filter data for the map
map_data = state_names[
    (state_names["Year"].between(*map_year_range)) &
    (state_names["Name"] == map_name) &
    ((state_names["Gender"] == "M") if map_gender == "Male" else
    (state_names["Gender"] == "F") if map_gender == "Female" else True)
].groupby("State").sum().reset_index()

# Plot the choropleth map
if not map_data.empty:
    fig = px.choropleth(map_data, locations="State", locationmode="USA-states", color="Count",
                         color_continuous_scale="Blues", title=f"Popularity of {map_name} Across States",
                         scope="usa")
    fig.update_layout(width=1000,height=500)
    st.plotly_chart(fig)
else:
    st.warning("No data available for selected filters.")


# --- Top 50 National and State Names Table Filters ---
st.subheader("Top 50 National and State Names Filter")

col1, col2 = st.columns(2)
with col1:

    top50_year = st.selectbox("Select Year for National Rankings:", sorted(national_names["Year"].unique(), reverse=True))

    # Filter data for the selected year
    top_national = national_names[national_names["Year"] == top50_year]

    # Get top 50 male names
    top_male = top_national[top_national["Gender"] == "M"].nlargest(50, "Count")[["Name", "Count"]].reset_index(drop=True)
    top_male.columns = ["Male Name", "Number of Males"]

    # Get top 50 female names
    top_female = top_national[top_national["Gender"] == "F"].nlargest(50, "Count")[["Name", "Count"]].reset_index(drop=True)
    top_female.columns = ["Female Name", "Number of Females"]

    # Create Rank column (1 to 50)
    rank = pd.DataFrame({"Rank": range(1, 51)})

    # Merge into a final table
    top_50_table = pd.concat([rank, top_male, top_female], axis=1)

    # Display the table
    st.header("Top 50 National Names")
    st.write(f"Top 50 names for {top50_year}:")
    st.dataframe(top_50_table, hide_index=True)

# --- Top 50 State Names Table Filters ---
with col2:
    col21, col22 = st.columns(2)
    # -------------------- TOP 50 STATE NAMES --------------------
    st.header("Top 50 State Names")

    with col21:
        top50_state_year = st.selectbox("Select Year for State Rankings:", sorted(state_names["Year"].unique(), reverse=True))

    with col22:
        top50_state = st.selectbox("Select State:", state_names["State"].unique())

    # Filter data for the selected year and state
    top_state = state_names[(state_names["Year"] == top50_state_year) & (state_names["State"] == top50_state)]

    # Get top 50 male names
    top_male_state = top_state[top_state["Gender"] == "M"].nlargest(50, "Count")[["Name", "Count"]].reset_index(drop=True)
    top_male_state.columns = ["Male Name", "Number of Males"]

    # Get top 50 female names
    top_female_state = top_state[top_state["Gender"] == "F"].nlargest(50, "Count")[["Name", "Count"]].reset_index(drop=True)
    top_female_state.columns = ["Female Name", "Number of Females"]

    # Create Rank column (1 to 50)
    rank_state = pd.DataFrame({"Rank": range(1, 51)})

    # Merge into a final table
    top_50_state_table = pd.concat([rank_state, top_male_state, top_female_state], axis=1)

    # Display the table
    st.write(f"Top 50 names for {top50_state} in {top50_state_year}:")
    st.dataframe(top_50_state_table, hide_index=True)


# ------------------ STREAMLIT APP ------------------
st.title("Unisex Name Analysis ♂️♀️")

# ------------------ FILTERS ------------------
col1, col2 = st.columns(2)

with col1:
    year_list = top50_unisex_national["Year"].unique().tolist()  # Get unique years from the CSV
    year_list.sort(reverse=True)  # Sort the years in descending order

    # Add a unique key for the year selectbox
    selected_year = st.selectbox("Select Year:", year_list, key="year_selectbox")

with col2:
    state_list = top30_unisex_state["State"].unique().tolist()  

    # Add a unique key for the state selectbox
    selected_state = st.selectbox("Select State:", state_list, key="state_selectbox")
# Tab layout for different views
tab1, tab2 = st.tabs(["📊 Top 50 Unisex Names (National)", "📍 Top 30 Unisex Names (State-wise)"])



# ------------------ NATIONAL LEVEL ANALYSIS ------------------
with tab1:
    st.subheader(f"Top 50 Unisex Names for {selected_year}")

    # Load and filter data for the selected year
    df_national_year = top50_unisex_national[top50_unisex_national["Year"] == selected_year].head(50)

    # Format Year column to display as a whole number without commas
    df_national_year['Year'] = df_national_year['Year'].apply(lambda x: f"{int(x)}")

    # Display the filtered data
    st.dataframe(df_national_year, use_container_width=True, hide_index=True)

# ------------------ STATE LEVEL ANALYSIS ------------------
with tab2:
    st.subheader(f"Top 30 Unisex Names by State for {selected_year}")

    # Load and filter data for the selected year and state
    df_state = top30_unisex_state[(top30_unisex_state["Year"] == selected_year) & (top30_unisex_state["State"] == selected_state)].head(30)

    # Check if the DataFrame is empty
    if df_state.empty:
        st.write(f"No data available for {selected_state} in {selected_year}")
    else:
        # Format Year column to display as a whole number without commas
        df_state['Year'] = df_state['Year'].apply(lambda x: f"{int(x)}")

        # Display the filtered data
        st.dataframe(df_state, use_container_width=True, hide_index=True)