from pathlib import Path

from backend.main import GoteroState, load_gotero_state, save_gotero_state


def test_gotero_state_survives_reload(tmp_path: Path) -> None:
    # Given
    state_file = tmp_path / "gotero.json"

    # When
    save_gotero_state(GoteroState(pending=25), state_file)

    # Then
    assert load_gotero_state(state_file).pending == 25


def test_backend_reads_pihole_password_from_environment() -> None:
    # Given
    source = Path(__file__).with_name("main.py").read_text(encoding="utf-8")

    # When
    reads_environment = 'PIHOLE_PASSWORD: Final = os.getenv("PIHOLE_PASSWORD", "")' in source

    # Then
    assert reads_environment is True
