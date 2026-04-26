<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  loading: Boolean,
})
const emit = defineEmits(['submit'])

const teamlist = ref(props.modelValue)

watch(() => props.modelValue, (val) => { teamlist.value = val })
</script>

<template>
  <form class="teamlist-form" @submit.prevent="emit('submit', teamlist)">
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
</template>
