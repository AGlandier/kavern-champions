<script setup>
import { useBattleRoomManager } from './BattleRoomManagerView.js'
import RoundsTab from '../../components/admin/RoundsTab.vue'
import PlayersTab from '../../components/admin/PlayersTab.vue'
import '../../styles/admin.css'

const {
  activeTab,
  room, battles, displayRound, loading, error, nextRoundLoading,
  hasPrevRound, hasNextRound, allBattlesFinished,
  goNextRound, onBattleEnded, prevRound, nextRound,
  players, playersLoading, playersError, dropLoading,
  dropPlayer,
  closeRoom, closeRoomLoading, closeRoomError,
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
        :disabled="nextRoundLoading || !allBattlesFinished"
        @click="goNextRound"
      >
        {{ nextRoundLoading ? '…' : 'Round suivant' }}
      </button>
      <button class="kc-btn kc-btn--danger" :disabled="closeRoomLoading || room?.closed" @click="closeRoom">
        {{ closeRoomLoading ? '…' : 'Fermer la room' }}
      </button>
    </div>
    <p v-if="closeRoomError" class="admin__error">{{ closeRoomError }}</p>

    <!-- Onglets -->
    <div class="admin__tabs">
      <button
        class="admin__tab"
        :class="{ 'admin__tab--active': activeTab === 'rounds' }"
        @click="activeTab = 'rounds'"
      >
        Rounds
      </button>
      <button
        class="admin__tab"
        :class="{ 'admin__tab--active': activeTab === 'players' }"
        @click="activeTab = 'players'"
      >
        Players
      </button>
    </div>

    <p v-if="error" class="admin__error">{{ error }}</p>

    <RoundsTab
      v-if="activeTab === 'rounds'"
      :room="room"
      :battles="battles"
      :display-round="displayRound"
      :loading="loading"
      :has-prev-round="hasPrevRound"
      :has-next-round="hasNextRound"
      @battle-ended="onBattleEnded"
      @prev-round="prevRound"
      @next-round="nextRound"
    />

    <PlayersTab
      v-else-if="activeTab === 'players'"
      :players="players"
      :players-loading="playersLoading"
      :players-error="playersError"
      :drop-loading="dropLoading"
      @drop="dropPlayer"
    />
  </div>
</template>
