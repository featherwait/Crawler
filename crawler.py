import requests
import pandas as pd
from time import sleep
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from random import uniform

def crawler_weather_data(area,year_month):#爬取指定地区和指定年份的天气
    url = f"http://tianqihoubao.com/lishi/{area}/month/{year_month}.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    # porxies = {
    #     "https": "http://159.203.44.177:3128",
    # }

    try:
        response = requests.get(url, headers = headers, timeout = (5, 10))
        # response = requests.get(url, proxies = porxies)
        response.encoding = 'gb2312'
        # 指定编码以防乱码
        soup = BeautifulSoup(response.text, "html.parser")
        # 找表格，提取数据
        table = soup.find("table", {"class": "b"})
        rows = table.find_all("tr")[1:]
        # 跳过表头
        data = []
        for row in rows:
            cols = [col.text.strip() for col in row.find_all("td")]
            data.append({
                "日期": cols[0],
                "天气状况（白天/夜晚）": cols[1],
                "气温": cols[2],
                "风力风向（白天/夜晚）": cols[3]
            })
        return data
    except Exception as e:
        print(f"错误： {year_month}: {e}")
        return []

def fetch_weather_data():#爬取指定地区和指定年份的天气
    area = "mianyang"
    start_year = 2011
    end_year = 2022
    end_month = 11
    all_data = []
    
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            if year == end_year and month > end_month:
                break
            year_month = f"{year}{month:02d}"
            print(f"当前爬取年份：{year_month}")
            data = crawler_weather_data(area,year_month)
            all_data.extend(data)
            sleep(uniform(1, 3))
            # 暂停
    
    for entry in all_data:
        for key in entry:
            entry[key] = entry[key].replace(" ", "")
            entry[key] = entry[key].replace("\n", "")
    # 直接保存会在/后面多换行和空格    
    # 保存到 CSV 文件
    df = pd.DataFrame(all_data)
    df.to_csv("mianyang_weather.csv", index=False, encoding="utf-8-sig")
    print("数据成功保存到mianyang_weather.csv")

def process_csv(file_path):#处理爬取数据
    df = pd.read_csv(file_path)
    if '日期' in df.columns:
        df[['年月','日']] = df['日期'].str.split('月', expand=True)
    if '年月' in df.columns and '日' in df.columns:
        df['年月'] = df['年月'].str.replace("年", "").astype(float)
        df['日'] = df['日'].str.replace("日", "").astype(float)
    # 分割日期，便于后续处理
    if '天气状况（白天/夜晚）' in df.columns:
        df[['天气白天', '天气夜晚']] = df['天气状况（白天/夜晚）'].str.split('/', expand=True)
    # 分割天气状况
    if '风力风向（白天/夜晚）' in df.columns:
        df[['风力白天', '风向夜晚']] = df['风力风向（白天/夜晚）'].str.split('/', expand=True)
    # 分割风力风向
    if '气温' in df.columns:
        df[['最高温度', '最低温度']] = df['气温'].str.split('/', expand=True)
    # 分割气温
    if '最高温度' in df.columns and '最低温度' in df.columns:
        df['最高温度'] = df['最高温度'].str.replace("℃", "").astype(float)
        df['最低温度'] = df['最低温度'].str.replace("℃", "").astype(float)
    # 去掉天气符号，便于后续处理
    column_to_delete = ['日期','天气状况（白天/夜晚）','气温','风力风向（白天/夜晚）',]
    df.drop(column_to_delete , axis = 1 , inplace = True)
    output_file = "mianyang_weather_new.csv"
    df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"处理完成，保存在 {output_file}")

def plot_temperature_curve(file_path, begin_yearmonth,end_yearmonth,is_Max_temperature):# 处理需要作图的温度数据
    df = pd.read_csv(file_path)
    plt.rcParams['font.family'] = 'SimHei'
    dates_df = df[(df['年月'] >= begin_yearmonth) & (df['年月'] <= end_yearmonth)]
    if(is_Max_temperature) :
        temperatures = dates_df[['最高温度']]
        temperatures.plot(kind='line', marker='o', color='red', linestyle='-')
        plt.title(f'最高温度折线图({begin_yearmonth}到{end_yearmonth})', fontsize=14)
    else :
        temperatures = dates_df[['最低温度']]
        temperatures.plot(kind='line', marker='o', color='blue', linestyle='-')
        plt.title(f'最低温度折线图({begin_yearmonth}到{end_yearmonth})', fontsize=14)
    plt.xlabel('天数', fontsize=12)
    plt.ylabel('温度', fontsize=12)
    plt.xticks(rotation=45)
    # 设置图表标题和轴标签
    plt.tight_layout()
    plt.show()
    # print(temperatures)

def plot_weather_category_pie(file_path, begin_yearmonth, end_yearmonth, category_column=''):
    df = pd.read_csv(file_path)
    plt.rcParams['font.family'] = 'SimHei'
    dates_df = df[(df['年月'] >= begin_yearmonth) & (df['年月'] <= end_yearmonth)]
    category_counts = dates_df[category_column].value_counts()
    category_ratios = category_counts / category_counts.sum()
    
    # 计算每个类别的占比
    plt.figure(figsize=(8, 8))
    plt.pie(
        category_ratios,
        labels = category_ratios.index,
        autopct = '%1.2f%%',  # 显示百分比
        pctdistance = 1.1,
        labeldistance = 1.2,
        colors = plt.cm.tab10.colors,  # 颜色方案
    )
    # 绘制饼状图
    plt.title(f'{category_column}类别占比({begin_yearmonth}到{end_yearmonth})', fontsize=14)
    plt.tight_layout()
    plt.show()
    
def main():
    fetch_weather_data()
    # 爬取保存天气数据到CSV文件
    process_csv("mianyang_weather.csv")
    # 对爬取的天气数据SCV文件进行处理
    plot_temperature_curve('mianyang_weather_new.csv',201201,201203,True)
    plot_temperature_curve('mianyang_weather_new.csv',201201,201203,False)
    # 一般是某一季度的温度？
    plot_weather_category_pie('mianyang_weather_new.csv',201201,201212,'天气白天')
    plot_weather_category_pie('mianyang_weather_new.csv',201201,201212,'天气夜晚')

if __name__ == "__main__":
    main()
