import { fireEvent, render, screen } from '@testing-library/vue'
import { describe, expect, it, vi } from 'vitest'
import ResultProcessingView from '../views/ResultProcessingView.vue'

describe('result processing', () => {
  it('reveals custom rules only for Custom and saves a valid structured payload', async () => {
    const save = vi.fn().mockResolvedValue(undefined)
    render(ResultProcessingView, {
      props: { initial: { preset: 'unfiltered', custom_rules: [] }, saving: false },
      attrs: { onSave: save },
    })

    expect(screen.queryByRole('heading', { name: 'Custom rules' })).toBeNull()
    await fireEvent.click(screen.getByLabelText('Custom'))
    await fireEvent.click(screen.getByRole('button', { name: 'Add rule' }))
    expect(screen.getByRole('heading', { name: 'Custom rules' })).toBeTruthy()

    await fireEvent.update(screen.getByLabelText('Rule 1 value'), '1080p')
    await fireEvent.update(screen.getByLabelText('Rule 1 action'), 'score')
    await fireEvent.update(screen.getByLabelText('Rule 1 score'), '25')
    await fireEvent.click(screen.getByRole('button', { name: 'Save result processing' }))
    expect(save).toHaveBeenCalledWith({
      preset: 'custom',
      custom_rules: [
        {
          enabled: true,
          field: 'title',
          operator: 'contains',
          value: '1080p',
          action: 'score',
          score: 25,
        },
      ],
    })

    await fireEvent.update(screen.getByLabelText('Rule 1 field'), 'seeders')
    expect((screen.getByLabelText('Rule 1 operator') as HTMLSelectElement).value).toBe('equals')
    await fireEvent.update(screen.getByLabelText('Rule 1 action'), 'exclude')
    expect(screen.queryByLabelText('Rule 1 score')).toBeNull()
    await fireEvent.click(screen.getByRole('button', { name: 'Remove rule 1' }))
    expect(screen.getByText('No custom rules yet.')).toBeTruthy()
  })

  it('preserves disabled rules and validates numeric values and scores', async () => {
    const save = vi.fn()
    render(ResultProcessingView, {
      props: {
        initial: {
          preset: 'custom',
          custom_rules: [
            {
              enabled: false,
              field: 'seeders',
              operator: 'gte',
              value: 5,
              action: 'score',
              score: 10,
            },
          ],
        },
      },
      attrs: { onSave: save },
    })
    expect((screen.getByRole('switch') as HTMLInputElement).checked).toBe(false)
    await fireEvent.update(screen.getByLabelText('Rule 1 value'), '')
    await fireEvent.update(screen.getByLabelText('Rule 1 score'), '1001')
    await fireEvent.click(screen.getByRole('button', { name: 'Save result processing' }))
    expect(screen.getByRole('alert').textContent).toContain('finite number')
    expect(screen.getByRole('alert').textContent).toContain('-1000 and 1000')
    expect(save).not.toHaveBeenCalled()
  })

  it('enforces the 100-rule builder limit', () => {
    const rules = Array.from({ length: 100 }, () => ({
      enabled: true,
      field: 'title' as const,
      operator: 'contains' as const,
      value: 'x',
      action: 'exclude' as const,
    }))
    render(ResultProcessingView, { props: { initial: { preset: 'custom', custom_rules: rules } } })
    expect((screen.getByRole('button', { name: 'Add rule' }) as HTMLButtonElement).disabled).toBe(
      true,
    )
    expect(screen.getAllByRole('group')).toHaveLength(100)
  })
})
