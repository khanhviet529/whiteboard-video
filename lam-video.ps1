<#
.SYNOPSIS
  Mot lenh: screenplay YAML -> mp4 co giong doc. Soi loi, sinh giong, dung video.

.DESCRIPTION
  Goi lien mach ba buoc van phai lam bang tay truoc day:
    1. src/lint.py    soi loi cach viet cau TRUOC khi ton thoi gian sinh giong
    2. src/render.py  sinh giong (co cache) + dung frame + mux
    3. bao ket qua    duong dan, dung luong, thoi gian tung buoc

  Chi con mot engine: voicestudio. Mac dinh tro vao http://127.0.0.1:3900;
  dat -Colab <url> de dung backend GPU tren Colab qua tunnel.

  Vong lap nhanh de chot cau chu: -ChiAudio (bo han buoc dung frame).

.EXAMPLE
  # chot cau chu: chi nghe loi doc, bo han buoc dung hinh (~40s tren T4)
  .\lam-video.ps1 screenplays\10-cache-stampede.yaml -Colab $env:VS_API -ChiAudio

.EXAMPLE
  # ban cuoi: giong clone qua Colab T4, ghim seed de re-render khong troi giong
  .\lam-video.ps1 screenplays\10-cache-stampede.yaml `
      -Colab https://abc-def.trycloudflare.com -Seed 12345

.EXAMPLE
  # ca loat
  Get-ChildItem screenplays\7*.yaml | ForEach-Object {
      .\lam-video.ps1 $_.FullName -Colab $env:VS_API -Seed 12345 }
#>
[CmdletBinding()]
param(
    # File screenplay. Bat buoc.
    [Parameter(Mandatory, Position = 0)]
    [string]$Screenplay,

    # URL backend VoiceStudio. Bo trong = http://127.0.0.1:3900 (may nay).
    # Vi du: -Colab https://abc.trycloudflare.com
    [string]$Colab,

    # Ten giong clone trong giong\manifest.json cua repo nay (namtre_v2...).
    # Bo trong = giong mac dinh trong tts.py (VS_DEFAULT_VOICE).
    [string]$Giong,

    # Ghim seed -> re-render ra dung audio cu. Nen dat cho ban cuoi.
    [int]$Seed,

    # Ban nhap: x264 preset veryfast + 20fps. Nhanh hon nhieu, hinh kem muot hon.
    [switch]$Nhanh,

    # Chi xuat wav loi doc, khong dung video. Dung khi chi muon nghe lai cau chu.
    [switch]$ChiAudio,

    # So tien trinh dung frame. 0 = tu chon theo so nhan CPU.
    [int]$Jobs = 0,

    # Bo qua buoc lint (khong khuyen khich - lint mien phi va bat loi som).
    [switch]$BoLint
)

$ErrorActionPreference = 'Stop'
$PY = 'py'
$goc = $PSScriptRoot
Set-Location $goc

if (-not (Test-Path $Screenplay)) {
    Write-Host "khong thay screenplay: $Screenplay" -ForegroundColor Red
    exit 1
}
$ten = [System.IO.Path]::GetFileNameWithoutExtension($Screenplay)

# Chi con mot engine. `edge` da bo khoi tool (giong khong dat yeu cau).
$engine = 'voicestudio'
if ($Colab) { $env:VS_API = $Colab.TrimEnd('/') }
if (-not $env:VS_API) { $env:VS_API = 'http://127.0.0.1:3900' }

Write-Host ""
Write-Host "=== $ten ===" -ForegroundColor Cyan
Write-Host "  backend  : $($env:VS_API)"
if ($Giong) { Write-Host "  giong    : $Giong" }
if ($Seed)  { Write-Host "  seed     : $Seed" }
Write-Host ("  che do   : {0}" -f $(if ($Nhanh) { 'ban nhap (veryfast, 20fps)' }
                                   else { 'ban cuoi (medium, 30fps)' }))

$dong_ho = [System.Diagnostics.Stopwatch]::StartNew()
$t_bat_dau = Get-Date
$moc = @{}

# ---- 1. lint -------------------------------------------------------------
if (-not $BoLint) {
    Write-Host "`n[1/2] soi screenplay..." -ForegroundColor Yellow
    $t = $dong_ho.Elapsed
    & $PY src\lint.py $Screenplay --engine $engine
    $ma = $LASTEXITCODE
    $moc['lint'] = $dong_ho.Elapsed - $t
    if ($ma -ne 0) {
        Write-Host "`nlint bao LOI - sua screenplay roi chay lai." -ForegroundColor Red
        Write-Host "(muon dung tiep bat chap: them -BoLint)" -ForegroundColor DarkGray
        exit 1
    }
}

# ---- 2. render -----------------------------------------------------------
Write-Host "`n[2/2] sinh giong + dung video..." -ForegroundColor Yellow
$args_r = @($Screenplay, '--engine', $engine, '-j', $Jobs)
if ($Giong)    { $args_r += @('--voice', $Giong) }
if ($Seed)     { $args_r += @('--seed', $Seed) }
if ($ChiAudio) { $args_r += '--audio-only' }
if ($Nhanh)    { $args_r += @('--preset', 'veryfast', '--fps', '20') }

$t = $dong_ho.Elapsed
& $PY src\render.py @args_r
$ma = $LASTEXITCODE
$moc['render'] = $dong_ho.Elapsed - $t
if ($ma -ne 0) {
    Write-Host "`nrender that bai (ma $ma)." -ForegroundColor Red
    exit $ma
}

# ---- 3. bao ket qua ------------------------------------------------------
$dong_ho.Stop()
Write-Host "`n=== xong sau $([int]$dong_ho.Elapsed.TotalMinutes)p $($dong_ho.Elapsed.Seconds)s ===" -ForegroundColor Green
foreach ($k in 'lint', 'render') {
    if ($moc.ContainsKey($k)) {
        Write-Host ("  {0,-8} {1,5:N1} phut" -f $k, $moc[$k].TotalMinutes)
    }
}

# Liet ke dung thu vua tao ra, khong lay lai ban mp4 cu tu luot render truoc:
# -ChiAudio khong sinh mp4, ma `out\<ten>.mp4` co the con nam do tu hom truoc va
# in ra thi nguoi doc tuong luot nay vua dung video.
$can = if ($ChiAudio) { @("out\$ten.wav", 'build\voice.wav') }
       else { @("out\$ten.mp4", "out\$ten-$engine.mp4") }
$ra = Get-ChildItem $can -EA SilentlyContinue |
      Where-Object { $_.LastWriteTime -gt $t_bat_dau } |
      Sort-Object LastWriteTime -Descending
foreach ($f in $ra) {
    Write-Host ("  {0,-40} {1,7:N1} MB" -f $f.FullName, ($f.Length / 1MB))
}

# KHONG tu mo explorer. Da lam render lan sau fail: Explorer giu handle de tao
# thumbnail cho part-*.mp4 trong build\, ffmpeg mo ghi khong duoc va chet voi
# stderr RONG - mat mot luot render de tim ra. Doi lai bang mot dong duong dan.

