# 首次使用

每個 AI agent session 共用一次套件開場。第一次實際執行 `program-animation` 或 `animation-grill`，包含接續既有作品的製作與修改，都先執行以下流程。用目前 session 的對話與工具結果記住檢查結果、歡迎是否已顯示，以及更新選擇是否待回覆。換技能、換階段或處理同一 session 的下一個作品時沿用該狀態。新 session 重新檢查。查看、安裝或維護技能本身時跳過開場。

## 先查版本

從目前載入的 `program-animation` 安裝目錄執行 `python3 scripts/check_update.py`，也可將指令中的腳本換成其絕對路徑。同套件的 `animation-grill` 使用相鄰的 `program-animation`。檢查器比較安裝目錄的 `VERSION` 與 [原倉庫 main 的 VERSION](https://raw.githubusercontent.com/shoung/ProgramAnimation-skills/main/skills/program-animation/VERSION)，可在任意專案目錄執行，也適用於複製安裝。

若環境限制腳本連網，可以用可用的 GitHub 讀取工具讀取同一檔案。比較三段數字，例如 `1.10.0` 大於 `1.9.0`。若仍讀不到版本，或本機缺版本資料，簡短說明本次無法確認並使用目前的技能繼續。

## 顯示歡迎

將 [SHOUNG ASCII 標記](../assets/shoung-logo.txt) 的完整內容放在純文字程式碼區塊，於對話中原樣顯示一次，接著用使用者的語言呈現這段說明。標記與歡迎專供對話開場。

> 歡迎使用 ProgramAnimation。告訴我你想做什麼動畫、想給誰看，已有故事或畫面想法也可以直接貼上來。用 `$program-animation` 開始，我會逐題問清楚，把劇本和分鏡放在對話裡給你確認。接著一起看風格預覽，選定後用程式完成畫面和聲音。若只想整理構想或釐清改片意見，可以用 `$animation-grill`。

## 依版本結果接續

- 若結果是 `update_available`，在開場說明本機與上游的版本號，附上[原倉庫](https://github.com/shoung/ProgramAnimation-skills)，詢問「要先更新再開始，還是這次先用目前的版本？」這輪只問更新選擇，收到答覆後再開始訪談或製作。
- 若使用者要更新，或已明確授權先更新，依原本安裝方式同步更新兩個技能，再確認已載入新版並接回本次任務。若執行環境需要重新載入技能，告知如何接回目前的任務。若使用者選擇沿用目前版本，這個 session 直接接續。
- 若已是最新、本機較新，或這次無法確認版本，歡迎後即可接續使用者原本的請求。
