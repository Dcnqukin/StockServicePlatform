from pytdx.hq import TdxHq_API
from pytdx.params import TDXParams
from mytt import *
from datetime import datetime, timedelta
import sys

# 标题格式，字体为中文字体，颜色为黑色，粗体，水平中心对齐
title_font = {'fontname': 'Arial', 
              'size':     '24',
              'color':    'black',
              'weight':   'bold',
              'va':       'bottom',
              'ha':       'center'}
# 红色数字格式（显示开盘收盘价）粗体红色24号字
large_red_font = {'fontname': 'Arial',
                  'size':     '24',
                  'color':    'red',
                  'weight':   'bold',
                  'va':       'bottom'}
# 绿色数字格式（显示开盘收盘价）粗体绿色24号字
large_green_font = {'fontname': 'Arial',
                    'size':     '24',
                    'color':    'green',
                    'weight':   'bold',
                    'va':       'bottom'}
# 小数字格式（显示其他价格信息）粗体红色12号字
small_red_font = {'fontname': 'Arial',
                  'size':     '12',
                  'color':    'red',
                  'weight':   'bold',
                  'va':       'bottom'}
# 小数字格式（显示其他价格信息）粗体绿色12号字
small_green_font = {'fontname': 'Arial',
                    'size':     '12',
                    'color':    'green',
                    'weight':   'bold',
                    'va':       'bottom'}
# 标签格式，可以显示中文，普通黑色12号字
normal_label_font = {'fontname': 'pingfang HK',
                     'size':     '12',
                     'color':    'black',
                     'va':       'bottom',
                     'ha':       'right'}
# 普通文本格式，普通黑色12号字
normal_font = {'fontname': 'Arial',
               'size':     '12',
               'color':    'black',
               'va':       'bottom',
               'ha':       'left'}

def format_date(date):
    year = date[:4]
    month = date[4:6]
    day = date[6:]
    formatted_date = "{}-{}-{}".format(year, month, day)
    return formatted_date

def get_stock_exchange(stock_code):
    if stock_code.startswith("600") or stock_code.startswith("601") or stock_code.startswith("603"):
        return TDXParams.MARKET_SH
    elif stock_code.startswith("000") or stock_code.startswith("001") or stock_code.startswith("002"):
        return TDXParams.MARKET_SZ
    else:
        return TDXParams.MARKET_SH

def draw(code, nowday, lastday):
    index = []
    start_time_before = datetime.strptime("2016/12/09 09:30:00", "%Y/%m/%d %H:%M:%S")
    end_time_before = datetime.strptime("2016/12/09 11:30:00", "%Y/%m/%d %H:%M:%S")
    current_time = start_time_before
    while current_time <= end_time_before:
        index.append(current_time.strftime("%Y/%m/%d %H:%M:%S"))
        current_time += timedelta(minutes=1)
    start_time_after = datetime.strptime("2016/12/09 13:01:00", "%Y/%m/%d %H:%M:%S")
    end_time_after = datetime.strptime("2016/12/09 14:59:00", "%Y/%m/%d %H:%M:%S")
    current_time = start_time_after
    while current_time <= end_time_after:
        index.append(current_time.strftime("%Y/%m/%d %H:%M:%S"))
        current_time += timedelta(minutes=1)

    api = TdxHq_API()
    with api.connect('119.147.212.81', 7709):
        lastdaykdata = api.get_k_data(code, format_date(lastday), format_date(lastday))
        nowdaykdata = api.get_k_data(code, format_date(nowday), format_date(nowday))
        df = api.to_df(api.get_history_minute_time_data(get_stock_exchange(code), code, nowday))
        df.index = pd.DatetimeIndex(index)
        df['open'] = df.price.values / lastdaykdata.close.values
        df['close'] = df.price.values / lastdaykdata.close.values
        df['high'] = df.price.values / lastdaykdata.close.values
        df['low'] = df.price.values / lastdaykdata.close.values
        df['open'][0] = nowdaykdata.open.values / lastdaykdata.close.values
        df['close'][0] = nowdaykdata.open.values / lastdaykdata.close.values
        df['high'][0] = nowdaykdata.open.values / lastdaykdata.close.values
        df['low'][0] = nowdaykdata.open.values / lastdaykdata.close.values
        df['volume'] = df.vol.values

    import matplotlib.pyplot as plt
    import mplfinance as mpf
    my_color = mpf.make_marketcolors(up='r',
                                    down='g',
                                    edge='inherit',
                                    wick='inherit',
                                    volume='inherit')
    # 设置图表的背景色
    # my_style = mpf.make_mpf_style(marketcolors=my_color,
    #                             figcolor='(0.82, 0.83, 0.85)',
    #                             gridcolor='(0.82, 0.83, 0.85)')
    fig = mpf.figure(style='yahoo', figsize=(12, 8), facecolor=(0.82, 0.83, 0.85))
    # 添加三个图表，四个数字分别代表图表左下角在figure中的坐标，以及图表的宽（0.88）、高（0.60）
    ax1 = fig.add_axes([0.06, 0.25, 0.88, 0.60])
    # 添加第二、三张图表时，使用sharex关键字指明与ax1在x轴上对齐，且共用x轴
    ax2 = fig.add_axes([0.06, 0.15, 0.88, 0.10], sharex=ax1)
    # 设置三张图表的Y轴标签
    ax1.set_ylabel('价格')
    ax2.set_ylabel('成交量')
    # 调用mpf.plot()函数，注意调用的方式跟上一节不同，这里需要指定ax=ax1，volume=ax2，将K线图显示在ax1中，交易量显示在ax2中
    t1 = fig.text(0.50, 0.94, "{0} - {1}:".format(code, nowday), **title_font)
    t2 = fig.text(0.12, 0.90, '开/收: ', **normal_label_font)
    t3 = fig.text(0.14, 0.89, f'{np.round(nowdaykdata["open"][0], 3)} / {np.round(nowdaykdata["close"][0], 3)}', **large_red_font)
    t4 = fig.text(0.14, 0.86, f'{np.round(nowdaykdata["close"][0] - lastdaykdata["close"][0], 3)}', **small_red_font)
    t5 = fig.text(0.22, 0.86, f'[{np.round(nowdaykdata["close"][0] / lastdaykdata["close"][0] * 100 - 100, 3)}%]', **small_red_font)
    t7 = fig.text(0.40, 0.90, '高: ', **normal_label_font)
    t8 = fig.text(0.40, 0.90, f'{nowdaykdata["high"][0]}', **small_red_font)
    t9 = fig.text(0.40, 0.86, '低: ', **normal_label_font)
    t10 = fig.text(0.40, 0.86, f'{nowdaykdata["low"][0]}', **small_green_font)
    t11 = fig.text(0.55, 0.90, '量(万手): ', **normal_label_font)
    t12 = fig.text(0.55, 0.90, f'{np.round(nowdaykdata["vol"][0] / 10000, 3)}', **normal_font)
    t13 = fig.text(0.55, 0.86, '额(亿元): ', **normal_label_font)
    t14 = fig.text(0.55, 0.86, f'{np.round(nowdaykdata["amount"][0] / 100000000, 3)}', **normal_font)
    t15 = fig.text(0.70, 0.90, '涨停: ', **normal_label_font)
    t16 = fig.text(0.70, 0.90, f'{np.round(lastdaykdata["close"][0] * 1.1, 3)}', **small_red_font)
    t17 = fig.text(0.70, 0.86, '跌停: ', **normal_label_font)
    t18 = fig.text(0.70, 0.86, f'{np.round(lastdaykdata["close"][0] * 0.9, 3)}', **small_green_font)
    t19 = fig.text(0.85, 0.90, '今量/昨量: ', **normal_label_font)
    t20 = fig.text(0.85, 0.90, f'[{np.round(nowdaykdata["vol"][0] / lastdaykdata["vol"][0] * 100 - 100, 3)}%]', **small_red_font)
    t21 = fig.text(0.85, 0.86, '昨收: ', **normal_label_font)
    t22 = fig.text(0.85, 0.86,  f'{np.round(lastdaykdata["close"][0], 3)}', **normal_font)

    mpf.plot(df,
            ax=ax1,
            volume=ax2,
            type='line',
            style='yahoo',
            mav=(20))
    mpf.show()



if __name__ == "__main__":
    # 从命令行获取参数
    arg1 = sys.argv[1]
    arg2 = sys.argv[2]
    arg3 = sys.argv[3]
    # 调用主程序
    draw(arg1, arg2, arg3)