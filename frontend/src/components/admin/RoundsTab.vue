<script setup>
import BattleRow from './BattleRow.vue'

defineProps({
  room:             { type: Object, default: null },
  battles:          { type: Array,  required: true },
  displayRound:     { type: Number, required: true },
  loading:          { type: Boolean, default: false },
  hasPrevRound:     { type: Boolean, default: false },
  hasNextRound:     { type: Boolean, default: false },
})

defineEmits(['battleEnded', 'prevRound', 'nextRound'])
</script>

<template>
  <div class="admin__table-wrapper">
    <p v-if="room && room.round === 0" class="admin__empty">
      Aucun round démarré — lancez le premier round.
    </p>
    <p v-else-if="loading">Chargement…</p>
    <table v-else class="admin__table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Joueur 1</th>
          <th>Joueur 2</th>
          <th>Room Champions</th>
          <th>État</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <BattleRow
          v-for="b in battles"
          :key="b.id"
          :battle="b"
          @ended="$emit('battleEnded', $event)"
        />
        <tr v-if="battles.length === 0">
          <td colspan="6" class="admin__empty">Aucune battle pour ce round.</td>
        </tr>
      </tbody>
    </table>
  </div>

  <div v-if="room && room.round > 0" class="admin__pagination">
    <button class="admin__pagination-btn" :disabled="!hasPrevRound" @click="$emit('prevRound')">
      &#8592; {{ hasPrevRound ? `Round ${displayRound - 1}` : '' }}
    </button>
    <span class="admin__round-indicator">Round {{ displayRound }}</span>
    <button class="admin__pagination-btn" :disabled="!hasNextRound" @click="$emit('nextRound')">
      {{ hasNextRound ? `Round ${displayRound + 1}` : '' }} &#8594;
    </button>
  </div>
</template>
