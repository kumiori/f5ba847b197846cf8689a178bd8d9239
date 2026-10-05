from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def asset_path(filename, folder):
    base = (ROOT / 'assets' / folder).resolve()
    path = (base / filename).resolve()
    if not path.is_relative_to(base) or not path.is_file():
        raise ValueError(f'Missing or invalid {folder} asset: {filename}')
    return path


def load_content(path=None):
    data = yaml.safe_load((path or ROOT / 'content/scenes.yaml').read_text())
    scenes = data['scenes']
    if data['start'] not in scenes:
        raise ValueError('Start scene missing')
    for sid, scene in scenes.items():
        if scene['id'] != sid:
            raise ValueError(f'Scene id mismatch: {sid}')
        ids = [c['id'] for c in scene.get('choices', [])]
        if len(ids) != len(set(ids)):
            raise ValueError(f'Duplicate choices: {sid}')
        for choice in scene.get('choices', []):
            target = choice.get('transition', scene.get('transition'))
            if target not in scenes:
                raise ValueError(f'Invalid transition: {sid}')
        if scene.get('media'):
            asset_path(scene['media']['file'], 'images')
    tracks = yaml.safe_load((ROOT / 'content/audio.yaml').read_text())['tracks']
    for track in tracks:
        if not all(track.get(k) for k in ('id', 'file', 'title', 'artist', 'credit', 'permission', 'license', 'scene')):
            raise ValueError('Audio metadata incomplete')
        if track['permission'] != 'authorized':
            raise ValueError('Audio must be explicitly authorized')
        asset_path(track['file'], 'audio')
        if track['scene'] not in scenes:
            raise ValueError('Audio scene missing')
    data['audio_tracks'] = tracks
    return data
