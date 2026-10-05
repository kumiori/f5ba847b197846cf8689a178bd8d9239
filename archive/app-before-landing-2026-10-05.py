import streamlit as st

if 'test' in st.query_params:
    from presentation.lab import run
    run(st.query_params['test'])
else:
    from presentation.ui import run
    run()
