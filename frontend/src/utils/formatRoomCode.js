export function formatRoomCode(code) {
  if (!code) return '—'
  const s = String(code)
  return s.length === 8 ? `${s.slice(0, 4)} ${s.slice(4)}` : s
}
