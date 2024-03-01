#使用于无限易python go 量化交口 策略名称test22 
# 2024年3月1日发布
# encoding: UTF-8
import datetime
from traceback import format_exc
from datetime import date
from datetime import datetime as mydt
from ctaBase import *
from ctaTemplate import *
import matplotlib.pyplot as plt

import ctaTemplate
import csv

# from core import MarketCenter
from typing import List

import matplotlib.pyplot as plt
import numpy as np


# arguments =sys.argv[1:]
def norm(x, u, sgm):#计算正态分布概率
    return np.exp(-1 * (u - x) * (u - x) / (2 * sgm * sgm)) / (sgm * np.sqrt(2 * np.pi))


def Nx(u, sgm, n=400):  # 返回x序列和x对应的概率密度
    a = [1] * n  # 定义了一系列的数组
    b = [1] * n
    for i in range(1, n + 1):
        a[i - 1] = u - (3 * sgm) + (6 * sgm * i / n)  # 代表3sgm范围内的其实横坐标
        b[i - 1] = norm(a[i - 1], u, sgm)  # 代表概率密度
    return a, b


def calc(u=186.86, k=200, days=77, yeariv=0.2,cp=0):
    #根据iv计算期权的价格
    sgm = u * yeariv * np.sqrt(1.0 * days / 365)  # 波动率
    n = 400  # 计算分度值
    x, p = Nx(u, sgm,n)
    x = np.array(x)  # x序列
    p = np.array(p)  # x对应的概率密度
    if   cp==0:  #看涨期权
        y = (x - k) * p  # 乘积
        mysum = 0
        for i in range(n):
            if u - 3 * sgm + i / n * 6 * sgm >= k:
                mysum += y[i] * 6 * sgm / n
    else:#看跌期权
        y = ( k-x) * p  # 乘积
        mysum = 0
        for i in range(n):
            if u - 3 * sgm + i / n * 6 * sgm <= k:
                mysum += y[i] * 6 * sgm / n

    return mysum
def calciv(u=186.86, k=186, days=77,price=2,cp=0):
    #用折半查找搜索iv
    iva,ivb=0,5
    ivmid=(iva+ivb)/2.0
    while ivb-iva>=0.0001:
        if calc(u,k,days,ivmid,cp)>=price:
            ivb=ivmid
            ivmid=(iva+ivb)/2.0
        else:
            iva=ivmid
            ivmid = (iva + ivb) / 2.0
    if  ivmid<0.00005:
        return 0
    return ivmid



class test22(CtaTemplate):

    # # 参数映射表
    paramMap = {
            # 'exchange': '交易所',
            # 'vtSymbol': '合约',
            'volume': '交易所',
            'price': '合约'
    }
    #
    # # 参数列表，保存了参数的名称
    paramList = list(paramMap.keys())
    #
    # # 变量映射表
    varMap = {
        'trading': '交易中',
        'pos': '持仓'
    }
    #
    # # 变量列表，保存了变量的名称
    varList = list(varMap.keys())

    # ----------------------------------------------------------------------
    def __init__(self, ctaEngine=None, setting={}):
        """Constructor"""
        super().__init__(ctaEngine, setting)

        self.paramMap = {
            # 'exchange': '交易所',
            # 'vtSymbol': '合约',

            'volume': '交易所',
            'price': '合约'
        }


        # 状态映射表
        self.varMap = {
            'trading': '交易中',
            'pos': '持仓'
        }

        # self.exchange = 'SHFE;SHFE;SHFE;SHFE;SHFE'  # 交易所和合约从界面填入，所以留空
        # self.vtSymbol = 'cu2403;au2404;ag2406;al2403;ao2403'
        # self.symbolList=['ag2406','al2403','ao2403','au2404']
        # self.exchangeList=['SHFE']*len(self.symbolList)
        # self.exchange = ''  # 交易所和合约从界面填入，所以留空
        # self.vtSymbol = ''

        self.volume = ''
        self.price = ''
        self.order_count = 1  # 报单次数
        self.tick_price1 = 0
        self.tick_price2 = 0
        self.account = "100117573"
        # self.widgetClass = KLWidget
        # self.widget = None
        # self.nMin = 5
        # self.cost = 0  # 持仓成本
        #
        # self.volume = 1  # 下单手数
        # self.ma0 = 0  # 当前K线慢均线数值
        # self.ma1 = 0  # 当前K线快均线数值
        # self.ma00 = 0  # 上一个K线慢均线数值
        #
        # self.ma10 = 0  # 上一个K线快均线数值
        # self.D = 0
        # self.trading = False
        #
        # # 启动界面
        # self.signal = 0  # 买卖标志
        # self.mainSigs = ['ma0', 'ma1', 'cost']  # 主图显示
        # self.subSigs = []  # 副图显示
        # self.getGui()
        #
        # # 注意策略类中的可变对象属性（通常是list和dict等），在策略初始化时需要重新创建，
        # # 否则会出现多个策略实例之间数据共享的情况，有可能导致潜在的策略逻辑错误风险，
        # # 策略类中的这些可变对象属性可以选择不写，全都放在__init__下面，写主要是为了阅读
        # # 策略时方便（更多是个编程习惯的选择）

    # ----------------------------------------------------------------------
    def onTick(self, tick):
        """收到行情TICK推送"""
        super().onTick(tick)  # 调用父类的 onTick 方法
        # is_askprice=True
        # if is_askprice:
        #     price=tick.askPrice1
        # else:
        #     price=tick.bidPrice1

        if not tick.lastPrice or self.order_count == 0:  # 最新价为空或者可报单次数为 0 直接返回
            return
        if tick.vtSymbol in self.biaodilist:
            self.output(str(tick.vtSymbol)+" : "+str(tick.lastPrice))
            #标的
            self.biao_dict[tick.vtSymbol]=tick.lastPrice;

        else:#是期权
            self.output(str(tick.vtSymbol)+" : "+str(tick.askPrice1)+" / "+str(tick.bidPrice1))
            symbol = tick.vtSymbol
            biaodi = str(symbol.split("P")[0]) if "P" in symbol else str(symbol.split("C")[0])
            k = int(symbol.split("P")[1]) if "P" in symbol else int(symbol.split("C")[1])
            cp = 0 if "C" in symbol else 1
            #计算到期天数
            strelse = str(symbol.split("P")[0]) if "P" in symbol else str(symbol.split("C")[0])
            mon = int(strelse[-2:])
            today = date.today()
            target_date = date(2024, mon - 1, 25)  # 目前只考虑24年 只考虑上期所 粗略计算
            days_diff = (target_date - today).days
            #获取品种 查询标的价格
            # exsymbol = strelse[:-4]
            biaodiprice = self.biao_dict.get(biaodi)
            if biaodiprice == 0:
                return
            if cp==0 and k<biaodiprice:
                return
            if cp==1 and k>biaodiprice:
                return 
            # 计算iv
            iv_ask = calciv(biaodiprice, k, days_diff, tick.askPrice1,cp)
            iv_bid= calciv(biaodiprice, k, days_diff, tick.bidPrice1,cp)
            iv= calciv(biaodiprice, k, days_diff, tick.lastPrice,cp)

            # 计算delta
            pricelow=calc(biaodiprice*0.999,k,days_diff,iv,cp)
            pricehigh=calc(biaodiprice*1.001,k,days_diff,iv,cp)
            deltalow=(tick.lastPrice-pricelow)/1.0/(biaodiprice*0.001)
            deltahigh=(pricehigh-tick.lastPrice)/1.0/(biaodiprice*0.001)
            delta=(deltalow+deltahigh)/2.0


            # 计算gamma
            gamma=(deltahigh-deltalow)/(biaodiprice*0.001)

            #计算vega
            price_high_vega=calc(biaodiprice,k,days_diff,iv+0.005,cp)
            price_low_vega=calc(biaodiprice,k,days_diff,iv-0.005,cp)
            vega= price_high_vega-price_low_vega

            #计算theta


            data = [symbol,tick.lastPrice ,iv,tick.askPrice1,iv_ask,tick.bidPrice1,iv_bid, k, cp, days_diff,
                     biaodi, biaodiprice, delta,gamma,vega]
            with open(self.filenamestr, mode='a', newline='') as file:
                writer = csv.writer(file)
                # 写入数据

                writer.writerow(data)


    # ----------------------------------------------------------------------
    # def onBar(self, bar):
    #     """收到Bar推送（必须由用户继承实现）"""
    #     self.bar = bar
    #     if self.tradeDate != bar.date:
    #         self.tradeDate = bar.date
    #
    #     # 记录数据
    #     if not self.bm.updateBar(bar):
    #         return
    #
    # def onBarX(self, bar):
    #     """收到Bar推送（必须由用户继承实现）"""
    #     self.bar = bar
    #
    #     # 记录数据
    #     if not self.am.updateBar(bar):
    #         return
    #
    #     # 计算指标
    #     self.getCtaIndictor(bar)
    #
    #     # 计算信号
    #     self.getCtaSignal(bar)
    #
    #     # 简易信号执行
    #     self.execSignal(self.volume)
    #
    #     # 前收盘
    #     self.refclose = bar.close
    #
    #     # 发出状态更新事件
    #     if (not self.widget is None) and (not self.bar is None):
    #         data = {'bar': self.bar, 'sig': self.signal, 'ma0': self.ma0, 'ma1': self.ma1, 'cost': self.cost}
    #         self.widget.addBar(data)
    #     if self.trading:
    #         self.putEvent()
    #
    # def getCtaIndictor(self, bar):
    #     """计算指标数据"""
    #     # 计算指标数值
    #     ma = self.am.sma(self.P, True)
    #     ma1 = self.am.sma(self.N, True)
    #     self.ma0, self.ma00 = ma[-1], ma[-2]
    #     self.ma1, self.ma10 = ma1[-1], ma1[-2]
    #
    # def getCtaSignal(self, bar):
    #     """计算交易信号"""
    #     close = bar.close
    #     hour = bar.datetime.hour
    #     minute = bar.datetime.minute
    #     # 定义尾盘，尾盘不交易并且空仓
    #     self.endOfDay = hour == 14 and minute >= 40
    #     # 判断是否要进行交易
    #     self.buySig = self.ma1 > self.ma0 and self.ma10 < self.ma00
    #     self.shortSig = self.ma1 < self.ma0 and self.ma10 > self.ma00
    #     # 交易价格
    #     self.longPrice = bar.close
    #     self.shortPrice = bar.close
    #
    # def execSignal(self, volume):
    #     """简易交易信号执行"""
    #     pos = self.pos[self.vtSymbol]
    #     # 挂单未成交
    #     if self.orderID is not None:
    #         self.cancelOrder(self.orderID)
    #
    #     self.signal = 0
    #
    #     if pos == 0 and not self.endOfDay:  #: 当前无仓位
    #         # 买开，卖开
    #         if self.shortSig:
    #             self.signal = -self.shortPrice
    #             self.orderID = self.short(self.shortPrice - self.D, volume)
    #             self.output('卖出开仓信号价格：{}'.format(self.shortPrice - self.D))
    #         elif self.buySig:
    #             self.signal = self.longPrice
    #             self.orderID = self.buy(self.longPrice + self.D, volume)
    #             self.output('买入开仓信号价格：{}'.format(self.longPrice + self.D))
    #     elif pos > 0 and self.shortSig:  #: 持有多头仓位
    #         self.signal = -self.shortPrice
    #         self.orderID = self.sell(self.shortPrice - self.D, pos)
    #         self.output('卖出平仓信号价格：{}'.format(self.shortPrice - self.D))
    #     elif pos < 0 and self.buySig:  #: 持有空头仓位
    #         self.signal = self.longPrice
    #         self.orderID = self.cover(self.longPrice + self.D, -pos)
    #         self.output('买入平仓信号价格：{}'.format(self.longPrice + self.D))

    def onInit(self):
        """本策略刚加载的时候不需要显示 QT 界面"""
        super().onInit()

        # self.closeGui()

    def onTrade(self, trade, log=True):
        super().onTrade(trade, log)

    def onStart(self):

        if self.price in ['au','cu','ag','al','br','rb','ru','zn']:
            self.volume='SHFE'
        res = self.get_InstListByExchAndProduct(self.volume, self.price)
        self.myoptionlist = res.get('2')
        self.symbolList = self.myoptionlist

        self.biaodilist=[]
        for item in self.myoptionlist:
            biaodi = str(item.split("P")[0]) if "P" in item else str(item.split("C")[0])
            if biaodi not in self.biaodilist:
                self.biaodilist.append(str(biaodi))
        self.biao_dict = {item: 0 for item in self.biaodilist}
        self.myoptionlist.extend(self.biaodilist)
        self.exchangeList = [self.volume] * len(self.symbolList)
        self.vtSymbol = str(";".join([str(item) for item in self.myoptionlist]))
        self.exchange = str(";".join([str(item) for item in self.exchangeList]))
        super().onStart()
        self.output(self.vtSymbol)
        data = ['symbol','lastPrice' ,'iv', 'askPrice1', 'iv_ask', 'bidPrice1', 'iv_bid', 'k', 'cp', 'days_diff',
                'biaodi', 'biaodiprice', 'delta', 'gamma', 'vega']
        self.filenamestr=str(mydt.now().hour)+'点'+str(mydt.now().minute)+self.price+'-option.csv'
        self.output(self.filenamestr)
        with open(self.filenamestr, mode='a', newline='') as file:
            writer = csv.writer(file)
            # 写入数据

            writer.writerow(data)





    def onStop(self):
        super().onStop()
