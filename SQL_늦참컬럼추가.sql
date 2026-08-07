-- 이그니스 늦참(N분) 정보 영구저장을 위한 컬럼 추가
-- Supabase SQL Editor에서 1회 실행 필요

ALTER TABLE ignis_votes
  ADD COLUMN IF NOT EXISTS late_arrival boolean DEFAULT false,
  ADD COLUMN IF NOT EXISTS late_minutes integer DEFAULT NULL;
