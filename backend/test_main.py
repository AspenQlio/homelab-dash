from pathlib import Path

from backend.main import GoteroState, load_gotero_state, save_gotero_state


def test_gotero_state_survives_reload(tmp_path: Path) -> None:
    # Given
    state_file = tmp_path / "gotero.json"

    # When
    save_gotero_state(GoteroState(pending=25), state_file)

    # Then
    assert load_gotero_state(state_file).pending == 25


def test_backend_source_does_not_contain_pihole_password() -> None:
    # Given
    source = Path(__file__).with_name("main.py").read_text(encoding="utf-8")

    # When
    contains_previous_secret = "2468Diez" in source

    # Then
    assert contains_previous_secret is False
