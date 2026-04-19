<script setup>
import { useCreateRoomForm } from './CreateRoomForm.js'
import '../../styles/admin.css'

const { roomName, creating, error, createRoom } = useCreateRoomForm()
</script>

<template>
  <div class="admin__create">
    <span class="admin__create-label">Créer une room :</span>
    <input
      v-model="roomName"
      type="text"
      class="kc-input"
      placeholder="Nom de la room"
      @keyup.enter="createRoom"
    />
    <button class="kc-btn" :disabled="creating" @click="createRoom">
      {{ creating ? '…' : 'Créer' }}
    </button>
    <span v-if="error" class="admin__error">{{ error }}</span>
  </div>
</template>
