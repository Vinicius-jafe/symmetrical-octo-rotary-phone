from ui.login import start_app
from core import banco

if __name__ == '__main__':
    banco.criar_tabelas()
    banco.seed_defaults()
    start_app()
