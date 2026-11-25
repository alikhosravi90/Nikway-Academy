from pathlib import Path
from alembic.config import Config
from alembic import command
if __name__ == '__main__':
    command.upgrade(Config(str(Path(__file__).parents[1] / 'alembic.ini')), 'head')
