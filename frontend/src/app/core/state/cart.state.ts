import { Injectable } from '@angular/core';
import { Action, Selector, State, StateContext } from '@ngxs/store';

import { CartResponse } from '@core/models/api.models';

export class SetCart {
  static readonly type = '[Cart] Set';
  constructor(public cart: CartResponse) {}
}

export interface CartStateModel {
  cart: CartResponse | null;
  sessionId: string;
}

@State<CartStateModel>({
  name: 'cart',
  defaults: {
    cart: null,
    sessionId: crypto.randomUUID(),
  },
})
@Injectable()
export class CartState {
  @Selector()
  static cart(state: CartStateModel): CartResponse | null {
    return state.cart;
  }

  @Selector()
  static itemCount(state: CartStateModel): number {
    return state.cart?.item_count ?? 0;
  }

  @Selector()
  static sessionId(state: CartStateModel): string {
    return state.sessionId;
  }

  @Action(SetCart)
  setCart(ctx: StateContext<CartStateModel>, action: SetCart) {
    ctx.patchState({ cart: action.cart });
  }
}
