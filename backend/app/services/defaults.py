from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.finance import Account, Category, UserFinanceSettings


DEFAULT_ACCOUNTS = [
    ("工资卡", "收入账户"),
    ("生活账户", "支出账户"),
    ("应急金账户", "储蓄账户"),
    ("投资账户", "投资账户"),
    ("快乐消费账户", "消费账户"),
    ("债务还款账户", "债务账户"),
    ("专项准备金账户", "准备金账户"),
]

DEFAULT_CATEGORIES = [
    ("工资", "收入", True, True),
    ("奖金/绩效", "收入", True, False),
    ("副业收入", "收入", True, False),
    ("理财收益", "收入", True, False),
    ("红包/礼金", "收入", True, False),
    ("报销", "收入", True, False),
    ("其他收入", "收入", True, False),
    ("房租/房贷", "必要支出", False, False),
    ("餐饮", "必要支出", False, False),
    ("交通", "必要支出", False, False),
    ("水电通讯", "必要支出", False, False),
    ("医疗", "必要支出", False, False),
    ("应急金", "储蓄投资", False, False),
    ("基金定投", "储蓄投资", False, False),
    ("信用卡/消费贷", "债务还款", False, False),
    ("专项准备金", "专项准备金", False, False),
    ("娱乐", "弹性消费", False, False),
    ("购物", "弹性消费", False, False),
]


def seed_user_defaults(db: Session, user_id: UUID) -> None:
    db.add(
        UserFinanceSettings(
            user_id=user_id,
            salary_min=Decimal("7000.00"),
            salary_max=Decimal("8500.00"),
            conservative_income_base=Decimal("7000.00"),
            necessity_ratio=Decimal("0.5000"),
            saving_ratio=Decimal("0.3000"),
            flex_ratio=Decimal("0.2000"),
            extra_saving_ratio=Decimal("0.7000"),
            extra_reserve_ratio=Decimal("0.2000"),
            extra_flex_ratio=Decimal("0.1000"),
            emergency_months=3,
            monthly_necessity_amount=Decimal("4000.00"),
            plan_year=2026,
        )
    )
    for name, account_type in DEFAULT_ACCOUNTS:
        db.add(Account(user_id=user_id, name=name, account_type=account_type))
    for sort_order, (name, transaction_type, is_income, is_salary) in enumerate(DEFAULT_CATEGORIES):
        db.add(
            Category(
                user_id=user_id,
                name=name,
                transaction_type=transaction_type,
                is_income=is_income,
                is_salary=is_salary,
                sort_order=sort_order,
            )
        )
