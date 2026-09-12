# 项目当前状态

**项目主题：** Cross-ancestry genetic effects of refractive error × retinal regulatory architecture  
**状态快照：** 2026-09-12  
**当前阶段：** Phase 2B post-primary robustness 已完成；停止 discovery analysis，进入 manuscript preparation  
**总体判定：** `MANUSCRIPT_GO_SHARED_ARCHITECTURE`

## 一句话结论

Phase 1B 的历史 source-level build 审计仍记录为 `NO-GO`，但 Phase 1C 已用 dbSNP Build 151 双 assembly 参考和独立 holdout 完成经验性 build adjudication：EUR/EAS/AFR 的释放坐标与 GRCh37 一致。Phase 1C.2 已完成 formal genome-wide EUR-EAS S-LDXR，GCORSQ 为 1.0099±0.1083，稳定性 PASS。Phase 2 Route B 已按正式 freeze 执行 DAR 异质性富集主检验，feature QC 全部 PASS；但 DAR vs matched non-DAR retinal OCR 的 top 5% heterogeneity enrichment 未获支持（OR=1.119，95% CI 0.867-1.423，Fisher P=0.367；matched permutation empirical P=0.334）。Phase 2B 进一步完成 primary reproduction、LD-reduced sensitivity、block-level robustness、effect-size precision、power bounds、broad retinal OCR S-LDXR context、cell-class descriptive summary 和 matching balance audit。最终判定为 `MANUSCRIPT_GO_SHARED_ARCHITECTURE`：论文主线应转为 predominantly shared EUR-EAS genetic architecture of refractive error, without detectable excess heterogeneity in ancestry-associated retinal regulatory regions。

> `reports/PHASE1B_DECISION.md` 是历史审计记录，保持不变；Phase 1C 的 reference-anchored 决策见 `reports/PHASE1C_BUILD_RESCUE_DECISION.md`。

## 当前 Gate 快照

| Gate | 当前状态 | 关键证据 |
|---|---|---|
| Phase 1C build adjudication | `PASS` | GRCh37 22 条常染色体均 100% 坐标一致；holdout 100% |
| canonical GWAS anchoring | `STRONG` | 3,261,022 / 3,262,168 行成功锚定 |
| retina liftover | `REVIEW_REQUIRED` | DAR 99.6858%；OCR union 99.8723%；宽度保持率已单独记录 |
| build-resolved overlap | `CONDITIONAL` | DAR global overlap 1,324；分祖源层级稀疏 |
| ancestry-matched LDSC h² | `COMPLETE` | EUR 0.1219±0.0072；EAS 0.1494±0.0119 |
| paired S-LDXR reference/score QC | `PASS` | row identity 22/22；baseline numerical 66/66；all-score universe 330/330 |
| formal genome-wide S-LDXR | `PASS` | GCORSQ 1.0099±0.1083；3,112,573 SNP；200-block jackknife PASS |
| global annotation pilot | `COMPLETE_ESTIMABILITY_ONLY` | OCR、DAR、matched non-DAR 均可计算；DAR shared usable SNP N=1,232，SE=0.5771 |
| Phase 2 Route B primary test | `PRIMARY_ENRICHMENT_NOT_SUPPORTED` | 3,112,573 formal SNP；DAR N=1,232；matched permutation empirical P=0.334 |
| Phase 2B robustness | `COMPLETE` | LD-pruned/block-level consistent；80% MDE OR=1.397；large enrichment OR=1.5 excluded |
| Manuscript readiness | `READY_FOR_DRAFTING` | manuscript tables and figure-ready TSVs generated; discovery stop rule active |

## 已完成工作

### 1. GWAS 数据审计

三份 ancestry-specific GWAS 文件均已完成下载完整性和基础格式审计，文件大小、SHA256 与远端记录一致。

| 数据集 | 总行数 | 双等位 SNP | 非 SNP/indel | 模糊链 SNP | `P < 5×10⁻⁸` |
|---|---:|---:|---:|---:|---:|
| EUR | 5,590,053 | 5,260,419 | 329,634 | 813,247 | 28,219 |
| EAS | 4,739,897 | 4,324,533 | 415,364 | 671,853 | 1,756 |
| AFR | 9,519,284 | 8,765,891 | 753,393 | 1,353,959 | 63 |

已记录的 GWAS 文件：

- `data/raw/gwas/` 下的 EUR、EAS、AFR 原始文件均已完成完整性校验。
- 跨祖源 METAL 文件已登记，但仅包含 Z 值，并含有 indel；目前不用于 EUR/EAS beta harmonization。

### 2. EUR–EAS harmonization

EUR 与 EAS 已基于 `CHR:POS` 完成位置匹配、等位基因方向处理和 palindromic SNP 排除。

| 指标 | 数值 |
|---|---:|
| EUR 有效且唯一的双等位 SNP | 5,260,419 |
| EAS 有效且唯一的双等位 SNP | 4,324,243 |
| `CHR:POS` 匹配位点 | 3,863,376 |
| 共同可用的非 palindromic 位点 | 3,262,663 |
| 等位基因匹配后的最终共享 SNP | 3,262,168 |
| 排除的 palindromic SNP | 600,713 |
| 未解决的等位基因不一致 | 671 |
| 共同可用非 palindromic 位点匹配率 | 0.999848 |
| allele flip count | 0 |
| strand-resolved count | 7 |

主结果文件为 `data/processed/EUR_EAS_HARMONIZED.parquet`，包含 3,262,168 行、22 列，已验证可读。该结果说明 EUR/EAS 的效应方向和等位基因 harmonization 在技术上可执行，但不等同于正式的 genetic correlation 结果。

### 3. 效应方向一致性审计

效应方向审计已完成，结果仅用于 QC 和优先级判断：

| 比较集合 | SNP 数 | Pearson | Spearman | 同方向比例 |
|---|---:|---:|---:|---:|
| 全部共享非 palindromic SNP | 3,262,168 | 0.2046 | 0.1464 | 0.5427 |
| EUR genome-wide significant SNP 在 EAS 中 | 20,104 | 0.7544 | 0.7413 | 0.8552 |
| EAS genome-wide significant SNP 在 EUR 中 | 1,435 | 0.8600 | 0.7647 | 0.9707 |

另有一项基于 `±250 kb` 位置窗口的 lead-SNP 诊断，但该结果不是 LD-independent 分析，不能替代 formal cross-ancestry genetic correlation 或 locus-level analysis。

### 4. 视网膜调控资源解析

HRCA supplementary resources 已完成初步整理：

- 有效的 HRCA M4 Excel 重试文件：`data/raw/retina/HRCA_41588_2025_2454_MOESM4_retry1.xlsx`
- 原始不完整/损坏文件仍被保留，未覆盖。
- HRCA M1 PDF 已通过 MinerU 完成分段解析。
- 已确认 S19 使用 hg38；S20/S21 使用 hg19。
- 已提取 S19 ancestry-DAR 表：2,228 行、2,227 个 unique intervals。
- 已提取 S12K union OCR 表：700,146 个区间。
- 已建立 `BC → Bipolar`、`AC → Amacrine`、`MG → Muller_glia` 的细胞类别映射。
- RPE 尚未在当前 S12/S19 主资源中确认，暂不纳入主分析。

HRCA S19 中的 East Asian ancestry-specific DAR 在部分细胞类别中较稀疏，尤其需要避免把缺少显著 DAR 解读为生物学上的“无效”或“无差异”。

### 5. 条件性 retinal annotation QC

在 Phase 1C reference-anchored 状态下，当前重叠统计已可作为 build-resolved QC；仍需等待下游统计 gate 后才能作生物学解释：

| 注释资源 | build | 注释区间 | 坐标诊断可用 SNP | 当前解释 |
|---|---|---:|---:|---|
| HRCA S19 ancestry DAR union | hg38 | 2,227 | 1,466 | conditional；不能作为生物学富集结论 |
| HRCA S12K union OCR | hg38 | 700,146 | 410,516 | technical positive control |
| S12K matched non-DAR OCR | hg38 | 697,837 | 408,977 | 操作性匹配对照；不代表已证明祖源间稳定 |

已形成的分析定义是：matched non-DAR OCR 作为主要 stable comparator；但 “non-DAR” 只表示未被当前 DAR 表标记，不能直接证明其在祖源间稳定。

### 6. S-LDXR 输入准备

S-LDXR 软件已克隆至：

`/Users/zy/.codex/tools/s-ldxr`

当前 S-LDXR 运行环境已可用，paired score 生成命令正在实际运行。正式分析状态仍取决于全部行身份、数值、score universe 和 freeze gate，而非软件能否启动。

过滤后的 S-LDXR 输入：

| Ancestry | 原始行数 | 双等位 SNP | 移除 palindromic | 移除重复 SNP | 输出行数 |
|---|---:|---:|---:|---:|---:|
| EUR | 5,590,053 | 5,260,419 | 813,247 | 1 | 4,447,171 |
| EAS | 4,739,897 | 4,324,533 | 671,853 | 5 | 3,652,675 |

历史过滤文件为 `data/interim/sldxr/EUR_sumstats.gz` 和 `data/interim/sldxr/EAS_sumstats.gz`。由于 S-LDXR 的交集步骤不负责重新排序，这两份历史文件没有进入正式回归。正式专用、与 score universe 同序的文件位于 `data/interim/sldxr_formal/`，EUR/EAS 共同保留 3,112,573 行，ordered-key SHA256 均为 `de1c5edf6d34928eaf6df5bd62c681c4902370e58ae2273afa870b44eb950d55`。baseline、all retinal OCR、DAR、matched non-DAR 和 weights score universe 均已通过统一 hard gate。

### 7. Phase 2 Route B 主检验

Phase 2 formal freeze 已生成：`config/PHASE2_ANALYSIS_FREEZE_v1.yaml`。主分析矩阵为 `data/processed/phase2/EUR_EAS_HETEROGENEITY_FEATURES.parquet`，保留 3,112,573 个 formal SNP，所有 `chi2_het` 均有限。

主结果文件为 `results/phase2/PHASE2_DAR_HETEROGENEITY_ENRICHMENT.tsv`。DAR vs matched non-DAR retinal OCR 的 top 5% 异质性富集未获支持：DAR 71/1,232，matched non-DAR 19,653/379,279，OR=1.119，P=0.367。连续 `chi2_het` Mann-Whitney P=0.711。严格分层 matched permutation 在 60,284 个可比较 SNP 中运行 1,000 次，observed mean chi-square difference=0.0647，empirical P=0.334。

完整报告见 `reports/PHASE2_ROUTE_B_PRIMARY_RESULTS.md`。

### 8. Phase 2B post-primary robustness

Phase 2B formal freeze 已生成：`config/PHASE2B_ROBUSTNESS_FREEZE_v1.yaml`。Primary reproduction 与 Phase 2 原始结果完全一致，所有 delta 均在预设容差内。LD-reduced sensitivity 使用 EUR/EAS paired PLINK reference、500 kb window、label-blind pruning；r²<0.1 后 DAR SNP N=9，top 5% P=0.0544；r²<0.01 后 DAR SNP N=1，top 5% P=1.0。由于 pruned DAR SNP 数很少，LD-pruned 结果应作为 sensitivity 而非主证据。

Block-level robustness 使用项目既有 S-LDXR 200-block jackknife boundaries；blocks with ≥1 DAR SNP vs non-DAR blocks 的 adjusted OLS P=0.3836，未提示 SNP-level pseudoreplication 改变主结论。Primary effect-size precision 显示 OR=1.119，95% CI 0.867-1.423；以 OR=1.5 作为 large-enrichment boundary，当前 CI 可排除 large enrichment。Power bounds 显示当前 DAR N=1,232 对 80% power 的 MDE OR 约为 1.397，对 90% power 的 MDE OR 约为 1.467；因此不能排除 modest enrichment。

Broad retinal OCR contextual S-LDXR 为 GCORSQ=0.9354±0.1011，和 genome-wide GCORSQ=1.0099±0.1083 broadly compatible。DAR S-LDXR 仅作 underpowered descriptive：0.5712±0.5771，N=1,232。

最终报告见 `reports/PHASE2B_FINAL_DECISION.md`。

## 当前未完成事项

### 1. GWAS source-level build 声明仍缺失，但分析 build 已救援

当前记录显示：

- GWAS EUR/EAS/AFR 及 cross-ancestry 文件仍没有上游来源级 assembly 声明。
- 独立 dbSNP Build 151 经验性 adjudication 支持 GRCh37；统一分析 build 冻结为 GRCh37.p13，所有 canonical coordinates 均保留可追溯 mapping 字段。
- HRCA S12/S19 为 hg38，HRCA S20/S21 为 hg19。
- LDSC 参考资源遵循 GRCh37-compatible convention。

source-level 缺失仍需在论文 provenance 中如实报告；在此之前，正式结果只能表述为 reference-anchored analysis。不能把 DAR overlap、富集比例或细胞类别差异写成机制或临床结论。

### 2. Ancestry-matched LDSC h² 已完成

`results/phase1/LDSC_H2_SUMMARY.tsv` 当前状态如下：

| Ancestry | 状态 | h² | h² SE | h² Z | 说明 |
|---|---|---:|---:|---:|---|
| EUR | `RUN_AND_BUILD_RESOLVED` | 0.1219 | 0.0072 | 16.93 | baseline/weights 22 条染色体，参考包 MD5/gzip 通过 |
| EAS | `RUN_AND_BUILD_RESOLVED` | 0.1494 | 0.0119 | 12.55 | baseline/weights 22 条染色体，参考包已可运行 |
| EUR | `DIAGNOSTIC_GENERIC_REFERENCE` | 0.0904 | 0.0046 | 19.65 | generic 1000G reference；仅诊断 |
| EAS | `DIAGNOSTIC_GENERIC_REFERENCE` | 0.1069 | 0.0081 | 13.20 | generic 1000G reference；仅诊断 |

EUR 的损坏 baseline tarball 已隔离保留，新的官方包已通过 MD5 `b261e0caf06a003e7522938e01b3d349` 和 gzip 校验并安装到 canonical raw 路径。generic-reference h² 仍仅作诊断，不替代 ancestry-matched 结果。

### 3. 配对 S-LDXR reference、baseline 修复及正式 GCOR² 已完成

S-LDXR 所需 ancestry-paired LD scores、weights、MAF、严格同序 annotation 和 formal-only sumstats 均已冻结。旧 baseline score 保留但永久排除。正式分析完成于 3,112,573 个 SNP，并通过 200-block jackknife与染色体影响诊断；LDSC triangulation 判定为 `CONDITIONAL_COMPATIBLE`。完整判定见 `reports/PHASE1C2_SLDXR_BASELINE_DECISION.md`。

当前可用的 QC 文件为：

- `results/phase1c/SLDXR_PANEL_PAIRING.tsv`：22/22 `PASS`；
- `results/phase1c/SLDXR_REFERENCE_QC.tsv`：44/44 `PASS`；
- `results/phase1c/SLDXR_SCORE_QC.tsv`：第一代文件生成记录 66/66 `PASS`，但 baseline annotation 行集合不一致，不能作为 formal-ready 证据；
- `results/phase1c/SLDXR_BASELINE_ANNOTATION_ALIGNMENT.tsv`：22/22 `PASS`；
- `results/phase1c/SLDXR_SCORE_QC_ALIGNED_BASELINE.tsv`：66/66 `PASS`；
- `results/phase1c/SLDXR_FORMAL_SUMSTATS_ALIGNMENT.tsv`：1/1 `PASS`；正式 EUR/EAS summary statistics 共 3,112,573 行且顺序哈希一致。
- `reports/SLDXR_INVALID_BASELINE_PROVENANCE.md`：旧 baseline score 及受影响第一代结果已标记为 `INVALID_FOR_FORMAL_ANALYSIS_ROWSET_MISMATCH`。

## 当前决策（Phase 2B 后）

Phase 2 Route B 的主检验已经执行，但未支持 ancestry-DAR SNP 中存在显著 excess EUR-EAS effect heterogeneity。Phase 2B 未发现明确 technical failure。按 freeze 和 stop rule，所有 discovery analysis 停止；下一阶段只允许 manuscript drafting、figure/table preparation、methods documentation 和基于现有 frozen results 的 reviewer-style robustness checks。

### 允许继续

- 把 Phase 1C.2 genome-wide shared architecture 写成主线结果；
- 把 Phase 2 Route B negative primary result 写成约束性结果；
- 使用已生成的 manuscript tables 和 figure-ready data 准备论文；
- 准备论文结构，但不得把 DAR heterogeneity enrichment 写成阳性机制发现。

### 暂不允许

- 继续任何新的 discovery analysis；
- 继续进入 locus/CRE/motif 阳性发现叙事；
- 宣称 ancestry-DAR 区域富集了 EUR-EAS 异质性；
- 将 DAR/OCR 坐标重叠直接解释为视网膜调控富集或机制；
- 进行细胞类型富集、fine-mapping、TWAS/SMR、MR 或药物靶点结论；
- 基于当前 DAR 结果撰写阳性摘要。

## 继续推进与最终放行条件

1. 保留并报告 source-level assembly 缺失；同时固定 GRCh37.p13 reference-anchored 坐标和 dbSNP/chain provenance。
2. 将正式 genome-wide S-LDXR 和 LDSC triangulation 作为主线结果。
3. 将 Phase 2 Route B 写成 negative/unsupported primary enrichment gate。
4. 使用 Phase 2B precision/power 结果界定“未检测到明显富集”和“不能排除 modest enrichment”的边界。
5. 下一步进入 manuscript drafting。

## 关键结果文件

- `reports/PHASE0_1_DECISION.md`
- `reports/GWAS_DATA_AUDIT.md`
- `reports/EFFECT_DIRECTION_AUDIT.md`
- `reports/RETINAL_POSITIVE_CONTROL.md`
- `reports/STABLE_VS_ANCESTRY_SENSITIVE_DEFINITION.md`
- `reports/SLDXR_FEASIBILITY.md`
- `reports/GWAS_BUILD_EVIDENCE.md`
- `reports/PHASE1B_DECISION.md`
- `results/phase0/GWAS_QC_SUMMARY.tsv`
- `results/phase0/EUR_EAS_HARMONIZATION.tsv`
- `results/phase0/EUR_EAS_HARMONIZATION_METRICS.tsv`
- `results/phase0/BUILD_HARMONIZATION.tsv`
- `results/phase0/RETINAL_ANNOTATION_QC.tsv`
- `results/phase1/LDSC_H2_SUMMARY.tsv`
- `results/phase1/SLDXR_INPUT_FILTER.tsv`
- `results/phase1c/GWAS_RSID_COVERAGE.tsv`
- `results/phase1c/EMPIRICAL_BUILD_CONCORDANCE.tsv`
- `results/phase1c/EMPIRICAL_BUILD_BY_CHROMOSOME.tsv`
- `results/phase1c/LD_REFERENCE_VARIANT_ANCHORING.tsv`
- `results/phase1c/RETINA_LIFTOVER_QC.tsv`
- `results/phase1c/BUILD_RESOLVED_SNP_COUNTS.tsv`
- `results/phase1c/SLDXR_PANEL_PAIRING.tsv`
- `results/phase1c/SLDXR_REFERENCE_QC.tsv`
- `results/phase1c/SLDXR_SCORE_QC.tsv`
- `config/PHASE2_ANALYSIS_FREEZE_v1.yaml`
- `data/processed/phase2/EUR_EAS_HETEROGENEITY_FEATURES.parquet`
- `results/phase2/PHASE2_HETEROGENEITY_FEATURE_QC.tsv`
- `results/phase2/PHASE2_DAR_HETEROGENEITY_ENRICHMENT.tsv`
- `reports/PHASE2_ROUTE_B_METHOD_DESIGN.md`
- `reports/PHASE2_ROUTE_B_PRIMARY_RESULTS.md`
- `config/PHASE2B_ROBUSTNESS_FREEZE_v1.yaml`
- `results/phase2b/PRIMARY_RESULT_REPRODUCTION.tsv`
- `results/phase2b/LD_PRUNED_SNP_UNIVERSE.tsv`
- `results/phase2b/LD_PRUNED_HETEROGENEITY_SENSITIVITY.tsv`
- `results/phase2b/LD_BLOCK_HETEROGENEITY_SUMMARY.tsv`
- `results/phase2b/LD_BLOCK_ROBUSTNESS.tsv`
- `results/phase2b/PRIMARY_EFFECT_SIZE_PRECISION.tsv`
- `results/phase2b/DAR_POWER_BOUNDS.tsv`
- `results/phase2b/RETINAL_OCR_SLDXR_CONTEXT.tsv`
- `results/phase2b/CELL_CLASS_DESCRIPTIVE_HETEROGENEITY.tsv`
- `results/phase2b/MATCHED_PERMUTATION_BALANCE_AUDIT.tsv`
- `results/phase2b/EQUIVALENCE_BOUNDARY.tsv`
- `reports/PHASE2B_POWER_INTERPRETATION.md`
- `reports/PHASE2B_FINAL_DECISION.md`
- `results/manuscript/TABLE1_ANALYSIS_COHORT_AND_QC.tsv`
- `results/manuscript/TABLE2_DAR_HETEROGENEITY_RESULTS.tsv`
- `results/manuscript/TABLE3_REGULATORY_ARCHITECTURE_CONTEXT.tsv`

## 当前项目状态标签

`RESCUED_FOR_REFERENCE-ANCHORED_ANALYSIS` · `source-level build declaration absent` · `ancestry-matched LDSC complete` · `formal S-LDXR complete` · `Phase 2 Route B primary enrichment not supported` · `Phase 2B robustness complete` · `MANUSCRIPT_GO_SHARED_ARCHITECTURE` · `STOP_DISCOVERY_ANALYSIS`
