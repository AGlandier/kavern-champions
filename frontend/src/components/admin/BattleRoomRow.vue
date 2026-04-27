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
    <td>{{ room.requires_teamlist ? 'OTS' : 'CTS' }}</td>
    <td>
      <span v-if="room.closed" class="room-row__status--closed">Fermée</span>
      <span v-else class="room-row__status--open">Ouverte</span>
    </td>
    <td>
      <button class="room-row__manage" :disabled="room.closed" @click="goToManager">Manage</button>
    </td>
  </tr>
</template>
