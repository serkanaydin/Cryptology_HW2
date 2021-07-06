from pony import orm
from pony.orm import Database, db_session, StrArray, IntArray

db = Database()
db.bind(provider='sqlite', filename="cryptology.db", create_db=True)


class Client(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    username = orm.Required(str)
    public_key = orm.Required(str)
    certificate = orm.Required(str)


class Image(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    name = orm.Required(str)
    mode = orm.Required(str)
    size = orm.Required(str)
    encrypted_image = orm.Required(str)
    uploader_name = orm.Required(str)
    iv = orm.Required(StrArray)
    aes = orm.Required(StrArray)
    digest = orm.Required(IntArray)


db.generate_mapping(create_tables=True)


@db_session()
def insert_user(username, public_key, certificate):
    client = Client(username=username, public_key=public_key, certificate=certificate)


@db_session
def delete_user(username):
    Client.select(lambda c: c.username == username).delete(bulk=True)


@db_session
def get_user(username):
    user = Client.get(lambda c: c.username == username)
    return user

@db_session
def update_user(username,public_key,certificate):
    user = Client.get(lambda c: c.username == username)
    user.set(public_key=public_key,certificate=certificate)



@db_session
def insert_image(name, mode, size, encrypted_image, uploader_name, aes, iv, digest):
    image = Image(name=name, mode=mode, size=size, encrypted_image=encrypted_image,
                  uploader_name=uploader_name, aes=aes, iv=iv, digest=digest)
