import json
import unittest
import yaml
from game.content import ROOT, load_content
from game.engine import act, enter, new_game, preference


class EngineTests(unittest.TestCase):
    def test_complete_trajectory_is_self_contained_and_serializable(self):
        state = new_game(load_content())
        for choice, answer in [('enter',''), ('look',''), ('whose',''), ('no',''), ('no',''),
                               ('set','2026: summers feel different'), ('locate','A coastal town; working outside'),
                               ('access',''), ('propose','Residents opened public buildings overnight'),
                               ('intervene','I would ask our library to trial a cool room; staffing is a difficulty')]:
            act(state, choice, answer)
        self.assertEqual(state['current_scene'], 'end')
        self.assertEqual(len(state['scene_history']), 11)
        self.assertEqual(len(state['choices']), 10)
        self.assertEqual(len(state['player_inputs']), 4)
        self.assertEqual(state['emotion_signals'], [])
        self.assertFalse(state['audio_opt_in'])
        self.assertTrue(state['completed_at'])
        self.assertEqual(json.loads(json.dumps(state)), state)
        self.assertEqual(yaml.safe_load(yaml.safe_dump(state)), state)

    def test_consent_required_and_revocable(self):
        state = new_game(load_content())
        enter(state, 'time')
        with self.assertRaises(ValueError):
            act(state, 'set', '2026', 'Curious')
        self.assertEqual(state['choices'], [])
        preference(state, 'emotion_opt_in', 'yes')
        act(state, 'set', '2026', 'Curious')
        self.assertEqual(state['emotion_signals'][0]['signal'], 'Curious')
        preference(state, 'emotion_opt_in', 'no')
        self.assertEqual(state['emotion_opt_in'], 'no')

    def test_empty_required_answer_does_not_transition(self):
        state = new_game(load_content())
        enter(state, 'time')
        with self.assertRaises(ValueError):
            act(state, 'set', '  ')
        self.assertEqual(state['current_scene'], 'time')
        self.assertEqual(state['choices'], [])

    def test_unknown_choice_and_scene_rejected(self):
        state = new_game(load_content())
        with self.assertRaises(ValueError):
            act(state, 'missing')
        with self.assertRaises(ValueError):
            enter(state, 'missing')


class StreamlitTests(unittest.TestCase):
    def game_app(self):
        from streamlit.testing.v1 import AppTest
        app = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=20)
        app.query_params['view'] = 'game'
        return app.run()

    def test_silent_playthrough_and_export(self):
        from streamlit.testing.v1 import AppTest
        app = self.game_app()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.sidebar), 0)
        labels = ['ENTER', 'Stay with the fragment', 'Whose future is this?', 'NO',
                  'Continue in silence', 'Establish contact', 'Fix these coordinates',
                  'Who gets access?', 'Place this turning point on the path', 'Commit this possibility']
        for label in labels:
            if app.text_area:
                app.text_area[0].input('A possible change, rooted in my present.')
            next(b for b in app.button if b.label == label).click().run()
            self.assertFalse(app.exception)
        self.assertEqual(app.session_state['game']['current_scene'], 'end')
        self.assertEqual(len(app.get('download_button')), 2)
        self.assertFalse(app.session_state['game']['audio_opt_in'])

    def test_emotion_consent_persists_and_debug_is_opt_in(self):
        from streamlit.testing.v1 import AppTest
        from unittest.mock import patch
        with patch.dict('os.environ', {'GAME_MODE':'test'}):
            app = self.game_app()
            self.assertFalse(app.exception)
            self.assertGreater(len(app.sidebar), 0)
        app = self.game_app()
        for label in ['ENTER', 'Stay with the fragment', 'What happened?', 'YES', 'Enable sound']:
            next(b for b in app.button if b.label == label).click().run()
        self.assertEqual(app.session_state['game']['emotion_opt_in'], 'yes')
        self.assertTrue(app.session_state['game']['audio_opt_in'])
        self.assertTrue(any(s.label == 'Optional: how does this feel?' for s in app.selectbox))


if __name__ == '__main__':
    unittest.main()
