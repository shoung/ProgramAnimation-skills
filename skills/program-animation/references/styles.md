# 十二種視覺樣本

每個「預覽」都是該列程式在相同相位直接繪製的 960 × 540 PNG。構圖保持可比較，材質、光線、空間表現及運動方式各有不同。[觀看總覽](../assets/gallery.jpg)。以使用者的劇本及播放尺寸判斷以下取捨。

| 風格與資源 | 適用的敘事 | 可能遇到的問題及可調整之處 |
|---|---|---|
| 層疊剪紙 [預覽](../assets/previews/paper-cut.png) · [程式](../scripts/styles/paper_cut.py) | 故事書、家庭回憶，景物輪廓與前後遮擋很清楚 | 多人疊在一起會糊成一塊。放大主要剪影、拉開前後景色階，按情節改紙層的移動速度。 |
| 山水水墨 [預覽](../assets/previews/ink-wash.png) · [程式](../scripts/styles/ink_wash.py) | 詩意回憶、呼吸感強的段落；濃墨能把眼睛帶往關鍵動作 | 淡墨與白底容易吃掉細節。把最深的墨留給主體，調整乾筆密度與留白停留時間。 |
| 浮世繪木版 [預覽](../assets/previews/woodblock.png) · [程式](../scripts/styles/woodblock.py) | 旅行、海景、時代敘事；輪廓和版紋建立場面的節奏 | 密集紋樣可能搶戲。按螢幕大小加寬波紋間距，把高對比描邊集中在敘事區。 |
| 青綠金箋 [預覽](../assets/previews/mineral.png) · [程式](../scripts/styles/mineral.py) | 地貌、傳說、探索；用石青、石綠色塊區分山勢與遠近 | 金地會降低淺色角色的辨識度。把面向光線的大色面留給主體，背景減少碎面。 |
| 黏土微縮 [預覽](../assets/previews/clay.png) · [程式](../scripts/styles/clay.py) | 物件擬人、兒童故事、溫暖的產品小劇場 | 太小的五官和手指看不清。放大表演物件，調軟光方向、表面壓痕和動作停頓。 |
| 孔版套色 [預覽](../assets/previews/riso.png) · [程式](../scripts/styles/riso.py) | 音樂節奏、編輯插畫、帶手作感的片頭 | 網點與錯版會干擾小字。穩住網屏座標、給字幕留單色區，按輸出尺寸縮小錯位量。 |
| 莫比烏斯式清線 [預覽](../assets/previews/clear-line.png) · [程式](../scripts/styles/clear_line.py) | 法式科幻漫畫感、異世界或精密道具；以清楚的外輪廓托住粉彩平塗，塔身曲面、山脊和岩壁各有自己的排線 | 遠景線條容易擠在一起。近景外框用較粗的筆，遠景和物件內部減細。讓排線沿背光面的轉折彎曲，在最深處加一層短交叉線。 |
| 復古工程圖 [預覽](../assets/previews/drafting.png) · [程式](../scripts/styles/drafting.py) | 結構講解、設計史、拆解動作；剖面與尺寸線能對準旁白 | 手機上標注容易太小。每鏡只展開必要視圖，局部放大，配合解說依序顯影。 |
| 等角場景模型 [預覽](../assets/previews/isometric.png) · [程式](../scripts/styles/isometric.py) | 空間關係、路徑、系統運作；同時看得見頂面與側面 | 前排物件可能擋住操作。調整方位角與逐步揭示順序，直幅時重新排模型。 |
| 粒子點雲 [預覽](../assets/previews/point-cloud.png) · [程式](../scripts/styles/point_cloud.py) | 記憶重組、掃描顯影、夜景；金色光束掃過紅白塔身，綠色樹冠、銅色岩壁與藍綠海面用不同色粒子顯形 | 粒子太稀會失去輪廓，影片壓縮也會吃點。依材質設定粒子密度，固定採樣位置，縮小並壓縮試看塔身條紋與水面反光。 |
| 1-bit 抖動 [預覽](../assets/previews/one-bit.png) · [程式](../scripts/styles/one_bit.py) | 推理、航海、壓迫或懷舊氣氛，接近《奧伯拉丁的回歸》的雙色讀圖方式 | 密格會閃動，細臉與小字會消失。用兩色輪廓拉開景別，將網格鎖定在畫面座標，用整數倍縮放。 |
| 厚塗油畫 [預覽](../assets/previews/impasto.png) · [程式](../scripts/styles/impasto.py) | 情緒轉折、抒情風景、音樂段落；筆觸可提示風向、水流與力道 | 粗筆觸會蓋掉表情。臉與道具邊緣縮筆，遠景放寬筆觸，固定亂數以保持跨幀連續。 |
