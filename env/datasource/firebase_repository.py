import firebase_admin
from firebase_admin import credentials, firestore
from env.config import cert


class FirebaseRepository:

    def __init__(self):
        self.cred = credentials.Certificate(cert)
        firebase_admin.initialize_app(self.cred)
        self.client = firestore.client()

    def getGoods(self):
        goods_ready = []
        goods_colref = self.client.collection(u'goods')
        docs = goods_colref.get()
        for doc in docs:
            goods_ready.append(doc.to_dict())
        return goods_ready

    def addGood(self, good):
        return self.client.collection(u'goods').document().set(good)
