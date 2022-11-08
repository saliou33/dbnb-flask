from main import app, db, migrate
from api.models.demandeurs import Demandeur
from api.models.users import User
from api.models.groupes import Groupe
from api.models.qrcodes import Qrcode

@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, migrate=migrate, User=User, Demandeur=Demandeur, Groupe=Groupe, Qrcode=Qrcode)
