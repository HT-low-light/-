import json
from pyecharts.charts import Pie, Bar
from pyecharts import options as opts


# 定义读取JSON文件并返回数据的函数
def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


# 函数：生成岗位饼图
def generate_position_pie_chart(data):
    # 初始化职位统计字典
    position_counts = {}

    # 处理每个数据条目中的position字段
    for item in data:
        positions = item.get('position', [])
        if isinstance(positions, list):  # 确保 positions 是一个列表
            for position in positions:
                if position in position_counts:
                    position_counts[position] += 1
                else:
                    position_counts[position] = 1
        else:  # 如果 position 不是列表，处理单一的职位字符串
            if positions in position_counts:
                position_counts[positions] += 1
            else:
                position_counts[positions] = 1

    # 转换为pyecharts需要的格式
    pie_data = [(k, v) for k, v in position_counts.items()]

    # 创建环形图
    pie = Pie()
    pie.add(
        "",
        pie_data,
        radius=["30%", "70%"],  # 调整环形图的内外半径
        label_opts=opts.LabelOpts(is_show=False)
    )
    pie.set_global_opts(
        title_opts=opts.TitleOpts(title="Python相关岗位有哪些", pos_top="bottom", pos_left="center"),
        legend_opts=opts.LegendOpts(
            orient="vertical",
            pos_left="left",
            pos_top="top",
            textstyle_opts=opts.TextStyleOpts(font_size=5),
            item_height=5,
            item_gap=1
        )
    )
    pie.set_series_opts(
        label_opts=opts.LabelOpts(is_show=False)
    )

    return pie


# 函数：解析薪资范围并计算平均薪资
def parse_and_average_salary(data):
    # 初始化平均薪资列表
    average_salaries = []

    # 处理每个数据条目中的salary字段
    for item in data:
        salaries = item.get('salary', [])  # 使用get方法获取salary字段，避免没有salary字段时报错

        total_salary = 0
        count = 0

        # 解析每个薪资范围字符串，计算平均薪资
        for salary_str in salaries:
            salary_str = salary_str.replace('万', '').replace('千', '').replace('·', '')  # 去除单位和特殊符号
            salary_parts = salary_str.split('-')

            if len(salary_parts) == 2:
                try:
                    min_salary = float(salary_parts[0])
                    max_salary = float(salary_parts[1])
                    average_salary = (min_salary + max_salary) / 2
                    total_salary += average_salary
                    count += 1
                except ValueError:
                    continue  # 忽略无法解析的薪资范围

        # 计算平均薪资
        if count > 0:
            average_salaries.append(total_salary / count)

    # 按照平均薪资大小排序
    average_salaries.sort()

    return average_salaries


# 函数：生成薪资柱状图
def generate_salary_bar_chart(data):
    # 解析并计算平均薪资
    average_salaries = parse_and_average_salary(data)

    # 创建柱状图
    bar = Bar()
    bar.add_xaxis([f"第{i + 1}档" for i in range(len(average_salaries))])  # 设置柱状图的x轴数据
    bar.add_yaxis("平均薪资（单位：万元）", average_salaries)  # 设置柱状图的y轴数据
    bar.set_global_opts(
        title_opts=opts.TitleOpts(title="平均薪资分布柱状图", pos_top="bottom", pos_left="center"),
        xaxis_opts=opts.AxisOpts(name="薪资档次"),
        yaxis_opts=opts.AxisOpts(name="平均薪资（单位：万元）")
    )

    return bar


if __name__ == "__main__":
    # 读取json文件
    file_path = "jobs_data.json"
    data = read_json_file(file_path)

    # 生成岗位饼图
    position_pie_chart = generate_position_pie_chart(data)
    position_pie_chart.render("./results/position_pie_chart.html")  # 渲染岗位饼图到HTML文件

    # 生成薪资柱状图
    salary_bar_chart = generate_salary_bar_chart(data)
    salary_bar_chart.render("./results/salary_bar_chart.html")  # 渲染薪资柱状图到HTML文件
