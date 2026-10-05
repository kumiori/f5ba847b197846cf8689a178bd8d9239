"""UI-independent, JSON-compatible state and deterministic transitions."""
from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4


def now():
    return datetime.now(timezone.utc).isoformat()


def new_game(content):
    state = dict(schema_version='future-fragment/trajectory-v1', session_id=str(uuid4()),
                 content=deepcopy(content), scene_history=[], choices=[], emotion_opt_in='later',
                 emotion_signals=[], audio_opt_in=False, coordinates={}, player_inputs=[],
                 started_at=now(), current_scene=content['start'], completed_at=None)
    enter(state, content['start'])
    return state


def enter(state, scene_id, reason='transition'):
    if scene_id not in state['content']['scenes']:
        raise ValueError(f'Unknown scene: {scene_id}')
    state['current_scene'] = scene_id
    state['scene_history'].append(dict(scene=scene_id, entered_at=now(), reason=reason))


def act(state, choice_id, answer='', signal=None):
    scene = state['content']['scenes'][state['current_scene']]
    choice = next((c for c in scene.get('choices', []) if c['id'] == choice_id), None)
    if choice is None:
        raise ValueError('Unknown choice')
    answer = answer.strip()
    if scene.get('input', {}).get('required') and not answer:
        raise ValueError('Add a few words to continue.')
    if signal and state['emotion_opt_in'] != 'yes':
        raise ValueError('Emotional input requires consent')
    if signal and signal not in state['content']['emotion_options']:
        raise ValueError('Unknown emotional signal')
    stamp = now()
    visit = len(state['scene_history']) - 1
    state['choices'].append(dict(scene=state['current_scene'], visit=visit, choice=choice_id,
                                 label=choice['label'], at=stamp))
    if answer:
        state['player_inputs'].append(dict(scene=state['current_scene'], visit=visit, text=answer, at=stamp))
        coordinate = scene.get('input', {}).get('coordinate')
        if coordinate:
            state['coordinates'][coordinate] = answer
    if signal:
        state['emotion_signals'].append(dict(scene=state['current_scene'], visit=visit, signal=signal, at=stamp))
    if scene['kind'] == 'emotion_consent':
        state['emotion_opt_in'] = choice['value']
    if scene['kind'] == 'audio_consent':
        state['audio_opt_in'] = choice['value']
    state['scene_history'][-1]['left_at'] = stamp
    target = choice.get('transition', scene.get('transition'))
    if target:
        enter(state, target)
        if state['content']['scenes'][target]['kind'] == 'end':
            state['completed_at'] = stamp


def preference(state, key, value):
    allowed = {'emotion_opt_in': ('yes', 'no', 'later'), 'audio_opt_in': (True, False)}
    if key not in allowed or value not in allowed[key]:
        raise ValueError('Invalid preference')
    state[key] = value
    state.setdefault('preference_history', []).append(dict(key=key, value=value, at=now()))
