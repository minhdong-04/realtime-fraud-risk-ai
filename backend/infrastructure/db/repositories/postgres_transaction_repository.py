"""
{
    module : postgres_transaction_repository.py
    desc   : Cài đặt thực tế của ITransactionRepository bằng SQLAlchemy / Postgres.
}
"""

from uuid import UUID
from sqlalchemy.orm import Session
from backend.domain.entities.transaction import Transaction, TransactionType, TransactionChannel, TransactionStatus
from backend.domain.repositories.i_transaction_repository import ITransactionRepository
from backend.infrastructure.db.models.orm_models import TransactionORM

class PostgresTransactionRepository(ITransactionRepository):
    """
    {
        class  : PostgresTransactionRepository
        desc   : Lớp Repository tương tác với cơ sở dữ liệu cho thực thể Transaction
        pattern: Repository Pattern
    }
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def save(self, transaction: Transaction) -> Transaction:
        """
        {
            func   : save
            desc   : Lưu thông tin thực thể giao dịch vào bảng dữ liệu SQL
            input  : transaction (Transaction)
            output : Transaction
            loop   : 0 loops
        }
        """
        existing = self._db.query(TransactionORM).filter_by(id=str(transaction.id)).first()
        if existing:
            existing.status = transaction.status.value
            existing.scored_at = transaction.scored_at
        else:
            orm = TransactionORM(
                id=str(transaction.id),
                transaction_id=transaction.transaction_id,
                account_id=str(transaction.account_id),
                merchant_id=str(transaction.merchant_id),
                device_id=str(transaction.device_id) if transaction.device_id else None,
                amount=transaction.amount,
                currency=transaction.currency,
                transaction_type=transaction.transaction_type.value,
                channel=transaction.channel.value,
                status=transaction.status.value,
                created_at=transaction.created_at,
                scored_at=transaction.scored_at,
            )
            self._db.add(orm)

        self._db.commit()
        return transaction

    def find_by_transaction_id(self, transaction_id: str) -> Transaction | None:
        """
        {
            func   : find_by_transaction_id
            desc   : Truy vấn giao dịch theo mã định danh bên ngoài transaction_id
            input  : transaction_id (str)
            output : Transaction | None
            loop   : 0 loops
        }
        """
        orm = self._db.query(TransactionORM).filter_by(transaction_id=transaction_id).first()
        if not orm:
            return None
        return self._to_domain(orm)

    def find_by_account_id(self, account_id: UUID, limit: int = 50) -> list[Transaction]:
        """
        {
            func   : find_by_account_id
            desc   : Truy vấn lịch sử giao dịch gần đây của tài khoản
            input  : account_id (UUID), limit (int)
            output : list[Transaction]
            loop   : 1 loop — chuyển đổi các bản ghi ORM thành các thực thể Domain
        }
        """
        rows = (
            self._db.query(TransactionORM)
            .filter_by(account_id=str(account_id))
            .order_by(TransactionORM.created_at.desc())
            .limit(limit)
            .all()
        )
        # { loop-1: chuyển đổi từng bản ghi ORM thành thực thể Transaction }
        return [self._to_domain(row) for row in rows]

    def _to_domain(self, orm: TransactionORM) -> Transaction:
        """
        {
            func   : _to_domain
            desc   : Chuyển đổi TransactionORM sang thực thể Domain Transaction
            input  : orm (TransactionORM)
            output : Transaction
            loop   : 0 loops
        }
        """
        return Transaction(
            id=UUID(orm.id),
            transaction_id=orm.transaction_id,
            account_id=UUID(orm.account_id),
            merchant_id=UUID(orm.merchant_id),
            device_id=UUID(orm.device_id) if orm.device_id else None,
            amount=orm.amount,
            currency=orm.currency,
            transaction_type=TransactionType(orm.transaction_type),
            channel=TransactionChannel(orm.channel),
            status=TransactionStatus(orm.status),
            created_at=orm.created_at,
            scored_at=orm.scored_at,
        )
