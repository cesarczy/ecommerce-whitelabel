import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/shared/api/client';

export function use{{Name}}() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: {{Name}}Input) => api.post('/{{endpoint}}', input),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['{{queryKey}}'] }),
  });
}

export interface {{Name}}Input {}
