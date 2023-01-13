import pandas as pd
import numpy as np
import warnings
import streamlit as st
#
from aggrid_select import st_aggrid_dataframe


# Parameters for size of dummy DataFrame
#  ... DataFrames with more rows (hence Aggrid pages) cause more flickering and warnings
with st.sidebar:
    st.subheader("Data Parametrs")
    number_of_rows = st.number_input(label="Number of Rows", min_value=1, max_value=1000, value=10)
    number_of_columns = st.number_input(label="Number of Columns", min_value=1, max_value=50, value=5)
    df = pd.DataFrame(
        data=np.arange(number_of_rows*number_of_columns).reshape((number_of_rows, number_of_columns))
    )

# Parameters for Aggrid display and selection
with st.sidebar:
    st.subheader("Aggrid Display Parameters")
    selection_mode = st.selectbox(label="selection_mode", options=["disabled", "single", "multiple"])
    if selection_mode=="multiple":
        # Is the glitch occuring because we have too many rows pre-selected?
        pre_select_all_rows = st.checkbox(
            label="Pre-Select All Rows",
            value=True,
            help="""True: pre-select all rows.  False: pre-select no rows."""
        )
    else:
        pre_select_all_rows = False

# Display
with warnings.catch_warnings(record=True) as warns:
    st.header("Data")
    st_aggrid_dataframe(df, selection_mode, pre_select_all_rows)
    
    st.header("Warnings")
    # Count and display total number of warnings
    if "warning_count" not in st.session_state:
        st.session_state["warning_count"] = 0
    st.session_state["warning_count"] += len(warns)
    st.write(f"""Number of warnings since app start: {st.session_state["warning_count"]}""")
    
    # Display warnings from this load
    st.subheader("Most Recent Warnings")
    st.write(warns)
    for w in warns:  st.write(w)

st.subheader("Discussion of Warnings")
st.markdown("""
    This section discusses my observations of the app behavior and how they provide clues as to what the underlying bug is.

    - The warnings occur at one of two lines in st_aggrid.__init__.py.  These seem easy enough to fix in the package.
    
    - But I am not sure why __init__.py is called so many times.  I thought it would be called only once, at the start of the app.  Instead it seems to be called:

        - Every time an option changes and the aggrid is reloaded
    
        - Every time a row of the grid is selected"
    
        - Many times for DataFrames with large number of rows (perhaps related to the number of pages in aggrid pagination?)

            - I am also not sure why, often, only a single warning is recorded and displayed.  This seems to suggest that the "with" warning block is being called multiple times by Streamlit, rather than that streamlit_aggrid is 
""")

# -------------------------------------------------
# Aggrid bug detection:


# • Is the problem with the RoverLS app or Streamlit-Aggrid?
#   - Make a simple (separate) app using just streamlit-aggrid
#   - This simple app has controls for the
#      - Size of dataframe  (in RoverLS app it seemed like problem was caused by large datasets).  This also uses simple numeric data (to ensure problem wasn't cauesd by more complex datatypes in RoverLS app)
#      - Type of selection method (in RoverLS app there seemed to be problems with multiple selection via checkbox and no problem with single selection, as on the AnalyzeRun page)


# • I discovered from the Streamlit logs that a warning was being thrown by AgGrid.__init__.py many times.  This is odd since the __init__.py should only be called once, when the app initializes.
#    - The app catches and counts the number of warnings, hence counts the number of times __init__.py is called.
#    - It is called many times with "multiple" selection and many pages of data
#    - I think this is the source of the problems


# • Is the problem with Streamlit Cloud?
#    - The code seemed to run slower or crash on Streamlit Cloud but not my local machine.  We were unsure if this is due to limitted resources on the Cloud or due to the structure of the Cloud itself
#    - Other people are having issues with Cloud and Aggrid.  Forum posts claim this is due to malfunctioning Cloud features which Streamlit team is working on / can disable.
#         (Many posts on aggrid in past few weeks:  https://discuss.streamlit.io/c/streamlit-components/18)
# I will send an email to streamlit Cloud support and also make a detailed forum post to get this fixed.

# • Options
#   - It seems like the issue is with pre-selecting all rows.
#   - When all rows are pre-selected, it throws a warning for each data page .... but not all the time.
#   - For large datasets, 500 rows, it