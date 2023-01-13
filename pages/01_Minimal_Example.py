# Showcase problem in the easiest way possible
import warnings
import numpy as np
import pandas as pd
import streamlit as st
#
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode
from st_aggrid.shared import ColumnsAutoSizeMode


# Make sample data
number_of_rows = 200
number_of_columns = 5
df = pd.DataFrame(
    data=np.arange(number_of_rows*number_of_columns).reshape((number_of_rows, number_of_columns))
)

# DataFrame for AgGrid
df = df.reset_index()   # aggrid doesn't show DataFrame index
df.columns = [str(c) for c in df.columns]    # bug: GridOptionsBuilder only allows string column names

# Displays the DataFrame and get click events
# Count the number of warnings it throws.
# These warnings all come from st_aggrid.__init__.py
with warnings.catch_warnings(record=True) as warns:
    st.header("Minimal Example")
    st.markdown("""
        This page is the minimum example illustrating the problem:
        
        - When select_mode="multiple" and all checkboxes are initialized to true, the data is slow to load, presumably related to the many warnings that are thrown, as can be seen by the warning count displayed below the aggrid DataFrame.  This problem is even worse for larger datasets.
    """)

    st.subheader("Aggrid Data Selection")
    # Set grid options.
    # Bug seems to occur when selection_mode="multiple" and all rows are pre-pre-selected
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection(
        selection_mode="multiple",
        use_checkbox=True,
        pre_selected_rows=list(range(len(df))),
    )
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)
    gridOptions = gb.build()

    # Display DataFrame and get click events
    grid_response = AgGrid(
        df,
        gridOptions=gridOptions,
        update_mode=GridUpdateMode.GRID_CHANGED,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
    )

    # Warning ....
    st.subheader("Warning Information")
    if "warning_count_mwe" not in st.session_state:
        st.session_state["warning_count_mwe"] = 0
    st.session_state["warning_count_mwe"] += len(warns)
    st.write(f"""Number of warnings since app start: {st.session_state["warning_count_mwe"]}""")

    st.write("Most recent warnings:")
    st.write(warns)
    for w in warns:  st.write(w)
