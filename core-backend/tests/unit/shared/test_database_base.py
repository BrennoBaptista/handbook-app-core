import datetime

from sqlalchemy.orm import Mapped, mapped_column

from platform_core.shared.database.base import Base
from platform_core.shared.database.mixins import TimestampMixin


class _SampleModel(Base, TimestampMixin):
    """Modelo de teste — prova que Base + TimestampMixin produzem um
    mapeamento ORM válido, com created_at/updated_at exigidos por toda
    tabela (RA-007, Seção 4)."""

    __tablename__ = "sample_models_for_test"

    id: Mapped[int] = mapped_column(primary_key=True)


def test_timestamp_mixin_should_add_created_at_and_updated_at_columns():
    columns = _SampleModel.__table__.columns

    assert "created_at" in columns
    assert "updated_at" in columns
    assert columns["created_at"].type.python_type is datetime.datetime
    assert columns["updated_at"].type.python_type is datetime.datetime


def test_base_subclass_should_register_in_shared_metadata():
    assert "sample_models_for_test" in Base.metadata.tables
