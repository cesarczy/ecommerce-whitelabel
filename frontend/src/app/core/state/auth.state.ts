import { Injectable } from '@angular/core';
import { Action, Selector, State, StateContext } from '@ngxs/store';
import { tap } from 'rxjs';

import { ApiService } from '@core/services/api.service';
import { TokenResponse, UserResponse } from '@core/models/api.models';

export class Login {
  static readonly type = '[Auth] Login';
  constructor(public email: string, public password: string) {}
}

export class Logout {
  static readonly type = '[Auth] Logout';
}

export class LoadProfile {
  static readonly type = '[Auth] Load Profile';
}

export interface AuthStateModel {
  accessToken: string | null;
  refreshToken: string | null;
  user: UserResponse | null;
}

@State<AuthStateModel>({
  name: 'auth',
  defaults: { accessToken: null, refreshToken: null, user: null },
})
@Injectable()
export class AuthState {
  constructor(private readonly api: ApiService) {}

  @Selector()
  static accessToken(state: AuthStateModel): string | null {
    return state.accessToken;
  }

  @Selector()
  static isAuthenticated(state: AuthStateModel): boolean {
    return !!state.accessToken;
  }

  @Selector()
  static user(state: AuthStateModel): UserResponse | null {
    return state.user;
  }

  @Selector()
  static isStaffOrAdmin(state: AuthStateModel): boolean {
    const roles = state.user?.roles ?? [];
    return roles.includes('admin') || roles.includes('staff');
  }

  @Action(Login)
  login(ctx: StateContext<AuthStateModel>, action: Login) {
    return this.api.login({ email: action.email, password: action.password }).pipe(
      tap((tokens: TokenResponse) => {
        ctx.patchState({ accessToken: tokens.access_token, refreshToken: tokens.refresh_token });
        ctx.dispatch(new LoadProfile());
      }),
    );
  }

  @Action(Logout)
  logout(ctx: StateContext<AuthStateModel>) {
    ctx.setState({ accessToken: null, refreshToken: null, user: null });
  }

  @Action(LoadProfile)
  loadProfile(ctx: StateContext<AuthStateModel>) {
    return this.api.me().pipe(tap((user) => ctx.patchState({ user })));
  }
}
