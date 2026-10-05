import streamlit as st

if 'test' in st.query_params:
    from presentation.lab import run
    run(st.query_params['test'])
elif st.query_params.get('view') == 'game':
    from presentation.ui import run
    run()
else:
    st.set_page_config(page_title='fallacia suppositionis', layout='wide', initial_sidebar_state='collapsed')
    st.markdown('''
<style>
.stApp { background: #101211; color: #f0f2e9; }
header[data-testid="stHeader"], [data-testid="stToolbar"],
[data-testid="stDecoration"], #MainMenu, footer { display: none; }
.block-container { padding: 0 1.5rem; max-width: none; }
.landing {
    min-height: 100svh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    font-family: 'Courier New', monospace;
}
.landing h1 {
    font-family: inherit;
    font-size: clamp(1.4rem, 5vw, 3.5rem);
    font-weight: 400;
    line-height: 1.2;
    letter-spacing: -0.04em;
    margin: 0;
    padding: 0;
    color: #f0f2e9;
}
.landing p {
    font-family: inherit;
    font-size: 0.9rem;
    line-height: 1.5;
    margin: 1.5rem 0 0;
    color: #b8bdb2;
}
</style>
<main class="landing">
    <h1>fallacia suppositionis</h1>
    <p>online soon</p>
</main>
''', unsafe_allow_html=True)
