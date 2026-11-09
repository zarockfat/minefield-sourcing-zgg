# OpenBoost 工具手册（本 skill 用到的部分）

服务端共 104 个工具，覆盖 Amazon / TikTok / 专利 / 社媒采集 / 账号五域。这里只列拆弹流水线真正需要的，参数为实测验证过的写法。

---

## Amazon 域

### `amz_aba_research_weekly` — ABA 搜索词周榜（需求信号主力）

必填：`webSiteId`

| 参数 | 说明 |
|---|---|
| `ds` | 查询日期 `yyyyMMdd`，传**查询周的周六**，如 `20261031` |
| `includeKeywords` / `excludeKeywords` | 包含/排除词，逗号分隔 |
| `exactFlag` | `true` 时只返回完全匹配 |
| `minSearches` / `maxSearches` | 搜索量区间 |
| `maxSearchRank` | 最大搜索排名 |
| `minTitleDensity` / `maxTitleDensity` | 标题密度 |
| `minMonopolyClickRate` / `maxMonopolyClickRate` | 点击集中度 |
| `minSpr` / `maxSpr` | SPR |
| `cat1NameList` | 一级类目数组，如 `["sports-and-outdoors"]` |
| `order.field` | `searchRank` / `cprExact` / `titleDensityExact` / `searches` |
| `order.desc` | `true` 降序 / `false` 升序 |
| `size` | **最大 15** |

返回关键字段：`searches`、`clicks`、`impressions`、`searchRank`、`searchRankCv`（周变化）、`w4SearchRank`、`w4RankGrowthRate`、`w12RankGrowthRate`、`top3ClickShareRate`、`top3CvsShareRate`、`titleDensityExact`、`cprExact`、`fstClkBrand`/`fstClkAsincode`/`fstClkAsinShare`（Top1 点击品牌/ASIN/份额）、`scd*`、`third*`。

### `amz_aba_research_trends` — ABA 排名趋势

必填：`webSiteId`、`keyword`、`timeGranularity`（`W` 周 / `M` 月）
返回 `weekRankJson` 或 `monthRankJson`。

### `amz_market_research` — 类目市场规模（供给结构）

必填：`marketplace`

| 参数 | 说明 |
|---|---|
| `nodeIdPath` | 类目路径，箭头分隔。**前缀式可模糊匹配父类目**：`"3760901->15342811"` 能命中子类目 |
| `month` | `yyyyMM`，不传取最新 |
| `order.field` | `total_units` / `total_amount` / `bsr_rank` / `price` / `rating` / `reviews` |
| `order.desc` | 默认 `true` |
| `topNum` | TopN 口径：3/5/10/20，默认 10 |
| `newProduct` | 新品周期（月）：1/3/6/12，默认 3 |
| `sellerLocation` | 卖家归属地中文，模糊匹配 |
| `size` | 最大 200 |

返回关键字段：`catId`、`catName`、`catCnName`、`catNamePaths`、`productCnt`、`avgSoldCntLst`、`totalSoldCntLst`、`avgSoldAmtLst`、`totalSoldAmtLst`、`avgPrice`、`avgScore`、`avgRatings`、`avgBsr`、`brandCnt`、`sellerCnt`、`avgSellerCnt`、`fbaRatio`、`fbmRatio`、`amzRatio`、`minDateFirstAvailable`、`maxDateFirstAvailable`、新品相关 `min/max` 字段。

### `amz_product_selection` — 商品级选品（落到底层商品）

必填：`webSiteId`

高频参数：

| 参数 | 说明 |
|---|---|
| `nodeIdPaths` | 类目 ID 路径数组，如 `["3375251"]` |
| `nodeIdPathEqual` | `true` 精确 / `false` 含子类目（默认） |
| `keyword` | 标题关键词，逗号分隔最多 100 个 |
| `matchType` | 1=词组 2=模糊子串（默认） 3=完全一致 |
| `month` | `yyyyMM`，**用月销筛选时必须传** |
| `minUnits` / `maxUnits` | SPU 月销量（需 `month`） |
| `minAmzUnit` / `maxAmzUnit` | SKU 月销量（需 `month`） |
| `minSpuSalesLast30d` / `minSkuSalesLast30d` | 近 30 天销量 |
| `minPrice` / `maxPrice` | 价格区间（字符串） |
| `minBsr` / `maxBsr` | 大类 BSR |
| `minSellers` / `maxSellers` | 卖家数 |
| `sellerNation` | 卖家所属地，如 `"中国,美国"` |
| `minVariations` / `maxVariations` | 变体数 |
| `badgeBS` / `badgeNR` | Best Seller / New Release 标识 `Y`/`N` |
| `sortField` / `sortOrder` | 单字段排序，字段名如 `spu_sales_last_30d` |
| `pagesSize` | 最大 100 |

返回关键字段：`sku_id`、`spu_id`、`item_title`、`item_link`、`main_image_url`、`brand_name`、`selling_price_dig`、`reviews_ratings`、`reviews_stars`、`date_first_available`、`cat_name_paths`、`cat_name_paths_cn`、`bus_cnty_cn`、`sku_cnt`、`spu_sales_last_30d`、`sku_sales_last_30d`、`seller_name`、`seller_item_cnt`、`fulfillment`、`is_a_plus`、`is_bestseller`、`score_map`（星级分布）、`item_feature`（五点描述）。

`main_image_url` 就是第 3 站专利检索的输入。

### `amz_category_query_v2` — 类目树

必填：`level`（1=拉一级类目及其完整子树）
可选 `webSiteId`、`current`、`size`（最大 5）
返回 `data.records[]`，每个节点含递归 `children`。

### `amz_review_query` — Amazon 评论

必填：`skuId`
可选 `webSiteId`（默认 1）、`current`、`size`（**最大 10**）
返回字段：`voiceScore`（星级）、`orginTitle`、`orginContent`、`gmtCreate`、`commentPlace`、`skuOption`、`voiceType`、`vine`

### `amz_market_seller_location` — 卖家所属地分布

必填：`marketplace`、`nodeIdPath`（须 `catIdPaths` **精确相等**）
可选 `month`、`topN`

> 注意：此接口对 `nodeIdPath` 要求精确匹配（不同于 `amz_market_research` 的前缀模糊）。传父类目 ID 会返回空数组。

### `amz_sku_query` — ASIN 详情

必填：`skuId`（**不是 `asin`**）
可选 `webSiteId`

---

## TikTok 域

### `tt_commodity_info_list` — 商品选品列表（信号源）

必填：`countryRegion`（中文，如 `"美国"`）

| 参数 | 说明 |
|---|---|
| `dataPeriod` | `last7d`（默认）/ `last30d` / `day` / `customScope` |
| `orderType` | `salesDesc` / `salesVolumeDesc` / `salesQoqDesc`（**销量环比，找暴增品**） |
| `salesStart` / `salesEnd` | 销量区间 |
| `priceStart` / `priceEnd` | 价格区间 |
| `scoreStart` / `scoreEnd` | 评分区间 |
| `powerSellerNumberStart` / `End` | 带货达人数区间 |
| `isNew` | `"1"` 新品 |
| `isCrossBorder` | `1` 全托管 |
| `commodityName` | 商品名关键词（**消耗搜索额度**） |
| `size` | 最大 30 |

### `tt_commodity_detail` — 商品详情

必填：`commodityId`、`countryRegion`
返回：`commodityTitle`、`price`、`totalSalesNumber`、`totalSaleIncomeNumber`、`powerSellerNumber`、`powerVideoNumber`、`commodityStarRate`、`reviewsNumber`、`shelfTime`、`inventorySummary`、`commissionRate`、`shopId`、`storeName`、`commodityImages`、`commodityThumbnailUrl`

> `commodityThumbnailUrl` 可作为专利图像检索的输入（TikTok 侧排雷）。

### `tt_commodity_voice_analyze` — 口碑分析（痛点逆向主力）

必填：`commodityId`
可选 `countryRegion`、`size`（**最大 10**）

返回 `data[]`，每块含 `type` / `typeName` / `openPointResponseList[]`：
- `typeName` 取值：`好评点` / `吐槽点` / `使用场景` / `时间频率`
- 每条：`result`（标签）、`percent`（占比%）、`number`（提及数）、`reason`（归因说明）

> 已聚类、带占比、带归因 —— 全网最好用的痛点数据形态。

### `tt_video_info_list` — 视频选品列表

必填：`countryRegion`
关键参数：`orderType`（`playNumberDesc` 等）、`dataPeriod`、`salesPeriod`、`videoTitle`、`expertId`、`commodityId`、`adSource`（0/1 是否投流）、`size`（最大 30）

### `tt_video_content` — 视频口播转写

必填：`videoId`，建议传 `countryRegion`
返回视频的口播/语音转写正文，可直接用于竞品话术拆解。

### `tt_expert_info_list` — 达人选品列表

必填：`countryRegion`（中文）
关键参数：`fansNumberStart/End`、`expertGPMStart/End`、`interactionRateStart/End`、`contactable`（`"1"` 可联系）、`hasVideo`、`expertCategory`

### `tt_dashboard_overview` / `tt_commodity_statistics_get_total_statistics`

大盘指标：总销量、总销售额、动销商品数、平均成交价、动销新品数。用于判断品类整体温度。

---

## 专利域

### `patent_image_search_single` — 以图搜外观专利（核心武器）

必填：`url`、`model`、`patent_type`

| 参数 | 说明 |
|---|---|
| `url` | 图片公网 URL（Amazon 主图 / TikTok 商品图均可） |
| `model` | 外观：1=智能联想，2=搜索此图；实用新型：3=匹配形状，4=匹配形状+图案+色彩 |
| `patent_type` | `D`=外观设计，`U`=实用新型 |
| `country` | 数组，如 `["US","EP","CN"]` |
| `query_text` | **Analytics 检索式，强烈建议必填**，如 `TACD:(yoga mat)` |
| `loc` | 洛迦诺分类，可用 AND/OR/NOT |
| `legal_status` | 法律状态码，逗号分隔 |
| `field` | 排序：`SCORE` / `APD` / `PBD` / `ISD` |
| `limit` | 1-100，默认 10 |

> **实测警告：不传 `query_text` 伪命中率极高。** 瑜伽垫主图无过滤时 Top1 是「柔性金属板」，命中 24150 条；加 `TACD:(yoga mat)` 后降到 17 条，全部相关。

返回 `data.total_search_result_count` 与 `data.patent_messages[]`：
`patent_pn`、`patent_id`、`title`、`current_assignee`、`original_assignee`、`inventor`、`apdt`（申请日）、`pbdt`（公开日）、`score`（相似度 0-1）、`authority`、`loc[]`、`url`（附图）

### `patent_image_search_multiple` — 多图融合检索

必填：`urls`（JSON 数组，1-4 张）、`model`、`patent_type`
其余同单图版。

### `patent_query_search` — 检索式检索

必填：`query_text`

检索式字段前缀：
- `ANCS` — 申请人/权利人
- `TACD` — 标题+摘要+权利要求+说明书
- `TAC` — 标题+摘要+权利要求
- `IPC` / `CPC` — 分类号

示例：`ANCS:(Spanx) AND TACD:(shapewear)`

返回 `data.total_search_result_count`、`data.results[]`（`pn`、`patent_id`、`title`、`original_assignee`、`current_assignee`、`inventor`、`apdt`、`pbdt`、`authority`）

### `patent_semantic_search` — 语义相似专利

必填：`text`（**建议 ≥200 字**技术描述）
可选 `country`（数组，如 `["USB","CNB"]`，后缀 A=申请/B=授权/U=实用新型/D=外观）、`relevancy`（如 `"70%"`）、`apd_from/to`、`pbd_from/to`、`limit`、`offset`

返回 `data.results[]` 含 `relevancy`（如 `"97%"`）。

### `patent_legal_status` — 法律状态（决定生死）

可选：`patent_id` 或 `patent_number`（至少一个，批量逗号分隔 ≤100）

返回 `data[].patent_legal`：
- `simple_legal_status[]` — 如 `["失效"]`
- `legal_status[]` — 如 `["期限届满"]`
- `event_status[]`

> **此接口返回「字段说明 markdown + 末尾内嵌原始 JSON」的包装格式**，`openboost_mcp.py` 已自动处理；若手写解析需注意。

外观专利保护期：美国 **15 年**（2013-05 后申请）、中国 **15 年**（2021-06 后）、欧盟 **25 年**。

### `patent_family` — 同族专利

按 `patent_id` 或 `patent_number` 查同族。用于判断「一个专利失效了，它的同族会不会在其他国家仍然有效」。

> 这一步容易被忽略但很关键：美国外观专利过期，不代表欧洲、日本同族也过期。要打多站点时必查。

### `patent_bibliography` / `patent_claim_data` / `patent_claim_translated`

`patent_bibliography` 拿完整著录项（百余字段）；`patent_claim_data` 拿权利要求原文；`patent_claim_translated` 拿**中文译文**（`lang` 参数），看不懂英文权项时用这个。

### `patent_abstract_translated` / `patent_description_translated`

摘要/说明书译文，`lang` 参数指定目标语言。

### `patent_pdf`

返回 PDF 全文下载地址（`data[].pdf.path`），交给专业人士做正式侵权分析时用。

---

## 账号域

### `account_info` — 套餐与余量

**每次跑流程前先调这个。** 返回 `services[]` 含 `apiName`、`planName`、`status`、`statusLabel`、`remaining`、`endingAt`。

### `account_catalog` — 套餐目录

`scope` — `all` / `mcp` / `api`；`platform` — `amazon` / `tiktok` / `patent` / `social`

---

## 通用坑位汇总

| 问题 | 正确做法 |
|---|---|
| 站点参数 | `webSiteId` 传数字字符串 `"1"`，不是 `"US"` |
| ASIN 参数名 | `amz_sku_query` 用 `skuId` |
| TikTok 地区 | 传中文 `"美国"` |
| ABA 日期 | `ds` 传查询周的周六 |
| 月销筛选 | 必须同时传 `month` |
| 分页上限 | TikTok `size` ≤30，口碑分析 ≤10，AMZ 评论 ≤10，ABA ≤15 |
| 类目路径精确度 | `amz_market_research` 前缀模糊；`amz_market_seller_location` 必须精确 |
| 专利图像检索 | 必须配 `query_text` 类目词 |
| 响应解析 | 可能两层序列化，或 markdown 文档包 JSON |
