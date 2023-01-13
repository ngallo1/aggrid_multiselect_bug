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
    st.header("Explore in Depth")
    st.write("This page has inputs that control the data size and selection options of aggrid.")
    st.write("These controls can be used to reproduce the problematic behavior on Streamlit Cloud as discussed at the bottom of this page.")


    st.subheader("Aggrid Data Selection")
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

    - The warnings occur in st_aggrid.\_\_init\_\_.py (at line 42 about iteritems() deprecation).  It seems easy enough to fix this in the package.
    
    - But I am not sure why \_\_init\_\_.py is called so many times.  I thought it would be called only once, at the start of the app.  Instead, by examining the accumulated warning count, we can see that it is called:

        - Every time a row of the grid is selected or deselected  (for selection_mode either "single" or "multiple")
    
        - Many times when selection_mode="multiple" and pre_select_all_rows=True.
        
            - Many (but not all) times it throws a warning for each page of data in the aggrid.  This causes datasets with a modest number of rows (like 200) to load slowly.

            - Although many warnings are raised, only one is recorded and displayed.  This seems to suggest that the code in the "with" warning block is being executed multiple times by Streamlit, each time raising one warning  (as opposed to many warnings being thrown by the one call to the Aggrid methods)

            - This behavior occurs only on Streamlit Cloud and not on my local machine (Windows 10, exact same package versions).  I haven't tested other cloud providers yet.
""")
