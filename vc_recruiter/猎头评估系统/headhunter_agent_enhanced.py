#!/usr/bin/env python3
"""
猎头智能Agent - 增强版（支持定时任务和自动化）
"""

import os
import json
import yaml
import glob
import time
import schedule
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
import subprocess

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/root/.openclaw/workspace/vc_recruiter/猎头评估系统/agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutomatedHeadhunterAgent:
    """自动化猎头Agent - 支持定时任务"""
    
    def __init__(self, workspace_dir=None):
        """初始化自动化Agent"""
        if workspace_dir is None:
            workspace_dir = "/root/.openclaw/workspace/vc_recruiter/猎头评估系统"
        
        self.workspace_dir = workspace_dir
        self.templates_dir = os.path.join(workspace_dir, "岗位模板")
        self.results_dir = os.path.join(workspace_dir, "评估结果")
        
        # 新增目录结构
        self.input_dir = os.path.join(workspace_dir, "简历输入")  # 简历输入文件夹
        self.inbox_dir = os.path.join(self.input_dir, "收件箱")     # 新简历收件箱
        self.processed_dir = os.path.join(self.input_dir, "已处理")  # 已处理简历
        self.archives_dir = os.path.join(self.input_dir, "存档")    # 历史存档
        
        # 创建目录结构
        self._create_directory_structure()
        
        # 加载模板
        self.templates = self._load_templates()
        
        # 定时任务相关
        self.scheduler_thread = None
        self.running = False
        
        logger.info(f"自动化猎头Agent初始化完成")
        logger.info(f"工作目录: {workspace_dir}")
        logger.info(f"简历收件箱: {self.inbox_dir}")
    
    def _create_directory_structure(self):
        """创建必要的目录结构"""
        directories = [
            self.templates_dir,
            self.results_dir,
            self.input_dir,
            self.inbox_dir,
            self.processed_dir,
            self.archives_dir
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            logger.debug(f"创建目录: {directory}")
    
    def _load_templates(self) -> Dict[str, Dict]:
        """加载所有岗位模板"""
        templates = {}
        template_files = glob.glob(os.path.join(self.templates_dir, "*.yaml")) + \
                        glob.glob(os.path.join(self.templates_dir, "*.yml"))
        
        # 如果模板目录为空，创建默认模板
        if not template_files:
            self._create_default_templates()
            template_files = glob.glob(os.path.join(self.templates_dir, "*.yaml"))
        
        for template_file in template_files:
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    template = yaml.safe_load(f)
                    template_name = template.get('岗位名称', os.path.basename(template_file))
                    templates[template_name] = template
                    logger.debug(f"加载模板: {template_name}")
            except Exception as e:
                logger.error(f"加载模板失败 {template_file}: {e}")
        
        return templates
    
    def _create_default_templates(self):
        """创建默认岗位模板"""
        default_templates = {
            "泛硬科技投资总监": {
                "岗位名称": "泛硬科技投资总监",
                "岗位描述": "硬科技领域投资总监，专注AI、半导体、新能源、商业航天等方向",
                "创建时间": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "否决标准": {
                    "学历": "硕士及以上学历，理工科背景",
                    "经验": "5年以上硬科技产业或投资经验",
                    "投资经验": "3年以上PE/VC投资经验"
                },
                "评估权重": {
                    "教育背景": 25,
                    "工作经验": 25,
                    "投资经验": 30,
                    "领域匹配": 20
                },
                "领域专注": "AI/半导体/新能源/商业航天/低空经济",
                "薪资范围": "80-200万",
                "级别要求": "总监/副总裁级别"
            },
            "AI投资经理": {
                "岗位名称": "AI投资经理",
                "岗位描述": "人工智能方向投资经理，专注大模型、AI应用、AI基础设施",
                "创建时间": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "否决标准": {
                    "学历": "硕士及以上学历，计算机/电子相关专业",
                    "经验": "3年以上AI相关经验",
                    "投资经验": "2年以上投资经验"
                },
                "评估权重": {
                    "教育背景": 20,
                    "工作经验": 25,
                    "投资经验": 25,
                    "AI经验": 30
                },
                "领域专注": "大模型/AI应用/AI基础设施/具身智能",
                "薪资范围": "50-120万",
                "级别要求": "经理/高级经理"
            }
        }
        
        for template_name, template_data in default_templates.items():
            template_file = os.path.join(self.templates_dir, f"{template_name}.yaml")
            with open(template_file, 'w', encoding='utf-8') as f:
                yaml.dump(template_data, f, allow_unicode=True, default_flow_style=False)
            
            logger.info(f"创建默认模板: {template_name}")
    
    def run_ocr_on_image(self, image_path: str) -> Dict:
        """对单个图片运行OCR"""
        try:
            logger.info(f"运行OCR: {image_path}")
            
            # 构建tesseract命令
            cmd = ['tesseract', image_path, 'stdout', '-l', 'chi_sim+eng']
            
            # 执行OCR
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.stdout:
                text = result.stdout.strip()
                logger.info(f"OCR成功，提取{len(text)}字符")
                
                # 提取关键信息
                candidate_info = self._extract_candidate_info(text)
                candidate_info['来源文件'] = os.path.basename(image_path)
                candidate_info['OCR原始文本长度'] = len(text)
                
                return candidate_info
            else:
                logger.error(f"OCR返回空文本: {image_path}")
                return {"状态": "OCR失败", "文件": os.path.basename(image_path)}
                
        except subprocess.TimeoutExpired:
            logger.error(f"OCR超时: {image_path}")
            return {"状态": "OCR超时", "文件": os.path.basename(image_path)}
        except Exception as e:
            logger.error(f"OCR失败 {image_path}: {e}")
            return {"状态": f"OCR失败: {str(e)}", "文件": os.path.basename(image_path)}
    
    def _extract_candidate_info(self, ocr_text: str) -> Dict:
        """从OCR文本中提取候选人信息"""
        info = {
            "姓名": "待确认",
            "教育": "",
            "工作经验": "",
            "投资经验": "",
            "当前职位": "",
            "领域": "",
            "薪资期望": "",
            "OCR摘要": ocr_text[:500] + "..." if len(ocr_text) > 500 else ocr_text
        }
        
        lines = [line.strip() for line in ocr_text.split('\n') if line.strip()]
        
        # 提取姓名（前5行中寻找）
        for line in lines[:5]:
            if '先生' in line:
                info['姓名'] = line.replace('先生', '先生').strip()
                break
            elif '女士' in line:
                info['姓名'] = line.replace('女士', '女士').strip()
                break
            elif line and len(line) <= 4 and not any(char.isdigit() for char in line):
                info['姓名'] = line + '先生'
                break
        
        # 提取教育信息
        edu_keywords = ['大学', '学院', '硕士', '博士', '本科', 'top', '985', '211']
        edu_lines = []
        for line in lines:
            if any(keyword in line for keyword in edu_keywords):
                edu_lines.append(line[:100])
                if len(edu_lines) >= 2:
                    break
        
        if edu_lines:
            info['教育'] = ' | '.join(edu_lines)
        
        # 提取工作经验
        exp_keywords = ['年经验', '年工作', '工作经历', '工作']
        for line in lines:
            if any(keyword in line for keyword in exp_keywords):
                info['工作经验'] = line[:80]
                break
        
        # 提取投资经验
        inv_keywords = ['投资经验', 'PE', 'VC', '投资经理', '投资总监']
        for line in lines:
            if any(keyword in line for keyword in inv_keywords):
                info['投资经验'] = line[:80]
                break
        
        # 提取领域信息
        domain_keywords = ['AI', '人工智能', '低空', '航天', '半导体', '新能源', '硬科技']
        domains_found = []
        for line in lines:
            for keyword in domain_keywords:
                if keyword in line and keyword not in domains_found:
                    domains_found.append(keyword)
                    if len(domains_found) >= 3:
                        break
        
        if domains_found:
            info['领域'] = ', '.join(domains_found)
        
        return info
    
    def check_inbox_for_new_resumes(self) -> List[Dict]:
        """检查收件箱中的新简历"""
        logger.info("检查收件箱新简历...")
        
        # 获取所有支持的文件
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        pdf_extensions = ['.pdf']
        
        new_resumes = []
        
        # 检查图片文件
        for ext in image_extensions:
            image_files = glob.glob(os.path.join(self.inbox_dir, f"*{ext}"))
            for image_file in image_files:
                logger.info(f"发现新图片简历: {os.path.basename(image_file)}")
                
                # 运行OCR
                candidate_info = self.run_ocr_on_image(image_file)
                new_resumes.append(candidate_info)
                
                # 移动文件到已处理文件夹
                processed_path = os.path.join(self.processed_dir, os.path.basename(image_file))
                os.rename(image_file, processed_path)
                logger.info(f"已移动文件到已处理: {processed_path}")
        
        # 检查PDF文件（这里简化处理，实际需要PDF解析）
        for ext in pdf_extensions:
            pdf_files = glob.glob(os.path.join(self.inbox_dir, f"*{ext}"))
            for pdf_file in pdf_files:
                logger.info(f"发现新PDF简历: {os.path.basename(pdf_file)}")
                
                # 这里可以添加PDF解析逻辑
                new_resumes.append({
                    "姓名": "PDF候选人",
                    "教育": "需要PDF解析",
                    "来源文件": os.path.basename(pdf_file),
                    "文件类型": "PDF"
                })
                
                # 移动文件
                processed_path = os.path.join(self.processed_dir, os.path.basename(pdf_file))
                os.rename(pdf_file, processed_path)
        
        logger.info(f"发现 {len(new_resumes)} 份新简历")
        return new_resumes
    
    def evaluate_candidates(self, candidates: List[Dict], template_name: str) -> Dict:
        """评估候选人列表"""
        if template_name not in self.templates:
            logger.error(f"模板不存在: {template_name}")
            return {}
        
        template = self.templates[template_name]
        evaluations = []
        
        for candidate in candidates:
            # 简化评估逻辑
            score = 0
            
            # 学历评分
            if candidate.get('教育'):
                if '清华' in candidate['教育'] or '北大' in candidate['教育']:
                    score += 25
                elif '985' in candidate['教育'] or '211' in candidate['教育']:
                    score += 20
                elif '硕士' in candidate['教育'] or '博士' in candidate['教育']:
                    score += 15
            
            # 经验评分
            if candidate.get('工作经验'):
                if '5年' in candidate['工作经验'] or '6年' in candidate['工作经验']:
                    score += 25
                elif '7年' in candidate['工作经验'] or '8年' in candidate['工作经验']:
                    score += 30
                elif '3年' in candidate['工作经验'] or '4年' in candidate['工作经验']:
                    score += 20
            
            # 投资经验评分
            if candidate.get('投资经验'):
                if '3年' in candidate['投资经验'] or '4年' in candidate['投资经验']:
                    score += 30
                elif '5年' in candidate['投资经验'] or '6年' in candidate['投资经验']:
                    score += 35
                elif '2年' in candidate['投资经验']:
                    score += 25
            
            # 确定评估结果
            if score >= 80:
                result = "强烈推荐"
            elif score >= 70:
                result = "推荐"
            elif score >= 50:
                result = "可考虑"
            else:
                result = "不推荐"
            
            evaluation = {
                "候选人": candidate,
                "匹配分数": score,
                "评估结果": result,
                "评估时间": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            evaluations.append(evaluation)
        
        # 排序
        evaluations.sort(key=lambda x: x['匹配分数'], reverse=True)
        
        return {
            "评估时间": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "岗位模板": template_name,
            "总候选人": len(candidates),
            "评估结果": evaluations,
            "推荐名单": [e for e in evaluations if e['评估结果'] in ['强烈推荐', '推荐']]
        }
    
    def generate_daily_report(self, evaluation_result: Dict) -> str:
        """生成日报"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = os.path.join(self.results_dir, f"日报_{timestamp}.md")
        
        report_lines = []
        report_lines.append(f"# 🎯 猎头Agent日报 - {datetime.now().strftime('%Y年%m月%d日')}")
        report_lines.append("")
        
        # 统计信息
        total_candidates = evaluation_result.get('总候选人', 0)
        recommended = len(evaluation_result.get('推荐名单', []))
        
        report_lines.append("## 📊 今日统计")
        report_lines.append(f"- 处理时间: {datetime.now().strftime('%H:%M:%S')}")
        report_lines.append(f"- 处理简历: {total_candidates}份")
        report_lines.append(f"- 推荐候选人: {recommended}人")
        report_lines.append(f"- 岗位模板: {evaluation_result.get('岗位模板', '未知')}")
        report_lines.append("")
        
        # 推荐名单
        if recommended > 0:
            report_lines.append("## 🚀 今日推荐候选人")
            for i, candidate in enumerate(evaluation_result['推荐名单'], 1):
                cand_info = candidate['候选人']
                report_lines.append(f"### {i}. {cand_info.get('姓名', '未知')}")
                report_lines.append(f"- 匹配分数: {candidate['匹配分数']}分")
                report_lines.append(f"- 评估结果: {candidate['评估结果']}")
                
                if cand_info.get('教育'):
                    report_lines.append(f"- 教育背景: {cand_info['教育'][:80]}...")
                if cand_info.get('工作经验'):
                    report_lines.append(f"- 工作经验: {cand_info['工作经验']}")
                if cand_info.get('领域'):
                    report_lines.append(f"- 专注领域: {cand_info['领域']}")
                
                report_lines.append("")
        else:
            report_lines.append("## ℹ️ 今日无推荐候选人")
            report_lines.append("今日处理的简历中未发现符合条件的候选人。")
            report_lines.append("")
        
        # 处理详情
        report_lines.append("## 📝 处理详情")
        report_lines.append(f"- 输入文件夹: {self.inbox_dir}")
        report_lines.append(f"- 已处理文件夹: {self.processed_dir}")
        report_lines.append(f"- 报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        report_lines.append("---")
        report_lines.append("**生成系统**: 自动化猎头Agent")
        report_lines.append("**下次运行**: 明天 09:00")
        
        report = "\n".join(report_lines)
        
        # 保存报告
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"日报已生成: {report_file}")
        return report
    
    def daily_check_task(self):
        """每日检查任务"""
        logger.info("🔍 执行每日检查任务...")
        
        try:
            # 1. 检查新简历
            new_resumes = self.check_inbox_for_new_resumes()
            
            if not new_resumes:
                logger.info("今日无新简历")
                
                # 生成空报告
                empty_result = {
                    "评估时间": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "岗位模板": "泛硬科技投资总监",
                    "总候选人": 0,
                    "评估结果": [],
                    "推荐名单": []
                }
                
                self.generate_daily_report(empty_result)
                return
            
            # 2. 评估候选人（使用第一个模板）
            template_name = list(self.templates.keys())[0]
            evaluation_result = self.evaluate_candidates(new_resumes, template_name)
            
            # 3. 生成日报
            report = self.generate_daily_report(evaluation_result)
            
            # 4. 发送通知（这里简单记录到日志，实际可以发送邮件/消息）
            recommended_count = len(evaluation_result.get('推荐名单', []))
            logger.info(f"✅ 每日检查完成！推荐 {recommended_count} 位候选人")
            
            # 打印报告摘要
            print("\n" + "="*60)
            print("🎯 每日检查报告摘要")
            print("="*60)
            print(f"处理简历: {len(new_resumes)}份")
            print(f"推荐候选人: {recommended_count}人")
            
            if recommended_count > 0:
                print("\n推荐名单:")
                for i, candidate in enumerate(evaluation_result['推荐名单'], 1):
                    cand_info = candidate['候选人']
                    print(f"  {i}. {cand_info.get('姓名', '未知')} - {candidate['匹配分数']}分")
            
            print("="*60)
            
        except Exception as e:
            logger.error(f"每日检查任务失败: {e}")
    
    def start_daily_schedule(self, check_time="09:00"):
        """启动每日定时任务"""
        logger.info(f"设置每日检查任务: {check_time}")
        
        # 使用schedule库设置定时任务
        schedule.every().day.at(check_time).do(self.daily_check_task)
        
        # 立即运行一次（用于测试）
        logger.info("立即运行一次测试...")
        self.daily_check_task()
        
        # 启动调度线程
        self.running = True
        
        def run_scheduler():
            logger.info("定时任务调度器启动")
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info(f"定时任务已启动，每天 {check_time} 自动运行")
    
    def stop_scheduler(self):
        """停止定时任务"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("定时任务已停止")
    
    def run_once_now(self):
        """立即运行一次检查"""
        logger.info("手动触发立即检查")
        self.daily_check_task()

# 使用示例
if __name__ == "__main__":
    print("🚀 启动自动化猎头Agent...")
    
    # 创建Agent实例
    agent = AutomatedHeadhunterAgent()
    
    print(f"📁 简历收件箱: {agent.inbox_dir}")
    print(f"📁 请将简历截图放入收件箱文件夹")
    print(f"🕒 Agent将每天自动检查新简历")
    
    # 列出可用模板
    templates = agent.list_templates()
    print(f"📋 可用岗位模板: {', '.join(templates)}")
    
    # 启动定时任务
    print("⏰ 启动定时任务（每天09:00自动运行）...")
    agent.start_daily_schedule("09:00")
    
    print("\n✅ Agent已启动！")
    print("  1. 将简历截图放入收件箱文件夹")
    print("  2. Agent每天09:00自动处理")
    print("  3. 查看评估结果文件夹获取报告")
    print("  4. 按Ctrl+C停止Agent")
    
    try:
        # 保持主线程运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 收到停止信号，正在关闭Agent...")
        agent.stop_scheduler()
        print("✅ Agent已停止")