# AWS Greengrass 原始資料儲存器

這是一個 AWS Greengrass 元件，用於收集並將 IoT 設備的原始資料儲存為 CSV 檔案。它監控 GPIO 狀態和原始資料流，並在符合特定條件時儲存資料。

## 功能特點

- 監控設備影子（Device Shadow）的 GPIO 狀態變化
- 訂閱原始資料主題
- 根據 GPIO 狀態規則將資料儲存為 CSV 檔案
- 可配置的日誌級別
- 自動建立資料儲存目錄

## 系統需求

- AWS Greengrass Core v2
- Python 3.7+
- 必要的 Python 套件（見 requirements.txt）

## 安裝步驟

1. 複製此儲存庫
2. 安裝相依套件：
   ```bash
   pip install -r requirements.txt
   ```

## 配置說明

此元件需要以下參數：

- `--thing-name`：Greengrass Thing 名稱
- `--shadow-name`：Greengrass 影子名稱
- `--rawdata-topic`：讀取原始資料的主題
- `--write-rule`：資料寫入規則
- `--save-directory`：CSV 檔案儲存目錄（預設：/mnt/rawdata）
- `--log-level`：日誌級別（預設：INFO）

## 使用方式

使用必要參數執行程式：

```bash
python src/main.py --thing-name 您的設備名稱 --shadow-name 您的影子名稱 --rawdata-topic 您的主題 --write-rule 您的規則
```

## 資料格式

元件將資料以 CSV 格式儲存，結構如下：

1. 元資料標頭和資料列，包含：
   - 時間戳記
   - 取樣率
   - 資料長度
   - 資料標頭
2. 包含實際測量值的資料列

## 授權條款

版權所有 (c) 2024 Raw Data Dumper 貢獻者

本軟體及其相關文件檔案（以下簡稱「軟體」）的授權條款如下：

1. 本軟體僅供非商業用途使用，任何人在取得本軟體的副本後，必須遵守以下條件：

2. 在所有的副本或重要部分中，都必須包含上述版權聲明和本授權聲明。

3. 未經版權持有者明確書面許可，本軟體不得用於商業用途。

4. 本軟體按「原樣」提供，不提供任何明示或暗示的擔保，包括但不限於對適銷性、特定用途適用性和非侵權性的擔保。

5. 在任何情況下，作者或版權持有人均不對任何索賠、損害或其他責任負責，無論是在合同訴訟、侵權行為或其他方面，由軟體或軟體的使用或其他交易引起、產生或與之相關。
