#!/usr/bin/env bash
# Colab에서 받은 body_validation_models ZIP 을 이 폴더로 복사하고 압축 해제합니다.
# 사용법:
#   ./import_from_downloads.sh
#   ./import_from_downloads.sh ~/Downloads/-f.zip
#   ./import_from_downloads.sh /path/to/body_validation_models.zip

set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ZIP_SRC="${1:-$HOME/Downloads/-f.zip}"

if [[ ! -f "$ZIP_SRC" ]]; then
  echo "ZIP 을 찾을 수 없습니다: $ZIP_SRC" >&2
  echo "사용법: $0 [ZIP경로]" >&2
  exit 1
fi

DEST_ZIP="$HERE/body_validation_bundle.zip"
cp -- "$ZIP_SRC" "$DEST_ZIP"
echo "복사됨: $DEST_ZIP"
unzip -o "$DEST_ZIP" -d "$HERE"
echo ""
echo "압축 해제 완료: $HERE"
echo ""
echo "backend/.env 에 예시 (경로는 실제 폴더 구조에 맞게 수정):"
if [[ -d "$HERE/body_validation_models/fashn-human-parser" ]]; then
  echo "  FASHN_HUMAN_PARSER_MODEL=$HERE/body_validation_models/fashn-human-parser"
elif [[ -d "$HERE/fashn-human-parser" ]]; then
  echo "  FASHN_HUMAN_PARSER_MODEL=$HERE/fashn-human-parser"
fi
echo ""
echo "MediaPipe pose (막힌 네트워크 대비):"
if [[ -f "$HERE/body_validation_models/mediapipe_pose/pose_landmarker_heavy.task" ]]; then
  echo "  cp \"$HERE/body_validation_models/mediapipe_pose/pose_landmarker_heavy.task\" /tmp/pose_landmarker_heavy.task"
elif [[ -f "$HERE/mediapipe_pose/pose_landmarker_heavy.task" ]]; then
  echo "  cp \"$HERE/mediapipe_pose/pose_landmarker_heavy.task\" /tmp/pose_landmarker_heavy.task"
fi
