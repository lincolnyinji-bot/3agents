#!/usr/bin/env python3
"""
AI-H 猎头自动化系统 V3
集成Judge算法V3和定时任务支持
"""
import asyncio
import sys
import json
import re
import os
from datetime import datetime
from pathlib import Path
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(str(Path(__file__).parent))

# ============================================================
# 配置区 - 支持从外部文件读取紧急需求
# ============================================================
def load_urgent_requirements():
    """从RecruitLite加载紧急需求"""
    try:
        # 尝试从RecruitLite API获取紧急需求
        from recruitlite_integration import RecruitLiteClient
        
        client = RecruitLiteClient()
        if client.check_connection():
            urgent_jobs = client.get_urgent_jobs()
            
            # 转换格式为AI-H需要的格式
            formatted_jobs = []
            for job in urgent_jobs:
                # 从职位描述中提取关键词
                description = job.get('description', '')
                keywords = extract_keywords_from_jd(description)
                
                formatted_jobs.append({
                    "id": job.get('id'),
                    "title": job.get('title', '未知职位'),
                    "company": job.get('client_name', '未知公司'),
                    "location": job.get('location', ''),
                    "experience": "3-5年",  # 默认值，实际应从JD解析
                    "education": "本科",  # 默认值
                    "urgency": job.get('priority', 'normal'),
                    "keywords": keywords,
                    "description": description
                })
            
            print(f"从RecruitLite加载了 {len(formatted_jobs)} 个紧急需求")
            return formatted_jobs
        else:
            print("RecruitLite服务不可用，使用模拟数据")
            return get_mock_urgent_requirements()
            
    except ImportError:
        print("RecruitLite集成模块未找到，使用模拟数据")
        return get_mock_urgent_requirements()
    except Exception as e:
        print(f"加载紧急需求出错: {e}")
        return get_mock_urgent_requirements()


def extract_keywords_from_jd(jd_text):
    """从职位描述中提取关键词"""
    if not jd_text:
        return DEFAULT_KEYWORDS
    
    # 简单关键词提取逻辑
    keywords = []
    
    # 常见职位关键词
    position_keywords = ['投资经理', '投资分析师', '投资总监', 'VP', '合伙人', '投资助理']
    for kw in position_keywords:
        if kw in jd_text:
            keywords.append(kw)
    
    # 行业关键词
    industry_keywords = ['航天', '商业航天', '半导体', 'AI', '人工智能', '新能源', '生物医疗', '先进制造']
    for kw in industry_keywords:
        if kw in jd_text:
            keywords.append(kw)
    
    # 技能关键词
    skill_keywords = ['投资', '融资', '并购', '行业研究', '财务分析', '尽职调查']
    for kw in skill_keywords:
        if kw in jd_text:
            keywords.append(kw)
    
    # 如果没有提取到关键词，使用默认关键词
    if not keywords:
        keywords = DEFAULT_KEYWORDS.copy()
    
    return list(set(keywords))  # 去重


def get_mock_urgent_requirements():
    """获取模拟紧急需求（备用）"""
    return [
        {
            "id": 1,
            "title": "商业航天投资经理",
            "company": "某航天科技公司",
            "location": "上海/深圳",
            "experience": "3-5年",
            "education": "985硕士",
            "urgency": "high",
            "keywords": ["投资经理", "航天", "商业航天"],
            "description": "职位：商业航天投资经理\n要求：3-5年投资经验，985硕士，有航天或硬科技投资背景"
        }
    ]

# 默认JD配置（当无紧急需求时使用）
DEFAULT_JD = """
职位：商业航天投资经理
工作地点：上海或深圳
工作经验：1-5年
学历要求：985本硕
职责：商业航天领域投资项目研究、尽职调查、投资决策支持
"""

DEFAULT_KEYWORDS = ["投资经理", "航天", "商业航天"]

# ============================================================
# Judge算法V3集成
# ============================================================
class JudgeV3Integrator:
    """Judge算法V3集成器"""
    
    def __init__(self):
        try:
            from optimized_judge_v3 import OptimizedJudgeV3
            self.JudgeClass = OptimizedJudgeV3
            self.judge_available = True
        except ImportError:
            print("警告: 未找到optimized_judge_v3，使用简化评估")
            self.judge_available = False
    
    def evaluate_candidate(self, candidate_data, position_level="IM"):
        """使用Judge V3评估候选人"""
        if not self.judge_available:
            return self._simple_evaluate(candidate_data)
        
        try:
            # 构建简历文本
            resume_text = self._build_resume_text(candidate_data)
            
            # 使用Judge V3评估
            judge = self.JudgeClass(position_level=position_level)
            result = judge.analyze_resume(resume_text, candidate_data.get('name', '候选人'))
            
            return {
                'score': result['total_score'],
                'recommendation': result['recommendation'],
                'direction': result['direction'],
                'details': result
            }
        except Exception as e:
            print(f"Judge V3评估出错: {e}")
            return self._simple_evaluate(candidate_data)
    
    def _build_resume_text(self, candidate):
        """构建简历文本"""
        text_parts = []
        
        # 基本信息
        if candidate.get('name'):
            text_parts.append(f"姓名: {candidate['name']}")
        if candidate.get('age'):
            text_parts.append(f"年龄: {candidate['age']}")
        if candidate.get('exp'):
            text_parts.append(f"工作经验: {candidate['exp']}")
        if candidate.get('degree'):
            text_parts.append(f"学历: {candidate['degree']}")
        if candidate.get('school'):
            text_parts.append(f"学校: {candidate['school']}")
        
        # 工作经历
        if candidate.get('company'):
            text_parts.append(f"公司: {candidate['company']}")
        if candidate.get('role'):
            text_parts.append(f"职位: {candidate['role']}")
        
        # 技能（如果有）
        if candidate.get('skills'):
            text_parts.append(f"技能: {', '.join(candidate['skills'])}")
        
        # 描述（重要信息）
        if candidate.get('description'):
            text_parts.append(f"描述: {candidate['description']}")
        
        return '\n'.join(text_parts)
    
    def _simple_evaluate(self, candidate):
        """简化评估（当Judge不可用时）"""
        score = 60  # 基础分
        
        # 经验加分
        exp_years = self._extract_years(candidate.get('exp', ''))
        if exp_years >= 5:
            score += 15
        elif exp_years >= 3:
            score += 10
        elif exp_years >= 1:
            score += 5
        
        # 学历加分
        degree = candidate.get('degree', '')
        if '硕士' in degree or '博士' in degree:
            score += 10
        elif '本科' in degree:
            score += 5
        
        # 学校加分
        school = candidate.get('school', '')
        if any(keyword in school for keyword in ['985', '211', '清华', '北大', '海外']):
            score += 10
        
        # 推荐建议
        if score >= 75:
            recommendation = "推荐"
        elif score >= 60:
            recommendation = "可考虑"
        else:
            recommendation = "淘汰"
        
        return {
            'score': score,
            'recommendation': recommendation,
            'direction': '待评估',
            'details': {'simple_score': score}
        }
    
    def _extract_years(self, exp_str):
        """从经验字符串提取年数"""
        if not exp_str:
            return 0
        match = re.search(r'(\\d+)', exp_str)
        return int(match.group(1)) if match else 0

# ============================================================
# 定时任务管理器
# ============================================================
class SchedulerManager:
    """定时任务管理器"""
    
    def __init__(self):
        self.cron_file = Path.home() / '.openclaw' / 'openclaw.json'
    
    def setup_midnight_schedule(self):
        """设置每天午夜12点执行任务"""
        try:
            # 读取当前配置
            import json
            if self.cron_file.exists():
                with open(self.cron_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = {}
            
            # 添加定时任务配置
            if 'cron' not in config:
                config['cron'] = {}
            
            config['cron']['aih_midnight_job'] = {
                'name': 'AI-H午夜搜索任务',
                'schedule': {
                    'kind': 'cron',
                    'expr': '0 0 * * *',  # 每天午夜12点
                    'tz': 'Asia/Shanghai'
                },
                'payload': {
                    'kind': 'agentTurn',
                    'message': '执行AI-H项目，搜索所有紧急需求',
                    'model': 'deepseek/deepseek-chat'
                },
                'sessionTarget': 'isolated',
                'delivery': {
                    'mode': 'announce',
                    'channel': 'webchat'
                },
                'enabled': True
            }
            
            # 保存配置
            with open(self.cron_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            print("✅ 已设置午夜12点定时任务")
            return True
            
        except Exception as e:
            print(f"设置定时任务出错: {e}")
            return False
    
    def check_schedule(self):
        """检查定时任务状态"""
        try:
            import json
            if self.cron_file.exists():
                with open(self.cron_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                if 'cron' in config and 'aih_midnight_job' in config['cron']:
                    job = config['cron']['aih_midnight_job']
                    return {
                        'enabled': job.get('enabled', False),
                        'schedule': job.get('schedule', {}),
                        'next_run': '今晚12点'  # 简化显示
                    }
            return None
        except:
            return None

# ============================================================
# 主流程函数
# ============================================================
async def run_aih_pipeline(job_config=None):
    """运行AI-H主流程"""
    print("=" * 60)
    print("AI-H 猎头自动化系统 V3")
    print("=" * 60)
    
    # 1. 加载需求
    if job_config:
        print(f"执行紧急需求: {job_config.get('title', '未知职位')}")
        jd_text = job_config.get('description', DEFAULT_JD)
        search_keywords = job_config.get('keywords', DEFAULT_KEYWORDS)
    else:
        print("使用默认配置")
        jd_text = DEFAULT_JD
        search_keywords = DEFAULT_KEYWORDS
    
    # 2. 初始化Judge V3
    print("\\n初始化Judge算法V3...")
    judge_integrator = JudgeV3Integrator()
    
    # 3. 模拟搜索和评估（实际应调用搜索模块）
    print("模拟搜索候选人...")
    
    # 模拟候选人数据
    mock_candidates = [
        {
            'name': '张航天',
            'age': '30岁',
            'exp': '5年',
            'degree': '硕士',
            'school': '北京航空航天大学',
            'company': '某航天科技投资公司',
            'role': '投资经理',
            'skills': ['航天', '投资', '财务分析']
        },
        {
            'name': '李投资',
            'age': '28岁',
            'exp': '3年',
            'degree': '硕士',
            'school': '上海交通大学',
            'company': '某VC机构',
            'role': '投资分析师',
            'skills': ['投资', '行业研究', 'AI']
        }
    ]
    
    # 4. 使用Judge V3评估
    print("\\n使用Judge V3评估候选人...")
    evaluated_candidates = []
    
    for candidate in mock_candidates:
        evaluation = judge_integrator.evaluate_candidate(candidate, "IM")
        candidate['evaluation'] = evaluation
        evaluated_candidates.append(candidate)
        
        print(f"  {candidate['name']}: {evaluation['score']}分 - {evaluation['recommendation']}")
        print(f"     方向: {evaluation['direction']}")
    
    # 5. 排序和筛选
    evaluated_candidates.sort(key=lambda x: x['evaluation']['score'], reverse=True)
    
    # 6. 输出结果
    print("\\n" + "=" * 60)
    print("评估结果汇总")
    print("=" * 60)
    
    for i, candidate in enumerate(evaluated_candidates[:5], 1):
        eval_data = candidate['evaluation']
        print(f"{i}. {candidate['name']} - {candidate['role']}")
        print(f"   评分: {eval_data['score']}分 | 推荐: {eval_data['recommendation']}")
        print(f"   方向: {eval_data['direction']}")
        print(f"   公司: {candidate['company']}")
        print()
    
    # 7. 保存结果
    output_file = f"aih_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'job_config': job_config or {'title': '默认搜索'},
            'timestamp': datetime.now().isoformat(),
            'candidates': evaluated_candidates
        }, f, ensure_ascii=False, indent=2)
    
    print(f"结果已保存到: {output_file}")
    
    # 8. 推送到RecruitLite系统（如果配置了职位ID）
    try:
        # 导入RecruitLite集成模块
        from recruitlite_integration import RecruitLiteClient
        
        client = RecruitLiteClient()
        if client.check_connection():
            # 如果有职位ID，推送候选人
            job_id = job_config.get('id') if job_config else None
            if job_id:
                print(f"\\n推送到RecruitLite职位 {job_id}...")
                print(f"准备推送 {len(evaluated_candidates)} 个候选人")
                
                # 调试：打印第一个候选人的数据结构
                if evaluated_candidates:
                    print(f"第一个候选人数据结构: {json.dumps(evaluated_candidates[0], ensure_ascii=False, indent=2)}")
                
                result = client.push_candidates_to_job(job_id, evaluated_candidates)
                if result.get('success'):
                    print(f"✅ 推送成功: {result.get('inserted', 0)}个新增，{result.get('skipped', 0)}个重复")
                else:
                    print(f"❌ 推送失败: {result.get('message', '未知错误')}")
                    print(f"详细错误: {result.get('error', '无')}")
            else:
                print("未指定职位ID，跳过推送（仅保存结果）")
        else:
            print("RecruitLite服务不可用，跳过推送")
    except ImportError:
        print("RecruitLite集成模块未找到，跳过推送")
    except Exception as e:
        print(f"推送过程中出错: {e}")
        import traceback
        traceback.print_exc()
    
    return evaluated_candidates

# ============================================================
# 主函数
# ============================================================
async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI-H 猎头自动化系统 V3')
    parser.add_argument('--urgent', action='store_true', help='执行所有紧急需求')
    parser.add_argument('--setup-schedule', action='store_true', help='设置定时任务')
    parser.add_argument('--check-schedule', action='store_true', help='检查定时任务状态')
    parser.add_argument('--job-id', type=int, help='执行特定紧急需求ID')
    
    args = parser.parse_args()
    
    # 检查定时任务状态
    if args.check_schedule:
        scheduler = SchedulerManager()
        status = scheduler.check_schedule()
        if status:
            print("📅 定时任务状态:")
            print(f"   启用: {'✅' if status['enabled'] else '❌'}")
            print(f"   计划: {status.get('schedule', {}).get('expr', '未知')}")
            print(f"   下次运行: {status.get('next_run', '未知')}")
        else:
            print("❌ 未找到定时任务配置")
        return
    
    # 设置定时任务
    if args.setup_schedule:
        scheduler = SchedulerManager()
        if scheduler.setup_midnight_schedule():
            print("✅ 定时任务设置成功")
            print("   任务: AI-H午夜搜索")
            print("   时间: 每天午夜12点")
            print("   目标: 搜索所有紧急需求")
        else:
            print("❌ 定时任务设置失败")
        return
    
    # 执行紧急需求
    if args.urgent or args.job_id:
        print("🔍 执行紧急需求搜索...")
        
        # 加载紧急需求
        urgent_jobs = load_urgent_requirements()
        
        if not urgent_jobs:
            print("⚠️ 未找到紧急需求，使用默认配置")
            await run_aih_pipeline()
            return
        
        # 执行特定任务或所有任务
        if args.job_id:
            target_jobs = [job for job in urgent_jobs if job.get('id') == args.job_id]
        else:
            target_jobs = urgent_jobs
        
        if not target_jobs:
            print(f"❌ 未找到ID为{args.job_id}的紧急需求")
            return
        
        # 执行每个任务
        all_results = []
        for job in target_jobs:
            print(f"\\n执行任务: {job.get('title')}")
            results = await run_aih_pipeline(job)
            all_results.extend(results)
        
        print(f"\\n✅ 完成 {len(target_jobs)} 个紧急需求搜索")
        print(f"   共评估 {len(all_results)} 个候选人")
        
    else:
        # 执行默认搜索
        await run_aih_pipeline()

if __name__ == "__main__":
    asyncio.run(main())