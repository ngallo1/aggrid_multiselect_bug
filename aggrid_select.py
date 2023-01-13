import pandas as pd
#
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode
from st_aggrid.shared import ColumnsAutoSizeMode


# ** todo: this is a common way to display tables across the application ....
def st_aggrid_dataframe(
        df,
        selection_mode="disabled",
        pre_select_all_rows=True,
    ):
    """
    Display a pd.DataFrame and allow user to select a single or multiple rows
    Usage taken from demo at:https://pablocfonseca-streamlit-aggrid-examples-example-jyosi3.streamlitapp.com/
    """
    if selection_mode not in ["disabled", "single", "multiple"]:
        raise Exception(f"Invalid selection_mode: {selection_mode}")
    original_index = df.index
    df = (df.to_frame() if isinstance(df, pd.Series) else df)
    df = df.reset_index()   # aggrid doesn't show DataFrame index
    df.columns = [str(c) for c in df.columns]    # bug: GridOptionsBuilder only allows string column names

    gb = GridOptionsBuilder.from_dataframe(df)
    if selection_mode=="multiple":
        gb.configure_selection(
            selection_mode="multiple",
            use_checkbox=True,
            pre_selected_rows=list(range(len(df))) if pre_select_all_rows else None,
        )
    else:
        gb.configure_selection(selection_mode=selection_mode)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)
    gridOptions = gb.build()

    # Displays the DataFrame, event for select
    grid_response = AgGrid(
        df,
        gridOptions=gridOptions,
        update_mode=GridUpdateMode.GRID_CHANGED,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
    )
    
    if selection_mode=="disabled":
        return None
    else:
        selected = grid_response["selected_rows"]
        selected_row_idxs = (
            None if not selected else
            [int(sel["_selectedRowNodeInfo"]["nodeId"]) for sel in selected]
        )
        return (
            None if selected_row_idxs is None else
            original_index[selected_row_idxs]
        )
