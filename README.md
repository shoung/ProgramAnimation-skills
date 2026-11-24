# ProgramAnimation-skills

把一句動畫想法做成可播放的影片。先逐題訪談，把劇本與分鏡寫在對話裡；定稿後用真實預覽選畫法，再用程式生成畫面、旁白、音樂和音效。題材、片長、螢幕方向與製作引擎都可依委託調整。

![同一座燈塔的十二種程序化畫法](skills/program-animation/assets/gallery.jpg)

[逐款看大圖、範例原始碼與取捨](skills/program-animation/references/styles.md)

## 安裝與使用

將這兩個技能資料夾一起放入 Codex 的 skills 目錄，保留原資料夾名稱。首次安裝可執行：

```sh
git clone https://github.com/shoung/ProgramAnimation-skills.git
cd ProgramAnimation-skills
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R skills/animation-grill skills/program-animation "${CODEX_HOME:-$HOME/.codex}/skills/"
```

開啟新的 Codex 對話，輸入「用 `$program-animation` 幫我做一支給家人看的直式短片。我最記得外婆每天拉開早餐店鐵門的聲音。」也可以用 `$animation-grill` 先把想法問清楚。

| 技能 | 工作 |
|---|---|
| [program-animation](skills/program-animation/SKILL.md) | 編寫逐鏡稿、推薦三款畫法、依選擇製作、檢查每一幀、合成與校對聲音並交片。 |
| [animation-grill](skills/animation-grill/SKILL.md) | 一次追問一個創作決定。初稿整理創作簡報；修改時整理時間碼、修改目標、驗收方式及保留項目，等同意後才動手。 |

## 試畫一鏡

以下指令從本倉庫根目錄執行。需 Python 3.9 以上；輸出影片另需含 libx264 的 FFmpeg 及 ffprobe。安裝技能和觀看隨附的 PNG 可直接使用上方步驟。

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r skills/program-animation/requirements.txt
python skills/program-animation/scripts/render.py --style one-bit --png /tmp/lighthouse.png
python skills/program-animation/scripts/render.py --style paper-cut --seconds 4 --fps 24 --video /tmp/lighthouse.mp4
```

[聲音合成範例、空白幀復原與成片驗證](skills/program-animation/references/production.md)
