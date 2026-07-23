import { {{Aggregate}} } from '../../domain/{{aggregate}}/{{aggregate}}.aggregate';
import { {{Aggregate}}Repository } from '../ports/{{aggregate}}.repository';

export interface {{Name}}Input {}
export interface {{Name}}Output {}

export class {{Name}}UseCase {
  constructor(private readonly repo: {{Aggregate}}Repository) {}

  async execute(input: {{Name}}Input): Promise<{{Name}}Output> {
    const entity = {{Aggregate}}.create({});
    await this.repo.save(entity);
    return {};
  }
}
