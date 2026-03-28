from django.db.models import Sum
from django.utils import timezone

from apps.accounts.models import Account
from apps.assets.models import Asset
from apps.goals.models import Goal
from apps.liabilities.models import Liability
from apps.transactions.models import Transaction

from .models import FlowRecord


def get_net_worth(user) -> dict:
    """计算净资产 = 总资产 - 总负债"""
    total_assets = Asset.objects.filter(
        user=user, is_deleted=False
    ).aggregate(total=Sum('current_value'))['total'] or 0

    total_liabilities = Liability.objects.filter(
        user=user, is_deleted=False
    ).aggregate(total=Sum('remaining_amount'))['total'] or 0

    account_balance = Account.objects.filter(
        user=user, is_deleted=False
    ).aggregate(total=Sum('balance'))['total'] or 0

    return {
        'total_assets': str(total_assets + account_balance),
        'total_liabilities': str(total_liabilities),
        'net_worth': str(total_assets + account_balance - total_liabilities),
    }


def get_monthly_summary(user, year: int, month: int) -> dict:
    """获取指定月份收支汇总"""
    base_qs = Transaction.objects.filter(
        user=user,
        transaction_date__year=year,
        transaction_date__month=month,
        is_deleted=False,
    )
    income = base_qs.filter(transaction_type='income').aggregate(total=Sum('amount'))['total'] or 0
    expense = base_qs.filter(transaction_type='expense').aggregate(total=Sum('amount'))['total'] or 0
    return {
        'year': year,
        'month': month,
        'income': str(income),
        'expense': str(expense),
        'balance': str(income - expense),
    }


def get_yearly_summary(user, year: int) -> list:
    """获取指定年份全年各月收支汇总"""
    result = []
    for month in range(1, 13):
        result.append(get_monthly_summary(user, year, month))
    return result


def get_expense_by_category(user, year: int, month: int) -> list:
    """获取指定月份各分类支出"""
    qs = Transaction.objects.filter(
        user=user,
        transaction_type='expense',
        transaction_date__year=year,
        transaction_date__month=month,
        is_deleted=False,
    ).values('category').annotate(total=Sum('amount')).order_by('-total')
    return [{'category': item['category'], 'amount': str(item['total'])} for item in qs]


def get_flow_records(user, year: int | None = None, month: int | None = None):
    qs = FlowRecord.objects.filter(user=user, is_deleted=False)
    if year:
        qs = qs.filter(flow_date__year=year)
    if month:
        qs = qs.filter(flow_date__month=month)
    return qs


def create_flow_record(user, validated_data: dict) -> FlowRecord:
    return FlowRecord.objects.create(user=user, **validated_data)


def delete_flow_record(record: FlowRecord) -> None:
    record.is_deleted = True
    record.save(update_fields=['is_deleted', 'updated_at'])


def get_flow_graph(user, year: int | None = None, month: int | None = None) -> dict:
    records = get_flow_records(user, year=year, month=month)

    node_map: dict[str, dict] = {}
    link_map: dict[tuple[str, str], dict] = {}

    for r in records:
        src_id = f'{r.source_type}:{r.source_name}'
        dst_id = f'{r.target_type}:{r.target_name}'

        if src_id not in node_map:
            node_map[src_id] = {
                'id': src_id,
                'label': r.source_name,
                'type': r.source_type,
                'value': 0,
            }
        if dst_id not in node_map:
            node_map[dst_id] = {
                'id': dst_id,
                'label': r.target_name,
                'type': r.target_type,
                'value': 0,
            }

        node_map[src_id]['value'] += float(r.amount)
        node_map[dst_id]['value'] += float(r.amount)

        key = (src_id, dst_id)
        if key not in link_map:
            link_map[key] = {
                'source': src_id,
                'target': dst_id,
                'amount': 0.0,
                'label': '',
            }
        link_map[key]['amount'] += float(r.amount)

    links = []
    for item in link_map.values():
        item['label'] = f"¥{item['amount']:,.2f}"
        links.append(item)

    total_income = sum(float(n['value']) for n in node_map.values() if n['type'] == 'income')
    total_expense = sum(float(n['value']) for n in node_map.values() if n['type'] == 'expense')
    total_flow = sum(float(l['amount']) for l in links)

    return {
        'nodes': list(node_map.values()),
        'links': links,
        'summary': {
            'income': total_income,
            'expense': total_expense,
            'flow': total_flow,
        },
    }


def get_heatmap_data(user, year: int, mode: str = 'expense') -> list:
    qs = Transaction.objects.filter(
        user=user,
        transaction_date__year=year,
        is_deleted=False,
    )

    inc_qs = qs.filter(transaction_type='income').values('transaction_date').annotate(total=Sum('amount'))
    exp_qs = qs.filter(transaction_type='expense').values('transaction_date').annotate(total=Sum('amount'))

    inc_map = {str(i['transaction_date']): float(i['total']) for i in inc_qs}
    exp_map = {str(i['transaction_date']): float(i['total']) for i in exp_qs}

    all_dates = sorted(set(inc_map.keys()) | set(exp_map.keys()))
    data = []
    for d in all_dates:
        inc = inc_map.get(d, 0.0)
        exp = exp_map.get(d, 0.0)
        if mode == 'income':
            val = inc
        elif mode == 'net':
            val = inc - exp
        else:
            val = exp
        data.append({'date': d, 'value': val})
    return data


def get_asset_network(user) -> dict:
    nodes = [{'id': 'user:self', 'label': '我', 'category': 'user', 'value': 1, 'sub': ''}]
    links = []

    accounts = Account.objects.filter(user=user, is_deleted=False)
    assets = Asset.objects.filter(user=user, is_deleted=False)
    liabilities = Liability.objects.filter(user=user, is_deleted=False)
    goals = Goal.objects.filter(user=user, is_deleted=False)

    for a in accounts:
        node_id = f'account:{a.id}'
        nodes.append({'id': node_id, 'label': a.name, 'category': 'account', 'value': float(a.balance), 'sub': f'¥{a.balance:,.2f}'})
        links.append({'source': 'user:self', 'target': node_id, 'label': '账户', 'strength': 0.8})

    for a in assets:
        node_id = f'asset:{a.id}'
        nodes.append({'id': node_id, 'label': a.name, 'category': 'asset', 'value': float(a.current_value), 'sub': f'¥{a.current_value:,.2f}'})
        links.append({'source': 'user:self', 'target': node_id, 'label': '资产', 'strength': 0.5})

    for l in liabilities:
        node_id = f'liability:{l.id}'
        nodes.append({'id': node_id, 'label': l.name, 'category': 'liability', 'value': float(l.remaining_amount), 'sub': f'-¥{l.remaining_amount:,.2f}'})
        links.append({'source': 'user:self', 'target': node_id, 'label': '负债', 'strength': 0.5})

    for g in goals:
        node_id = f'goal:{g.id}'
        progress = 0.0 if g.target_amount == 0 else float(g.current_amount / g.target_amount * 100)
        nodes.append({'id': node_id, 'label': g.name, 'category': 'goal', 'value': float(g.target_amount), 'sub': f'{progress:.0f}%'})
        links.append({'source': 'user:self', 'target': node_id, 'label': '目标', 'strength': 0.4})

    records = get_flow_records(user, year=timezone.now().year)
    account_name_to_id = {a.name: f'account:{a.id}' for a in accounts}
    for r in records:
        src = account_name_to_id.get(r.source_name)
        dst = account_name_to_id.get(r.target_name)
        if src and dst and src != dst:
            links.append({'source': src, 'target': dst, 'label': '流转', 'strength': 0.35})

    return {'nodes': nodes, 'links': links}
