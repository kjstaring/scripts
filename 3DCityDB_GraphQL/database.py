
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base, DeferredReflection
from sqlalchemy.orm import scoped_session, sessionmaker

# 1. Connect to the database with the prefixed defined schemas 
dbschema='citydb,public' 
connection = "postgres+psycopg2://postgres:1234@localhost:5432/delfshaven_3DCityDB"
engine = create_engine(connection, connect_args={'options': '-csearch_path={}'.format(dbschema)})

# 2. Create a scoped session, which has a pool of connection to the server, to access the database 
made_session = sessionmaker(autocommit=False, autoflush=True, bind=engine)
db_session = scoped_session(made_session)

# 3. Create a base class from which all mapped classses should inherit 
Base = declarative_base(cls=DeferredReflection)

# 4. This simplifies the queries, because the session object does not have to be called anymore 
Base.query = db_session.query_property()


