<script setup>
import { useBattleRoomRow } from './BattleRoomRow.js'
import '../../styles/admin.css'

const props = defineProps({
  room: { type: Object, required: true },
  playerCount: { type: Number, default: null },
})

const { timeAgo, goToManager } = useBattleRoomRow(props)
</script>

<template>
  <tr>
    <td>{{ room.name }}</td>
    <td>{{ playerCount ?? '…' }}</td>
    <td>{{ timeAgo(room.date) }}</td>
    <td><span class="room-row__status--open">Ouverte</span></td>
    <td>
      <button class="room-row__manage" @click="goToManager">Manage</button>
    </td>
  </tr>
</template>
