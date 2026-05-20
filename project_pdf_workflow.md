---
name: pdf-processing-workflow
description: 银行函证PDF处理工作流（整理PDF文件编辑）
metadata: 
  node_type: memory
  type: project
  originSessionId: 996c414e-0a34-4e80-91d3-cba583b2d9a6
---

# 整理PDF文件编辑 — 银行函证PDF处理

完整的PDF处理工作流记录在 `C:\Users\AORUS\CLAUDE.md`。

## 核心脚本
- `C:\Users\AORUS\tmp\reprocess_pdfs.py` — 主脚本，给PDF添加参考编号、签名、remark、页码

## 关键要点
- 部分PRC银行PDF旋转270°（mediabox 842×595，rect 595×842），需用 `rotate=270` 参数抵消
- 坐标转换（rot=270）：`raw_x = mb.width - y_disp`, `raw_y = disp_x`
- 从输出文件名提取日期追加到remark，签名日期晚于文件名日期则更新签名
- Excel路径：`D:/AI/整理hard copy/整理hard copy/T780_QE100_Bank and cash_2025.xlsx`

## 运行
```bash
powershell -Command 'Stop-Process -Name "wps","wpspdf" -Force -ErrorAction SilentlyContinue'
/c/Users/AORUS/AppData/Local/Programs/Python/Python312/python.exe /c/Users/AORUS/tmp/reprocess_pdfs.py
```