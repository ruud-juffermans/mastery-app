from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

from shared.storage.models import Base

ALEMBIC_INI = Path(__file__).resolve().parents[1] / "alembic.ini"


def test_single_head_revision():
    script = ScriptDirectory.from_config(Config(str(ALEMBIC_INI)))

    assert len(script.get_heads()) == 1


def test_models_match_migration_tables():
    assert set(Base.metadata.tables) == {"ai_run"}