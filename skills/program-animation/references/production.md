# 製作與品管

以下指令從 `program-animation` 技能目錄執行，預覽 PNG 已隨附。重畫樣本需 Python 3.9 以上及 `requirements.txt` 的套件。影片編碼和聲音轉檔另需 PATH 中的 FFmpeg、ffprobe 與 libx264 編碼器。範例可作為單鏡起點，完整成片應依分鏡自訂內容、尺寸及片長。

## 畫面與時間軸

```sh
python3 -m pip install -r requirements.txt
python3 scripts/render.py --style clear-line --png /tmp/still.png
python3 scripts/render.py --style clear-line --seconds 6 --fps 24 --video /tmp/study.mp4
python3 scripts/gallery.py
```

每一款的 `frame(t)` 接受以弧度表示的一個循環相位，回傳含風格題字的 Pillow 圖像。傳入 `title` 與 `font_path` 可換片名，空字串可輸出無題字畫面。[字樣與排版範例](lettering.md)。`coast.py` 描述圖形版的場景與語意色塊，`miniature.py` 提供等角模型。`headland.py` 描述台地與地標，`print_landscape.py` 提供印刷畫法可調整的山勢、雲帶與水紋，點雲程式自繪粒子光束，`night.py` 則供雙色抖動取樣夜景。要製作全新的影片，可讓 `draw_shot(i)` 依總幀號查找鏡頭及鏡內時間，再選對應的畫法。長片可按鏡頭分批，快取檔以來源版本、參數與幀號對應，接續渲染時重新驗證讀回的影格。

## 每幀檢查與恢復

`scripts/checked_render.py` 可接其他後端。將含此模組的 `scripts` 資料夾加入 Python 匯入路徑。以下為串接範式，函式名代表你的鏡頭程式應提供的介面。

```python
from checked_render import checked_frame, encode


def frames():
    for i in range(frame_count):
        yield checked_frame(
            i,
            draw_shot,
            (width, height),
            restart=recreate_renderer,
            flat=planned_hold_rgb(i),  # 一般影格回傳 None，全黑轉場可回傳 (0, 0, 0)
            probes=subject_boxes(i),  # 一般影格內，預期看得到細節的矩形
            verify=matches_shot,  # 可選的場景檢查，接受 (i, RGB影格)
        )


encode(movie_path, frames(), count=frame_count, size=(width, height), fps=fps, audio=mix_path)
```

檢查器會在白色底合成透明圖層，再驗證尺寸、全透明與實際色差。成片要用其他底色時，讓後端先依該底色合成。對接近全黑、仍看得見輪廓的淡出幀，可指定 `min_contrast=0`，並用主體區或 `verify` 核對輪廓。此時真正的單色影格仍會被攔下。若輸出透明母帶，保留原 RGBA 走支援 alpha 的編碼路徑，另用合成畫面做內容檢查。

瀏覽器有時仍回傳尺寸正常的 PNG，畫布內的 GPU 圖層卻已經消失。讀回**完成繪製的畫布或最終合成影格**。若紙紋背景、字幕或 DOM 仍有內容，全圖色差可能通過，此時按鏡設定主體區域或比對空背景與主體遮罩。讓 `verify` 在關鍵位置回傳實際內容是否存在；預期留白時改用該幀自己的判準。讀回前等待資產、字型、相機、模擬狀態與 GPU 繪製完成，時間由幀索引決定。

遇到 WebGL context lost、壞圖或像素檢查失敗時，丟出 `InvalidFrame` 或 `RuntimeError`，由 `restart()` 重建頁面／context、貼圖、字型及時間軸，重畫**原幀號**。預設同一幀最多嘗試三次；仍失敗時保留幀號、錯誤與診斷畫面，修復後繼續。只將通過的幀寫入編碼器，維持原片長與順序。刻意全黑、全白或其他純色只對分鏡指定的幀號放行，且要比對預期顏色。完整影片編碼後再解碼，核對幀數；失敗輸出不會取代已完成的影片。

## 語音校對、配樂與音效

1. 逐句核對畫面原文和口說稿。把多音字放回句意，人名、品牌、地名優先採用委託人或當事人的讀法。金額、年份、序號、百分比、範圍和單位各有讀法，例如同樣是「110」，門牌、電話與數量需要分別處理。
2. 記下每個詞、預期讀音及 TTS 實際輸入。同音替字只進語音稿，畫面文字維持原文。某類沒有疑點時可記空清單。遇到有多種合理念法的專名，記下暫用值、理由及需要回聽的字。這一步由製作者作語意判讀；程式會在啟動 TTS 前檢查校對欄位是否填齊。
3. 用本地 TTS 或使用者指定的聲音製作旁白。配樂可用振盪器、和弦、包絡和節拍，音效可用噪聲濾波、物理模型或音色合成。依劇情安排入點、靜默與混音，旁白出現時壓低音樂。音色、聲道及音樂編制由製作者依片子決定。
4. 回聽實際念法、語速、停頓和混音。排程以合成結果的實際長度核對；超過鏡頭時間就改節奏、用字或剪接，再次合成。將未確定處對應到最終版時間碼，剪接若移動了句子要同步更新。

[六秒聲音範例](sound-example.json)示範校對欄位、和弦頻率、海浪及鐘聲。範例裡的港名是虛構的，用來演示如何標記待聽讀音。

```sh
python3 scripts/sound.py references/sound-example.json --out /tmp/mix.wav --report /tmp/listen.json
python3 scripts/render.py --style clear-line --seconds 6 --fps 24 --audio /tmp/mix.wav --video /tmp/film.mp4
```

macOS 預設 `say` 與 Meijia，Linux 可裝 `espeak-ng` 並指定 `--engine espeak-ng --voice cmn`。其他語言改用該語言的聲線。無旁白時可省略 `narration`，配樂與效果同樣各自選用。報告列出每句實際起訖秒數、原文、語音稿與待聽詞；需要更精確的時間碼時，從最終音軌定位該詞。交片前比對最終檔的影音軌及時長，並看片頭片尾、每個剪接點及所有疑讀段落。
