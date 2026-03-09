#!/bin/bash
# 猎头Agent启动脚本

echo "🚀 启动自动化猎头Agent..."
echo "==============================="

# 创建工作目录
WORKSPACE="/root/.openclaw/workspace/vc_recruiter/猎头评估系统"
cd "$WORKSPACE"

# 检查必要目录
echo "📁 检查目录结构..."
mkdir -p "简历输入/收件箱"
mkdir -p "简历输入/已处理"
mkdir -p "简历输入/存档"
mkdir -p "评估结果"
mkdir -p "岗位模板"

echo "✅ 目录结构就绪"

# 检查必要的工具
echo "🔧 检查工具..."
if command -v tesseract &> /dev/null; then
    echo "✅ Tesseract OCR 已安装"
else
    echo "❌ Tesseract OCR 未安装"
    echo "安装命令: sudo apt install tesseract-ocr tesseract-ocr-chi-sim"
    exit 1
fi

# 运行简单的Agent测试
echo "🧪 运行Agent测试..."
python3 -c "
import os
import subprocess

# 创建默认模板
templates_dir = '岗位模板'
os.makedirs(templates_dir, exist_ok=True)

default_template = '''岗位名称: 泛硬科技投资总监
岗位描述: 硬科技领域投资总监
否决标准:
  学历: 硕士及以上学历，理工科背景
  经验: 5年以上硬科技产业或投资经验
  投资经验: 3年以上PE/VC投资经验
评估权重:
  教育背景: 25
  工作经验: 25
  投资经验: 30
  领域匹配: 20
领域专注: AI/半导体/新能源/商业航天
薪资范围: 80-200万
'''

template_file = os.path.join(templates_dir, '泛硬科技投资总监.yaml')
with open(template_file, 'w', encoding='utf-8') as f:
    f.write(default_template)

print('✅ 默认模板已创建')

# 测试OCR
test_image = '/root/.openclaw/media/inbound/4b1faa94-65c0-44fa-b7bd-6d74854e695d.jpg'
if os.path.exists(test_image):
    try:
        result = subprocess.run(['tesseract', test_image, 'stdout', '-l', 'chi_sim+eng'], 
                              capture_output=True, text=True, timeout=10)
        if result.stdout:
            text = result.stdout[:200]
            print(f'✅ OCR测试成功，提取文本: {text}...')
        else:
            print('⚠️ OCR返回空文本')
    except Exception as e:
        print(f'❌ OCR测试失败: {e}')
else:
    print('ℹ️ 无测试图片可用')
"

echo ""
echo "🎯 使用方法："
echo "1. 将简历截图放入: $WORKSPACE/简历输入/收件箱/"
echo "2. 运行Agent评估: python3 简易Agent.py"
echo "3. 查看评估结果: $WORKSPACE/评估结果/"
echo ""
echo "📅 建议设置定时任务（每天09:00运行）："
echo "crontab -e 添加："
echo "0 9 * * * cd $WORKSPACE && python3 简易Agent.py > agent_cron.log 2>&1"
echo ""
echo "✅ 准备就绪！"