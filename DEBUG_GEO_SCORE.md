# GEO Score 为 0 的诊断指南

## 问题描述
GEO Score 总是返回 0 分，可能的原因有多个。本文档帮助你诊断和修复问题。

## 可能的原因

### 1. probe_results 为空（最常见）

**症状：**
- GEO Score = 0.0
- 日志中显示 "Empty probe results, returning zero score"

**原因：**
- `probe_responses` 为空（没有成功查询到模型响应）
- `extract_entities` 步骤失败，返回空列表
- EntityExtractor 提取失败，返回了空的 ProbeResult 列表

**检查方法：**
查看日志中的以下信息：
```
Step 2: Querying models in parallel
Retrieved X probe responses
```

如果 X = 0，说明查询模型失败。

**修复方法：**
1. 检查 API 密钥配置（OpenAI, Google Vertex AI, Perplexity）
2. 检查网络连接
3. 检查模型服务是否可用

### 2. EntityExtractor 提取失败

**症状：**
- 有 probe_responses，但没有成功提取实体
- 日志显示 "Extracted entities from X probe responses" 但所有 has_target_brand 都是 False

**原因：**
- LLM 提取实体时失败（JSON 解析错误、API 调用失败等）
- 提取的 JSON 格式不符合预期
- target_brand 名称不匹配

**检查方法：**
查看日志：
```
Extracting entities from probe response: <probe_id>
Entity extraction completed. Target brand mentioned: False/True
```

**修复方法：**
1. 检查 EntityExtractor 的日志，查看 JSON 解析错误
2. 确认 target_brand 名称是否正确
3. 检查 OpenAI API 是否正常工作

### 3. 所有子评分都是 0

**症状：**
- probe_results 不为空
- 但所有 has_target_brand = False
- 所有 citations = 0
- 所有 ranking = None

**原因：**
- 目标品牌在所有查询中都没有被提及
- 没有引用链接
- 品牌名称不匹配

**检查方法：**
查看详细评分日志（已添加诊断信息）：
```
Calculating GEO Score from X probe results
Probe results summary: Total: X, Target mentioned: 0/X, Total citations: 0, Rankings: None
```

**修复方法：**
1. 检查目标品牌名称是否正确
2. 尝试不同的关键词
3. 检查目标品牌是否真的存在于相关查询的结果中

### 4. 数据序列化问题

**症状：**
- 工作流中 geo_score 不为空
- 但保存到数据库或返回给 API 时为 None 或 0

**原因：**
- GeoScore 对象序列化失败
- model_to_dict 转换时丢失数据

**检查方法：**
查看 API 日志：
```
GEO Score™ calculated: <score>
Audit workflow completed: <audit_id>
```

**修复方法：**
检查 `src/models/utils.py` 中的序列化逻辑

## 诊断步骤

### 步骤 1：查看日志

运行审计后，检查日志文件或控制台输出：

```bash
# 查看后端日志
tail -f logs/app.log | grep -E "GEO Score|probe_results|Extracted entities"
```

关键日志点：
1. `Retrieved X probe responses` - 应该 > 0
2. `Extracted entities from X probe responses` - 应该 > 0
3. `Probe results summary: Target mentioned: X/Y` - 应该 > 0
4. `GEO Score calculation completed. Overall: X.XX` - 应该 > 0

### 步骤 2：检查数据库

连接到 MongoDB，查看审计结果：

```python
from src.database.mongodb_pool import get_pool
from src.database.operations import find_one
import asyncio

async def check_audit(audit_id):
    await get_pool()
    doc = await find_one("audit_results", {"audit_id": audit_id})
    print(f"GEO Score: {doc.get('geo_score', {}).get('overall_score') if doc.get('geo_score') else None}")
    print(f"Status: {doc.get('status')}")
    print(f"Probe results count: {len(doc.get('probe_results', []))}")

# 使用
# asyncio.run(check_audit("your_audit_id"))
```

### 步骤 3：手动测试评分器

创建一个测试脚本：

```python
# test_scorer.py
from src.scorers import GeoScorer
from src.models.analysis import ProbeResult, BrandMention, Sentiment
from datetime import datetime

# 创建一个测试 ProbeResult
test_result = ProbeResult(
    probe_id="test_001",
    probe_type="direct_recommendation",
    keyword="test keyword",
    model="gpt-4o",
    temperature=0.7,
    brand_mentions=[
        BrandMention(
            brand_name="TestBrand",
            is_mentioned=True,
            ranking=1,
            sentiment=Sentiment.POSITIVE,
            mention_text="TestBrand is great"
        )
    ],
    total_mentions=1,
    has_target_brand=True,
    target_brand_ranking=1,
    target_brand_sentiment=Sentiment.POSITIVE,
    official_citations_count=1,
    authoritative_citations_count=0,
    timestamp=datetime.utcnow()
)

# 测试评分器
scorer = GeoScorer()
geo_score = scorer.calculate_geo_score([test_result])
print(f"Test GEO Score: {geo_score.overall_score}")
print(f"Breakdown: {geo_score.breakdown}")
```

如果测试脚本返回非 0 分，说明评分器本身没问题，问题在于数据。

## 常见修复方案

### 修复 1：确保 API 密钥配置正确

检查 `.env` 文件：
```bash
OPENAI_API_KEY=your_key_here
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
PERPLEXITY_API_KEY=your_key_here
```

### 修复 2：检查品牌名称匹配

确保 `target_brand` 与查询结果中实际出现的品牌名称匹配（注意大小写、空格等）。

### 修复 3：增加调试日志

已添加诊断日志，查看：
- `src/scorers/geo_scorer.py` - 评分计算时的诊断信息
- `src/workflows/geo_workflow.py` - 工作流各步骤的诊断信息

### 修复 4：检查网络和 API 服务

确保能够访问：
- OpenAI API
- Google Vertex AI（如果使用）
- Perplexity API（如果使用）

## 下一步

如果以上步骤都无法解决问题，请：
1. 收集完整的日志输出
2. 记录一个具体的 audit_id
3. 检查数据库中该 audit 的完整数据
4. 报告问题并附上这些信息

