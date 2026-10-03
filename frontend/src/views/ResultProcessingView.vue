<script setup lang="ts">
import { computed, onMounted, reactive, watch } from 'vue'
import type {
  CustomRule,
  Preset,
  ResultProcessing,
  RuleAction,
  RuleField,
  RuleOperator,
} from '../api/types'
import { useAppStore } from '../composables/appStore'
import ToggleSwitch from '../components/ToggleSwitch.vue'
const props = defineProps<{ initial?: ResultProcessing; saving?: boolean }>()
const emit = defineEmits<{ save: [value: ResultProcessing] }>()
const store = useAppStore()
const errors = reactive<string[]>([])
onMounted(() => {
  if (props.initial === undefined) store.loadAll()
})
const model = reactive<ResultProcessing>({ preset: 'unfiltered', custom_rules: [] })
const cloneProcessing = (value: ResultProcessing): ResultProcessing => ({
  preset: value.preset,
  custom_rules: value.custom_rules.map((rule) => ({ ...rule })),
})
watch(
  () => props.initial ?? store.state.settings?.result_processing,
  (value) => {
    if (value) Object.assign(model, cloneProcessing(value))
  },
  { immediate: true },
)
const presetOptions: { value: Preset; title: string; text: string }[] = [
  {
    value: 'unfiltered',
    title: 'Unfiltered',
    text: 'Preserve the original ICVDB order and include every result.',
  },
  {
    value: 'italian_preferred',
    title: 'Italian preferred',
    text: 'Rank likely Italian releases first without removing fallback results.',
  },
  {
    value: 'italian_only',
    title: 'Italian only',
    text: 'Hard filter results without an explicit Italian marker.',
  },
  { value: 'custom', title: 'Custom', text: 'Apply your ordered score and exclusion rules.' },
]
const operators = (field: RuleField): { value: RuleOperator; label: string }[] =>
  field === 'title' || field === 'provider'
    ? [
        { value: 'contains', label: 'contains' },
        { value: 'not_contains', label: 'does not contain' },
        { value: 'equals', label: 'equals' },
      ]
    : [
        { value: 'equals', label: 'equals' },
        { value: 'gte', label: 'at least' },
        { value: 'lte', label: 'at most' },
      ]
function addRule() {
  if (model.custom_rules.length < 100)
    model.custom_rules.push({
      enabled: true,
      field: 'title',
      operator: 'contains',
      value: '',
      action: 'exclude',
    })
}
function fieldChanged(rule: CustomRule) {
  rule.operator = 'equals'
  rule.value = rule.field === 'size' || rule.field === 'seeders' ? 0 : ''
}
function actionChanged(rule: CustomRule) {
  if (rule.action === 'score') rule.score = 0
  else delete rule.score
}
function validate() {
  errors.splice(0)
  model.custom_rules.forEach((rule, index) => {
    const numeric = rule.field === 'size' || rule.field === 'seeders'
    if (
      !numeric &&
      (typeof rule.value !== 'string' || !rule.value.trim() || rule.value.length > 512)
    )
      errors.push(`Rule ${index + 1} needs a text value up to 512 characters.`)
    if (numeric && (typeof rule.value !== 'number' || !Number.isFinite(rule.value)))
      errors.push(`Rule ${index + 1} needs a finite number.`)
    if (
      rule.action === 'score' &&
      (!Number.isFinite(rule.score) || Math.abs(rule.score ?? 1001) > 1000)
    )
      errors.push(`Rule ${index + 1} score must be between -1000 and 1000.`)
  })
  return !errors.length
}
function submit() {
  if (!validate()) return
  const payload = cloneProcessing(model)
  if (props.initial !== undefined) emit('save', payload)
  else store.saveResultProcessing(payload).catch(() => undefined)
}
const isSaving = computed(() => props.saving ?? store.state.saving)
</script>
<template>
  <section class="page">
    <div class="page-heading">
      <div>
        <p class="eyebrow">Settings</p>
        <h1>Result processing</h1>
        <p>Choose ranking behavior or apply bounded structured rules.</p>
      </div>
    </div>
    <div class="preset-grid" role="radiogroup" aria-label="Result processing preset">
      <label
        v-for="option in presetOptions"
        :key="option.value"
        class="choice-card"
        :class="{ 'choice-card--selected': model.preset === option.value }"
        ><input
          v-model="model.preset"
          type="radio"
          name="preset"
          :value="option.value"
          :aria-label="option.title"
        /><span
          ><strong>{{ option.title }}</strong
          ><small>{{ option.text }}</small></span
        ></label
      >
    </div>
    <div class="notice">
      <strong>Ranking versus hard filtering</strong>
      <p>
        Score rules and Italian preferred reorder matching results. Exclude rules and Italian only
        remove results entirely.
      </p>
    </div>
    <article v-if="model.preset === 'custom'" class="card rules-card">
      <div class="card-heading">
        <div>
          <h2>Custom rules</h2>
          <p>Rules run in order. Disabled rules are saved but ignored.</p>
        </div>
        <button
          class="button button--secondary"
          type="button"
          :disabled="model.custom_rules.length >= 100"
          @click="addRule"
        >
          Add rule
        </button>
      </div>
      <p v-if="!model.custom_rules.length" class="empty-state">No custom rules yet.</p>
      <fieldset v-for="(rule, index) in model.custom_rules" :key="index" class="rule">
        <legend>Rule {{ index + 1 }}</legend>
        <div class="rule-grid">
          <ToggleSwitch v-model="rule.enabled" :label="`Rule ${index + 1} enabled`" /><label
            >Field<select
              v-model="rule.field"
              :aria-label="`Rule ${index + 1} field`"
              @change="fieldChanged(rule)"
            >
              <option value="title">Title</option>
              <option value="provider">Provider</option>
              <option value="size">Size</option>
              <option value="seeders">Seeders</option>
            </select></label
          ><label
            >Operator<select v-model="rule.operator" :aria-label="`Rule ${index + 1} operator`">
              <option
                v-for="operator in operators(rule.field)"
                :key="operator.value"
                :value="operator.value"
              >
                {{ operator.label }}
              </option>
            </select></label
          ><label
            >Value<input
              v-if="rule.field === 'size' || rule.field === 'seeders'"
              v-model.number="rule.value"
              type="number"
              :aria-label="`Rule ${index + 1} value`" /><input
              v-else
              v-model="rule.value"
              type="text"
              maxlength="512"
              :aria-label="`Rule ${index + 1} value`" /></label
          ><label
            >Action<select
              v-model="rule.action"
              :aria-label="`Rule ${index + 1} action`"
              @change="actionChanged(rule)"
            >
              <option value="exclude">Exclude</option>
              <option value="score">Adjust score</option>
            </select></label
          ><label v-if="rule.action === 'score'"
            >Score<input
              v-model.number="rule.score"
              type="number"
              min="-1000"
              max="1000"
              :aria-label="`Rule ${index + 1} score`"
          /></label>
        </div>
        <button
          class="text-button danger-text"
          type="button"
          :aria-label="`Remove rule ${index + 1}`"
          @click="model.custom_rules.splice(index, 1)"
        >
          Remove rule
        </button>
      </fieldset>
    </article>
    <ul v-if="errors.length" class="inline-error" role="alert">
      <li v-for="error in errors" :key="error">{{ error }}</li>
    </ul>
    <p v-else-if="store.state.error" class="inline-error" role="alert">{{ store.state.error }}</p>
    <p v-if="store.state.feedback" class="success-message" role="status">
      {{ store.state.feedback }}
    </p>
    <button class="button" type="button" :disabled="isSaving" @click="submit">
      {{ isSaving ? 'Saving…' : 'Save result processing' }}
    </button>
  </section>
</template>
