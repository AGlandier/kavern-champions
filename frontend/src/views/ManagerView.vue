<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { user, battle, battleroom } from '../api/index.js'
import { formatRoomCode } from '../utils/formatRoomCode.js'
import { useUserAuth } from '../composables/useUserAuth.js'
import { useSocket } from '../composables/useSocket.js'
import UpdateTeamlistForm from '../components/UpdateTeamlistForm.vue'
import '../styles/admin.css'
import '../styles/manager.css'

const route = useRoute()
const router = useRouter()
const { currentUser } = useUserAuth()

const username = route.query.user
const teamlist = ref('')
const currentBattleroomId = ref(null)
const currentBattleroomRequiresTeamlist = ref(false)
const loading = ref(false)
const loadError = ref(null)
const saveSuccess = ref(false)
const saveError = ref(null)

const activeBattle = ref(null)
const player1Stats = ref(null)
const player2Stats = ref(null)
const endingBattle = ref(false)
const endBattleError = ref(null)
const endBattleSuccess = ref(false)

const roomCode = ref('')
const settingRoom = ref(false)
const setRoomError = ref(null)
const setRoomSuccess = ref(false)

async function loadPlayerStats(battleData) {
  const { player1, player2 } = battleData.content
  const roomId = battleData.battleroom_id
  const [p1, p2] = await Promise.allSettled([
    player1 ? user.getStats(player1, roomId) : Promise.resolve(null),
    player2 ? user.getStats(player2, roomId) : Promise.resolve(null),
  ])
  player1Stats.value = p1.status === 'fulfilled' ? p1.value : null
  player2Stats.value = p2.status === 'fulfilled' ? p2.value : null
}

function onRoomCodeUpdated({ battle_id, champions_room_id }) {
  if (activeBattle.value && activeBattle.value.id === battle_id) {
    activeBattle.value.content.champions_room_id = champions_room_id
  }
}

async function onRoundStarted({ battles }) {
  const myBattle = battles.find(b =>
    !b.finished && (b.content.player1 === username || b.content.player2 === username)
  )
  if (myBattle) {
    activeBattle.value = myBattle
    await loadPlayerStats(myBattle)
  }
}

onMounted(async () => {
  if (!currentUser.value || currentUser.value !== username) {
    router.push({ name: 'login' })
    return
  }
  loading.value = true
  try {
    const [battleData, battleroomData] = await Promise.all([
      user.getActiveBattle(username),
      user.getBattleroom(),
    ])

    currentBattleroomId.value = battleroomData.battleroom_id

    if (currentBattleroomId.value !== null) {
      const [stats, roomData] = await Promise.all([
        user.getStats(username, currentBattleroomId.value),
        battleroom.getById(currentBattleroomId.value),
      ])
      teamlist.value = stats.teamlist ?? ''
      currentBattleroomRequiresTeamlist.value = roomData.requires_teamlist ?? false
    }

    if (battleData.battle) {
      activeBattle.value = battleData.battle
      await loadPlayerStats(battleData.battle)
    }

    if (currentBattleroomId.value !== null) {
      const socket = useSocket()
      socket.emit('join_battleroom', { battleroom_id: currentBattleroomId.value })
      socket.on('room_code_updated', onRoomCodeUpdated)
      socket.on('round_started', onRoundStarted)
    }
  } catch {
    loadError.value = 'Impossible de charger les données.'
  } finally {
    loading.value = false
  }
})

onUnmounted(() => {
  const socket = useSocket()
  if (currentBattleroomId.value !== null) {
    socket.emit('leave_battleroom', { battleroom_id: currentBattleroomId.value })
  }
  socket.off('room_code_updated', onRoomCodeUpdated)
  socket.off('round_started', onRoundStarted)
})

async function handleSave(newTeamlist) {
  saveSuccess.value = false
  saveError.value = null
  if (currentBattleroomId.value === null) {
    saveError.value = 'Vous n\'êtes dans aucune battleroom.'
    return
  }
  loading.value = true
  try {
    await user.updateTeamlist(currentBattleroomId.value, newTeamlist)
    teamlist.value = newTeamlist
    saveSuccess.value = true
  } catch {
    saveError.value = 'Erreur lors de la sauvegarde.'
  } finally {
    loading.value = false
  }
}

function handleRoomCodeInput(e) {
  roomCode.value = e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 8)
}

async function handleSetRoom() {
  setRoomError.value = null
  setRoomSuccess.value = false
  if (roomCode.value.length !== 8) {
    setRoomError.value = 'Le code doit faire exactement 8 caractères (lettres majuscules et chiffres).'
    return
  }
  settingRoom.value = true
  try {
    await battle.setRoom(activeBattle.value.id, roomCode.value)
    activeBattle.value.content.champions_room_id = roomCode.value
    setRoomSuccess.value = true
  } catch {
    setRoomError.value = 'Erreur lors de l\'enregistrement du code.'
  } finally {
    settingRoom.value = false
  }
}

async function handleEndBattle() {
  endBattleError.value = null
  endBattleSuccess.value = false
  endingBattle.value = true
  try {
    await battle.end(activeBattle.value.id, {})
    endBattleSuccess.value = true
    activeBattle.value = null
    player1Stats.value = null
    player2Stats.value = null
  } catch {
    endBattleError.value = 'Erreur lors de la clôture de la battle.'
  } finally {
    endingBattle.value = false
  }
}
</script>

<template>
  <div class="manager">
    <h1 class="manager__title">Mon espace — {{ username }}</h1>

    <p v-if="loadError" class="manager__error">{{ loadError }}</p>

    <template v-else>
      <section class="manager__section">
        <h2 class="manager__section-title">Battle active</h2>

        <p v-if="loading" class="manager__muted">Chargement…</p>

        <p v-else-if="!activeBattle && currentBattleroomRequiresTeamlist && !teamlist" class="manager__muted">Ajoutez votre teamlist pour démarrer !</p>
        <p v-else-if="!activeBattle" class="manager__muted">Aucune battle en cours.</p>

        <div v-else class="manager__battle-card">
          <div class="manager__battle-meta">
            <div class="manager__battle-meta-item">
              <span class="manager__battle-label">Room</span>
              <span class="manager__battle-value">{{ activeBattle.battleroom_id }}</span>
            </div>
            <div class="manager__battle-meta-item">
              <span class="manager__battle-label">Round</span>
              <span class="manager__battle-value">{{ activeBattle.round }}</span>
            </div>
            <div class="manager__battle-meta-item">
              <span class="manager__battle-label">Code salon</span>
              <span class="manager__battle-value">{{ formatRoomCode(activeBattle.content.champions_room_id) }}</span>
            </div>
          </div>

          <div class="manager__battle-players">
            <div class="manager__battle-player">
              <div class="manager__battle-player-name">
                {{ activeBattle.content.player1 ?? '—' }}
              </div>
              <pre class="manager__battle-teamlist">{{ player1Stats?.teamlist || '(pas de teamlist)' }}</pre>
            </div>

            <div class="manager__battle-vs">VS</div>

            <div class="manager__battle-player">
              <div class="manager__battle-player-name">
                {{ activeBattle.content.player2 ?? '—' }}
              </div>
              <pre class="manager__battle-teamlist">{{ player2Stats?.teamlist || '(pas de teamlist)' }}</pre>
            </div>
          </div>

          <div class="manager__battle-set-room">
            <label class="manager__battle-label" for="room-code">Code du salon</label>
            <div class="manager__battle-set-room-row">
              <input
                id="room-code"
                class="kc-input manager__battle-code-input"
                type="text"
                maxlength="8"
                placeholder="AB12CD34"
                :value="roomCode"
                @input="handleRoomCodeInput"
              />
              <button
                class="kc-btn"
                :disabled="settingRoom || roomCode.length !== 8"
                @click="handleSetRoom"
              >
                {{ settingRoom ? 'Envoi…' : 'Valider' }}
              </button>
            </div>
            <p v-if="setRoomSuccess" class="manager__success">Code enregistré.</p>
            <p v-if="setRoomError" class="manager__error">{{ setRoomError }}</p>
          </div>

          <div class="manager__battle-actions">
            <button
              class="kc-btn kc-btn--danger"
              :disabled="endingBattle"
              @click="handleEndBattle"
            >
              {{ endingBattle ? 'Clôture…' : 'Terminer la battle' }}
            </button>
            <p v-if="endBattleSuccess" class="manager__success">Battle terminée.</p>
            <p v-if="endBattleError" class="manager__error">{{ endBattleError }}</p>
          </div>
        </div>
      </section>

      <section v-if="currentBattleroomRequiresTeamlist" class="manager__section">
        <UpdateTeamlistForm :model-value="teamlist" :loading="loading" @submit="handleSave" />
        <p v-if="saveSuccess" class="manager__success">Teamlist mise à jour.</p>
        <p v-if="saveError" class="manager__error">{{ saveError }}</p>
      </section>
    </template>
  </div>
</template>
