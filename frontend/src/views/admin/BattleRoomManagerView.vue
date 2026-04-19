<script setup>
import { useBattleRoomManager } from './BattleRoomManagerView.js'
import BattleRow from '../../components/admin/BattleRow.vue'
import '../../styles/admin.css'

const {
  room, battles, displayRound, loading, error, nextRoundLoading,
  hasPrevRound, hasNextRound,
  goNextRound, onBattleEnded, prevRound, nextRound,
} = useBattleRoomManager()
</script>

<template>
  <div class="admin">
    <!-- En-tête -->
    <div class="admin__room-header">
      <h2 class="admin__room-title">
        {{ room ? room.name : '…' }}
      </h2>
      <span v-if="room" class="admin__room-round">Round {{ room.round }}</span>
      <button
        class="kc-btn"
        :disabled="nextRoundLoading"
        @click="goNextRound"
      >
        {{ nextRoundLoading ? '…' : 'Round suivant' }}
      </button>
    </div>

    <p v-if="error" class="admin__error">{{ error }}</p>

    <!-- Table des battles -->
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
            @ended="onBattleEnded"
          />
          <tr v-if="battles.length === 0">
            <td colspan="6" class="admin__empty">Aucune battle pour ce round.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Navigation rounds (masquée si aucun round) -->
    <div v-if="room && room.round > 0" class="admin__pagination">
      <button class="admin__pagination-btn" :disabled="!hasPrevRound" @click="prevRound">
        &#8592; {{ hasPrevRound ? `Round ${displayRound - 1}` : '' }}
      </button>
      <span class="admin__round-indicator">Round {{ displayRound }}</span>
      <button class="admin__pagination-btn" :disabled="!hasNextRound" @click="nextRound">
        {{ hasNextRound ? `Round ${displayRound + 1}` : '' }} &#8594;
      </button>
    </div>
  </div>
</template>
