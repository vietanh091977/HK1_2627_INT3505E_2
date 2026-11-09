from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Extensions are initialized by the application factory.
db = SQLAlchemy()
migrate = Migrate()
