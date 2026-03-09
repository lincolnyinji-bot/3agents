# 批量简历处理系统

## 目录结构
```
batch_processing/
├── input/              # 原始简历文件
│   ├── raw_pdfs/       # PDF简历
│   ├── raw_texts/      # 文本简历
│   └── raw_reports/    # 推荐报告
├── processed/          # 处理后的结构化数据
│   ├── csv/           # CSV格式
│   ├── json/          # JSON格式
│   └── parsed/        # 解析后的文本
└── output/            # 评估结果
    ├── evaluations/   # 详细评估
    ├── summaries/     # 摘要报告
    └── statistics/    # 统计信息
```

## 处理流程
1. 简历上传到 `input/` 对应目录
2. 运行 `batch_processor.py` 进行批量处理
3. 查看 `output/` 中的评估结果
4. 使用 `analyzer.py` 进行数据分析
5. 基于结果优化算法

## 文件命名规范
- 简历：`姓名_职位_公司_日期.pdf/txt`
- 推荐报告：`姓名_推荐报告_日期.txt`
- 评估结果：`批次_日期_评估.csv`

## 质量控制
- 每份简历人工验证关键信息
- 记录处理日志和错误
- 定期备份原始数据