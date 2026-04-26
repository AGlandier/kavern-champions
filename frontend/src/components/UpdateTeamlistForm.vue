<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  loading: Boolean,
})
const emit = defineEmits(['submit'])

const teamlist = ref(props.modelValue)
const validationError = ref(null)

watch(() => props.modelValue, (val) => { teamlist.value = val })

const ALLOWED_PREFIXES = ['https://pokepast.es/', 'https://www.vrpastes.com/']

function isValidUrl(url) {
  return ALLOWED_PREFIXES.some(prefix => url.startsWith(prefix))
}

function handleSubmit() {
  if (!isValidUrl(teamlist.value)) {
    validationError.value = 'L\'URL doit provenir de pokepast.es ou vrpastes.com.'
    return
  }
  validationError.value = null
  emit('submit', teamlist.value)
}
</script>

<template>
  <div class="teamlist-form-wrapper">
    <form class="teamlist-form" @submit.prevent="handleSubmit">
      <label class="teamlist-form__label" for="teamlist-input">Teamlist</label>
      <input
        id="teamlist-input"
        v-model="teamlist"
        class="kc-input teamlist-form__input"
        type="text"
        placeholder="www.pokepast.es/team"
      />
      <button type="submit" class="kc-btn" :disabled="loading">
        Enregistrer
      </button>
    </form>
    <p v-if="validationError" class="teamlist-form__error">{{ validationError }}</p>
  </div>
</template>
