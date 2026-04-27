<script setup>
defineProps({
  players:        { type: Array,   required: true },
  playersLoading: { type: Boolean, default: false },
  playersError:   { type: String,  default: null },
  dropLoading:    { type: Object,  default: () => ({}) },
})

defineEmits(['drop'])
</script>

<template>
  <p v-if="playersError" class="admin__error">{{ playersError }}</p>
  <div class="admin__table-wrapper">
    <p v-if="playersLoading">Chargement…</p>
    <table v-else class="admin__table">
      <thead>
        <tr>
          <th>Joueur</th>
          <th>Teamlist</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="p in players" :key="p.username">
          <td>{{ p.username }}</td>
          <td>
            <a
              v-if="p.teamlist"
              :href="p.teamlist"
              target="_blank"
              rel="noopener noreferrer"
              class="admin__teamlist-link"
            >{{ p.teamlist }}</a>
            <span v-else class="admin__empty" style="padding: 0;">—</span>
          </td>
          <td>
            <button
              class="kc-btn kc-btn--danger"
              :disabled="dropLoading[p.username]"
              @click="$emit('drop', p.username)"
            >
              {{ dropLoading[p.username] ? '…' : 'Drop' }}
            </button>
          </td>
        </tr>
        <tr v-if="players.length === 0">
          <td colspan="3" class="admin__empty">Aucun participant.</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
