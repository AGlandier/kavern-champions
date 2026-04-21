<script setup>
import { useBattleRow } from './BattleRow.js'
import { formatRoomCode } from '../../utils/formatRoomCode.js'
import '../../styles/admin.css'

const props = defineProps({
  battle: { type: Object, required: true },
})

const emit = defineEmits(['ended'])

const { forceEnd } = useBattleRow(props, emit)
</script>

<template>
  <tr>
    <td>{{ battle.id }}</td>
    <td>{{ battle.content.player1 ?? '—' }}</td>
    <td>{{ battle.content.player2 ?? '—' }}</td>
    <td>{{ formatRoomCode(battle.content.champions_room_id) }}</td>
    <td>
      <span v-if="battle.finished" class="room-row__status--closed">Terminé</span>
      <span v-else class="room-row__status--open">En cours</span>
    </td>
    <td>
      <button
        class="room-row__manage"
        :disabled="battle.finished"
        @click="forceEnd"
      >
        Forcer fin
      </button>
    </td>
  </tr>
</template>
