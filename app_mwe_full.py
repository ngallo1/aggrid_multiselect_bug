import warnings
import numpy as np
import pandas as pd
import streamlit as st
#
from aggrid_select import st_aggrid_dataframe


# Make sample data
number_of_rows = 500
number_of_columns = 5
df = pd.DataFrame(
    data=np.arange(number_of_rows*number_of_columns).reshape((number_of_rows, number_of_columns))
)

selection_mode="multiple"
pre_select_all_rows = True
with warnings.catch_warnings(record=True) as warns:
    st_aggrid_dataframe(df, selection_mode, pre_select_all_rows)
    
    st.subheader("Warning Info")
    if "warning_count" not in st.session_state:
        st.session_state["warning_count"] = 0
    st.session_state["warning_count"] += len(warns)
    st.write(f"""Number of warnings since app start: {st.session_state["warning_count"]}""")
    #
    st.write("Most recent warnings:")
    st.write(warns)
    for w in warns:  st.write(w)

st.subheader("Warning analysis")
st.write(f"""Many warnings are thrown when the selection_mode="multiple" """)