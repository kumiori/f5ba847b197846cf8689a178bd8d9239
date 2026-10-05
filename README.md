# HERE / THERE — opening experiment

Codename: IASEAI.

A small Streamlit state machine for the first 3–5 minutes of a speculative game. Copy is provisional. The sequence ends at the first player intervention. Actual duration and emotional response need a human playtest.

## Run

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/streamlit run app.py
```

Ordinary play has no developer sidebar. For local inspection only:

```sh
GAME_MODE=local .venv/bin/streamlit run app.py
```

The developer sidebar provides state inspection, scene history, jump, reset and JSON/YAML export. Do not set `GAME_MODE=local` or `test` on a public deployment. Debug jumps are marked in history.

## Boundaries

- `content/scenes.yaml`: scene IDs, narrative, voice fragments, questions, choices, transitions and input definitions. Each choice can override a scene's default `transition`.
- `game/engine.py`: UI-independent state, consent and transitions. No Streamlit dependency.
- `game/content.py`: YAML loading and local asset/transition validation.
- `presentation/`: Streamlit UI, theme application, streamed text and persistent native audio component.
- `content/theme.yaml`: typography, spacing, palette, static glitch offset and milliseconds per character. Use zero text speed to disable streaming. Player settings also support immediate text.
- `assets/{images,audio,typography,fragments,references}/`: supplied assets. No generated imagery or third-party music is bundled.

A scene can use `media: {file: example.png, alt: Description}` for one image relative to `assets/images`. Audio is linked by scene in `content/audio.yaml`. Add the documented metadata and set `permission: authorized` only after permission has been established; provide the actual permission/license context in `credit` and `license`. Tracks persist into subsequent scenes until another track becomes eligible. Native controls provide play/pause, seeking/progress and volume. Playback always requires pressing play; consent alone never starts sound. Disabling sound removes the player. There is no soundtrack in this build.

Text streams in a small local component with immediate completion, a screen-reader text alternative and reduced-motion support. Other voices remain visible immediately. No animation blocks navigation. The audio iframe remains keyed across scene transitions, so an unchanged track is not recreated on normal rerenders. Playback position is ephemeral and is not part of the trajectory.

## State and exports

`st.session_state.game` holds a JSON-compatible trajectory, including UUID, timestamps, current scene, scene visits, choices, separate optional emotional signals, consent values, coordinates, player inputs and a snapshot of content. End-screen JSON/YAML downloads contain the complete trajectory. Data lives only in session memory until the player downloads it; browser reconnection/server restart may lose it. Exports can contain personal material typed by the player. No authentication, database, analytics or external services are used.

Consent can be changed in Experience settings. Turning emotion off prevents new signals; previously volunteered signals remain in the export. Optional emotional input only acknowledges the player's explicit selection; it does not infer feelings or rewrite the narrative. No automatic replay UI is implemented, but the ordered visits and content snapshot preserve the material needed to build one later.

## Check

```sh
.venv/bin/python -m unittest discover -s tests -v
```

Tests exercise the full engine trajectory, serialisation, invalid transitions, required input, emotion consent, silent Streamlit play, exports and the developer-mode gate. Browser-level text/audio behaviour and timing with unfamiliar players should be checked separately. For authorised audio QA, add a local track and verify pause/resume, seeking, volume, continuity between scenes and withdrawal of consent.

## Visual test pages

These are isolated from the narrative and game session. Open manually:

- `/?test=index` — test directory
- `/?test=text-scroller` — scroll-spy text timeline, adjustable type size and snap
- `/?test=radial-controller` — circular navigation synchronised with a scrollable record
- `/?test=css-glitch` — supplied skew/RGB effect with editable text, typography and duration

The CodePen editor pages exposed titles but not source through HTTP, so the first two are local interpretations, not exact reproductions. References are linked on each page. HTML/CSS/JS specimens live in `presentation/labs/`; `presentation/lab.py` only hosts them. The glitch specimen uses the supplied keyframes and shadows, unprefixed for modern browsers, and replaces sustained hover distortion with a finite burst. It optionally fetches the supplied Google Fonts, with local fallbacks. All three support reduced motion and keyboard interaction. No browser was launched for this implementation; visual review is pending.

## Public landing

The root URL shows only “fallacia suppositionis” / “online soon”. The opening prototype is at `/?view=game`; visual tests retain their `/?test=…` URLs. These routes are accessible to anyone who knows the URL. The previous entry point is archived at `archive/app-before-landing-2026-10-05.py`.
