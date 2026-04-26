<script setup>
import { useAdminView } from './AdminView.js'
import CreateRoomForm from '../../components/admin/CreateRoomForm.vue'
import BattleRoomRow from '../../components/admin/BattleRoomRow.vue'
import '../../styles/admin.css'

const {
  rooms, playerCounts, loading, error,
  hasPrev, hasNext,
  prevPage, nextPage,
} = useAdminView()
</script>

<template>
  <div class="admin">
    <CreateRoomForm />

    <div class="admin__table-wrapper">
      <p v-if="error" class="admin__error">{{ error }}</p>
      <p v-else-if="loading">Chargement…</p>
      <table v-else class="admin__table">
        <thead>
          <tr>
            <th>Nom</th>
            <th>Nombre de joueurs</th>
            <th>Création</th>
            <th>OTS/CTS</th>
            <th>Etat</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <BattleRoomRow
            v-for="room in rooms"
            :key="room.id"
            :room="room"
            :player-count="playerCounts[room.id] ?? null"
          />
        </tbody>
      </table>
    </div>

    <div class="admin__pagination">
      <button class="admin__pagination-btn" :disabled="!hasPrev" @click="prevPage">
        &lt;&lt; Prev
      </button>
      <button class="admin__pagination-btn" :disabled="!hasNext" @click="nextPage">
        Next &gt;&gt;
      </button>
    </div>
  </div>
</template>
