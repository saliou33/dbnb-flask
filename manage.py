from main import app, db, migrate
from api.models.demandeurs import Demandeur
from api.models.users import User
from api.models.groupes import Groupe
from api.models.qrcodes import Qrcode


def create_user(user):
    user.password = User.generate_hash(user.password)
    db.session.add(user)
    db.session.commit()


@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, migrate=migrate, User=User, Demandeur=Demandeur, Groupe=Groupe, Qrcode=Qrcode, create_user=create_user)
