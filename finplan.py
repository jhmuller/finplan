
import sys
import os
import warnings
import datetime
import subprocess
import inspect
import traceback
from collections import OrderedDict
from collections import namedtuple
import numpy as np
import pandas as pd


class Utilities(object):
    def __init__(self):
        pass

    colors_txt = OrderedDict()
    colors_txt['black'] = "\033[90m"
    colors_txt['red'] = "\033[91m"
    colors_txt["green"] = "\033[92m"
    colors_txt["yellow"] = "\033[93m"
    colors_txt["blue"] = "\033[94m"
    colors_txt["gray"] = "\033[97m"

    colors_bg = OrderedDict()
    colors_bg['black'] = "\033[100m"
    colors_bg["red"] = "\033[101m"
    colors_bg["green"] = "\033[102m"
    colors_bg["yellow"] = "\033[103m"
    colors_bg["blue"] = "\033[104m"
    colors_bg["gray"] = "\033[107m"
    colors_bg["none"] = "\033[107m"

    txt_effects = OrderedDict()
    txt_effects["end"] = "\033[0m"
    txt_effects["bold"] = "\033[1m"
    txt_effects["underline"] = "\033[4m"
    txt_effects["blackback"] = "\033[7m"

    @staticmethod
    def username():
        return os.getenv("USERNAME")

    @staticmethod
    def os_whoami():
        proc = subprocess.Popen(['whoami'], stdout=subprocess.PIPE)
        out, errs = proc.communicate()
        return out

    @staticmethod
    def now():
        return datetime.datetime.now()

    @staticmethod
    def nowshortstr(fmt="%Y%m%d_%H%M%S"):
        return datetime.datetime.now().strftime(fmt)

    @staticmethod
    def nowstr(fmt="%Y-%m-%d__%H_%M_%S"):
        return datetime.datetime.now().strftime(fmt)

    @staticmethod
    def color_str(s, txt_color='black', bg_color=None,
                  bold=False, underline=False,
                  verbosity=0):
        """
        embedd hex codes for color or effects

        Parameters
        ----------
        s: srting to be enhanced
        txt_color: color for text.  e.g. black, red, green, blue
        bg_color: background color
        bold: boolean
        underline: boolean
        verbosity: level of diagnostics

        Returns
        -------
        string with original and enhancements at the start
        """
        if verbosity > 0:
            print("{0} <{1}>".format(Utilities.whoami(), Utilities.now()))
        if not isinstance(s, str):
            msg0 = "input s must be string, got {0}".format(type(s))
            msg0 += "trying to convert to string"
            msg = Utilities.color_str(msg0, txt_color="red")
            print(msg)
        try:
            s = str(s)
        except Exception as e:
            msg2 = Utilities.color_str(str(e), txt_color="red", bg_color="red")
            print(msg2)
            raise RuntimeError(msg2)
        result = ''
        if txt_color:
            txt_color = txt_color.lower()
            if txt_color not in Utilities.colors_txt.keys():
                warnings.warn("txt_color '{0}' not a valid color".format(txt_color))
                txt_color = 'black'
        else:
            txt_color = 'black'
        result += Utilities.colors_txt[txt_color]
        if bg_color:
            bg_color = bg_color.lower()
            if bg_color not in Utilities.colors_bg.keys():
                warnings.warn("bg_color '{0}' not a valid color".format(txt_color))
                bg_color = 'none'
        else:
            bg_color = 'none'
        result += Utilities.colors_bg[bg_color]
        if bold:
            result += Utilities.txt_effects['bold']
        if underline:
            result += Utilities.txt_effects['underline']
        result += s + Utilities.txt_effects['end']
        return result

    @staticmethod
    def last_exception_parts():
        (extype, exval, tb) = sys.exc_info()
        return extype, exval, tb

    @staticmethod
    def last_exception_info(verbose=0):
        """
        returns a string with info about the last exception
        :param verbose:
        :return: string with info about the last exception
        """
        if verbose > 0:
            print("{0} {1}".format(Utilities.whoami(), Utilities.now()))
        msg = "Exception {0}".format(datetime.datetime.now())
        (extype, exval, tb) = sys.exc_info()
        msg += "\n {0}  type: {1}".format(str(exval), extype)
        tblist = traceback.extract_tb(tb, limit=None)
        lines = traceback.format_list(tblist)
        for i, line in enumerate(lines):
            msg += "\n[{0}] {1}".format(i, line)
        result = Utilities.color_str(msg, txt_color="red")
        return result

    @staticmethod
    def module_versions(verbosity=0):
        if verbosity > 0:
            print("{0} {1}".format(Utilities.whoami(), Utilities.now()))
        mlist = list(filter(lambda x: inspect.ismodule(x[1]), globals().items()))
        if verbosity > 0:
            print(mlist)
        fields = ["filename", "asname", "ver"]
        ModTup = namedtuple("ModTup", fields)
        tlist = []
        for asname, mod in mlist:
            fname = asname
            ver = None
            if asname.startswith("__"):
                continue
            if hasattr(mod, "__version__"):
                fname = asname
                if hasattr(mod, "__path__"):
                    fname = os.path.split(mod.__path__[0])[1]
                ver = mod.__version__
            mt = ModTup(fname, asname, ver)
            tlist.append(mt)
        df = pd.DataFrame(tlist)
        df.columns = fields
        return df

    @staticmethod
    def warning_on_one_line(message, category, filename, lineno, file=None, line=None):
        return ' %s:%s: %s:%s' % (filename, lineno, category.__name__, message)

    @staticmethod
    def whoami():
        return sys._getframe(1).f_code.co_name


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
                 monthly_growth_rate_mean=1,
                 monthly_growth_rate_vol=0,
                 start_value=0,
                 monthly_value=0,
                 end_date=None):
        self.name = name
        self.start_date = make_month_day_1(start_date)
        self.monthly_growth_rate_mean = monthly_growth_rate_mean
        self.monthly_growth_rate_vol = monthly_growth_rate_vol
        if end_date is None:
            end_date = datetime.date(2050, 1, 1)
        self.end_date = make_month_day_1(end_date)
        self.start_value = start_value
        self.monthly_value = monthly_value

    def get_name(self):
        return self.name

    def get_values_df(self, end_date, paths=1, rand=None, verbosity=0):
        argdict = locals().copy()
        if verbosity > 0:
            print("{0} {1} <{2}>".format(Utilities.whoami(), self.name, Utilities.now()))
            if verbosity > 1:
                for k in argdict.keys():
                    print("{0}: {1}".format(k, argdict[k]))
        vtups = []
        if paths > 1 and rand is False:
            warnings.warn("paths= {0}, setting rand to True".format(paths))
            rand = True
        if rand is None:
            rand = False
            if paths > 1:
                rand = True
        for pi in range(paths):
            if verbosity > 1:
                print("path: {0}".format(pi))
            date = self.start_date
            growth_value = self.start_value
            monthly_value = self.monthly_value
            while date < end_date:
                if date > self.end_date:
                    break
                tot_value = growth_value + monthly_value
                try:
                    vtup = (date, tot_value, pi)
                    vtups.append(vtup)
                    if rand:
                        rate = np.random.normal(loc=self.monthly_growth_rate_mean,
                                                scale=self.monthly_growth_rate_vol,
                                                size=1)[0]
                    else:
                        rate = self.monthly_growth_rate_mean
                    growth_value = growth_value * rate
                    monthly_value = monthly_value * rate
                    date = get_next_month(date)
                except Exception as e:
                    msg = Utilities.last_exception_info()
                    extype, exval, tb = Utilities.last_exception_parts()
                    raise extype(exval)
        df = pd.DataFrame(vtups)
        df.columns = ["date", self.name, "path"]
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

    def get_value_df(self, end_date, paths=1, rand=False, verbosity=0):
        argdict = locals().copy()
        if verbosity > 0:
            print("{0} <{1}>".format(Utilities.whoami(), Utilities.now()))
            if verbosity > 1:
                for k in argdict.keys():
                    print("{0}: {1}".format(k, argdict[k]))
        vdf = None
        for name in self.cash_flows.keys():
            if verbosity > 1:
                print("cf: {0}".format(name))
            cf = self.cash_flows[name]
            try:
                df = cf.get_values_df(end_date, paths=paths, rand=rand, verbosity=verbosity)
            except Exception as e:
                msg = Utilities.last_exception_info()
                extype, exval, tb = Utilities.last_exception_parts()
                raise extype(exval)
            if vdf is None:
                vdf = df
            else:
                res = vdf.merge(df, on=["date", "path"], how="outer")
                vdf = res
        vdf.set_index("date")
        vdf["total"] = vdf.sum(axis=1)
        if verbosity > 0:
            print("Done {0} {1}".format(Utilities.whoami(), Utilities.now()))
        return vdf


if __name__ == "__main__":
    today = datetime.date.today()
    equity = CashFlow(name="equity", start_date=today, start_value = 10**6,
                      monthly_growth_rate_mean=1+.05/12.0, monthly_growth_rate_vol=.05)
    bonds = CashFlow(name="bonds", start_date=today, start_value=10**6,
                     monthly_growth_rate_mean=1+.01/12.0, monthly_growth_rate_vol=.02)
    income = CashFlow(name="income", start_date=today, monthly_value=50000,
                      monthly_growth_rate_mean=1+.01/12.0, monthly_growth_rate_vol=0.001)
    expenses = CashFlow(name="expenses", start_date=today, monthly_value=50000,
                        monthly_growth_rate_mean=1+.01/12.0, monthly_growth_rate_vol=.01)

    ava_college = CashFlow(name="ava_college", start_date=datetime.date(2025, 9, 1), end_date=datetime.date(2028, 6, 1),
                           monthly_value=-50000, monthly_growth_rate_mean=1, monthly_growth_rate_vol=0.0)
    NV = NetValue("wealth", start_date=today)
    NV.add_cash_flow(ava_college)
    NV.add_cash_flow(equity)
    NV.add_cash_flow(bonds)
    NV.add_cash_flow(income)
    NV.add_cash_flow(expenses)
    df = NV.get_value_df(end_date=datetime.date(2029, 12,1), paths=10, rand=True)
    print(df)
    df.plot(x="date", y="total")
    print(datetime.datetime.now())
