import base64
import html
import json
import mimetypes
import os
import streamlit as st
import streamlit.components.v1 as components
import yaml
from game.content import ROOT, asset_path, load_content
from game.engine import act, enter, new_game, preference

component = components.declare_component('opening_media', path=str(ROOT / 'presentation/component'))


def downloads(state, prefix):
    st.download_button('Export JSON', json.dumps(state, indent=2, ensure_ascii=False),
                       f"trajectory-{state['session_id']}.json", 'application/json', key=f'{prefix}_json')
    st.download_button('Export YAML', yaml.safe_dump(state, allow_unicode=True, sort_keys=False),
                       f"trajectory-{state['session_id']}.yaml", 'application/yaml', key=f'{prefix}_yaml')


def run():
    st.set_page_config(page_title='HERE / THERE', page_icon='↯', layout='centered')
    theme = yaml.safe_load((ROOT / 'content/theme.yaml').read_text())
    st.markdown(f'''<style>
    .stApp {{background:{theme['background']};color:{theme['foreground']};font-family:{theme['font']}}}
    .block-container {{max-width:{theme['width']}px;padding-top:3rem;padding-bottom:4rem}}
    h1,h2,h3,p,button,textarea,input,label {{font-family:{theme['font']} !important}}
    .stVerticalBlock {{gap:{theme['spacing']}rem}}
    .fragment {{border-left:2px solid {theme['accent']};padding-left:1rem;color:{theme['muted']};font-size:.85rem}}
    .interruption {{color:{theme['accent']};transform:translateX({theme['glitch_intensity']}px);letter-spacing:.04em}}
    .player {{border:1px solid {theme['muted']};padding:1rem;white-space:pre-wrap}}
    .stButton button,.stDownloadButton button {{border-radius:0}}
    </style>''', unsafe_allow_html=True)
    if 'game' not in st.session_state:
        st.session_state.game = new_game(load_content())
    state = st.session_state.game
    content = state['content']
    if os.getenv('GAME_MODE', 'play') in ('local', 'test'):
        with st.sidebar:
            st.caption('DEVELOPER / LOCAL ONLY')
            st.write('Current scene:', state['current_scene'])
            st.json(state)
            st.write('Scene history', state['scene_history'])
            target = st.selectbox('Jump to scene', list(content['scenes']))
            if st.button('Jump'):
                enter(state, target, 'developer_jump')
                st.rerun()
            if st.button('Reset game'):
                st.session_state.game = new_game(load_content())
                st.rerun()
            downloads(state, 'debug')
    st.caption('HERE / THERE       •       A POSSIBLE FUTURE')
    # The same keyed component stays mounted across scenes; native audio controls
    # supply seek, play/pause and volume. No audio data enters the UI before consent.
    with st.expander('Experience settings', expanded=False):
        e = st.selectbox('Emotions', ['later', 'yes', 'no'],
                         index=['later', 'yes', 'no'].index(state['emotion_opt_in']),
                         format_func=lambda x: {'later':'Maybe later', 'yes':'Enabled', 'no':'Disabled'}[x])
        a = st.checkbox('Enable sound', value=state['audio_opt_in'])
        if e != state['emotion_opt_in']:
            preference(state, 'emotion_opt_in', e)
        if a != state['audio_opt_in']:
            preference(state, 'audio_opt_in', a)
        instant = st.checkbox('Show text immediately', value=False)
        st.caption('This session lives in this browser connection. Export before leaving. No account or server-side saving.')
    if state['audio_opt_in']:
        tracks = content['audio_tracks']
        eligible = [t for t in tracks if t['scene'] in [h['scene'] for h in state['scene_history']]]
        if eligible:
            track = eligible[-1]
            path = asset_path(track['file'], 'audio')
            src = f"data:{mimetypes.guess_type(path.name)[0] or 'audio/mpeg'};base64," + base64.b64encode(path.read_bytes()).decode()
            component(mode='audio', theme=theme, track_id=track['id'], src=src,
                      title=track['title'], credit=f"{track['title']} — {track['artist']} · {track['credit']} · {track['license']}", key='soundtrack')
        else:
            st.caption('SOUND ENABLED / No authorised soundtrack loaded for this scene.')
    scene = content['scenes'][state['current_scene']]
    visit = len(state['scene_history'])
    st.caption(f"TRANSMISSION {visit:02d}")
    if scene.get('fragment'):
        st.markdown(f'<div class="fragment">{html.escape(scene["fragment"])}</div>', unsafe_allow_html=True)
    component(mode='text', theme=theme, identity=f'{state["session_id"]}-{visit}-{instant}',
              text=scene['text'], speed=0 if instant else theme['text_speed_ms'], key='scene_text')
    if scene.get('media'):
        st.image(str(asset_path(scene['media']['file'], 'images')), caption=scene['media'].get('alt', ''))
    if scene.get('interruption'):
        st.markdown(f'<div class="interruption">↯ {html.escape(scene["interruption"])}</div>', unsafe_allow_html=True)
    if state['emotion_opt_in'] == 'yes' and state['emotion_signals']:
        st.caption(f"You signalled: {state['emotion_signals'][-1]['signal']}. There is no required way to feel here.")
    st.subheader(scene.get('question', ''))
    if scene['id'] == 'intervention' and state['player_inputs']:
        st.caption('YOUR PROPOSED TURNING POINT')
        st.markdown(f'<div class="player">{html.escape(state["player_inputs"][-1]["text"])}</div>', unsafe_allow_html=True)
    if scene['kind'] == 'end':
        for item in state['player_inputs']:
            st.caption(content['scenes'][item['scene']]['input']['label'])
            st.markdown(f'<div class="player">{html.escape(item["text"])}</div>', unsafe_allow_html=True)
        st.caption('Your export includes the scene text, choices, coordinates, optional emotional signals and timestamps.')
        downloads(state, 'end')
        return
    with st.form(f'scene_{visit}', clear_on_submit=False):
        answer = ''
        if scene.get('input'):
            field = scene['input']
            answer = st.text_area(field['label'], placeholder=field.get('placeholder', ''), max_chars=4000)
        signal = None
        if state['emotion_opt_in'] == 'yes' and scene.get('emotion'):
            signal = st.selectbox('Optional: how does this feel?', [None] + content['emotion_options'], format_func=lambda x: x or 'Prefer not to say')
        for choice in scene['choices']:
            if st.form_submit_button(choice['label']):
                try:
                    act(state, choice['id'], answer, signal)
                except ValueError as exc:
                    st.error(str(exc))
                else:
                    st.rerun()
