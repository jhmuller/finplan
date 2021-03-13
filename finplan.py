
import os
import sys
import datetime
import pandas as pd


def make_month_day_1(date):
    res = datetime.date(date.year, date.month, 1)
    return res


def get_months_between(start_date, end_date):
    num_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
    return num_months


def get_next_month(date):
    next_year = date.year
    next_month = date.month + 1
    if date.month == 12:
        next_month = 1
        next_year = date.year + 1
    next_date = datetime.date(next_year, next_month, 1)
    return next_date


class CashFlow(object):
    def __init__(self,
                 name,
                 start_date,
                 monthly_growth_rate,
                 start_value=0,
                 monthly_value=0,
                 end_date=None):
        self.name = name
        self.start_date = make_month_day_1(start_date)
        self.monthly_growth_rate = monthly_growth_rate
        if end_date is None:
            end_date = datetime.date(2050, 1, 1)
        self.end_date = make_month_day_1(end_date)
        self.start_value = start_value
        self.monthly_value = monthly_value

    def get_name(self):
        return self.name

    def get_values_df(self, end_date):
        vtups = []
        date = self.start_date
        growth_value = self.start_value
        monthly_value = self.monthly_value
        while date < end_date:
            if date > self.end_date:
                break
            tot_value = growth_value + monthly_value
            vtup = (date, tot_value)
            vtups.append(vtup)
            growth_value = growth_value * self.monthly_growth_rate
            monthly_value = monthly_value * self.monthly_growth_rate
            date = get_next_month(date)
        df = pd.DataFrame(vtups)
        df.columns = ["date", self.name]
        return df


class NetValue(object):
    def __init__(self, name, start_date, end_date=None):
        self.name = name
        self.start_date = make_month_day_1(start_date)
        if end_date is None:
            end_date = datetime.date(2050, 1, 1)
        self.end_date = make_month_day_1(end_date)
        self.cash_flows = {}

    def add_cash_flow(self, cf):
        name = cf.get_name()
        if name in self.cash_flows.keys():
            msg = "Error, trying to add 2 cash flows with the same name: {0}".format(name)
            raise ValueError(msg)
        self.cash_flows[name] = cf

    def get_value_df(self, end_date):
        vdf = None
        for name in self.cash_flows.keys():
            cf = self.cash_flows[name]
            df = cf.get_values_df(end_date)
            if vdf is None:
                vdf = df
            else:
                res = vdf.merge(df, on="date", how="outer")
                vdf = res
        vdf.set_index("date")
        vdf["total"] = vdf.sum(axis=1)
        return vdf


if __name__ == "__main__":
    today = datetime.date.today()
    equity = CashFlow(name="equity", start_date=today, start_value = 10**6, monthly_growth_rate=1+.05/12.0)
    bonds = CashFlow(name="bonds", start_date=today, start_value=10**6, monthly_growth_rate=1+.01/12.0)
    income = CashFlow(name="income", start_date=today, monthly_value=50000, monthly_growth_rate=1+.01/12.0)
    expenses = CashFlow(name="expenses", start_date=today, monthly_value=50000, monthly_growth_rate=1+.01/12.0)

    ava_college = CashFlow(name="ava_college", start_date=datetime.date(2025, 9, 1), end_date=datetime.date(2028, 6, 1),
                           monthly_value=-50000, monthly_growth_rate=1)
    NV = NetValue("wealth", start_date=today)
    NV.add_cash_flow(ava_college)
    NV.add_cash_flow(equity)
    NV.add_cash_flow(bonds)
    NV.add_cash_flow(income)
    NV.add_cash_flow(expenses)
    df = NV.get_value_df(end_date=datetime.date(2029, 12,1))
    print(df)
    df.plot(x="date", y="total")
    print(datetime.datetime.now())
