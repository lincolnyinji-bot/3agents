#!/usr/bin/env python3
# 猎聘网数据采集助手
# 安全的手动辅助工具，不直接访问网站

import csv
from datetime import datetime

class LiepinDataCollector:
    def __init__(self):
        self.fields = [
            '姓名', '当前职位', '当前公司', '工作年限', '学历',
            '期望薪资', '投资经验', '本科学历', '本科专业',
            '硕士学历', '硕士专业', '项目经验', '原始链接'
        ]
    
    def create_template(self):
        """创建采集模板"""
        template_data = [
            # 示例数据 - 说明如何填写
            ['张三', '投资经理', '红杉资本', '3年', '硕士', '25K', '2年', '清华大学', '计算机', '清华大学', '计算机', 'TMT领域项目挖掘', 'https://example.com/1'],
            ['李四', '分析师', 'IDG资本', '2年', '硕士', '22K', '1年', '北京大学', '电子信息', '剑桥大学', 'CS', 'AI赛道研究', 'https://example.com/2'],
            ['王五', '投资经理', '高瓴资本', '4年', '硕士', '30K', '3年', '上海交大', '软件工程', '上海交大', '软件工程', '多个项目尽调', 'https://example.com/3']
        ]
        
        filename = f"../data/collected/liepin_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        
        with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(self.fields)
            writer.writerows(template_data)
        
        return filename
    
    def generate_collection_guide(self):
        """生成采集指南"""
        guide = """
        ==============================================
        猎聘网简历采集操作指南
        ==============================================
        
        步骤1：登录猎聘网
        ----------------------------------------------
        网址：https://h.liepin.com/account/login
        账号：13751048972
        密码：123456aA
        
        步骤2：搜索候选人
        ----------------------------------------------
        搜索关键词（选1-2个组合）：
        • "投资经理"
        • "一级市场"  
        • "VC"
        • "风险投资"
        • "股权投资"
        
        筛选条件：
        • 工作经验：1-5年
        • 学历要求：本科及以上
        • 期望薪资：15-40K
        • 地区：按需求选择
        
        步骤3：查看列表页信息
        ----------------------------------------------
        每页约15-20个候选人，包含以下信息：
        
        [姓名] - [当前职位] - [当前公司]
        [工作年限] | [学历] | [期望薪资]
        
        示例显示：
        王明 - 投资经理 - 启明创投
        3年 | 硕士 | 25k
        
        步骤4：填写采集表格
        ----------------------------------------------
        根据列表页信息填写：
        
        必填字段（列表页直接可见）：
        1. 姓名
        2. 当前职位
        3. 当前公司
        4. 工作年限（如"3年"）
        5. 学历（如"硕士"）
        6. 期望薪资（如"25K"）
        
        可选字段（需要点开简历查看）：
        7. 投资经验（如"2年一级市场经验"）
        8. 本科学历（学校）
        9. 本科专业
        10. 硕士学历（学校）
        11. 硕士专业
        12. 项目经验（简要描述）
        13. 原始链接（简历URL）
        
        步骤5：保存和导入
        ----------------------------------------------
        1. 将CSV文件保存为：resumes.csv
        2. 复制到：vc_recruiter/data/input/resumes.csv
        3. 运行筛选脚本：python scripts/resume_filter.py
        
        安全注意事项：
        ----------------------------------------------
        ⚠️ 不要频繁刷新页面
        ⚠️ 每小时不超过100次查看
        ⚠️ 分批采集，每20份休息2分钟
        ⚠️ 优先采集列表页完整信息
        
        效率技巧：
        ----------------------------------------------
        • 打开多个标签页（每个标签不同搜索条件）
        • 使用Excel直接复制粘贴
        • 先采集必填字段，后续补充详细信息
        • 标注疑问项，后续重点核实
        
        ==============================================
        """
        return guide
    
    def estimate_time(self, num_resumes: int) -> dict:
        """估算采集时间"""
        times = {
            10: "约5-10分钟",
            20: "约10-15分钟", 
            50: "约20-30分钟",
            100: "约40-60分钟"
        }
        
        return {
            '简历数量': num_resumes,
            '预计时间': times.get(num_resumes, f"约{num_resumes*0.5}分钟"),
            '推荐数量': min(20, num_resumes),  # 首次测试推荐数量
            '效率提示': f"每小时可处理约{min(100, num_resumes*3)}份简历"
        }

def main():
    """主函数"""
    print("=" * 60)
    print("猎聘网数据采集助手")
    print("=" * 60)
    
    collector = LiepinDataCollector()
    
    print("\n1. 生成采集指南...")
    guide = collector.generate_collection_guide()
    print(guide)
    
    print("\n2. 创建采集模板...")
    template_file = collector.create_template()
    print(f"模板已创建: {template_file}")
    
    print("\n3. 时间估算:")
    for num in [10, 20, 50, 100]:
        estimate = collector.estimate_time(num)
        print(f"  • {num}份简历: {estimate['预计时间']}")
    
    print("\n" + "=" * 60)
    print("操作建议:")
    print("1. 先采集10-20份简历测试系统")
    print("2. 验证筛选准确率后，再扩大规模")
    print("3. 保存好原始数据备份")
    print("=" * 60)
    
    print("\n📋 下一步:")
    print("1. 登录猎聘网，按指南采集数据")
    print("2. 保存为CSV文件")
    print("3. 替换 data/input/resumes.csv")
    print("4. 运行筛选脚本")

if __name__ == "__main__":
    main()