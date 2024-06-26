from typing import List
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker
from domain.entities.Account import Account
from domain.entities.Tag import Tag
from domain.repositories.IDatabaseRepository import IDatabaseRepository
from .model.Account import Account as AccountModel
from .model.Tag import Tag as TagModel
from utils.with_retry import with_retry
import os

accounts = None
tags = None
class SQLAlchemyAdapter(IDatabaseRepository):
    session: sessionmaker = None
    engine: Engine = None

    @with_retry(retries=10, backoff=20)
    def __connect(self):
        try:
            if self.session is None:
                self.engine = create_engine(
                    os.getenv("DATABASE_URI"), pool_size=2, pool_recycle=200
                )
                Session = sessionmaker(bind=self.engine)

                self.session = Session()
        except Exception as e:
            raise e

    def __disconnect(self):
        self.session.close()
        self.session = None
        self.engine = None

    def create_account(self, account: Account) -> Account:
        self.__connect()
        accountModel = account.dict()
        newAccount = AccountModel(**accountModel)
        self.session.add(newAccount)
        self.session.commit()
        self.session.close()
        self.__disconnect()
        return account

    @with_retry(retries=2, backoff=30)
    def get_all_accounts(self) -> List[Account]:
        global accounts
        if accounts is None:
            self.__connect()
            accounts = self.session.query(AccountModel).all()
            self.__disconnect()
        return [Account.from_orm(account) for account in accounts]

    def find_account_by_id(self, id: int) -> Account:
        self.__connect()
        account = self.session.query(AccountModel).filter_by(id=id).first()
        self.__disconnect()
        return Account.from_orm(account)

    def create_tag(self, tag: Tag) -> Tag:
        self.__connect()
        tagModel = tag.dict()
        newTag = TagModel(**tagModel)
        self.session.add(newTag)
        self.session.commit()
        self.session.close()
        self.__disconnect()
        return tag

    @with_retry(retries=2, backoff=30)
    def get_all_tags(self) -> List[Tag]:
        global tags
        if tags is None:
            self.__connect()
            tags = self.session.query(TagModel).all()
            self.__disconnect()
        return [Tag.from_orm(tag) for tag in tags]

    def find_tag(self, tag: str) -> Tag:
        self.__connect()
        tag = self.session.query(TagModel).filter_by(tag=tag).first()
        self.__disconnect()
        return Tag.from_orm(tag)
