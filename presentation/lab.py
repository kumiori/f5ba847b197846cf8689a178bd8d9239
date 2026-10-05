"""Isolated visual experiments; never read or mutate game state."""
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

LABS = {
    'text-scroller': ('Text scroller', 'Scroll-spy timeline · local interpretation', 'https://codepen.io/editor/Maseone/pen/019ec283-e15f-754e-9e21-8f345fc2f4df'),
    'radial-controller': ('Radial controller', 'Circular scroll navigation · local interpretation', 'https://codepen.io/editor/cbolson/pen/01a0a174-adfe-709e-8d70-a053acf0527e'),
    'css-glitch': ('CSS glitch', 'Supplied skew keyframes and RGB shadows · local adaptation', None),
}


def run(page):
    st.set_page_config(page_title='HERE / THERE · Experiments', layout='wide')
    st.caption('HERE / THERE    /    VISUAL TESTS')
    st.markdown('[Game](/?view=game) · [All tests](/?test=index) · [Text scroller](/?test=text-scroller) · [Radial controller](/?test=radial-controller) · [CSS glitch](/?test=css-glitch)')
    if page not in LABS:
        st.title('Interaction studies')
        st.write('Separate specimens for visual review. These controls do not affect the game or its trajectory.')
        for slug, (title, description, _) in LABS.items():
            st.markdown(f'### [{title}](/?test={slug})\n{description}')
        return
    title, description, source = LABS[page]
    st.title(title)
    st.caption(description)
    if source:
        st.markdown(f'[Reference]({source}) · Source files could not be retrieved; this is not an exact reproduction.')
    components.html((Path(__file__).parent / 'labs' / f'{page}.html').read_text(), height=780, scrolling=True)
